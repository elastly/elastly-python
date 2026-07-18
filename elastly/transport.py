"""Resilient request layer composed over the generated urllib3 client.

Adds what the generated client lacks: typed errors, full-jitter retries that
honor Retry-After, per-call idempotency keys, an overall deadline budget, and
best-effort fire-and-forget beacons off the latency path.
"""

from __future__ import annotations

import json
import random as random_module
import threading
import time
from typing import Any, Callable, Mapping, Optional, Tuple

import urllib3.exceptions

from elastly import errors
from elastly.api.prices_api import PricesApi
from elastly.exceptions import ApiException
from elastly.models.prices_request import PricesRequest
from elastly.models.prices_response import PricesResponse
from elastly.resilience.idempotency import generate_idempotency_key
from elastly.resilience.retry import (
    DEFAULT_RETRY_POLICY,
    RetryPolicy,
    retry_after_ms_from_headers,
    retry_delay_ms,
)

DEFAULT_TIMEOUT_MS = 10_000.0
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})

_TIMEOUT_EXCEPTIONS = (
    urllib3.exceptions.ReadTimeoutError,
    urllib3.exceptions.ConnectTimeoutError,
)


def _monotonic_ms() -> float:
    return time.monotonic() * 1000.0


def _default_sleep(ms: float) -> None:
    if ms > 0:
        time.sleep(ms / 1000.0)


def _start_daemon_thread(target: Callable[[], None]) -> None:
    threading.Thread(target=target, daemon=True).start()


def _classify_transport_failure(exc: Exception, attempt_timeout_ms: float) -> errors.ElastlyError:
    if isinstance(exc, _TIMEOUT_EXCEPTIONS):
        return errors.TimeoutError(attempt_timeout_ms, None)
    if isinstance(exc, urllib3.exceptions.MaxRetryError) and isinstance(
        exc.reason, _TIMEOUT_EXCEPTIONS
    ):
        return errors.TimeoutError(attempt_timeout_ms, None)
    return errors.NetworkError(str(exc) or "The request failed to send.", None)


def _header(headers: Optional[Mapping[str, str]], name: str) -> Optional[str]:
    if headers is None:
        return None
    value = headers.get(name)
    if value is not None:
        return value
    lowered = name.lower()
    for key, candidate in headers.items():
        if key.lower() == lowered:
            return candidate
    return None


def error_from_api_exception(exc: ApiException) -> Tuple[errors.ApiError, Optional[float]]:
    headers = exc.headers
    request_id = _header(headers, "x-elastly-request-id")
    retry_after_ms = retry_after_ms_from_headers(headers) if headers is not None else None
    payload: Any = None
    if exc.body:
        try:
            payload = json.loads(exc.body)
        except ValueError:
            payload = None
    status = exc.status if isinstance(exc.status, int) else 0
    return (
        errors.error_from_payload(status, payload, request_id, retry_after_ms=retry_after_ms),
        retry_after_ms,
    )


class ElastlyTransport:
    """Wraps the generated ``PricesApi`` with retries, deadlines, and beacons."""

    def __init__(
        self,
        api_client: Any,
        *,
        timeout_ms: float = DEFAULT_TIMEOUT_MS,
        retry: RetryPolicy = DEFAULT_RETRY_POLICY,
        sleep: Optional[Callable[[float], None]] = None,
        random: Optional[Callable[[], float]] = None,
        clock: Optional[Callable[[], float]] = None,
        idempotency_key_factory: Optional[Callable[[], str]] = None,
        prices_api: Optional[Any] = None,
        beacon_runner: Optional[Callable[[Callable[[], None]], None]] = None,
    ) -> None:
        self._api_client = api_client
        self._prices_api = prices_api if prices_api is not None else PricesApi(api_client)
        self._timeout_ms = timeout_ms
        self._retry = retry
        self._sleep = sleep if sleep is not None else _default_sleep
        self._random = random if random is not None else random_module.random
        self._clock = clock if clock is not None else _monotonic_ms
        self._idempotency_key_factory = (
            idempotency_key_factory if idempotency_key_factory is not None else generate_idempotency_key
        )
        self._beacon_runner = beacon_runner if beacon_runner is not None else _start_daemon_thread

    def request_prices(
        self,
        request: PricesRequest,
        *,
        deadline_ms: Optional[float] = None,
    ) -> PricesResponse:
        # One idempotency key per logical request; every retry replays the same key.
        idempotency_key = self._idempotency_key_factory()
        started = self._clock()
        attempt = 0

        while True:
            remaining: Optional[float] = None
            if deadline_ms is not None:
                remaining = deadline_ms - (self._clock() - started)
                if remaining <= 0:
                    raise errors.TimeoutError(deadline_ms, None)
            attempt_timeout_ms = (
                self._timeout_ms if remaining is None else min(self._timeout_ms, remaining)
            )

            error: errors.ElastlyError
            retry_after_ms: Optional[float] = None
            try:
                return self._prices_api.get_prices(
                    idempotency_key=idempotency_key,
                    prices_request=request,
                    _request_timeout=attempt_timeout_ms / 1000.0,
                )
            except ApiException as exc:
                error, retry_after_ms = error_from_api_exception(exc)
                retryable = exc.status in RETRYABLE_STATUS
            except (urllib3.exceptions.HTTPError, OSError) as exc:
                error = _classify_transport_failure(exc, attempt_timeout_ms)
                error.__cause__ = exc
                retryable = True
            except ValueError as exc:
                # A 2xx body the generated deserializer could not parse.
                malformed = errors.MalformedResponseError(
                    "The response body does not match the API contract.", None
                )
                raise malformed from exc

            if not (retryable and attempt < self._retry.max_attempts - 1):
                raise error

            delay = retry_delay_ms(self._retry, attempt, retry_after_ms, self._random)
            if deadline_ms is not None:
                remaining = deadline_ms - (self._clock() - started)
                if delay >= remaining:
                    # Match the async race semantics: wait out the budget, then time out.
                    self._sleep(max(remaining, 0.0))
                    raise errors.TimeoutError(deadline_ms, None)
            self._sleep(delay)
            attempt += 1

    def fire_and_forget(self, path: str, body: Mapping[str, Any]) -> None:
        payload = dict(body)

        def send() -> None:
            try:
                configuration = self._api_client.configuration
                headers = {"Content-Type": "application/json"}
                for setting in configuration.auth_settings().values():
                    if setting.get("in") == "header" and setting.get("value") is not None:
                        headers[setting["key"]] = setting["value"]
                self._api_client.rest_client.request(
                    "POST",
                    configuration.host + path,
                    headers=headers,
                    body=payload,
                    _request_timeout=self._timeout_ms / 1000.0,
                )
            except Exception:
                pass

        self._beacon_runner(send)
