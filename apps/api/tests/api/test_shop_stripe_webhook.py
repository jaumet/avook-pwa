"""Tests for the Stripe webhook integration."""

from __future__ import annotations

from sqlmodel import Session, select

from app.core.database import get_engine
from app.models import User


def test_checkout_session_completed_creates_user(client, monkeypatch) -> None:
    """Stripe webhook should provision full access for the customer."""

    email = "buyer@example.com"
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"customer_details": {"email": email}}},
    }

    monkeypatch.setattr(
        "app.api.shop.stripe.Webhook.construct_event",
        lambda payload, sig_header, secret: event,
    )

    response = client.post(
        "/api/shop/stripe/webhook",
        content="{}",
        headers={"stripe-signature": "sig"},
    )

    assert response.status_code == 200

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        assert user is not None
        assert user.full_access is True
        assert user.is_active is True
