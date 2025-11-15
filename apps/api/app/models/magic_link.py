"""Magic link token model definitions."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class MagicLinkToken(SQLModel, table=True):
    """Represents a single-use magic link token issued to a user."""

    __tablename__ = "magic_link_token"
    __table_args__ = (
        Index("idx_magic_link_token_user", "user_id"),
        Index("idx_magic_link_token_hash", "token_hash"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False),
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    token_hash: str = Field(
        sa_column=Column(Text, nullable=False, unique=True),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    used_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_ip: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    created_user_agent: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )


__all__ = ["MagicLinkToken"]
