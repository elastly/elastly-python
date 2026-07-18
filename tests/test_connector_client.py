import json
from types import SimpleNamespace

import pytest

import elastly
from connector_fakes import product, quote
from elastly.api.ingest_api import IngestApi
from elastly.connector import (
    AckOutcome,
    DrainTimeoutError,
    IngestClient,
    WritebackResult,
    WritebacksClient,
)
from elastly.errors import BatchNotFoundError, UnauthorizedError
from elastly.exceptions import ApiException
from elastly.models.ack_writebacks_response import AckWritebacksResponse
from elastly.models.batch_created_response import BatchCreatedResponse
from elastly.models.batch_status_response import BatchStatusResponse
from elastly.models.claim_writebacks_response import ClaimWritebacksResponse
from elastly.models.commit_batch_response import CommitBatchResponse
from elastly.models.stage_records_response import StageRecordsResponse


BATCH_ID = "11111111-1111-4111-8111-111111111111"


def api_exception(status, code):
    exc = ApiException(
        status=status,
        reason="error",
        body=json.dumps({"error": {"code": code, "message": "boom", "requestId": "req_1"}}),
    )
    exc.headers = {"x-elastly-request-id": "req_1"}
    return exc


def batch_status(status, skipped_over_cap=0, error=None):
    return BatchStatusResponse(
        status=status,
        entities=[],
        recordCount=0,
        skippedOverCap=skipped_over_cap,
        error=error,
    )


class FakeIngestApi:
    def __init__(self, statuses=None, error=None):
        self.stage_calls = []
        self.statuses = list(statuses or [])
        self.error = error

    def create_ingest_batch(self):
        if self.error is not None:
            raise self.error
        return BatchCreatedResponse(batchId="batch-1", connectorId="push_erp")

    def stage_ingest_records(self, batch_id, request):
        if self.error is not None:
            raise self.error
        payload = request.actual_instance
        self.stage_calls.append(
            {"batch_id": batch_id, "entity": payload["entity"], "count": len(payload["records"])}
        )
        return StageRecordsResponse(staged=len(payload["records"]))

    def commit_ingest_batch(self, batch_id):
        if self.error is not None:
            raise self.error
        return CommitBatchResponse(jobId="job-1")

    def get_ingest_batch_status(self, batch_id):
        if self.error is not None:
            raise self.error
        return self.statuses.pop(0)


class FakeWritebacksApi:
    def __init__(self, tasks=None, error=None):
        self.tasks = tasks or []
        self.error = error
        self.claim_requests = []
        self.ack_requests = []

    def claim_writebacks(self, request):
        if self.error is not None:
            raise self.error
        self.claim_requests.append(request)
        return ClaimWritebacksResponse.from_dict({"tasks": self.tasks})

    def ack_writebacks(self, request):
        if self.error is not None:
            raise self.error
        self.ack_requests.append(request)
        ok = sum(1 for r in request.results if r.ok)
        return AckWritebacksResponse(applied=ok, failed=len(request.results) - ok, expired=0)


class FakeClock:
    def __init__(self):
        self.ms = 0.0

    def __call__(self):
        return self.ms


def test_stage_chunks_records_into_batches_of_one_thousand():
    api = FakeIngestApi()
    client = IngestClient(api)
    result = client.stage(BATCH_ID, "product", [product(i) for i in range(2500)])
    assert result.staged == 2500
    assert [call["count"] for call in api.stage_calls] == [1000, 1000, 500]
    assert all(call["entity"] == "product" for call in api.stage_calls)


