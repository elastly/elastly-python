"""Typed error hierarchy for the Elastly SDK."""

from __future__ import annotations

import builtins
from typing import Any, Dict, Mapping, Optional, Type

API_ERROR_CODES = (
    "unauthorized",
    "forbidden",
    "feature_not_enabled",
    "subscription_inactive",
    "rate_limited",
    "monthly_volume_exceeded",
    "invalid_request",
    "invalid_json",
    "unknown_product",
    "unknown_customer",
    "no_cost_basis",
    "fx_rate_unavailable",
    "fx_rate_stale",
    "idempotency_key_reused",
    "idempotency_key_in_flight",
    "batch_not_found",
    "batch_already_committed",
    "batch_entity_order_violation",
    "entity_not_supported",
    "writeback_lease_expired",
    "internal_error",
)

API_ERROR_STATUS: Dict[str, int] = {
    "unauthorized": 401,
    "forbidden": 403,
    "feature_not_enabled": 403,
    "subscription_inactive": 402,
    "rate_limited": 429,
    "monthly_volume_exceeded": 429,
    "invalid_request": 422,
    "invalid_json": 400,
    "unknown_product": 404,
    "unknown_customer": 404,
    "no_cost_basis": 422,
    "fx_rate_unavailable": 422,
    "fx_rate_stale": 422,
    "idempotency_key_reused": 409,
    "idempotency_key_in_flight": 409,
    "batch_not_found": 404,
    "batch_already_committed": 409,
    "batch_entity_order_violation": 422,
    "entity_not_supported": 422,
    "writeback_lease_expired": 409,
    "internal_error": 500,
}


class ElastlyError(Exception):
    """Base class for every error raised by the Elastly SDK extras layer."""

    def __init__(self, message: str, request_id: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id


class ApiError(ElastlyError):
    """An error response returned by the Elastly API."""

    def __init__(
        self,
        *,
        code: str,
        status: int,
        message: str,
        request_id: Optional[str] = None,
        param: Optional[str] = None,
        retry_after_ms: Optional[float] = None,
    ) -> None:
        super().__init__(message, request_id)
        self.code = code
        self.status = status
        self.param = param


class UnauthorizedError(ApiError):
    pass


class ForbiddenError(ApiError):
    pass


class FeatureNotEnabledError(ApiError):
    pass


class SubscriptionInactiveError(ApiError):
    pass


class RateLimitError(ApiError):
    def __init__(
        self,
        *,
        code: str,
        status: int,
        message: str,
        request_id: Optional[str] = None,
        param: Optional[str] = None,
        retry_after_ms: Optional[float] = None,
    ) -> None:
        super().__init__(
            code=code, status=status, message=message, request_id=request_id, param=param
        )
        self.retry_after_ms = retry_after_ms


class MonthlyVolumeExceededError(ApiError):
    pass


class ValidationError(ApiError):
    pass


class InvalidJsonError(ApiError):
    pass


class UnknownProductError(ApiError):
    pass


class UnknownCustomerError(ApiError):
    pass


class NoCostBasisError(ApiError):
    pass


class FxRateUnavailableError(ApiError):
    pass


class FxRateStaleError(ApiError):
    pass


class IdempotencyReusedError(ApiError):
    pass


class IdempotencyInFlightError(ApiError):
    pass


class BatchNotFoundError(ApiError):
    pass


class BatchAlreadyCommittedError(ApiError):
    pass


class BatchEntityOrderViolationError(ApiError):
    pass


class EntityNotSupportedError(ApiError):
    pass


class WritebackLeaseExpiredError(ApiError):
    pass


class InternalServerError(ApiError):
    pass


class NetworkError(ElastlyError):
    """The request never produced an HTTP response."""


class TimeoutError(ElastlyError, builtins.TimeoutError):
    """The request did not complete within its time budget."""

    def __init__(self, timeout_ms: float, request_id: Optional[str] = None) -> None:
        super().__init__(f"The request did not complete within {timeout_ms:g}ms.", request_id)
        self.timeout_ms = timeout_ms


class MalformedResponseError(ElastlyError):
    """The server responded with a body that does not match the API contract."""


class FallbackError(ElastlyError):
    """The caller-supplied fail-open fallback itself raised."""

    def __init__(self, message: str, fail_open_cause: Any) -> None:
        super().__init__(message, None)
        self.fail_open_cause = fail_open_cause


_ERROR_REGISTRY: Dict[str, Type[ApiError]] = {
    "unauthorized": UnauthorizedError,
    "forbidden": ForbiddenError,
    "feature_not_enabled": FeatureNotEnabledError,
    "subscription_inactive": SubscriptionInactiveError,
    "rate_limited": RateLimitError,
    "monthly_volume_exceeded": MonthlyVolumeExceededError,
    "invalid_request": ValidationError,
    "invalid_json": InvalidJsonError,
    "unknown_product": UnknownProductError,
    "unknown_customer": UnknownCustomerError,
    "no_cost_basis": NoCostBasisError,
    "fx_rate_unavailable": FxRateUnavailableError,
    "fx_rate_stale": FxRateStaleError,
    "idempotency_key_reused": IdempotencyReusedError,
    "idempotency_key_in_flight": IdempotencyInFlightError,
    "batch_not_found": BatchNotFoundError,
    "batch_already_committed": BatchAlreadyCommittedError,
    "batch_entity_order_violation": BatchEntityOrderViolationError,
    "entity_not_supported": EntityNotSupportedError,
    "writeback_lease_expired": WritebackLeaseExpiredError,
    "internal_error": InternalServerError,
}


def api_error_from_code(
    *,
    code: str,
    status: int,
    message: str,
    request_id: Optional[str] = None,
    param: Optional[str] = None,
    retry_after_ms: Optional[float] = None,
) -> ApiError:
    error_class = _ERROR_REGISTRY.get(code, ApiError)
    return error_class(
        code=code,
        status=status,
        message=message,
        request_id=request_id,
        param=param,
        retry_after_ms=retry_after_ms,
    )


def _parse_api_error_payload(payload: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return None
    error = payload.get("error")
    if not isinstance(error, Mapping):
        return None
    code = error.get("code")
    message = error.get("message")
    payload_request_id = error.get("requestId")
    param = error.get("param")
    if code not in API_ERROR_CODES:
        return None
    if not isinstance(message, str) or not isinstance(payload_request_id, str):
        return None
    if param is not None and not isinstance(param, str):
        return None
    return {"code": code, "message": message, "request_id": payload_request_id, "param": param}


def error_from_payload(
    status: int,
    payload: Any,
    request_id: Optional[str],
    *,
    retry_after_ms: Optional[float] = None,
) -> ApiError:
    parsed = _parse_api_error_payload(payload)
    if parsed is None:
        return InternalServerError(
            code="internal_error",
            status=status,
            message=f"The server returned HTTP {status} with an unrecognized error body.",
            request_id=request_id,
        )
    return api_error_from_code(
        code=parsed["code"],
        status=status,
        message=parsed["message"],
        request_id=request_id if request_id is not None else parsed["request_id"],
        param=parsed["param"],
        retry_after_ms=retry_after_ms,
    )
