"""Rate limiting and security headers (added in Module 10)."""
from __future__ import annotations

import threading
import time
from typing import Dict, Tuple

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",                       # API responses contain personal data: never cache
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


class RateLimiter:
    """Token bucket per key (e.g. client IP, or username for logins). In-memory: per process.

    With several API instances, each enforces its own limit. Use a shared store (Redis) or the
    platform's gateway/WAF for a global limit (Lesson 03).
    """

    def __init__(self, rate_per_minute: float, burst: int):
        self.rate = rate_per_minute / 60.0
        self.burst = burst
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, now: float = None) -> Tuple[bool, float]:
        """Returns (allowed, seconds until the next request would be allowed)."""
        now = time.monotonic() if now is None else now
        with self._lock:
            tokens, last = self._buckets.get(key, (float(self.burst), now))
            tokens = min(self.burst, tokens + (now - last) * self.rate)
            if tokens >= 1:
                self._buckets[key] = (tokens - 1, now)
                return True, 0.0
            self._buckets[key] = (tokens, now)
            return False, (1 - tokens) / self.rate
