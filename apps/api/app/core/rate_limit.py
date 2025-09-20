"""Rate limiting primitives for the Audiovook API."""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Deque, DefaultDict


@dataclass(slots=True)
class RateLimitRule:
    """Configuration for a basic token bucket style rate limit."""

    requests: int
    period: timedelta


class RateLimitExceeded(Exception):
    """Raised when a rate limit has been exceeded."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = max(0.0, retry_after)
        super().__init__(f"Rate limit exceeded. Retry after {self.retry_after:.2f}s")


class RateLimiter:
    """Simple in-memory rate limiter suitable for unit tests."""

    def __init__(self) -> None:
        self._buckets: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, rule: RateLimitRule) -> None:
        """Register a request and raise if the limit would be exceeded."""

        now = time.monotonic()
        window_start = now - rule.period.total_seconds()

        with self._lock:
            bucket = self._buckets[key]

            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= rule.requests:
                retry_after = bucket[0] + rule.period.total_seconds() - now
                raise RateLimitExceeded(retry_after)

            bucket.append(now)

    def reset(self) -> None:
        """Clear all tracking state (primarily for tests)."""

        with self._lock:
            self._buckets.clear()

    @staticmethod
    def format_retry_after(seconds: float) -> str:
        """Return a header-friendly retry-after value."""

        return str(max(1, math.ceil(seconds)))


DEFAULT_ACCESS_RULE = RateLimitRule(requests=30, period=timedelta(minutes=1))
DEFAULT_PREVIEW_RULE = RateLimitRule(requests=10, period=timedelta(minutes=1))


__all__ = [
    "DEFAULT_ACCESS_RULE",
    "DEFAULT_PREVIEW_RULE",
    "RateLimitExceeded",
    "RateLimitRule",
    "RateLimiter",
]
