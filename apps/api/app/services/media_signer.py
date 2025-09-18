"""Media signing helper placeholders."""

from __future__ import annotations

from datetime import datetime

from app.core.security import sign_payload


def sign_media_url(secret: str, url: str, expires_at: datetime) -> str:
    """Return a dummy signed URL for development purposes."""

    signature = sign_payload(secret, f"{url}|{int(expires_at.timestamp())}")
    return f"{url}?sig={signature}&exp={int(expires_at.timestamp())}"
