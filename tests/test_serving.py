import json

import pytest

from elastly import errors
from elastly.models.prices_request_lines_inner import PricesRequestLinesInner
from elastly.models.prices_response import PricesResponse
from elastly.resilience import CircuitBreaker
from elastly.serving import (
    ElastlyPrice,
    FailOpenCause,
    FallbackPrice,
    FallbackPriceResult,
    PricesNamespace,
    UnavailablePrice,
    static_fallback,
    throw_on_failure,
)

PRICED_LINE = {
    "ok": True,
    "priceCents": 1299,
    "currency": "USD",
    "pricingDecisionId": "pd-A",
    "reason": [{"param": "base", "marginDeltaBps": 120}],
    "reasonSummary": "Base margin",
    "explanation": {
        "short": "held",
        "drivers": [{"param": "base", "label": "Base", "points": 1.2, "direction": "up"}],
        "stance": "standard",
        "marginPct": 18.5,
        "targetMarginPct": 19,
        "confidence": "high",
    },
    "guardrailsApplied": [],
    "confidence": "high",
    "confidenceScore": 0.91,
}

FAILED_LINE = {"ok": False, "code": "unknown_product", "message": "Unknown product.", "param": "lines.1"}


def make_response(*line_bodies):
    return PricesResponse.from_json(json.dumps({"lines": list(line_bodies)}))


def make_line(**overrides):
    fields = {"product_sku": "SKU-1", "customer_external_id": "CUST-1", "quantity": 5}
    fields.update(overrides)
    return PricesRequestLinesInner(**fields)


class FakeTransport:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.beacons = []

    def request_prices(self, request, *, deadline_ms=None):
        self.requests.append((request, deadline_ms))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def fire_and_forget(self, path, body):
        self.beacons.append((path, dict(body)))


def make_prices(outcomes, breaker=None):
    transport = FakeTransport(outcomes)
    prices = PricesNamespace(transport, breaker, clock=lambda: 0.0)
    return prices, transport


def fallback_policy(**options):
    return static_fallback(
        lambda line, cause: FallbackPrice(price_cents=999, currency="USD"), **options
    )


def internal_error(status=500):
    return errors.api_error_from_code(
        code="internal_error", status=status, message="boom", request_id="req_1"
    )


def test_success_returns_elastly_price():
    prices, transport = make_prices([make_response(PRICED_LINE)])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert isinstance(result, ElastlyPrice)
    assert result.source == "elastly"
    assert result.price_cents == 1299
    assert result.currency == "USD"
    assert result.pricing_decision_id == "pd-A"
    assert result.reason_summary == "Base margin"
    assert result.confidence_score == 0.91
    assert transport.beacons == []
    assert transport.requests[0][1] == 800


def test_deadline_ms_option_is_passed_through():
    prices, transport = make_prices([make_response(PRICED_LINE)])
    prices.get(make_line(), fail_open=fallback_policy(deadline_ms=250))
    assert transport.requests[0][1] == 250


def test_infra_http_fault_fails_open_to_fallback():
    prices, transport = make_prices([internal_error()])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert isinstance(result, FallbackPriceResult)
    assert result.source == "fallback"
    assert result.price_cents == 999
    assert result.currency == "USD"
    assert result.cause.reason == "http_error"
    assert result.cause.status_code == 500
    assert result.cause.code == "internal_error"
    paths = [path for path, _ in transport.beacons]
    assert paths == ["/api/price/fail-open", "/api/price/fallback"]
    fail_open_body = transport.beacons[0][1]
    assert fail_open_body["reason"] == "http_error"
    assert fail_open_body["statusCode"] == 500
    fallback_body = transport.beacons[1][1]
    assert fallback_body["reason"] == "http_error"
    assert fallback_body["httpCode"] == 500
    assert fallback_body["externalProductId"] == "SKU-1"
    assert fallback_body["externalCustomerId"] == "CUST-1"


def test_network_fault_fails_open_with_exception_reason():
    prices, _ = make_prices([errors.NetworkError("connection refused")])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert isinstance(result, FallbackPriceResult)
    assert result.cause.reason == "exception"


def test_deadline_timeout_fails_open_with_timeout_reason():
    prices, _ = make_prices([errors.TimeoutError(800)])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert isinstance(result, FallbackPriceResult)
    assert result.cause.reason == "timeout"
    assert result.cause.status_code is None


def test_malformed_response_fails_open():
    prices, _ = make_prices([errors.MalformedResponseError("bad body")])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert result.cause.reason == "malformed"


def test_unexpected_exception_fails_open():
    prices, _ = make_prices([RuntimeError("surprise")])
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert result.cause.reason == "exception"
    assert isinstance(result.cause.error, RuntimeError)


