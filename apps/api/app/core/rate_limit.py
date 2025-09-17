"""Rate limiting primitives for the Audiovook API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(slots=True)
class RateLimitRule:
    """Configuration for a basic token bucket style rate limit."""

    requests: int
    period: timedelta


DEFAULT_ACCESS_RULE = RateLimitRule(requests=30, period=timedelta(minutes=1))
DEFAULT_PREVIEW_RULE = RateLimitRule(requests=10, period=timedelta(minutes=1))
