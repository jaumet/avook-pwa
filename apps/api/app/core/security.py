"""Security helpers for the Audiovook API."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


def sign_payload(secret: str, payload: str) -> str:
    """Return an HMAC signature for the given payload."""

    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""

    return secrets.token_urlsafe(length)


def expires_in(seconds: int) -> datetime:
    """Return an expiration datetime offset from now."""

    return datetime.utcnow() + timedelta(seconds=seconds)


def hash_token(raw_token: str) -> str:
    """Return the SHA-256 hash of a raw token value."""

    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    subject: str,
    secret: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a signed JWT access token for the given subject."""

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    payload: Dict[str, Any] = {"sub": subject, "exp": expire}
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> Dict[str, Any]:
    """Decode and validate an access token, returning its payload."""

    return jwt.decode(token, secret, algorithms=["HS256"])


__all__ = [
    "create_access_token",
    "decode_access_token",
    "expires_in",
    "generate_token",
    "hash_token",
    "sign_payload",
]
