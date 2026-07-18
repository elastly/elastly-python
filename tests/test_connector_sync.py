import logging

import pytest

from connector_fakes import FakeConnectorClient, connector_ports, customer, product, quote
from elastly.connector import (
    ConnectorSyncError,
    FetchRetryPolicy,
    InMemoryCheckpointStore,
    Page,
    define_connector,
)
from elastly.errors import UnauthorizedError


def empty_page(cursor):
    return Page(records=[], next_cursor=None)


def test_pages_through_every_implemented_entity_in_order_advancing_checkpoints():
    cursors_seen = []

    def fetch_products(cursor):
        cursors_seen.append(cursor)
        page = 0 if cursor is None else int(cursor)
        return Page(
            records=[product(page * 500 + i) for i in range(500)],
            next_cursor=str(page + 1) if page < 19 else None,
        )

    def fetch_customers(cursor):
        return Page(records=[customer(1)] if cursor is None else [], next_cursor=None)

    connector = define_connector(
        connector_ports(fetch_products=fetch_products, fetch_customers=fetch_customers)
    )
    client = FakeConnectorClient()
    checkpoints = InMemoryCheckpointStore()
    report = connector.sync(client, checkpoints)

    assert cursors_seen == [None] + [str(i + 1) for i in range(19)]
    assert report.staged["product"] == 10_000
    assert report.staged["customer"] == 1
    assert report.status == "drained"
    assert report.job_id == "job-1"
    entity_order = list(dict.fromkeys(s["entity"] for s in client.staged))
    assert entity_order == ["product", "customer"]
    assert checkpoints.get("product") is None


def test_resumes_from_persisted_checkpoint_after_crash():
    checkpoints = InMemoryCheckpointStore()
    state = {"killed": True}
    cursors_seen = []

    def fetch_products(cursor):
        cursors_seen.append(cursor)
        page = 0 if cursor is None else int(cursor)
        if state["killed"] and page == 2:
            raise RuntimeError("process killed")
        return Page(records=[product(page)], next_cursor=str(page + 1) if page < 3 else None)

    connector = define_connector(
        connector_ports(fetch_products=fetch_products, fetch_customers=empty_page)
    )
    client = FakeConnectorClient()
    with pytest.raises(ConnectorSyncError):
        connector.sync(
            client,
            checkpoints,
            retry=FetchRetryPolicy(max_attempts=1),
            sleep=lambda ms: None,
        )
    assert checkpoints.get("product") == "2"

    state["killed"] = False
    cursors_seen.clear()
    report = connector.sync(client, checkpoints)
    assert cursors_seen[0] == "2"
    assert report.status == "drained"


def test_resumes_same_open_batch_after_crash():
    checkpoints = InMemoryCheckpointStore()
    state = {"killed": True}

    def fetch_products(cursor):
        page = 0 if cursor is None else int(cursor)
        if state["killed"] and page == 1:
            raise RuntimeError("process killed")
        return Page(records=[product(page)], next_cursor=str(page + 1) if page < 1 else None)

    connector = define_connector(
        connector_ports(fetch_products=fetch_products, fetch_customers=empty_page)
    )
    client = FakeConnectorClient()
    with pytest.raises(ConnectorSyncError):
        connector.sync(
            client,
            checkpoints,
            retry=FetchRetryPolicy(max_attempts=1),
            sleep=lambda ms: None,
        )
    assert checkpoints.get("batch") == "batch-1"

    state["killed"] = False
    report = connector.sync(client, checkpoints)
    assert report.batch_id == "batch-1"
    assert checkpoints.get("batch") is None


def test_discards_stale_cursors_when_stored_batch_is_no_longer_open():
    checkpoints = InMemoryCheckpointStore()
    checkpoints.set("batch", "batch-dead")
    checkpoints.set("product", "7")
    cursors_seen = []

    def fetch_products(cursor):
        cursors_seen.append(cursor)
        return Page(records=[product(1)], next_cursor=None)

    connector = define_connector(
        connector_ports(fetch_products=fetch_products, fetch_customers=empty_page)
    )
    client = FakeConnectorClient(batch_status={"status": "drained"})
    report = connector.sync(client, checkpoints)
    assert cursors_seen == [None]
    assert report.batch_id == "batch-1"


def test_skips_unimplemented_optional_entities_and_syncs_the_rest():
    connector = define_connector(
        connector_ports(
            fetch_products=lambda cursor: Page(records=[product(1)], next_cursor=None),
            fetch_customers=lambda cursor: Page(records=[customer(1)], next_cursor=None),
        )
    )
    client = FakeConnectorClient()
    report = connector.sync(client, InMemoryCheckpointStore())
    assert "quote" not in report.staged
    assert "order" not in report.staged
    assert [s["entity"] for s in client.staged] == ["product", "customer"]


