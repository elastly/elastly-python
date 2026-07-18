from datetime import datetime, timezone

import pytest

from connector_fakes import FakeConnectorClient, connector_ports, writeback_task
from elastly.connector import (
    ConnectorSyncError,
    Page,
    WritebackResult,
    define_connector,
)


def empty_page(cursor):
    return Page(records=[], next_cursor=None)


def iso_at_epoch_ms(epoch_ms):
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc).isoformat()


def far_lease():
    return iso_at_epoch_ms(datetime.now(tz=timezone.utc).timestamp() * 1000.0 + 300_000)


def make_connector(apply_price):
    return define_connector(
        connector_ports(
            fetch_products=empty_page,
            fetch_customers=empty_page,
            apply_price=apply_price,
        )
    )


def test_claims_applies_and_acks_until_the_queue_is_dry():
    applied_tasks = []

    def apply_price(task):
        applied_tasks.append(task.id)
        return WritebackResult(id=task.id, ok=True)

    connector = make_connector(apply_price)
    client = FakeConnectorClient(
        writeback_tasks=[[writeback_task(f"w-{i}", far_lease()) for i in range(10)], []]
    )
    report = connector.drain_writebacks(client)
    assert applied_tasks == [f"w-{i}" for i in range(10)]
    assert len(client.acked) == 1
    assert report.applied == 10


def test_acks_a_rejecting_apply_price_as_failed_and_a_raising_one_with_the_message():
    def apply_price(task):
        if task.id == "w-reject":
            return WritebackResult(id=task.id, ok=False, error="ERP said no")
        raise RuntimeError("ERP exploded")

    connector = make_connector(apply_price)
    client = FakeConnectorClient(
        writeback_tasks=[
            [writeback_task("w-reject", far_lease()), writeback_task("w-throw", far_lease())],
            [],
        ]
    )
    report = connector.drain_writebacks(client)
    assert report.failed == 2
    assert client.acked[0] == [
        WritebackResult(id="w-reject", ok=False, error="ERP said no"),
        WritebackResult(id="w-throw", ok=False, error="ERP exploded"),
    ]


def test_skips_apply_price_entirely_for_a_task_whose_lease_is_already_spent():
    now = 1_000_000.0
    spent_lease = iso_at_epoch_ms(now + 5_000)
    applied_tasks = []

    def apply_price(task):
        applied_tasks.append(task.id)
        return WritebackResult(id=task.id, ok=True)

    connector = make_connector(apply_price)
    client = FakeConnectorClient(writeback_tasks=[[writeback_task("w-spent", spent_lease)], []])
    report = connector.drain_writebacks(client, now=lambda: now)
    assert applied_tasks == []
    assert client.acked == []
    assert report.expired == 1


def test_never_acks_a_task_whose_lease_expired_while_apply_price_ran():
    clock = {"now": 1_000_000.0}
    lease_until = iso_at_epoch_ms(clock["now"] + 300_000)

    def apply_price(task):
        clock["now"] += 400_000
        return WritebackResult(id=task.id, ok=True)

    connector = make_connector(apply_price)
    client = FakeConnectorClient(writeback_tasks=[[writeback_task("w-slow", lease_until)], []])
    report = connector.drain_writebacks(client, now=lambda: clock["now"])
    assert client.acked == []
    assert report.expired == 1
    assert report.applied == 0


def test_stops_draining_when_a_whole_batch_expires_locally():
    clock = {"now": 1_000_000.0}

    def lease_until():
        return iso_at_epoch_ms(clock["now"] + 300_000)

    def apply_price(task):
        clock["now"] += 400_000
        return WritebackResult(id=task.id, ok=True)

    connector = make_connector(apply_price)
    client = FakeConnectorClient(
        writeback_tasks=[
            [writeback_task("w-1", lease_until())],
            [writeback_task("w-2", lease_until())],
            [],
        ]
    )
    report = connector.drain_writebacks(client, now=lambda: clock["now"])
    assert report.expired == 1
    assert client.acked == []


def test_emits_writeback_settled_events_for_expired_and_applied_tasks():
    now = 1_000_000.0
    events = []

    def apply_price(task):
        return WritebackResult(id=task.id, ok=True)

    connector = make_connector(apply_price)
    client = FakeConnectorClient(
        writeback_tasks=[
            [
                writeback_task("w-spent", iso_at_epoch_ms(now + 5_000)),
                writeback_task("w-live", iso_at_epoch_ms(now + 300_000)),
            ],
            [],
        ]
    )
    connector.drain_writebacks(client, now=lambda: now, on_event=events.append)
    assert [(e.type, e.task.id, e.result.ok) for e in events] == [
        ("writeback_settled", "w-spent", False),
        ("writeback_settled", "w-live", True),
    ]


def test_refuses_to_drain_when_apply_price_is_not_implemented():
    connector = define_connector(
        connector_ports(fetch_products=empty_page, fetch_customers=empty_page)
    )
    client = FakeConnectorClient()
    with pytest.raises(ConnectorSyncError):
        connector.drain_writebacks(client)
