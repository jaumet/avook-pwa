"""Access management endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.database import get_session
from app.models import QrCode, QrStatus

router = APIRouter(prefix="/access")


class AccessValidateRequest(BaseModel):
    """Payload used to validate a QR token."""

    token: str = Field(..., min_length=1)
    device_id: Optional[uuid.UUID] = None


class ProductInfo(BaseModel):
    """Basic product metadata returned with validation results."""

    id: Optional[int] = None
    title: Optional[str] = None


class AccessValidateResponse(BaseModel):
    """Response schema for token validation attempts."""

    status: Literal["new", "registered", "invalid", "blocked"]
    can_reregister: bool
    preview_available: bool
    cooldown_until: Optional[datetime] = None
    product: Optional[ProductInfo] = None
    token: str


def _build_product_payload(qr: QrCode) -> Optional[ProductInfo]:
    if qr.product_id is None:
        return None

    title = f"Product #{qr.product_id}" if qr.product_id is not None else None
    return ProductInfo(id=qr.product_id, title=title)


@router.post("/validate", response_model=AccessValidateResponse)
def validate_access(
    payload: AccessValidateRequest,
    session: Session = Depends(get_session),
) -> AccessValidateResponse:
    """Validate a QR token and return its access status."""

    token = payload.token.strip()
    if not token:
        return AccessValidateResponse(
            status="invalid",
            can_reregister=False,
            preview_available=False,
            cooldown_until=None,
            product=None,
            token=payload.token,
        )

    query = select(QrCode).where(QrCode.token == token)
    qr_code = session.exec(query).first()

    if qr_code is None:
        return AccessValidateResponse(
            status="invalid",
            can_reregister=False,
            preview_available=False,
            cooldown_until=None,
            product=None,
            token=token,
        )

    if qr_code.status is QrStatus.BLOCKED:
        status: Literal["new", "registered", "invalid", "blocked"] = "blocked"
    elif qr_code.status is QrStatus.NEW:
        status = "new"
    else:
        status = "registered"

    return AccessValidateResponse(
        status=status,
        can_reregister=status in {"new", "registered"},
        preview_available=status != "blocked",
        cooldown_until=qr_code.cooldown_until,
        product=_build_product_payload(qr_code),
        token=qr_code.token,
    )


__all__ = ["router"]
