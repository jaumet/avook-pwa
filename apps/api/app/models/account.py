"""Account model placeholder."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String

from .base import Base


class Account(Base):
    """Represents an Audiovook account."""

    __tablename__ = "account"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=True)
    provider = Column(String, nullable=False, default="guest")
    created_at = Column(DateTime)
