"""A tiny in-memory rate limiter for the public /api/analyze endpoint.

Good enough for a single-instance demo deployment: it protects Gemini's
free-tier request quota and caps how much a stranger can run up on a
public link. Counters reset whenever the process restarts (e.g. Render's
free tier spinning down on idle) -- an accepted tradeoff for a demo, not
meant to survive a real multi-instance deployment (that would need a
shared store like Redis).
"""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from .config import get_settings


class RateLimitExceeded(Exception):
    def __init__(self, message: str, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class RateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._per_ip_hits: dict[str, list[float]] = defaultdict(list)
        self._global_hits: list[float] = []

    def check(self, client_ip: str) -> None:
        settings = get_settings()
        now = time.time()

        with self._lock:
            hour_ago = now - 3600
            day_ago = now - 86400

            ip_hits = [t for t in self._per_ip_hits[client_ip] if t > hour_ago]
            global_hits = [t for t in self._global_hits if t > day_ago]

            if len(ip_hits) >= settings.rate_limit_per_ip_per_hour:
                raise RateLimitExceeded(
                    f"Limit of {settings.rate_limit_per_ip_per_hour} requests/hour "
                    "per visitor reached. Try again later.",
                    retry_after_seconds=int(ip_hits[0] + 3600 - now),
                )
            if len(global_hits) >= settings.rate_limit_global_per_day:
                raise RateLimitExceeded(
                    "This demo has hit its daily request cap (protects the free "
                    "Gemini quota for everyone). Try again tomorrow, or run it "
                    "locally with your own key.",
                    retry_after_seconds=int(global_hits[0] + 86400 - now),
                )

            ip_hits.append(now)
            global_hits.append(now)
            self._per_ip_hits[client_ip] = ip_hits
            self._global_hits = global_hits


rate_limiter = RateLimiter()
