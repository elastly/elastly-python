import hashlib
import hmac
import json

import pytest

from elastly.webhooks import (
    PriceWrittenBackEvent,
    RecommendationCreatedEvent,
    SignatureVerificationError,
    SyncCompletedEvent,
    TestPingEvent,
    UnknownWebhookEvent,
    WebhooksNamespace,
    is_event_of_type,
    is_known_elastly_event,
)

SECRET = "whsec_test_secret"
NOW = 1_752_800_000


def sign(body, secret=SECRET, timestamp=NOW):
    signature = hmac.new(
        secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def make_body(event="sync.completed", data=None):
    if data is None:
        data = {"connector": "netsuite", "totals": {"products": 10}}
    return json.dumps({"event": event, "created_at": "2026-07-18T00:00:00Z", "data": data})


def verify(body, header, **kwargs):
    kwargs.setdefault("now", lambda: NOW)
    return WebhooksNamespace().verify(body, header, SECRET, **kwargs)


def test_valid_signature_returns_the_typed_event():
    body = make_body()
    event = verify(body, sign(body))
    assert isinstance(event, SyncCompletedEvent)
    assert event.event == "sync.completed"
    assert event.created_at == "2026-07-18T00:00:00Z"
    assert event.data == {"connector": "netsuite", "totals": {"products": 10}}
    assert is_known_elastly_event(event) is True
    assert is_event_of_type(event, "sync.completed") is True
    assert is_event_of_type(event, "test.ping") is False


@pytest.mark.parametrize(
    "event_type,data,event_class",
    [
        ("recommendation.created", {"count": 3}, RecommendationCreatedEvent),
        ("price.written_back", {"connector": "netsuite", "skus": ["A", "B"]}, PriceWrittenBackEvent),
        ("test.ping", {}, TestPingEvent),
    ],
)
def test_each_known_event_type_resolves_its_class(event_type, data, event_class):
    body = make_body(event=event_type, data=data)
    event = verify(body, sign(body))
    assert isinstance(event, event_class)
    assert event.data == data


def test_bad_signature_raises():
    body = make_body()
    tampered = make_body(data={"connector": "netsuite", "totals": {"products": 999}})
    with pytest.raises(SignatureVerificationError, match="does not match"):
        verify(tampered, sign(body))


def test_wrong_secret_raises():
    body = make_body()
    with pytest.raises(SignatureVerificationError, match="does not match"):
        verify(body, sign(body, secret="whsec_other"))


def test_one_valid_signature_among_many_passes():
    body = make_body()
    valid = sign(body).split("v1=")[1]
    header = f"t={NOW},v1={'0' * 64},v1={valid}"
    event = verify(body, header)
    assert isinstance(event, SyncCompletedEvent)


def test_replay_outside_tolerance_raises():
    body = make_body()
    header = sign(body, timestamp=NOW - 301)
    with pytest.raises(SignatureVerificationError, match="replay tolerance"):
        verify(body, header)


def test_timestamp_at_the_tolerance_edge_passes():
    body = make_body()
    header = sign(body, timestamp=NOW - 300)
    assert isinstance(verify(body, header), SyncCompletedEvent)


def test_custom_tolerance_is_honored():
    body = make_body()
    header = sign(body, timestamp=NOW - 100)
    with pytest.raises(SignatureVerificationError, match="10s replay tolerance"):
        verify(body, header, tolerance_seconds=10)


def test_malformed_header_raises():
    body = make_body()
    for header in ("", "nonsense", f"t=abc,v1={'0' * 64}", f"t={NOW}", "v1=aa"):
        with pytest.raises(SignatureVerificationError, match="t=...,v1=..."):
            verify(body, header)


def test_empty_secret_raises():
    body = make_body()
    with pytest.raises(SignatureVerificationError, match="signing secret"):
        WebhooksNamespace().verify(body, sign(body), "", now=lambda: NOW)


def test_signed_non_json_body_raises():
    body = "not json"
    with pytest.raises(SignatureVerificationError, match="not valid JSON"):
        verify(body, sign(body))


def test_signed_non_envelope_body_raises():
    body = json.dumps({"hello": "world"})
    with pytest.raises(SignatureVerificationError, match="not a webhook event envelope"):
        verify(body, sign(body))


def test_unknown_event_type_returns_unknown_event():
    body = make_body(event="pricing.v2_launched", data={"foo": 1})
    event = verify(body, sign(body))
    assert isinstance(event, UnknownWebhookEvent)
    assert event.event == "pricing.v2_launched"
    assert is_known_elastly_event(event) is False


def test_known_event_with_invalid_data_shape_degrades_to_unknown_wrapper():
    body = make_body(event="recommendation.created", data={"count": "three"})
    event = verify(body, sign(body))
    assert isinstance(event, UnknownWebhookEvent)
    assert event.event == "recommendation.created"
