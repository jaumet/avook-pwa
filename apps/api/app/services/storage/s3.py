"""S3-compatible storage backend placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class S3Settings:
    """Configuration required to interact with an S3 bucket."""

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str


class S3Storage:
    """Placeholder S3 storage client."""

    def __init__(self, settings: S3Settings) -> None:
        self.settings = settings

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"S3Storage(bucket={self.settings.bucket!r})"
