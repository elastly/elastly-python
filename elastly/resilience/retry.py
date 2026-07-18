"""Retry policy: full-jitter exponential backoff that honors server rate-limit hints."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Callable, Mapping, Optional


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_ms: float = 250.0
    max_delay_ms: float = 10_000.0


DEFAULT_RETRY_POLICY = RetryPolicy()


def retry_delay_ms(
    policy: RetryPolicy,
    attempt: int,
    retry_after_ms: Optional[float],
    random: Callable[[], float],
) -> float:
    if retry_after_ms is not None and retry_after_ms >= 0:
        return min(retry_after_ms, policy.max_delay_ms)
    ceiling = min(policy.max_delay_ms, policy.base_delay_ms * (2**attempt))
    return math.floor(random() * ceiling)


def _header(headers: Mapping[str, str], name: str) -> Optional[str]:
    value = headers.get(name)
    if value is not None:
        return value
    lowered = name.lower()
    for key, candidate in headers.items():
        if key.lower() == lowered:
            return candidate
    return None


def _finite_seconds(value: str) -> Optional[float]:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if math.isfinite(seconds) else None


def retry_after_ms_from_headers(
    headers: Mapping[str, str],
    now_ms: Optional[Callable[[], float]] = None,
) -> Optional[float]:
    wall_clock_ms = now_ms if now_ms is not None else lambda: time.time() * 1000.0
    retry_after = _header(headers, "retry-after")
    if retry_after is not None:
        seconds = _finite_seconds(retry_after)
        if seconds is not None:
            return max(0.0, seconds * 1000.0)
        try:
            at = parsedate_to_datetime(retry_after)
        except (TypeError, ValueError):
            at = None
        if at is not None:
            return max(0.0, at.timestamp() * 1000.0 - wall_clock_ms())
    reset = _header(headers, "ratelimit-reset")
    if reset is not None:
        seconds = _finite_seconds(reset)
        if seconds is not None:
            return max(0.0, seconds * 1000.0)
    return None