def test_retries_throwing_fetcher_with_backoff_then_fails_typed_with_safe_checkpoint():
    delays = []
    attempts = []

    def fetch_products(cursor):
        attempts.append(1)
        raise RuntimeError("ERP down")

    connector = define_connector(
        connector_ports(fetch_products=fetch_products, fetch_customers=empty_page)
    )
    client = FakeConnectorClient()
    with pytest.raises(ConnectorSyncError) as excinfo:
        connector.sync(
            client,
            InMemoryCheckpointStore(),
            retry=FetchRetryPolicy(max_attempts=3, base_delay_ms=100),
            sleep=delays.append,
        )
    assert excinfo.value.entity == "product"
    assert len(attempts) == 3
    assert delays == [100, 200]


def test_warns_loudly_when_every_quote_line_is_missing_its_pricing_decision_id():
    events = []
    connector = define_connector(
        connector_ports(
            fetch_products=empty_page,
            fetch_customers=empty_page,
            fetch_quotes=lambda cursor: Page(
                records=[quote(1, None), quote(2, None)], next_cursor=None
            ),
        )
    )
    client = FakeConnectorClient()
    report = connector.sync(client, InMemoryCheckpointStore(), on_event=events.append)
    assert "missing_decision_ids" in [w.kind for w in report.warnings]
    assert any(
        e.warning is not None and e.warning.kind == "missing_decision_ids" for e in events
    )


def test_does_not_warn_when_quote_lines_round_trip_their_decision_ids():
    connector = define_connector(
        connector_ports(
            fetch_products=empty_page,
            fetch_customers=empty_page,
            fetch_quotes=lambda cursor: Page(records=[quote(1, "dec-1")], next_cursor=None),
        )
    )
    client = FakeConnectorClient()
    report = connector.sync(client, InMemoryCheckpointStore())
    assert report.warnings == ()


def test_surfaces_the_sku_cap_as_a_typed_warning():
    connector = define_connector(
        connector_ports(
            fetch_products=lambda cursor: Page(records=[product(1)], next_cursor=None),
            fetch_customers=empty_page,
        )
    )
    client = FakeConnectorClient(drain_status={"skipped_over_cap": 25})
    report = connector.sync(client, InMemoryCheckpointStore())
    assert report.skipped_over_cap == 25
    assert "skipped_over_cap" in [w.kind for w in report.warnings]


def test_raises_typed_error_when_server_side_drain_fails():
    connector = define_connector(
        connector_ports(
            fetch_products=lambda cursor: Page(records=[product(1)], next_cursor=None),
            fetch_customers=empty_page,
        )
    )
    client = FakeConnectorClient(drain_status={"status": "failed", "error": "persist blew up"})
    with pytest.raises(ConnectorSyncError) as excinfo:
        connector.sync(client, InMemoryCheckpointStore())
    assert excinfo.value.report is not None
    assert excinfo.value.report.status == "failed"
    assert "persist blew up" in excinfo.value.message


def test_names_the_required_connector_scope_when_the_key_is_rejected():
    connector = define_connector(
        connector_ports(fetch_products=empty_page, fetch_customers=empty_page)
    )
    client = FakeConnectorClient(
        open_batch_error=UnauthorizedError(
            code="unauthorized",
            status=401,
            message="Invalid or missing API key.",
            request_id="r-1",
        )
    )
    with pytest.raises(UnauthorizedError) as excinfo:
        connector.sync(client, InMemoryCheckpointStore())
    assert "connector scope" in excinfo.value.message


def test_commits_nothing_when_no_entity_produced_records():
    connector = define_connector(
        connector_ports(fetch_products=empty_page, fetch_customers=empty_page)
    )
    client = FakeConnectorClient()
    checkpoints = InMemoryCheckpointStore()
    report = connector.sync(client, checkpoints)
    assert report.status == "empty"
    assert report.job_id is None
    assert client.ingest.committed is False
    assert checkpoints.get("batch") is None


def test_entities_lists_only_implemented_fetchers():
    connector = define_connector(
        connector_ports(
            fetch_products=empty_page,
            fetch_customers=empty_page,
            fetch_orders=empty_page,
        )
    )
    assert connector.entities() == ["product", "customer", "order"]


def test_emits_page_and_entity_progress_events():
    events = []
    connector = define_connector(
        connector_ports(
            fetch_products=lambda cursor: Page(records=[product(1)], next_cursor=None),
            fetch_customers=lambda cursor: Page(records=[customer(1)], next_cursor=None),
        )
    )
    client = FakeConnectorClient()
    connector.sync(client, InMemoryCheckpointStore(), on_event=events.append)
    assert [(e.type, e.entity) for e in events] == [
        ("page_staged", "product"),
        ("entity_completed", "product"),
        ("page_staged", "customer"),
        ("entity_completed", "customer"),
    ]


def test_warns_via_logging_when_no_event_handler_is_provided(caplog):
    connector = define_connector(
        connector_ports(
            fetch_products=empty_page,
            fetch_customers=empty_page,
            fetch_quotes=lambda cursor: Page(records=[quote(1, None)], next_cursor=None),
        )
    )
    client = FakeConnectorClient()
    with caplog.at_level(logging.WARNING, logger="elastly.connector"):
        connector.sync(client, InMemoryCheckpointStore())
    assert any("missing_decision_ids" in record.getMessage() for record in caplog.records)
