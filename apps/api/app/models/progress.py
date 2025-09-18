"""Listening progress model definitions using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class ListeningProgress(SQLModel, table=True):
    """Tracks the playback progress for a QR/account/device combination."""

    __tablename__ = "listening_progress"
    __table_args__ = (Index("idx_progress_updated_at", "updated_at"),)

    qr_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("qr_code.id", ondelete="CASCADE"),
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
    device_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("device.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )
    track_id: str = Field(
        sa_column=Column(Text, primary_key=True, nullable=False),
    )
    position_ms: int = Field(
        sa_column=Column(Integer, nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


__all__ = ["ListeningProgress"]
