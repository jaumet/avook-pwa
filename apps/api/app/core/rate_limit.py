"""Rate limiting primitives for the Audiovook API."""

from __future__ import annotations

import math
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Deque, DefaultDict, Optional, Set

from redis import Redis
from redis.exceptions import RedisError


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
    """Rate limiter supporting Redis-backed buckets with in-memory fallback."""

    def __init__(self, redis_client: Optional[Redis] = None) -> None:
        self._redis: Optional[Redis] = redis_client
        self._buckets: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._redis_keys: Set[str] = set()
        self._redis_lock = threading.Lock()

    def configure_redis(self, redis_client: Optional[Redis]) -> None:
        """Replace the Redis client used for distributed rate limiting."""

        with self._redis_lock:
            self._redis = redis_client
            self._redis_keys.clear()

    def check(self, key: str, rule: RateLimitRule) -> None:
        """Register a request and raise if the limit would be exceeded."""

        if self._redis is not None:
            if self._check_redis(key, rule):
                return

        self._check_local(key, rule)

    # ------------------------------------------------------------------
    # Redis handling
    # ------------------------------------------------------------------
    def _check_redis(self, key: str, rule: RateLimitRule) -> bool:
        redis_client = self._redis
        if redis_client is None:
            return False

        bucket_key = self._format_bucket_key(key)
        now = time.time()
        member = f"{now:.6f}:{uuid.uuid4().hex}"
        window = rule.period.total_seconds()

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(bucket_key, 0, now - window)
            pipe.zadd(bucket_key, {member: now})
            pipe.zcard(bucket_key)
            pipe.zrange(bucket_key, 0, 0, withscores=True)
            pipe.expire(bucket_key, math.ceil(window))
            _, _, count, oldest_entries, _ = pipe.execute()

            with self._redis_lock:
                self._redis_keys.add(bucket_key)

        except RedisError:
            self.configure_redis(None)
            return False

        if count > rule.requests:
            retry_after = window
            if oldest_entries:
                # ``oldest_entries`` contains ``(member, score)`` pairs where the score
                # matches the request timestamp we stored in ``zadd``.
                retry_after = max(0.0, float(oldest_entries[0][1]) + window - now)

            try:
                cleanup_pipe = redis_client.pipeline()
                cleanup_pipe.zrem(bucket_key, member)
                cleanup_pipe.expire(bucket_key, math.ceil(window))
                cleanup_pipe.execute()
            except RedisError:
                self.configure_redis(None)

            raise RateLimitExceeded(retry_after)

        return True

    @staticmethod
    def _format_bucket_key(key: str) -> str:
        return f"rate:{key}"

    # ------------------------------------------------------------------
    # Local fallback implementation
    # ------------------------------------------------------------------
    def _check_local(self, key: str, rule: RateLimitRule) -> None:
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

        redis_client = self._redis
        if redis_client is None:
            return

        with self._redis_lock:
            keys = list(self._redis_keys)
            self._redis_keys.clear()

        if not keys:
            return

        try:
            redis_client.delete(*keys)
        except RedisError:
            self.configure_redis(None)

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
