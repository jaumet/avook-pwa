"""Account model definitions using SQLModel."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class AccountProvider(str, Enum):
    """Supported identity providers for Audiovook accounts."""

    GOOGLE = "google"
    APPLE = "apple"
    OTP = "otp"
    GUEST = "guest"


class Account(SQLModel, table=True):
    """Persisted representation of an end-user account."""

    __tablename__ = "account"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False),
    )
    email: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True, unique=True),
    )
    provider: AccountProvider = Field(
        sa_column=Column(
            SAEnum(AccountProvider, name="account_provider"),
            nullable=False,
        ),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


__all__ = ["Account", "AccountProvider"]
