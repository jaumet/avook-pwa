"""Access management endpoints."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.rate_limit import DEFAULT_ACCESS_RULE, RateLimitExceeded, RateLimiter
from app.core.redis import get_redis_client
from app.models import Device, QrBinding, QrCode, QrStatus

logger = logging.getLogger("app.access")

rate_limiter = RateLimiter(redis_client=get_redis_client())


def _hash_identifier(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _log_event(
    request: Request,
    event_type: str,
    token: str,
    device_id: Optional[uuid.UUID],
    **extra: Any,
) -> None:
    client_host = request.client.host if request.client else ""
    request_id = request.headers.get("X-Request-ID")
    user_agent = request.headers.get("User-Agent", "unknown")

    payload: dict[str, Any] = {
        "event_type": event_type,
        "token_hash": _hash_identifier(token),
        "device_id": str(device_id) if device_id else None,
        "ip_hash": _hash_identifier(client_host) if client_host else None,
        "request_id": request_id,
        "user_agent_hash": _hash_identifier(user_agent),
    }
    if extra:
        payload.update(extra)

    logger.info(json.dumps(payload))


def enforce_access_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "anonymous"
    key = f"access:{client_host}"

    try:
        rate_limiter.check(key, DEFAULT_ACCESS_RULE)
    except RateLimitExceeded as exc:  # pragma: no cover - handled via HTTPException
        retry_after = RateLimiter.format_retry_after(exc.retry_after)
        _log_event(
            request,
            "access.rate_limited",
            token="",
            device_id=None,
            retry_after=retry_after,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Retry-After": retry_after},
        ) from exc


router = APIRouter(prefix="/access", dependencies=[Depends(enforce_access_rate_limit)])


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


def _build_validation_payload(qr_code: QrCode) -> AccessValidateResponse:
    if qr_code.status is QrStatus.BLOCKED:
        status: Literal["new", "registered", "invalid", "blocked"] = "blocked"
    elif qr_code.status is QrStatus.NEW:
        status = "new"
    else:
        status = "registered"

    cooldown_active = (
        qr_code.cooldown_until is not None
        and qr_code.cooldown_until > datetime.utcnow()
    )

    return AccessValidateResponse(
        status=status,
        can_reregister=status in {"new", "registered"} and not cooldown_active,
        preview_available=status != "blocked",
        cooldown_until=qr_code.cooldown_until,
        product=_build_product_payload(qr_code),
        token=qr_code.token,
    )


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

    return _build_validation_payload(qr_code)


class AccessRegisterRequest(BaseModel):
    """Payload for the initial device registration flow."""

    token: str = Field(..., min_length=1)
    device_id: uuid.UUID
    account_id: Optional[uuid.UUID] = None


class AccessReregisterRequest(BaseModel):
    """Payload for moving an existing binding to a new device."""

    token: str = Field(..., min_length=1)
    new_device_id: uuid.UUID
    account_id: Optional[uuid.UUID] = None


def _get_active_binding(session: Session, qr_id: uuid.UUID) -> Optional[QrBinding]:
    binding_query = (
        select(QrBinding)
        .where(QrBinding.qr_id == qr_id)
        .where(QrBinding.active.is_(True))
    )
    return session.exec(binding_query).first()


def _ensure_device(
    session: Session,
    device_id: uuid.UUID,
    ua_hash: str,
    account_id: Optional[uuid.UUID],
) -> Device:
    device = session.get(Device, device_id)
    if device is None:
        device = Device(id=device_id, ua_hash=ua_hash, account_id=account_id)
        session.add(device)
    elif account_id is not None and device.account_id != account_id:
        device.account_id = account_id
    return device


def _check_cooldown(
    qr_code: QrCode,
    request: Request,
    token: str,
    device_id: uuid.UUID,
    action: str,
) -> None:
    if (
        qr_code.cooldown_until is not None
        and qr_code.cooldown_until > datetime.utcnow()
    ):
        _log_event(
            request,
            f"access.{action}.cooldown",
            token,
            device_id,
            cooldown_until=qr_code.cooldown_until.isoformat(),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is temporarily on cooldown",
        )


@router.post("/register", response_model=AccessValidateResponse)
def register_access(
    payload: AccessRegisterRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> AccessValidateResponse:
    """Create the initial binding between a QR token and a device."""

    token = payload.token.strip()
    if not token:
        _log_event(request, "access.register.invalid", payload.token, payload.device_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required")

    qr_code = session.exec(select(QrCode).where(QrCode.token == token)).first()
    if qr_code is None:
        _log_event(request, "access.register.not_found", token, payload.device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    if qr_code.status is QrStatus.BLOCKED:
        _log_event(request, "access.register.blocked", token, payload.device_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is blocked")

    _check_cooldown(qr_code, request, token, payload.device_id, "register")

    active_binding = _get_active_binding(session, qr_code.id)
    if active_binding is not None:
        if active_binding.device_id == payload.device_id:
            if (
                payload.account_id is not None
                and active_binding.account_id != payload.account_id
            ):
                active_binding.account_id = payload.account_id
                session.add(active_binding)
                session.commit()
                session.refresh(qr_code)
            _log_event(request, "access.register.idempotent", token, payload.device_id)
            return _build_validation_payload(qr_code)

        _log_event(
            request,
            "access.register.conflict",
            token,
            payload.device_id,
            conflict_device=str(active_binding.device_id),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Token already bound to a different device",
        )

    ua_hash = _hash_identifier(request.headers.get("User-Agent", "unknown"))
    _ensure_device(session, payload.device_id, ua_hash, payload.account_id)

    binding = QrBinding(
        qr_id=qr_code.id,
        device_id=payload.device_id,
        account_id=payload.account_id,
        active=True,
    )
    session.add(binding)

    qr_code.status = QrStatus.ACTIVE
    qr_code.registered_at = datetime.utcnow()
    session.add(qr_code)

    session.commit()
    session.refresh(qr_code)

    _log_event(
        request,
        "access.register.success",
        token,
        payload.device_id,
        account_id=str(payload.account_id) if payload.account_id else None,
    )

    return _build_validation_payload(qr_code)


def _count_total_bindings(session: Session, qr_id: uuid.UUID) -> int:
    return session.exec(
        select(func.count())
        .select_from(QrBinding)
        .where(QrBinding.qr_id == qr_id)
    ).one()


def _count_recent_reactivations(session: Session, qr_id: uuid.UUID, now: datetime) -> int:
    cutoff = now - timedelta(hours=24)
    return session.exec(
        select(func.count())
        .select_from(QrBinding)
        .where(QrBinding.qr_id == qr_id)
        .where(QrBinding.revoked_at.is_not(None))
        .where(QrBinding.revoked_at >= cutoff)
    ).one()


@router.post("/reregister", response_model=AccessValidateResponse)
def reregister_access(
    payload: AccessReregisterRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> AccessValidateResponse:
    """Move an existing registration to a new device."""

    token = payload.token.strip()
    if not token:
        _log_event(request, "access.reregister.invalid", payload.token, payload.new_device_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required")

    qr_code = session.exec(select(QrCode).where(QrCode.token == token)).first()
    if qr_code is None:
        _log_event(request, "access.reregister.not_found", token, payload.new_device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    if qr_code.status is QrStatus.BLOCKED:
        _log_event(request, "access.reregister.blocked", token, payload.new_device_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is blocked")

    _check_cooldown(qr_code, request, token, payload.new_device_id, "reregister")

    active_binding = _get_active_binding(session, qr_code.id)
    if active_binding is None:
        _log_event(request, "access.reregister.missing_binding", token, payload.new_device_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active registration to move",
        )

    if active_binding.device_id == payload.new_device_id:
        if (
            payload.account_id is not None
            and active_binding.account_id != payload.account_id
        ):
            active_binding.account_id = payload.account_id
            session.add(active_binding)
            session.commit()
            session.refresh(qr_code)
        _log_event(request, "access.reregister.idempotent", token, payload.new_device_id)
        return _build_validation_payload(qr_code)

    total_bindings = _count_total_bindings(session, qr_code.id)
    if total_bindings - 1 >= qr_code.max_reactivations:
        _log_event(
            request,
            "access.reregister.max_reached",
            token,
            payload.new_device_id,
            total_bindings=total_bindings,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maximum number of re-registrations reached",
        )

    now = datetime.utcnow()

    active_binding.active = False
    active_binding.revoked_at = now
    session.add(active_binding)

    ua_hash = _hash_identifier(request.headers.get("User-Agent", "unknown"))
    _ensure_device(session, payload.new_device_id, ua_hash, payload.account_id)

    new_binding = QrBinding(
        qr_id=qr_code.id,
        device_id=payload.new_device_id,
        account_id=payload.account_id,
        active=True,
    )
    session.add(new_binding)

    qr_code.status = QrStatus.ACTIVE
    qr_code.registered_at = now

    recent_reactivations = _count_recent_reactivations(session, qr_code.id, now)
    if recent_reactivations > 3:
        qr_code.cooldown_until = now + timedelta(hours=48)

    session.add(qr_code)
    session.commit()
    session.refresh(qr_code)

    _log_event(
        request,
        "access.reregister.success",
        token,
        payload.new_device_id,
        account_id=str(payload.account_id) if payload.account_id else None,
        recent_reactivations=recent_reactivations,
    )

    return _build_validation_payload(qr_code)


__all__ = ["router"]
