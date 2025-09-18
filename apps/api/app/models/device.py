"""Device model placeholder."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String

from .base import Base


class Device(Base):
    """Represents a listening device bound to an account."""

    __tablename__ = "device"

    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=True)
    ua_hash = Column(String, nullable=False)
    created_at = Column(DateTime)
