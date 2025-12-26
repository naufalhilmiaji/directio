import time
from backend.utils.rate_limit import SimpleRateLimiter


def test_rate_limiter_allows_within_limit():
    limiter = SimpleRateLimiter(max_requests=3, window_seconds=5)
    key = "client1"

    assert limiter.allow(key) is True
    assert limiter.allow(key) is True
    assert limiter.allow(key) is True


def test_rate_limiter_blocks_after_limit():
    limiter = SimpleRateLimiter(max_requests=2, window_seconds=5)
    key = "client1"

    assert limiter.allow(key) is True
    assert limiter.allow(key) is True
    assert limiter.allow(key) is False


def test_rate_limiter_resets_after_window():
    limiter = SimpleRateLimiter(max_requests=2, window_seconds=2)
    key = "client1"

    assert limiter.allow(key) is True
    assert limiter.allow(key) is True
    assert limiter.allow(key) is False

    time.sleep(2.1)

    assert limiter.allow(key) is True
