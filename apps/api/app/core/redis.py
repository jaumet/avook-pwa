"""Redis client helpers for the Audiovook API."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from redis import Redis
from redis.exceptions import RedisError

from .config import get_settings

logger = logging.getLogger("app.redis")


@lru_cache
def get_redis_client() -> Optional[Redis]:
    """Return a Redis client for shared infrastructure features.

    The helper performs a connectivity check when initialising the client. If the
    Redis instance is unavailable (as is often the case when running the unit
    test suite without Docker), ``None`` is returned so callers can fall back to
    in-memory implementations while still supporting Redis-backed behaviour in
    real deployments.
    """

    settings = get_settings()

    try:
        client = Redis.from_url(settings.redis_url)
        client.ping()
    except RedisError as exc:  # pragma: no cover - defensive logging path
        logger.warning(
            "Redis unavailable at %s: %s — falling back to in-memory handling",
            settings.redis_url,
            exc,
        )
        return None

    return client


__all__ = ["get_redis_client"]
