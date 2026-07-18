"""Concrete connector client composed over the generated ingest and write-back APIs."""

from __future__ import annotations

import time
from typing import Any, Callable, List, Optional, Sequence, TypeVar
from uuid import UUID

from elastly.api.ingest_api import IngestApi
from elastly.api.writebacks_api import WritebacksApi
from elastly.connector.ports import (
    AckOutcome,
    BatchCreated,
    BatchStatus,
    CommitResult,
    IngestEntity,
    Record,
    StageResult,
    WritebackResult,
    WritebackTask,
)
from elastly.errors import ElastlyError
from elastly.exceptions import ApiException
from elastly.models.claim_writebacks_request import ClaimWritebacksRequest
from elastly.models.stage_records_request import StageRecordsRequest
from elastly.models.writeback_ack_request import WritebackAckRequest
from elastly.models.writeback_ack_request_results_inner import WritebackAckRequestResultsInner
from elastly.transport import error_from_api_exception

MAX_RECORDS_PER_CALL = 1000
DEFAULT_POLL_INTERVAL_MS = 2_000.0
DEFAULT_DRAIN_TIMEOUT_MS = 600_000.0

R = TypeVar("R")


class DrainTimeoutError(ElastlyError):
    def __init__(self, batch_id: str, timeout_ms: float) -> None:
        super().__init__(f"Batch {batch_id} did not drain within {timeout_ms:g}ms.", None)
        self.batch_id = batch_id
        self.timeout_ms = timeout_ms


def _monotonic_ms() -> float:
    return time.monotonic() * 1000.0


def _default_sleep(ms: float) -> None:
    if ms > 0:
        time.sleep(ms / 1000.0)


def _call(operation: Callable[[], R]) -> R:
    try:
        return operation()
    except ApiException as exc:
        error, _ = error_from_api_exception(exc)
        raise error from exc


class IngestClient:
    def __init__(
        self,
        api: IngestApi,
        *,
        clock: Optional[Callable[[], float]] = None,
        sleep: Optional[Callable[[float], None]] = None,
    ) -> None:
        self._api = api
        self._clock = clock if clock is not None else _monotonic_ms
        self._sleep = sleep if sleep is not None else _default_sleep

    def open_batch(self) -> BatchCreated:
        response = _call(self._api.create_ingest_batch)
        return BatchCreated(batch_id=response.batch_id, connector_id=response.connector_id)

    def stage(
        self, batch_id: str, entity: IngestEntity, records: Sequence[Record]
    ) -> StageResult:
        staged = 0
        for offset in range(0, len(records), MAX_RECORDS_PER_CALL):
            chunk = records[offset:offset + MAX_RECORDS_PER_CALL]
            # model_construct skips client-side validation on purpose: the generated
            # date-time regex validators run after pydantic coerces the string to a
            # datetime, so every valid RFC3339 quote/order timestamp is rejected.
            # The server validates the payload; this matches the TypeScript SDK.
            request = StageRecordsRequest.model_construct(
                actual_instance={"entity": entity, "records": [dict(record) for record in chunk]}
            )
            response = _call(lambda: self._api.stage_ingest_records(UUID(batch_id), request))
            staged += response.staged
        return StageResult(staged=staged)

    def commit(self, batch_id: str) -> CommitResult:
        response = _call(lambda: self._api.commit_ingest_batch(UUID(batch_id)))
        return CommitResult(job_id=response.job_id)

    def status(self, batch_id: str) -> BatchStatus:
        response = _call(lambda: self._api.get_ingest_batch_status(UUID(batch_id)))
        return BatchStatus(
            status=response.status,
            entities=tuple(response.entities),
            record_count=response.record_count,
            skipped_over_cap=response.skipped_over_cap,
            error=response.error,
        )

    def wait_for_drain(
        self,
        batch_id: str,
        *,
        poll_interval_ms: Optional[float] = None,
        timeout_ms: Optional[float] = None,
        sleep: Optional[Callable[[float], None]] = None,
    ) -> BatchStatus:
        poll = max(
            1.0, poll_interval_ms if poll_interval_ms is not None else DEFAULT_POLL_INTERVAL_MS
        )
        timeout = max(0.0, timeout_ms if timeout_ms is not None else DEFAULT_DRAIN_TIMEOUT_MS)
        sleep_fn = sleep if sleep is not None else self._sleep
        started = self._clock()
        while True:
            status = self.status(batch_id)
            if status.status in ("drained", "failed"):
                return status
            remaining = timeout - (self._clock() - started)
            if remaining <= 0:
                raise DrainTimeoutError(batch_id, timeout)
            sleep_fn(min(poll, remaining))


class WritebacksClient:
    def __init__(self, api: WritebacksApi) -> None:
        self._api = api

    def claim(self, limit: Optional[int] = None) -> Sequence[WritebackTask]:
        request = ClaimWritebacksRequest() if limit is None else ClaimWritebacksRequest(limit=limit)
        response = _call(lambda: self._api.claim_writebacks(request))
        return [
            WritebackTask(
                id=task.id,
                product_sku=task.product_sku,
                product_external_id=task.product_external_id,
                price_cents=task.price_cents,
                currency=task.currency,
                lease_until=task.lease_until,
                exchange_rate_to_base=task.exchange_rate_to_base,
                reason_summary=task.reason_summary,
                pricing_decision_id=task.pricing_decision_id,
                target=task.target,
            )
            for task in response.tasks
        ]

    def ack(self, results: Sequence[WritebackResult]) -> AckOutcome:
        if not results:
            return AckOutcome(applied=0, failed=0, expired=0)
        inner: List[WritebackAckRequestResultsInner] = [
            WritebackAckRequestResultsInner(id=result.id, ok=result.ok, error=result.error)
            for result in results
        ]
        response = _call(lambda: self._api.ack_writebacks(WritebackAckRequest(results=inner)))
        return AckOutcome(
            applied=response.applied, failed=response.failed, expired=response.expired
        )


class ElastlyConnectorClient:
    def __init__(
        self,
        api_client: Any,
        *,
        ingest: Optional[IngestClient] = None,
        writebacks: Optional[WritebacksClient] = None,
    ) -> None:
        self.ingest = ingest if ingest is not None else IngestClient(IngestApi(api_client))
        self.writebacks = (
            writebacks if writebacks is not None else WritebacksClient(WritebacksApi(api_client))
        )


def connector_client(api_client: Any) -> ElastlyConnectorClient:
    return ElastlyConnectorClient(api_client)
