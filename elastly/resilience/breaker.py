"""Thread-safe circuit breaker with a single half-open probe."""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional


def _monotonic_ms() -> float:
    return time.monotonic() * 1000.0


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        cooldown_ms: float = 30_000.0,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_ms = cooldown_ms
        self._now = now if now is not None else _monotonic_ms
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._opened_at: Optional[float] = None
        self._probing = False
        self._beaconed_this_open = False

    def allow_request(self) -> bool:
        with self._lock:
            if self._opened_at is None:
                return True
            if self._now() - self._opened_at < self._cooldown_ms:
                return False
            if self._probing:
                return False
            self._probing = True
            return True

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self._opened_at is not None and self._now() - self._opened_at < self._cooldown_ms

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._opened_at = None
            self._probing = False
            self._beaconed_this_open = False

    def record_failure(self) -> None:
        with self._lock:
            self._consecutive_failures += 1
            self._probing = False
            if self._consecutive_failures >= self._failure_threshold:
                if self._opened_at is None:
                    self._beaconed_this_open = False
                self._opened_at = self._now()

    def should_beacon_while_open(self) -> bool:
        with self._lock:
            if self._beaconed_this_open:
                return False
            self._beaconed_this_open = True
            return True
