import json
import re
import uuid
from types import SimpleNamespace

import pytest
import urllib3.exceptions

from elastly import errors
from elastly.configuration import Configuration
from elastly.exceptions import ApiException
from elastly.models.prices_request import PricesRequest
from elastly.models.prices_request_lines_inner import PricesRequestLinesInner
from elastly.models.prices_response import PricesResponse
from elastly.transport import ElastlyTransport

PRICES_RESPONSE = PricesResponse.from_json(
    json.dumps(
        {
            "lines": [
                {
                    "ok": True,
                    "priceCents": 1299,
                    "currency": "USD",
                    "pricingDecisionId": "pd-A",
                    "reason": [],
                    "reasonSummary": "Base margin",
                    "explanation": {
                        "short": "held",
                        "drivers": [],
                        "stance": "standard",
                        "marginPct": 18.5,
                        "targetMarginPct": 19,
                        "confidence": "high",
                    },
                    "guardrailsApplied": [],
                    "confidence": "high",
                    "confidenceScore": 0.91,
                }
            ]
        }
    )
)


def api_exception(status, code="internal_error", headers=None):
    exc = ApiException(
        status=status,
        reason="error",
        body=json.dumps({"error": {"code": code, "message": "boom", "requestId": "req_1"}}),
    )
    exc.headers = {"x-elastly-request-id": "req_header", **(headers or {})}
    return exc


class FakeClock:
    def __init__(self):
        self.ms = 0.0

    def __call__(self):
        return self.ms


class SleepRecorder:
    def __init__(self, clock):
        self.clock = clock
        self.delays = []

    def __call__(self, ms):
        self.delays.append(ms)
        self.clock.ms += ms


class FakePricesApi:
    def __init__(self, script, clock=None, call_cost_ms=0.0):
        self.script = list(script)
        self.calls = []
        self.clock = clock
        self.call_cost_ms = call_cost_ms

    def get_prices(self, *, idempotency_key, prices_request, _request_timeout=None):
        self.calls.append(
            {
                "idempotency_key": idempotency_key,
                "prices_request": prices_request,
                "timeout": _request_timeout,
            }
        )
        if self.clock is not None:
            self.clock.ms += self.call_cost_ms
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class FakeRestClient:
    def __init__(self, error=None):
        self.error = error
        self.requests = []

    def request(self, method, url, headers=None, body=None, post_params=None, _request_timeout=None):
        self.requests.append(
            {"method": method, "url": url, "headers": headers, "body": body, "timeout": _request_timeout}
        )
        if self.error is not None:
            raise self.error


def make_transport(script, *, clock=None, call_cost_ms=0.0, rest_error=None, **overrides):
    clock = clock or FakeClock()
    sleep = SleepRecorder(clock)
    prices_api = FakePricesApi(script, clock=clock, call_cost_ms=call_cost_ms)
    rest_client = FakeRestClient(error=rest_error)
    api_client = SimpleNamespace(
        configuration=Configuration(access_token="elastly_live_test"),
        rest_client=rest_client,
    )
    overrides.setdefault("random", lambda: 0.5)
    overrides.setdefault("beacon_runner", lambda fn: fn())
    transport = ElastlyTransport(
        api_client,
        prices_api=prices_api,
        sleep=sleep,
        clock=clock,
        **overrides,
    )
    return transport, prices_api, sleep, rest_client


def request_body():
    return PricesRequest(lines=[PricesRequestLinesInner(product_sku="SKU-1", quantity=1)])


def test_success_attaches_a_uuid4_idempotency_key():
    transport, prices_api, _, _ = make_transport([PRICES_RESPONSE])
    response = transport.request_prices(request_body())
    assert response is PRICES_RESPONSE
    key = prices_api.calls[0]["idempotency_key"]
    assert uuid.UUID(key).version == 4


def test_retryable_status_retries_with_full_jitter_and_reuses_the_key():
    transport, prices_api, sleep, _ = make_transport(
        [api_exception(503), api_exception(503), PRICES_RESPONSE]
    )
    response = transport.request_prices(request_body())
    assert response is PRICES_RESPONSE
    assert len(prices_api.calls) == 3
    assert sleep.delays == [125, 250]
    keys = {call["idempotency_key"] for call in prices_api.calls}
    assert len(keys) == 1


def test_exhausted_retries_raise_the_typed_error():
    transport, prices_api, sleep, _ = make_transport([api_exception(503)] * 3)
    with pytest.raises(errors.InternalServerError) as excinfo:
        transport.request_prices(request_body())
    assert len(prices_api.calls) == 3
    assert excinfo.value.status == 503
    assert excinfo.value.request_id == "req_header"


