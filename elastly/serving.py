"""Fail-open price serving: never let pricing take down the caller's checkout path.

Port of the TypeScript SDK's serving policy. A price call either returns an
Elastly price, a caller-supplied fallback price, or an explicit "unavailable"
result, discriminated by ``result.source``. Caller-fault API errors always
raise; infrastructure faults fail open.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, List, Mapping, Optional, Protocol, Sequence, Union

from elastly import errors
from elastly.models.prices_request import PricesRequest
from elastly.models.prices_request_lines_inner import PricesRequestLinesInner
from elastly.models.prices_response import PricesResponse
from elastly.resilience.breaker import CircuitBreaker

FAIL_OPEN_REASONS = (
    "timeout",
    "http_error",
    "line_error",
    "malformed",
    "exception",
    "breaker_open",
)

DEFAULT_DEADLINE_MS = 800.0
DEFAULT_LINE_BEACON_CAP = 10

CALLER_FAULT_CODES = frozenset(
    {
        "unauthorized",
        "forbidden",
        "feature_not_enabled",
        "subscription_inactive",
        "invalid_request",
        "invalid_json",
        "idempotency_key_reused",
        "idempotency_key_in_flight",
    }
)


@dataclass(frozen=True)
class FailOpenCause:
    reason: str
    status_code: Optional[int]
    latency_ms: float
    code: Optional[str] = None
    error: Optional[Any] = None


@dataclass(frozen=True)
class FallbackPrice:
    price_cents: int
    currency: Optional[str] = None


@dataclass(frozen=True)
class ElastlyPrice:
    price_cents: float
    currency: str
    pricing_decision_id: Optional[str]
    reason: List[Any]
    reason_summary: str
    explanation: Any
    guardrails_applied: List[str]
    confidence: str
    confidence_score: float

    source: ClassVar[str] = "elastly"

    @classmethod
    def from_line(cls, line: Any) -> "ElastlyPrice":
        return cls(
            price_cents=line.price_cents,
            currency=line.currency,
            pricing_decision_id=line.pricing_decision_id,
            reason=line.reason,
            reason_summary=line.reason_summary,
            explanation=line.explanation,
            guardrails_applied=line.guardrails_applied,
            confidence=line.confidence,
            confidence_score=line.confidence_score,
        )


@dataclass(frozen=True)
class FallbackPriceResult:
    price_cents: int
    cause: FailOpenCause
    currency: Optional[str] = None

    source: ClassVar[str] = "fallback"


@dataclass(frozen=True)
class UnavailablePrice:
    cause: FailOpenCause

    source: ClassVar[str] = "unavailable"


PriceResult = Union[ElastlyPrice, FallbackPriceResult, UnavailablePrice]

FallbackResolver = Callable[[PricesRequestLinesInner, FailOpenCause], Optional[FallbackPrice]]


@dataclass(frozen=True)
class FailOpenPolicy:
    deadline_ms: float
    beacon: bool
    line_beacon_cap: int
    throw_on_failure: bool
    fallback: FallbackResolver


def static_fallback(
    resolve: FallbackResolver,
    *,
    deadline_ms: float = DEFAULT_DEADLINE_MS,
    beacon: bool = True,
    line_beacon_cap: int = DEFAULT_LINE_BEACON_CAP,
) -> FailOpenPolicy:
    return FailOpenPolicy(
        deadline_ms=deadline_ms,
        beacon=beacon,
        line_beacon_cap=line_beacon_cap,
        throw_on_failure=False,
        fallback=resolve,
    )


def throw_on_failure(
    *,
    deadline_ms: float = DEFAULT_DEADLINE_MS,
    beacon: bool = True,
    line_beacon_cap: int = DEFAULT_LINE_BEACON_CAP,
) -> FailOpenPolicy:
    return FailOpenPolicy(
        deadline_ms=deadline_ms,
        beacon=beacon,
        line_beacon_cap=line_beacon_cap,
        throw_on_failure=True,
        fallback=lambda line, cause: None,
    )


class ServingTransport(Protocol):
    def request_prices(
        self, request: PricesRequest, *, deadline_ms: Optional[float] = None
    ) -> PricesResponse: ...

    def fire_and_forget(self, path: str, body: Mapping[str, Any]) -> None: ...


def _monotonic_ms() -> float:
    return time.monotonic() * 1000.0


class PricesNamespace:
    def __init__(
        self,
        transport: ServingTransport,
        breaker: Optional[CircuitBreaker] = None,
        *,
        clock: Optional[Callable[[], float]] = None,
    ) -> None:
        self._transport = transport
        self._breaker = breaker if breaker is not None else CircuitBreaker()
        self._clock = clock if clock is not None else _monotonic_ms

    def get(self, line: PricesRequestLinesInner, *, fail_open: FailOpenPolicy) -> PriceResult:
        results = self.get_many([line], fail_open=fail_open)
        if not results:
            raise errors.MalformedResponseError(
                "The server returned no result for the requested line.", None
            )
        return results[0]

    def get_many(
        self,
        lines: Sequence[PricesRequestLinesInner],
        *,
        fail_open: FailOpenPolicy,
    ) -> List[PriceResult]:
        policy = fail_open
        started = self._clock()

        if not self._breaker.allow_request():
            cause = FailOpenCause(reason="breaker_open", status_code=None, latency_ms=0)
            return self._fail_open(lines, cause, policy, throttle_beacon=True)

        request = PricesRequest(lines=list(lines))
        try:
            response = self._transport.request_prices(request, deadline_ms=policy.deadline_ms)
        except errors.ApiError as error:
            latency_ms = self._clock() - started
            if error.code in CALLER_FAULT_CODES:
                self._breaker.record_success()
                raise
            cause = FailOpenCause(
                reason="http_error",
                status_code=error.status,
                latency_ms=latency_ms,
                code=error.code,
                error=error,
            )
            return self._handle_failure(lines, error, cause, policy)
        except errors.MalformedResponseError as error:
            cause = FailOpenCause(
                reason="malformed",
                status_code=None,
                latency_ms=self._clock() - started,
                error=error,
            )
            return self._handle_failure(lines, error, cause, policy)
        except errors.TimeoutError as error:
            cause = FailOpenCause(
                reason="timeout", status_code=None, latency_ms=self._clock() - started, error=error
            )
            return self._handle_failure(lines, error, cause, policy)
        except errors.NetworkError as error:
            cause = FailOpenCause(
                reason="exception",
                status_code=None,
                latency_ms=self._clock() - started,
                error=error,
            )
            return self._handle_failure(lines, error, cause, policy)
        except Exception as raw:
            wrapped = errors.ElastlyError(str(raw) or "The price call failed.", None)
            wrapped.__cause__ = raw
            cause = FailOpenCause(
                reason="exception", status_code=None, latency_ms=self._clock() - started, error=raw
            )
            return self._handle_failure(lines, wrapped, cause, policy)

        latency_ms = self._clock() - started
        if len(response.lines) != len(lines):
            self._breaker.record_failure()
            mismatch = errors.MalformedResponseError(
                f"The server returned {len(response.lines)} results for {len(lines)} lines.", None
            )
            if policy.throw_on_failure:
                raise mismatch
            cause = FailOpenCause(
                reason="malformed", status_code=None, latency_ms=latency_ms, error=mismatch
            )
            return self._fail_open(lines, cause, policy, throttle_beacon=False)

        self._breaker.record_success()
        return self._map_response(lines, response, policy, latency_ms)

    def _handle_failure(
        self,
        lines: Sequence[PricesRequestLinesInner],
        error: errors.ElastlyError,
        cause: FailOpenCause,
        policy: FailOpenPolicy,
    ) -> List[PriceResult]:
        self._breaker.record_failure()
        if policy.throw_on_failure:
            raise error
        return self._fail_open(lines, cause, policy, throttle_beacon=False)

    def _map_response(
        self,
        lines: Sequence[PricesRequestLinesInner],
        response: PricesResponse,
        policy: FailOpenPolicy,
        latency_ms: float,
    ) -> List[PriceResult]:
        line_beacons = 0
        results: List[PriceResult] = []
        for index, wrapper in enumerate(response.lines):
            result = getattr(wrapper, "actual_instance", wrapper)
            if getattr(result, "ok", False):
                results.append(ElastlyPrice.from_line(result))
                continue
            line = lines[index]
            code = getattr(result, "code", None) or "internal_error"
            cause = FailOpenCause(
                reason="line_error", status_code=None, latency_ms=latency_ms, code=code
            )
            if policy.throw_on_failure:
                raise errors.api_error_from_code(
                    code=code,
                    status=errors.API_ERROR_STATUS.get(code, 500),
                    message=result.message,
                    request_id=None,
                    param=result.param,
                )
            if policy.beacon and line_beacons < policy.line_beacon_cap:
                line_beacons += 1
                self._beacon_fallback(cause, line)
            results.append(self._resolve_fallback(line, cause, policy))
        return results

    def _fail_open(
        self,
        lines: Sequence[PricesRequestLinesInner],
        cause: FailOpenCause,
        policy: FailOpenPolicy,
        *,
        throttle_beacon: bool,
    ) -> List[PriceResult]:
        if policy.throw_on_failure:
            if isinstance(cause.error, BaseException):
                raise cause.error
            raise errors.ElastlyError(f"The price call failed open: {cause.reason}.", None)
        if policy.beacon and (not throttle_beacon or self._breaker.should_beacon_while_open()):
            self._beacon_fail_open(cause)
            self._beacon_fallback(cause, lines[0] if len(lines) == 1 else None)
        return [self._resolve_fallback(line, cause, policy) for line in lines]

    def _resolve_fallback(
        self,
        line: PricesRequestLinesInner,
        cause: FailOpenCause,
        policy: FailOpenPolicy,
    ) -> PriceResult:
        try:
            fallback = policy.fallback(line, cause)
        except Exception as fallback_error:
            raise errors.FallbackError(
                "The fail-open fallback itself threw. "
                "The original Elastly failure is attached as fail_open_cause.",
                cause,
            ) from fallback_error
        if fallback is None:
            return UnavailablePrice(cause=cause)
        return FallbackPriceResult(
            price_cents=fallback.price_cents, currency=fallback.currency, cause=cause
        )

    def _beacon_fail_open(self, cause: FailOpenCause) -> None:
        self._transport.fire_and_forget(
            "/api/price/fail-open",
            {
                "reason": cause.reason,
                "latencyMs": cause.latency_ms,
                "statusCode": cause.status_code if cause.status_code is not None else 0,
            },
        )

    def _beacon_fallback(
        self, cause: FailOpenCause, line: Optional[PricesRequestLinesInner]
    ) -> None:
        if cause.reason in ("http_error", "line_error"):
            reason = "http_error"
        elif cause.reason == "malformed":
            reason = "malformed"
        else:
            reason = "exception"
        body: dict = {"reason": reason}
        if cause.status_code is not None:
            body["httpCode"] = cause.status_code
        if cause.reason == "line_error" and cause.code is not None:
            body["message"] = f"line failed: {cause.code}"
        if line is not None:
            product_id = line.product_external_id or line.product_sku
            if product_id:
                body["externalProductId"] = product_id
            customer_id = line.customer_external_id or line.customer_id
            if customer_id:
                body["externalCustomerId"] = customer_id
        self._transport.fire_and_forget("/api/price/fallback", body)
