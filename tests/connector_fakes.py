from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence

from elastly.connector import (
    AckOutcome,
    BatchCreated,
    BatchStatus,
    CommitResult,
    StageResult,
    WritebackResult,
    WritebackTask,
)


def product(i: int) -> Dict[str, Any]:
    return {
        "sku": f"SKU-{i}",
        "name": f"P{i}",
        "category": "widgets",
        "costCents": 100,
        "currentPriceCents": 200,
    }


def customer(i: int) -> Dict[str, Any]:
    return {"name": f"C{i}", "externalId": f"cust-{i}"}


def quote(i: int, pricing_decision_id: Optional[str]) -> Dict[str, Any]:
    return {
        "externalId": f"q-{i}",
        "customerExternalId": "cust-1",
        "outcome": "won",
        "createdAt": "2026-07-16T10:00:00Z",
        "lines": [
            {
                "productSku": "SKU-1",
                "quantity": 2,
                "costCents": 100,
                "quotedPriceCents": 210,
                "pricingDecisionId": pricing_decision_id,
            }
        ],
    }


def writeback_task(task_id: str, lease_until: str) -> WritebackTask:
    return WritebackTask(
        id=task_id,
        product_sku="SKU-1",
        product_external_id="ext-1",
        price_cents=1500,
        currency="USD",
        lease_until=lease_until,
    )


class FakeIngestClient:
    def __init__(
        self,
        staged: List[Dict[str, Any]],
        *,
        drain_status: Optional[Dict[str, Any]] = None,
        batch_status: Optional[Dict[str, Any]] = None,
        open_batch_error: Optional[Exception] = None,
    ) -> None:
        self._staged = staged
        self._drain_status = drain_status or {}
        self._batch_status = batch_status or {}
        self._open_batch_error = open_batch_error
        self.committed = False
        self.opened = 0

    def open_batch(self) -> BatchCreated:
        if self._open_batch_error is not None:
            raise self._open_batch_error
        self.opened += 1
        return BatchCreated(batch_id=f"batch-{self.opened}", connector_id="push_erp")

    def stage(self, batch_id: str, entity: str, records: Sequence[Any]) -> StageResult:
        self._staged.append({"entity": entity, "count": len(records)})
        return StageResult(staged=len(records))

    def commit(self, batch_id: str) -> CommitResult:
        self.committed = True
        return CommitResult(job_id="job-1")

    def status(self, batch_id: str) -> BatchStatus:
        defaults = {"status": "committed" if self.committed else "open"}
        return BatchStatus(**{**defaults, **self._batch_status})

    def wait_for_drain(self, batch_id: str, **kwargs: Any) -> BatchStatus:
        return BatchStatus(**{**{"status": "drained"}, **self._drain_status})


class FakeWritebacksClient:
    def __init__(self, task_batches: List[List[WritebackTask]]) -> None:
        self._task_batches = list(task_batches)
        self.acked: List[List[WritebackResult]] = []

    def claim(self, limit: Optional[int] = None) -> Sequence[WritebackTask]:
        return self._task_batches.pop(0) if self._task_batches else []

    def ack(self, results: Sequence[WritebackResult]) -> AckOutcome:
        self.acked.append(list(results))
        return AckOutcome(
            applied=sum(1 for r in results if r.ok),
            failed=sum(1 for r in results if not r.ok),
            expired=0,
        )


class FakeConnectorClient:
    def __init__(
        self,
        *,
        drain_status: Optional[Dict[str, Any]] = None,
        batch_status: Optional[Dict[str, Any]] = None,
        open_batch_error: Optional[Exception] = None,
        writeback_tasks: Optional[List[List[WritebackTask]]] = None,
    ) -> None:
        self.staged: List[Dict[str, Any]] = []
        self.ingest = FakeIngestClient(
            self.staged,
            drain_status=drain_status,
            batch_status=batch_status,
            open_batch_error=open_batch_error,
        )
        self.writebacks = FakeWritebacksClient(writeback_tasks or [])

    @property
    def acked(self) -> List[List[WritebackResult]]:
        return self.writebacks.acked


def connector_ports(**methods: Any) -> SimpleNamespace:
    return SimpleNamespace(**methods)
