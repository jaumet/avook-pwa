"""One-time password helper placeholders."""

from __future__ import annotations

import secrets
from dataclasses import dataclass


@dataclass(slots=True)
class OtpCode:
    """Represents an OTP that can be sent to a user."""

    code: str
    ttl_seconds: int


def generate_otp(length: int = 6, ttl_seconds: int = 300) -> OtpCode:
    """Generate a numeric OTP suitable for SMS/email delivery."""

    digits = "".join(str(secrets.randbelow(10)) for _ in range(length))
    return OtpCode(code=digits, ttl_seconds=ttl_seconds)
