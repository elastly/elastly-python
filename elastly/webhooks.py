"""Webhook signature verification and typed event envelopes."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from elastly.errors import ElastlyError

WEBHOOK_EVENT_TYPES = (
    "sync.completed",
    "recommendation.created",
    "price.written_back",
    "test.ping",
)

DEFAULT_TOLERANCE_SECONDS = 300


class SignatureVerificationError(ElastlyError):
    def __init__(self, message: str) -> None:
        super().__init__(message, None)


@dataclass(frozen=True)
class VerifiedWebhookEvent:
    event: str
    created_at: str
    data: Any


class SyncCompletedEvent(VerifiedWebhookEvent):
    pass


class RecommendationCreatedEvent(VerifiedWebhookEvent):
    pass


class PriceWrittenBackEvent(VerifiedWebhookEvent):
    pass


class TestPingEvent(VerifiedWebhookEvent):
    # Not a test case; the marker stops pytest from trying to collect it.
    __test__ = False


class UnknownWebhookEvent(VerifiedWebhookEvent):
    pass


def is_known_elastly_event(event: VerifiedWebhookEvent) -> bool:
    return event.event in WEBHOOK_EVENT_TYPES


def is_event_of_type(event: VerifiedWebhookEvent, event_type: str) -> bool:
    return event.event == event_type


def _valid_sync_completed(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and isinstance(data.get("connector"), str)
        and isinstance(data.get("totals"), dict)
        and all(isinstance(key, str) for key in data["totals"])
    )


def _valid_recommendation_created(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    count = data.get("count")
    return isinstance(count, int) and not isinstance(count, bool)


def _valid_price_written_back(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and isinstance(data.get("connector"), str)
        and isinstance(data.get("skus"), list)
        and all(isinstance(sku, str) for sku in data["skus"])
    )


def _valid_test_ping(data: Any) -> bool:
    return isinstance(data, dict)


_KNOWN_EVENTS: Dict[str, Tuple[type, Callable[[Any], bool]]] = {
    "sync.completed": (SyncCompletedEvent, _valid_sync_completed),
    "recommendation.created": (RecommendationCreatedEvent, _valid_recommendation_created),
    "price.written_back": (PriceWrittenBackEvent, _valid_price_written_back),
    "test.ping": (TestPingEvent, _valid_test_ping),
}


def _parse_signature_header(header: str) -> Tuple[Optional[int], List[str]]:
    timestamp: Optional[int] = None
    signatures: List[str] = []
    for segment in header.split(","):
        key, _, value = segment.partition("=")
        key = key.strip()
        value = value.strip()
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                timestamp = None
        elif key == "v1" and value:
            signatures.append(value)
    return timestamp, signatures


def _event_from_payload(payload: Any) -> VerifiedWebhookEvent:
    if isinstance(payload, dict):
        event = payload.get("event")
        created_at = payload.get("created_at")
        if isinstance(event, str) and isinstance(created_at, str):
            known = _KNOWN_EVENTS.get(event)
            if known is not None:
                event_class, is_valid_data = known
                if is_valid_data(payload.get("data")):
                    return event_class(event=event, created_at=created_at, data=payload["data"])
            return UnknownWebhookEvent(event=event, created_at=created_at, data=payload.get("data"))
    raise SignatureVerificationError("The signed body is not a webhook event envelope.")


class WebhooksNamespace:
    def verify(
        self,
        raw_body: str,
        signature_header: str,
        secret: str,
        *,
        tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
        now: Optional[Callable[[], float]] = None,
    ) -> VerifiedWebhookEvent:
        if not secret:
            raise SignatureVerificationError("A webhook signing secret is required.")
        now_seconds = (now if now is not None else time.time)()

        timestamp, signatures = _parse_signature_header(signature_header)
        if timestamp is None or not signatures:
            raise SignatureVerificationError("The signature header is not in the t=...,v1=... form.")
        if abs(math.floor(now_seconds) - timestamp) > tolerance_seconds:
            raise SignatureVerificationError(
                f"The signature timestamp is outside the {tolerance_seconds}s replay tolerance."
            )

        expected = hmac.new(
            secret.encode("utf-8"),
            f"{timestamp}.{raw_body}".encode("utf-8"),
            hashlib.sha256,
        ).digest()
        if not any(_matches(expected, provided) for provided in signatures):
            raise SignatureVerificationError("The signature does not match the body.")

        try:
            payload = json.loads(raw_body)
        except ValueError:
            raise SignatureVerificationError("The signed body is not valid JSON.") from None
        return _event_from_payload(payload)


def _matches(expected: bytes, provided: str) -> bool:
    try:
        provided_bytes = bytes.fromhex(provided)
    except ValueError:
        return False
    return hmac.compare_digest(expected, provided_bytes)
