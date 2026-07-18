from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

from elastly.resilience import DEFAULT_RETRY_POLICY, RetryPolicy, retry_after_ms_from_headers, retry_delay_ms


def test_default_policy_values():
    assert DEFAULT_RETRY_POLICY == RetryPolicy(max_attempts=3, base_delay_ms=250, max_delay_ms=10_000)


def test_full_jitter_scales_with_attempt():
    policy = DEFAULT_RETRY_POLICY
    assert retry_delay_ms(policy, 0, None, lambda: 1.0) == 250
    assert retry_delay_ms(policy, 1, None, lambda: 1.0) == 500
    assert retry_delay_ms(policy, 2, None, lambda: 1.0) == 1000
    assert retry_delay_ms(policy, 0, None, lambda: 0.0) == 0
    assert retry_delay_ms(policy, 1, None, lambda: 0.5) == 250


def test_full_jitter_ceiling_capped_at_max_delay():
    policy = DEFAULT_RETRY_POLICY
    assert retry_delay_ms(policy, 10, None, lambda: 1.0) == 10_000


def test_retry_after_takes_precedence_and_is_capped():
    policy = DEFAULT_RETRY_POLICY
    assert retry_delay_ms(policy, 0, 2000, lambda: 1.0) == 2000
    assert retry_delay_ms(policy, 0, 60_000, lambda: 1.0) == 10_000
    assert retry_delay_ms(policy, 0, 0, lambda: 1.0) == 0


def test_negative_retry_after_falls_back_to_jitter():
    assert retry_delay_ms(DEFAULT_RETRY_POLICY, 0, -1, lambda: 1.0) == 250


def test_retry_after_seconds_header():
    assert retry_after_ms_from_headers({"Retry-After": "2"}) == 2000
    assert retry_after_ms_from_headers({"retry-after": "0.5"}) == 500


def test_retry_after_http_date_header():
    now = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
    header = format_datetime(now + timedelta(seconds=30), usegmt=True)
    delay = retry_after_ms_from_headers(
        {"Retry-After": header}, now_ms=lambda: now.timestamp() * 1000
    )
    assert delay == 30_000


def test_retry_after_http_date_in_the_past_clamps_to_zero():
    now = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
    header = format_datetime(now - timedelta(seconds=30), usegmt=True)
    delay = retry_after_ms_from_headers(
        {"Retry-After": header}, now_ms=lambda: now.timestamp() * 1000
    )
    assert delay == 0


def test_ratelimit_reset_header_used_when_no_retry_after():
    assert retry_after_ms_from_headers({"RateLimit-Reset": "30"}) == 30_000


def test_no_hint_headers_returns_none():
    assert retry_after_ms_from_headers({}) is None
    assert retry_after_ms_from_headers({"Retry-After": "not-a-date"}) is None
