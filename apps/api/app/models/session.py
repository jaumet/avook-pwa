"""Playback session model placeholder."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String

from .base import Base


class PlaySession(Base):
    """Represents a listening session tied to a device and QR code."""

    __tablename__ = "play_session"

    id = Column(String, primary_key=True)
    qr_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    ip_hash = Column(String, nullable=True)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
