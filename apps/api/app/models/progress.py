"""Listening progress model placeholder."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


class ListeningProgress(Base):
    """Represents listening progress for a specific track."""

    __tablename__ = "listening_progress"

    id = Column(String, primary_key=True)
    qr_id = Column(String, nullable=False)
    account_id = Column(String, nullable=True)
    device_id = Column(String, nullable=False)
    track_id = Column(String, nullable=False)
    position_ms = Column(Integer, default=0)
    updated_at = Column(DateTime)
