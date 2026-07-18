"""Narrow ports the connector runtime depends on, mirroring the TypeScript SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
)

IngestEntity = Literal["product", "customer", "quote", "order"]

INGEST_ENTITIES: Tuple[IngestEntity, ...] = ("product", "customer", "quote", "order")

Record = Mapping[str, Any]

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    records: Sequence[T]
    next_cursor: Optional[str] = None


@dataclass(frozen=True)
class BatchCreated:
    batch_id: str
    connector_id: str


@dataclass(frozen=True)
class StageResult:
    staged: int


@dataclass(frozen=True)
class CommitResult:
    job_id: str


@dataclass(frozen=True)
class BatchStatus:
    status: str
    entities: Sequence[str] = ()
    record_count: int = 0
    skipped_over_cap: int = 0
    error: Optional[str] = None


@dataclass(frozen=True)
class WritebackTask:
    id: str
    product_sku: str
    product_external_id: str
    price_cents: float
    currency: str
    lease_until: str
    exchange_rate_to_base: Optional[float] = None
    reason_summary: Optional[str] = None
    pricing_decision_id: Optional[str] = None
    target: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WritebackResult:
    id: str
    ok: bool
    error: Optional[str] = None


@dataclass(frozen=True)
class AckOutcome:
    applied: int
    failed: int
    expired: int


class ElastlyConnector(Protocol):
    """The user-implemented connector port.

    ``fetch_quotes``, ``fetch_orders``, and ``apply_price`` are optional
    capabilities: the runtime discovers them with ``getattr`` so a connector
    only implements what its source system supports.
    """

    def fetch_products(self, cursor: Optional[str]) -> Page[Record]: ...

    def fetch_customers(self, cursor: Optional[str]) -> Page[Record]: ...


class CheckpointStore(Protocol):
    def get(self, key: str) -> Optional[str]: ...

    def set(self, key: str, cursor: Optional[str]) -> None: ...


class ConnectorIngestClient(Protocol):
    def open_batch(self) -> BatchCreated: ...

    def stage(
        self, batch_id: str, entity: IngestEntity, records: Sequence[Record]
    ) -> StageResult: ...

    def commit(self, batch_id: str) -> CommitResult: ...

    def status(self, batch_id: str) -> BatchStatus: ...

    def wait_for_drain(
        self,
        batch_id: str,
        *,
        poll_interval_ms: Optional[float] = None,
        timeout_ms: Optional[float] = None,
        sleep: Optional[Callable[[float], None]] = None,
    ) -> BatchStatus: ...


class ConnectorWritebacksClient(Protocol):
    def claim(self, limit: Optional[int] = None) -> Sequence[WritebackTask]: ...

    def ack(self, results: Sequence[WritebackResult]) -> AckOutcome: ...


class ConnectorClient(Protocol):
    @property
    def ingest(self) -> ConnectorIngestClient: ...

    @property
    def writebacks(self) -> ConnectorWritebacksClient: ...
