"""User management helpers for Audiovook."""

from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from app.models import User


def normalize_email(email: str) -> str:
    """Return a consistently formatted email address."""

    return email.strip().lower()


def get_active_user_by_email(session: Session, email: str) -> Optional[User]:
    """Return an active user with the provided email if one exists."""

    normalized = normalize_email(email)
    statement = select(User).where(User.email == normalized, User.is_active == True)  # noqa: E712
    return session.exec(statement).first()


def upsert_user_with_full_access(session: Session, email: str) -> User:
    """Ensure a user exists with full access enabled for the given email."""

    normalized = normalize_email(email)
    statement = select(User).where(User.email == normalized)
    user = session.exec(statement).first()

    if user is None:
        user = User(email=normalized, full_access=True, is_active=True)
        session.add(user)
    else:
        user.full_access = True
        user.is_active = True

    session.commit()
    session.refresh(user)
    return user


__all__ = [
    "get_active_user_by_email",
    "normalize_email",
    "upsert_user_with_full_access",
]
