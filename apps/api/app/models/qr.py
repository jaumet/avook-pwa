"""Data model definitions for QR codes."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


class QrCode(Base):
    """Placeholder SQLAlchemy model for QR codes."""

    __tablename__ = "qr_code"

    id = Column(String, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False, default="new")
    product_id = Column(Integer, nullable=True)
    batch_id = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    registered_at = Column(DateTime)
