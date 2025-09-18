"""QR code model definitions using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, Index, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class QrStatus(str, Enum):
    """Lifecycle status for QR codes."""

    NEW = "new"
    ACTIVE = "active"
    BLOCKED = "blocked"


class QrCode(SQLModel, table=True):
    """Represents a QR token that grants access to Audiovook content."""

    __tablename__ = "qr_code"
    __table_args__ = (Index("idx_qr_token", "token"),)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False),
    )
    token: str = Field(
        sa_column=Column(Text, unique=True, nullable=False),
    )
    status: QrStatus = Field(
        default=QrStatus.NEW,
        sa_column=Column(
            SAEnum(QrStatus, name="qr_status"),
            nullable=False,
        ),
    )
    product_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    batch_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    registered_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    max_reactivations: int = Field(
        default=999,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=text("999"),
        ),
    )
    cooldown_until: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


__all__ = ["QrCode", "QrStatus"]