def test_stage_serializes_quote_records_through_the_real_generated_api(monkeypatch):
    captured = {}
    api_client = elastly.ApiClient(elastly.Configuration(access_token="key"))

    def fake_call_api(
        method, url, header_params=None, body=None, post_params=None, _request_timeout=None
    ):
        captured["method"] = method
        captured["url"] = url
        captured["body"] = body
        return SimpleNamespace(read=lambda: None)

    monkeypatch.setattr(api_client, "call_api", fake_call_api)
    monkeypatch.setattr(
        api_client,
        "response_deserialize",
        lambda response_data, response_types_map: SimpleNamespace(
            data=StageRecordsResponse(staged=1)
        ),
    )
    client = IngestClient(IngestApi(api_client))
    result = client.stage(BATCH_ID, "quote", [quote(1, None)])
    assert result.staged == 1
    assert captured["method"] == "POST"
    assert BATCH_ID in captured["url"]
    assert captured["body"]["entity"] == "quote"
    record = captured["body"]["records"][0]
    assert record["createdAt"] == "2026-07-16T10:00:00Z"
    assert record["lines"][0]["pricingDecisionId"] is None


def test_open_batch_maps_api_exceptions_to_typed_errors():
    client = IngestClient(FakeIngestApi(error=api_exception(401, "unauthorized")))
    with pytest.raises(UnauthorizedError):
        client.open_batch()


def test_status_maps_batch_not_found_to_the_typed_error():
    client = IngestClient(FakeIngestApi(error=api_exception(404, "batch_not_found")))
    with pytest.raises(BatchNotFoundError):
        client.status(BATCH_ID)


def test_wait_for_drain_polls_until_the_batch_drains():
    clock = FakeClock()
    delays = []

    def sleep(ms):
        delays.append(ms)
        clock.ms += ms

    api = FakeIngestApi(
        statuses=[batch_status("committed"), batch_status("committed"), batch_status("drained")]
    )
    client = IngestClient(api, clock=clock, sleep=sleep)
    status = client.wait_for_drain(BATCH_ID, poll_interval_ms=100)
    assert status.status == "drained"
    assert delays == [100, 100]


def test_wait_for_drain_raises_after_the_timeout():
    clock = FakeClock()

    def sleep(ms):
        clock.ms += ms

    api = FakeIngestApi(statuses=[batch_status("committed") for _ in range(10)])
    client = IngestClient(api, clock=clock, sleep=sleep)
    with pytest.raises(DrainTimeoutError):
        client.wait_for_drain(BATCH_ID, poll_interval_ms=100, timeout_ms=250)


def test_claim_maps_generated_tasks_to_writeback_tasks():
    api = FakeWritebacksApi(
        tasks=[
            {
                "id": "w-1",
                "productSku": "SKU-1",
                "productExternalId": "ext-1",
                "priceCents": 1500,
                "currency": "USD",
                "leaseUntil": "2026-07-18T10:00:00Z",
                "pricingDecisionId": "dec-1",
                "target": {"quoteExternalId": "q-1"},
            }
        ]
    )
    client = WritebacksClient(api)
    tasks = client.claim(50)
    assert len(tasks) == 1
    assert tasks[0].id == "w-1"
    assert tasks[0].product_sku == "SKU-1"
    assert tasks[0].lease_until == "2026-07-18T10:00:00Z"
    assert tasks[0].pricing_decision_id == "dec-1"
    assert tasks[0].target == {"quoteExternalId": "q-1"}
    assert api.claim_requests[0].limit == 50


def test_ack_maps_results_and_returns_the_outcome():
    api = FakeWritebacksApi()
    client = WritebacksClient(api)
    outcome = client.ack(
        [
            WritebackResult(id="w-1", ok=True),
            WritebackResult(id="w-2", ok=False, error="ERP said no"),
        ]
    )
    assert outcome == AckOutcome(applied=1, failed=1, expired=0)
    sent = api.ack_requests[0].results
    assert [(r.id, r.ok, r.error) for r in sent] == [
        ("w-1", True, None),
        ("w-2", False, "ERP said no"),
    ]


def test_ack_short_circuits_on_an_empty_result_list():
    api = FakeWritebacksApi(error=RuntimeError("must not be called"))
    client = WritebacksClient(api)
    assert client.ack([]) == AckOutcome(applied=0, failed=0, expired=0)
