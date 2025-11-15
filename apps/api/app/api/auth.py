"""Authentication endpoints implementing the magic link flow."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import create_access_token, hash_token
from app.models import MagicLinkToken, User
from app.services.email import send_magic_link_email
from app.services.user import get_active_user_by_email, normalize_email

router = APIRouter(prefix="/auth", tags=["auth"])


GENERIC_RESPONSE = {
    "detail": "If this email is registered, a login link has been sent.",
}


class MagicLinkRequestPayload(BaseModel):
    """Request payload for initiating a magic link login."""

    email: EmailStr


class MagicLinkUser(BaseModel):
    """Public user payload returned alongside tokens."""

    id: str
    email: EmailStr
    full_access: bool


class MagicLinkLoginResponse(BaseModel):
    """Response payload when redeeming a magic link."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: MagicLinkUser


def _issue_magic_link(
    session: Session,
    user: User,
    expires_at: datetime,
    ip_address: str | None,
    user_agent: str | None,
) -> str:
    """Persist a magic link token and return the raw token value."""

    for _ in range(5):
        raw_token = secrets.token_urlsafe(32)
        token = MagicLinkToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=expires_at,
            created_ip=ip_address,
            created_user_agent=user_agent,
        )
        session.add(token)
        try:
            session.commit()
            return raw_token
        except IntegrityError:
            session.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unable to generate login link",
    )


@router.post("/magic-link/request", status_code=status.HTTP_200_OK)
async def request_magic_link(
    payload: MagicLinkRequestPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Issue a single-use magic link for the provided email address."""

    normalized_email = normalize_email(payload.email)
    user = get_active_user_by_email(session, normalized_email)

    if user is None or not user.full_access:
        return GENERIC_RESPONSE

    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.magic_link_token_ttl_minutes
    )
    client = request.client
    raw_token = _issue_magic_link(
        session=session,
        user=user,
        expires_at=expires_at,
        ip_address=client.host if client else None,
        user_agent=request.headers.get("user-agent"),
    )

    magic_link_url = f"{settings.frontend_magic_login_url}?token={raw_token}"
    background_tasks.add_task(
        send_magic_link_email,
        user.email,
        magic_link_url,
    )

    return GENERIC_RESPONSE


@router.get("/magic-login", response_model=MagicLinkLoginResponse)
async def magic_login(
    token: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> MagicLinkLoginResponse:
    """Redeem a magic link token and return a JWT for the user."""

    token_hash = hash_token(token)
    statement = select(MagicLinkToken).where(MagicLinkToken.token_hash == token_hash)
    magic_link = session.exec(statement).first()

    if magic_link is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    if magic_link.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")
    expires_at = magic_link.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    user = session.get(User, magic_link.user_id)
    if user is None or not user.is_active or not user.full_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")

    magic_link.used_at = now
    session.add(magic_link)
    session.commit()

    settings = get_settings()
    access_token = create_access_token(
        subject=str(user.id),
        secret=settings.jwt_secret,
        expires_delta=timedelta(minutes=settings.access_token_ttl_minutes),
        additional_claims={"email": user.email},
    )

    return MagicLinkLoginResponse(
        access_token=access_token,
        user=MagicLinkUser(
            id=str(user.id),
            email=user.email,
            full_access=user.full_access,
        ),
    )


__all__ = ["magic_login", "request_magic_link"]
