"""Email delivery helpers for Audiovook."""

from __future__ import annotations

import logging

logger = logging.getLogger("app.services.email")


def send_magic_link_email(recipient: str, magic_link_url: str) -> None:
    """Send a magic login link to the provided recipient."""

    logger.info("Sending magic link email", extra={"recipient": recipient, "url": magic_link_url})


__all__ = ["send_magic_link_email"]
