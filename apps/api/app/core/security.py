"""Security helpers for the Audiovook API."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta


def sign_payload(secret: str, payload: str) -> str:
    """Return an HMAC signature for the given payload."""

    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""

    return secrets.token_urlsafe(length)


def expires_in(seconds: int) -> datetime:
    """Return an expiration datetime offset from now."""

    return datetime.utcnow() + timedelta(seconds=seconds)
