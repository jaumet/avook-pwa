"""Binding model placeholder."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String

from .base import Base


class QrBinding(Base):
    """Represents the relation between QR codes and devices."""

    __tablename__ = "qr_binding"

    id = Column(String, primary_key=True)
    qr_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    account_id = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    revoked_at = Column(DateTime)
