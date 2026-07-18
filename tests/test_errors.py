import pytest

from elastly import errors


CODE_TO_CLASS = {
    "unauthorized": errors.UnauthorizedError,
    "forbidden": errors.ForbiddenError,
    "feature_not_enabled": errors.FeatureNotEnabledError,
    "subscription_inactive": errors.SubscriptionInactiveError,
    "rate_limited": errors.RateLimitError,
    "monthly_volume_exceeded": errors.MonthlyVolumeExceededError,
    "invalid_request": errors.ValidationError,
    "invalid_json": errors.InvalidJsonError,
    "unknown_product": errors.UnknownProductError,
    "unknown_customer": errors.UnknownCustomerError,
    "no_cost_basis": errors.NoCostBasisError,
    "fx_rate_unavailable": errors.FxRateUnavailableError,
    "fx_rate_stale": errors.FxRateStaleError,
    "idempotency_key_reused": errors.IdempotencyReusedError,
    "idempotency_key_in_flight": errors.IdempotencyInFlightError,
    "batch_not_found": errors.BatchNotFoundError,
    "batch_already_committed": errors.BatchAlreadyCommittedError,
    "batch_entity_order_violation": errors.BatchEntityOrderViolationError,
    "entity_not_supported": errors.EntityNotSupportedError,
    "writeback_lease_expired": errors.WritebackLeaseExpiredError,
    "internal_error": errors.InternalServerError,
}


def test_every_contract_code_has_a_registry_mapping():
    assert set(CODE_TO_CLASS) == set(errors.API_ERROR_CODES)
    assert set(errors.API_ERROR_STATUS) == set(errors.API_ERROR_CODES)


@pytest.mark.parametrize("code,error_class", sorted(CODE_TO_CLASS.items()))
def test_api_error_from_code_maps_each_code(code, error_class):
    error = errors.api_error_from_code(
        code=code,
        status=errors.API_ERROR_STATUS[code],
        message="boom",
        request_id="req_1",
        param="lines.0",
    )
    assert type(error) is error_class
    assert isinstance(error, errors.ApiError)
    assert isinstance(error, errors.ElastlyError)
    assert error.code == code
    assert error.status == errors.API_ERROR_STATUS[code]
    assert error.message == "boom"
    assert error.request_id == "req_1"
    assert error.param == "lines.0"


def test_api_error_from_code_falls_back_to_base_class_for_unknown_code():
    error = errors.api_error_from_code(code="not_a_real_code", status=500, message="boom")
    assert type(error) is errors.ApiError


def test_error_from_payload_builds_the_typed_error():
    payload = {
        "error": {
            "code": "unknown_product",
            "message": "Unknown product.",
            "param": "lines.0.productSku",
            "requestId": "req_body",
        }
    }
    error = errors.error_from_payload(404, payload, "req_header")
    assert type(error) is errors.UnknownProductError
    assert error.status == 404
    assert error.param == "lines.0.productSku"
    assert error.request_id == "req_header"


def test_error_from_payload_uses_payload_request_id_when_header_missing():
    payload = {"error": {"code": "forbidden", "message": "No.", "requestId": "req_body"}}
    error = errors.error_from_payload(403, payload, None)
    assert error.request_id == "req_body"


def test_error_from_payload_rate_limited_carries_retry_after_ms():
    payload = {"error": {"code": "rate_limited", "message": "Slow down.", "requestId": "r"}}
    error = errors.error_from_payload(429, payload, None, retry_after_ms=2000)
    assert isinstance(error, errors.RateLimitError)
    assert error.retry_after_ms == 2000


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "oops",
        {},
        {"error": "nope"},
        {"error": {"code": "made_up", "message": "m", "requestId": "r"}},
        {"error": {"code": "forbidden", "message": 5, "requestId": "r"}},
        {"error": {"code": "forbidden", "message": "m"}},
    ],
)
def test_error_from_payload_unrecognized_body_becomes_internal_server_error(payload):
    error = errors.error_from_payload(502, payload, "req_1")
    assert type(error) is errors.InternalServerError
    assert error.code == "internal_error"
    assert error.status == 502
    assert "unrecognized error body" in error.message
    assert error.request_id == "req_1"


def test_timeout_error_is_also_a_builtin_timeout():
    error = errors.TimeoutError(800)
    assert isinstance(error, TimeoutError)
    assert isinstance(error, errors.ElastlyError)
    assert error.timeout_ms == 800
    assert "800ms" in error.message
