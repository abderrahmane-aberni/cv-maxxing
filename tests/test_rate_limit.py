from app.rate_limit import RateLimiter, RateLimitExceeded


def test_allows_requests_under_the_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_IP_PER_HOUR", "3")
    monkeypatch.setenv("RATE_LIMIT_GLOBAL_PER_DAY", "100")
    limiter = RateLimiter()
    for _ in range(3):
        limiter.check("1.2.3.4")  # should not raise


def test_blocks_requests_over_the_per_ip_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_IP_PER_HOUR", "2")
    monkeypatch.setenv("RATE_LIMIT_GLOBAL_PER_DAY", "100")
    limiter = RateLimiter()
    limiter.check("1.2.3.4")
    limiter.check("1.2.3.4")
    try:
        limiter.check("1.2.3.4")
        assert False, "expected RateLimitExceeded"
    except RateLimitExceeded:
        pass


def test_per_ip_limit_does_not_affect_other_ips(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_IP_PER_HOUR", "1")
    monkeypatch.setenv("RATE_LIMIT_GLOBAL_PER_DAY", "100")
    limiter = RateLimiter()
    limiter.check("1.1.1.1")
    limiter.check("2.2.2.2")  # different IP, should not raise


def test_blocks_requests_over_the_global_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_IP_PER_HOUR", "100")
    monkeypatch.setenv("RATE_LIMIT_GLOBAL_PER_DAY", "2")
    limiter = RateLimiter()
    limiter.check("1.1.1.1")
    limiter.check("2.2.2.2")
    try:
        limiter.check("3.3.3.3")
        assert False, "expected RateLimitExceeded"
    except RateLimitExceeded:
        pass
