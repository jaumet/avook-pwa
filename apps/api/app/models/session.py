"""Play session model definitions using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class PlaySession(SQLModel, table=True):
    """Represents an active playback session for a QR/device pair."""

    __tablename__ = "play_session"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False),
    )
    qr_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("qr_code.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    device_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("device.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    started_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    ended_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    ip_hash: str = Field(
        sa_column=Column(Text, nullable=False),
    )


__all__ = ["PlaySession"]
