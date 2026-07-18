"""Connector runtime: multi-entity resumable sync and lease-safe write-back drain.

Synchronous port of the TypeScript SDK's ``defineConnector`` runtime with the
same observable behavior: dependency-ordered entities, per-page checkpoints,
per-page fetch retry, decision-id and SKU-cap warnings, and a write-back drain
that never acks work that outlived its lease.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Literal, Mapping, Optional, Sequence, Tuple

from dateutil.parser import isoparse

from elastly.connector.ports import (
    INGEST_ENTITIES,
    CheckpointStore,
    ConnectorClient,
    ElastlyConnector,
    IngestEntity,
    Page,
    Record,
    WritebackResult,
    WritebackTask,
)
from elastly.errors import BatchNotFoundError, ElastlyError, UnauthorizedError

BATCH_CHECKPOINT_KEY = "batch"
DEFAULT_LEASE_SAFETY_MS = 10_000.0

_ENTITY_FETCHER_NAMES: Dict[IngestEntity, str] = {
    "product": "fetch_products",
    "customer": "fetch_customers",
    "quote": "fetch_quotes",
    "order": "fetch_orders",
}

_logger = logging.getLogger("elastly.connector")

Fetcher = Callable[[Optional[str]], Page[Record]]

WarningKind = Literal["missing_decision_ids", "skipped_over_cap"]

EventType = Literal["page_staged", "entity_completed", "warning", "writeback_settled"]


@dataclass(frozen=True)
class FetchRetryPolicy:
    max_attempts: int = 3
    base_delay_ms: float = 500.0


DEFAULT_FETCH_RETRY_POLICY = FetchRetryPolicy()


@dataclass(frozen=True)
class ConnectorWarning:
    kind: WarningKind
    message: str


@dataclass(frozen=True)
class ConnectorRuntimeEvent:
    type: EventType
    entity: Optional[IngestEntity] = None
    staged: Optional[int] = None
    warning: Optional[ConnectorWarning] = None
    task: Optional[WritebackTask] = None
    result: Optional[WritebackResult] = None


@dataclass(frozen=True)
class SyncReport:
    batch_id: str
    job_id: Optional[str]
    status: Literal["drained", "failed", "committed", "empty"]
    staged: Mapping[IngestEntity, int]
    skipped_over_cap: int
    warnings: Tuple[ConnectorWarning, ...]
    error: Optional[str]


@dataclass(frozen=True)
class DrainReport:
    applied: int
    failed: int
    expired: int


class ConnectorSyncError(ElastlyError):
    def __init__(
        self,
        message: str,
        entity: Optional[IngestEntity] = None,
        report: Optional[SyncReport] = None,
    ) -> None:
        super().__init__(message, None)
        self.entity = entity
        self.report = report


@dataclass
class _QuoteLineTally:
    total: int = 0
    with_decision_id: int = 0


def _default_sleep(ms: float) -> None:
    if ms > 0:
        time.sleep(ms / 1000.0)


def _default_now_ms() -> float:
    return time.time() * 1000.0


def _default_on_event(event: ConnectorRuntimeEvent) -> None:
    if event.type == "warning" and event.warning is not None:
        _logger.warning("%s: %s", event.warning.kind, event.warning.message)


def _lease_epoch_ms(lease_until: str) -> float:
    return isoparse(lease_until).timestamp() * 1000.0


class ConnectorDefinition:
    def __init__(self, ports: ElastlyConnector) -> None:
        self._ports = ports

    def entities(self) -> List[IngestEntity]:
        fetchers = self._fetchers()
        return [entity for entity in INGEST_ENTITIES if entity in fetchers]

    def sync(
        self,
        client: ConnectorClient,
        checkpoints: CheckpointStore,
        *,
        entities: Optional[Sequence[IngestEntity]] = None,
        wait_for_drain: bool = True,
        drain_timeout_ms: Optional[float] = None,
        poll_interval_ms: Optional[float] = None,
        on_event: Optional[Callable[[ConnectorRuntimeEvent], None]] = None,
        retry: Optional[FetchRetryPolicy] = None,
        sleep: Optional[Callable[[float], None]] = None,
    ) -> SyncReport:
        fetchers = self._fetchers()
        requested = tuple(entities) if entities is not None else INGEST_ENTITIES
        selected = [
            entity for entity in INGEST_ENTITIES if entity in requested and entity in fetchers
        ]
        emit = on_event if on_event is not None else _default_on_event
        retry_policy = retry if retry is not None else DEFAULT_FETCH_RETRY_POLICY
        sleep_fn = sleep if sleep is not None else _default_sleep
        warnings: List[ConnectorWarning] = []
        staged: Dict[IngestEntity, int] = {}
        tally = _QuoteLineTally()

        batch_id, resumed = self._resolve_batch(client, checkpoints)

        for entity in selected:
            self._sync_entity(
                entity,
                fetchers[entity],
                batch_id,
                staged,
                tally,
                client,
                checkpoints,
                emit,
                retry_policy,
                sleep_fn,
            )

        if tally.total > 0 and tally.with_decision_id == 0:
            warning = ConnectorWarning(
                kind="missing_decision_ids",
                message=(
                    f"Every one of the {tally.total} ingested quote lines has a null "
                    "pricingDecisionId. Without the decision-id round-trip Elastly cannot learn "
                    "from these quotes: persist the pricingDecisionId returned by prices.get() "
                    "against your quote line and echo it back here."
                ),
            )
            warnings.append(warning)
            emit(ConnectorRuntimeEvent(type="warning", warning=warning))

        total_staged = sum(staged.values())
        if total_staged == 0 and not resumed:
            checkpoints.set(BATCH_CHECKPOINT_KEY, None)
            return SyncReport(
                batch_id=batch_id,
                job_id=None,
                status="empty",
                staged=dict(staged),
                skipped_over_cap=0,
                warnings=tuple(warnings),
                error=None,
            )

        committed = client.ingest.commit(batch_id)
        checkpoints.set(BATCH_CHECKPOINT_KEY, None)

        if not wait_for_drain:
            return SyncReport(
                batch_id=batch_id,
                job_id=committed.job_id,
                status="committed",
                staged=dict(staged),
                skipped_over_cap=0,
                warnings=tuple(warnings),
                error=None,
            )

        final = client.ingest.wait_for_drain(
            batch_id,
            timeout_ms=drain_timeout_ms,
            poll_interval_ms=poll_interval_ms,
            sleep=sleep,
        )
        if final.skipped_over_cap > 0:
            warning = ConnectorWarning(
                kind="skipped_over_cap",
                message=(
                    f"{final.skipped_over_cap} new products were not persisted because the "
                    "workspace is at its SKU cap. The sync succeeded for everything else; raise "
                    "the cap or retire SKUs, then re-sync."
                ),
            )
            warnings.append(warning)
            emit(ConnectorRuntimeEvent(type="warning", warning=warning))
        report = SyncReport(
            batch_id=batch_id,
            job_id=committed.job_id,
            status="drained" if final.status == "drained" else "failed",
            staged=dict(staged),
            skipped_over_cap=final.skipped_over_cap,
            warnings=tuple(warnings),
            error=final.error,
        )
        if report.status == "failed":
            raise ConnectorSyncError(
                f"The sync job failed server-side: {final.error or 'unknown error'}.",
                None,
                report,
            )
        return report

    def drain_writebacks(
        self,
        client: ConnectorClient,
        *,
        limit: Optional[int] = None,
        lease_safety_ms: Optional[float] = None,
        on_event: Optional[Callable[[ConnectorRuntimeEvent], None]] = None,
        now: Optional[Callable[[], float]] = None,
    ) -> DrainReport:
        apply_price = getattr(self._ports, "apply_price", None)
        if not callable(apply_price):
            raise ConnectorSyncError(
                "This connector does not implement apply_price, so it cannot drain write-backs.",
                None,
                None,
            )
        emit = on_event if on_event is not None else _default_on_event
        now_ms = now if now is not None else _default_now_ms
        safety_ms = lease_safety_ms if lease_safety_ms is not None else DEFAULT_LEASE_SAFETY_MS
        applied = failed = expired = 0

        while True:
            tasks = client.writebacks.claim(limit)
            if not tasks:
                return DrainReport(applied=applied, failed=failed, expired=expired)

            results: List[WritebackResult] = []
            for task in tasks:
                lease_expires_at = _lease_epoch_ms(task.lease_until)
                if now_ms() >= lease_expires_at - safety_ms:
                    expired += 1
                    emit(
                        ConnectorRuntimeEvent(
                            type="writeback_settled",
                            task=task,
                            result=WritebackResult(
                                id=task.id,
                                ok=False,
                                error="lease expired before apply_price ran; skipped",
                            ),
                        )
                    )
                    continue
                try:
                    result = apply_price(task)
                except Exception as cause:
                    result = WritebackResult(
                        id=task.id, ok=False, error=str(cause) or "apply_price raised"
                    )
                if now_ms() >= lease_expires_at - safety_ms:
                    expired += 1
                    emit(
                        ConnectorRuntimeEvent(
                            type="writeback_settled",
                            task=task,
                            result=WritebackResult(
                                id=task.id,
                                ok=False,
                                error="lease expired during apply_price; not acked",
                            ),
                        )
                    )
                    continue
                results.append(result)
                emit(ConnectorRuntimeEvent(type="writeback_settled", task=task, result=result))

            if not results:
                return DrainReport(applied=applied, failed=failed, expired=expired)
            outcome = client.writebacks.ack(results)
            applied += outcome.applied
            failed += outcome.failed
            expired += outcome.expired

    def _sync_entity(
        self,
        entity: IngestEntity,
        fetcher: Fetcher,
        batch_id: str,
        staged: Dict[IngestEntity, int],
        tally: _QuoteLineTally,
        client: ConnectorClient,
        checkpoints: CheckpointStore,
        emit: Callable[[ConnectorRuntimeEvent], None],
        retry: FetchRetryPolicy,
        sleep: Callable[[float], None],
    ) -> None:
        cursor = checkpoints.get(entity)
        while True:
            page = self._fetch_page(fetcher, entity, cursor, retry, sleep)
            if page.records:
                result = client.ingest.stage(batch_id, entity, page.records)
                staged[entity] = staged.get(entity, 0) + result.staged
                emit(ConnectorRuntimeEvent(type="page_staged", entity=entity, staged=result.staged))
                if entity == "quote":
                    for quote in page.records:
                        for line in quote.get("lines", ()):
                            tally.total += 1
                            if line.get("pricingDecisionId") is not None:
                                tally.with_decision_id += 1
            if page.next_cursor is None:
                break
            cursor = page.next_cursor
            checkpoints.set(entity, cursor)
        checkpoints.set(entity, None)
        emit(ConnectorRuntimeEvent(type="entity_completed", entity=entity))

    def _resolve_batch(
        self, client: ConnectorClient, checkpoints: CheckpointStore
    ) -> Tuple[str, bool]:
        stored = checkpoints.get(BATCH_CHECKPOINT_KEY)
        if stored:
            try:
                status = client.ingest.status(stored)
                if status.status == "open":
                    return stored, True
            except BatchNotFoundError:
                pass
            for entity in INGEST_ENTITIES:
                checkpoints.set(entity, None)
            checkpoints.set(BATCH_CHECKPOINT_KEY, None)
        opened = self._open_batch(client)
        checkpoints.set(BATCH_CHECKPOINT_KEY, opened.batch_id)
        return opened.batch_id, False

    def _open_batch(self, client: ConnectorClient):
        try:
            return client.ingest.open_batch()
        except UnauthorizedError as cause:
            raise UnauthorizedError(
                code="unauthorized",
                status=401,
                message=(
                    "Invalid or missing API key. Ingest and write-back endpoints require a key "
                    "with the connector scope; an erp or storefront key will not work."
                ),
                request_id=cause.request_id,
            ) from cause

    def _fetch_page(
        self,
        fetcher: Fetcher,
        entity: IngestEntity,
        cursor: Optional[str],
        retry: FetchRetryPolicy,
        sleep: Callable[[float], None],
    ) -> Page[Record]:
        attempt = 0
        while True:
            try:
                return fetcher(cursor)
            except Exception as cause:
                attempt += 1
                if attempt >= retry.max_attempts:
                    raise ConnectorSyncError(
                        f"{_ENTITY_FETCHER_NAMES[entity]} failed after {retry.max_attempts} "
                        "attempts. The checkpoint was persisted after the last successful page, "
                        "so a re-run resumes there.",
                        entity,
                        None,
                    ) from cause
                sleep(retry.base_delay_ms * 2 ** (attempt - 1))

    def _fetchers(self) -> Dict[IngestEntity, Fetcher]:
        fetchers: Dict[IngestEntity, Fetcher] = {
            "product": self._ports.fetch_products,
            "customer": self._ports.fetch_customers,
        }
        optional_fetchers: Tuple[Tuple[IngestEntity, str], ...] = (
            ("quote", "fetch_quotes"),
            ("order", "fetch_orders"),
        )
        for entity, name in optional_fetchers:
            optional = getattr(self._ports, name, None)
            if callable(optional):
                fetchers[entity] = optional
        return fetchers


def define_connector(ports: ElastlyConnector) -> ConnectorDefinition:
    return ConnectorDefinition(ports)
