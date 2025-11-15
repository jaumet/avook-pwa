"""Commerce endpoints for Audiovook."""

from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.services.user import upsert_user_with_full_access

router = APIRouter(prefix="/shop", tags=["shop"])


@router.post("/stripe/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    """Handle Stripe webhook notifications for completed purchases."""

    settings = get_settings()
    if settings.stripe_api_key:
        stripe.api_key = settings.stripe_api_key

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.stripe_webhook_secret,
        )
    except stripe.error.SignatureVerificationError as exc:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook signature",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook payload",
        ) from exc

    if event.get("type") == "checkout.session.completed":
        data = event.get("data", {}).get("object", {})
        customer_details = data.get("customer_details") or {}
        customer_email = customer_details.get("email") or data.get("customer_email")

        if customer_email:
            upsert_user_with_full_access(session, customer_email)

    return {"ok": True}


__all__ = ["stripe_webhook"]
