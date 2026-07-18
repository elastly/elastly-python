from elastly.resilience import CircuitBreaker


class FakeClock:
    def __init__(self):
        self.ms = 0.0

    def __call__(self):
        return self.ms


def make_breaker(clock, **overrides):
    return CircuitBreaker(failure_threshold=5, cooldown_ms=30_000, now=clock, **overrides)


def trip(breaker, failures=5):
    for _ in range(failures):
        breaker.record_failure()


def test_closed_breaker_allows_requests():
    breaker = make_breaker(FakeClock())
    assert breaker.allow_request() is True
    assert breaker.is_open is False


def test_opens_after_threshold_consecutive_failures():
    clock = FakeClock()
    breaker = make_breaker(clock)
    trip(breaker, 4)
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.is_open is True
    assert breaker.allow_request() is False


def test_success_resets_the_failure_streak():
    breaker = make_breaker(FakeClock())
    trip(breaker, 4)
    breaker.record_success()
    trip(breaker, 4)
    assert breaker.is_open is False


def test_half_open_allows_a_single_probe_after_cooldown():
    clock = FakeClock()
    breaker = make_breaker(clock)
    trip(breaker)
    clock.ms = 30_000
    assert breaker.allow_request() is True
    assert breaker.allow_request() is False


def test_probe_success_closes_the_breaker():
    clock = FakeClock()
    breaker = make_breaker(clock)
    trip(breaker)
    clock.ms = 30_000
    assert breaker.allow_request() is True
    breaker.record_success()
    assert breaker.is_open is False
    assert breaker.allow_request() is True


def test_probe_failure_reopens_for_a_fresh_cooldown():
    clock = FakeClock()
    breaker = make_breaker(clock)
    trip(breaker)
    clock.ms = 30_000
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.is_open is True
    assert breaker.allow_request() is False
    clock.ms = 59_999
    assert breaker.allow_request() is False
    clock.ms = 60_000
    assert breaker.allow_request() is True


def test_should_beacon_while_open_fires_once_per_open_episode():
    clock = FakeClock()
    breaker = make_breaker(clock)
    trip(breaker)
    assert breaker.should_beacon_while_open() is True
    assert breaker.should_beacon_while_open() is False
    breaker.record_success()
    trip(breaker)
    assert breaker.should_beacon_while_open() is True
