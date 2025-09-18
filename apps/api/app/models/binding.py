"""Binding model definitions using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class QrBinding(SQLModel, table=True):
    """Represents the relationship between a QR code and a device/account."""

    __tablename__ = "qr_binding"
    __table_args__ = (Index("idx_binding_qr_active", "qr_id", "active"),)

    qr_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("qr_code.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )
    device_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("device.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )
    account_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("account.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=text("true"),
        ),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    revoked_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


__all__ = ["QrBinding"]