def test_retry_after_header_overrides_the_backoff_delay():
    transport, _, sleep, _ = make_transport(
        [api_exception(429, code="rate_limited", headers={"Retry-After": "2"}), PRICES_RESPONSE]
    )
    transport.request_prices(request_body())
    assert sleep.delays == [2000]


def test_rate_limit_error_carries_retry_after_ms():
    transport, _, _, _ = make_transport(
        [api_exception(429, code="rate_limited", headers={"Retry-After": "2"})] * 3
    )
    with pytest.raises(errors.RateLimitError) as excinfo:
        transport.request_prices(request_body())
    assert excinfo.value.retry_after_ms == 2000


def test_non_retryable_status_raises_immediately():
    transport, prices_api, _, _ = make_transport([api_exception(422, code="invalid_request")])
    with pytest.raises(errors.ValidationError):
        transport.request_prices(request_body())
    assert len(prices_api.calls) == 1


def test_network_errors_are_retried():
    transport, prices_api, _, _ = make_transport(
        [urllib3.exceptions.ProtocolError("connection reset"), PRICES_RESPONSE]
    )
    response = transport.request_prices(request_body())
    assert response is PRICES_RESPONSE
    assert len(prices_api.calls) == 2


def test_network_errors_exhausting_retries_raise_network_error():
    transport, _, _, _ = make_transport([urllib3.exceptions.ProtocolError("reset")] * 3)
    with pytest.raises(errors.NetworkError):
        transport.request_prices(request_body())


def test_deadline_caps_the_per_attempt_timeout():
    transport, prices_api, _, _ = make_transport([PRICES_RESPONSE])
    transport.request_prices(request_body(), deadline_ms=800)
    assert prices_api.calls[0]["timeout"] == pytest.approx(0.8)


def test_slow_attempt_exhausting_the_deadline_raises_timeout():
    clock = FakeClock()
    transport, prices_api, _, _ = make_transport(
        [urllib3.exceptions.ReadTimeoutError(None, "", "read timed out")] * 3,
        clock=clock,
        call_cost_ms=900.0,
    )
    with pytest.raises(errors.TimeoutError) as excinfo:
        transport.request_prices(request_body(), deadline_ms=800)
    assert excinfo.value.timeout_ms == 800
    assert len(prices_api.calls) == 1


def test_backoff_never_sleeps_past_the_deadline():
    clock = FakeClock()
    transport, prices_api, sleep, _ = make_transport(
        [api_exception(503)] * 3, clock=clock, call_cost_ms=700.0
    )
    with pytest.raises(errors.TimeoutError) as excinfo:
        transport.request_prices(request_body(), deadline_ms=800)
    assert excinfo.value.timeout_ms == 800
    assert len(prices_api.calls) == 1
    assert sleep.delays == [100]
    assert clock.ms == 800


def test_undeserializable_success_body_raises_malformed_response():
    transport, prices_api, _, _ = make_transport([ValueError("bad body")])
    with pytest.raises(errors.MalformedResponseError):
        transport.request_prices(request_body())
    assert len(prices_api.calls) == 1


def test_unrecognized_error_body_maps_to_internal_server_error():
    exc = ApiException(status=500, reason="error", body="<html>gateway</html>")
    exc.headers = {}
    transport, _, _, _ = make_transport([exc] * 3)
    with pytest.raises(errors.InternalServerError) as excinfo:
        transport.request_prices(request_body())
    assert excinfo.value.code == "internal_error"
    assert re.search(r"unrecognized error body", excinfo.value.message)


def test_fire_and_forget_posts_an_authenticated_beacon():
    transport, _, _, rest_client = make_transport([])
    transport.fire_and_forget("/api/price/fail-open", {"reason": "timeout", "latencyMs": 812})
    assert len(rest_client.requests) == 1
    sent = rest_client.requests[0]
    assert sent["method"] == "POST"
    assert sent["url"] == "https://app.elastly.io/api/price/fail-open"
    assert sent["headers"]["Authorization"] == "Bearer elastly_live_test"
    assert sent["headers"]["Content-Type"] == "application/json"
    assert sent["body"] == {"reason": "timeout", "latencyMs": 812}


def test_fire_and_forget_swallows_transport_errors():
    transport, _, _, rest_client = make_transport(
        [], rest_error=urllib3.exceptions.ProtocolError("down")
    )
    transport.fire_and_forget("/api/price/fallback", {"reason": "exception"})
    assert len(rest_client.requests) == 1