def test_caller_fault_always_raises_and_does_not_trip_the_breaker():
    caller_fault = errors.api_error_from_code(
        code="invalid_request", status=422, message="Bad line.", request_id="req_1"
    )
    breaker = CircuitBreaker(now=lambda: 0.0)
    prices, transport = make_prices([caller_fault] * 6 + [make_response(PRICED_LINE)], breaker)
    for _ in range(6):
        with pytest.raises(errors.ValidationError):
            prices.get(make_line(), fail_open=fallback_policy())
    result = prices.get(make_line(), fail_open=fallback_policy())
    assert isinstance(result, ElastlyPrice)
    assert len(transport.requests) == 7


def test_throw_on_failure_raises_infra_faults_instead_of_falling_back():
    prices, _ = make_prices([internal_error()])
    with pytest.raises(errors.InternalServerError):
        prices.get(make_line(), fail_open=throw_on_failure())


def test_line_error_falls_back_per_line():
    prices, transport = make_prices([make_response(PRICED_LINE, FAILED_LINE)])
    results = prices.get_many([make_line(), make_line(product_sku="SKU-2")], fail_open=fallback_policy())
    assert isinstance(results[0], ElastlyPrice)
    assert isinstance(results[1], FallbackPriceResult)
    assert results[1].cause.reason == "line_error"
    assert results[1].cause.code == "unknown_product"
    paths = [path for path, _ in transport.beacons]
    assert paths == ["/api/price/fallback"]
    body = transport.beacons[0][1]
    assert body["reason"] == "http_error"
    assert body["message"] == "line failed: unknown_product"
    assert body["externalProductId"] == "SKU-2"


def test_line_error_with_throw_policy_raises_the_typed_error():
    prices, _ = make_prices([make_response(FAILED_LINE)])
    with pytest.raises(errors.UnknownProductError) as excinfo:
        prices.get(make_line(), fail_open=throw_on_failure())
    assert excinfo.value.status == 404
    assert excinfo.value.param == "lines.1"


def test_line_beacon_cap_limits_fallback_beacons():
    prices, transport = make_prices([make_response(*([FAILED_LINE] * 4))])
    results = prices.get_many([make_line() for _ in range(4)], fail_open=fallback_policy(line_beacon_cap=2))
    assert len(results) == 4
    assert len(transport.beacons) == 2


def test_fallback_resolver_none_means_unavailable():
    prices, _ = make_prices([internal_error()])
    policy = static_fallback(lambda line, cause: None)
    result = prices.get(make_line(), fail_open=policy)
    assert isinstance(result, UnavailablePrice)
    assert result.source == "unavailable"
    assert result.cause.reason == "http_error"


def test_fallback_resolver_raising_wraps_in_fallback_error():
    prices, _ = make_prices([internal_error()])

    def broken(line, cause):
        raise KeyError("missing price book")

    with pytest.raises(errors.FallbackError) as excinfo:
        prices.get(make_line(), fail_open=static_fallback(broken))
    assert isinstance(excinfo.value.fail_open_cause, FailOpenCause)
    assert excinfo.value.fail_open_cause.reason == "http_error"
    assert isinstance(excinfo.value.__cause__, KeyError)


def test_line_count_mismatch_is_malformed_and_fails_open():
    prices, _ = make_prices([make_response(PRICED_LINE)])
    results = prices.get_many([make_line(), make_line()], fail_open=fallback_policy())
    assert len(results) == 2
    assert all(isinstance(result, FallbackPriceResult) for result in results)
    assert results[0].cause.reason == "malformed"


def test_open_breaker_short_circuits_and_throttles_the_beacon():
    breaker = CircuitBreaker(now=lambda: 0.0)
    prices, transport = make_prices([internal_error()] * 5, breaker)
    for _ in range(5):
        prices.get(make_line(), fail_open=fallback_policy())
    assert len(transport.requests) == 5
    assert breaker.is_open is True

    first = prices.get(make_line(), fail_open=fallback_policy())
    second = prices.get(make_line(), fail_open=fallback_policy())
    assert len(transport.requests) == 5
    assert first.cause.reason == "breaker_open"
    assert second.cause.reason == "breaker_open"

    open_beacons = [
        body for path, body in transport.beacons
        if path == "/api/price/fail-open" and body["reason"] == "breaker_open"
    ]
    assert len(open_beacons) == 1


def test_open_breaker_with_throw_policy_raises():
    breaker = CircuitBreaker(now=lambda: 0.0)
    prices, _ = make_prices([internal_error()] * 5, breaker)
    for _ in range(5):
        prices.get(make_line(), fail_open=fallback_policy())
    with pytest.raises(errors.ElastlyError, match="breaker_open"):
        prices.get(make_line(), fail_open=throw_on_failure())
