"""Tests for the magic link authentication flow."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from sqlmodel import Session

from app.core.database import get_engine
from app.models import User


def _create_user(email: str) -> None:
    """Persist an active, full-access user for testing."""

    with Session(get_engine()) as session:
        session.add(User(email=email, full_access=True, is_active=True))
        session.commit()


def test_request_magic_link_returns_generic_response(client) -> None:
    """The request endpoint should not reveal account existence."""

    response = client.post(
        "/api/auth/magic-link/request",
        json={"email": "unknown@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["detail"].startswith("If this email is registered")


def test_magic_link_flow_returns_access_token(client, monkeypatch) -> None:
    """Requesting and consuming a magic link yields a JWT."""

    email = "user@example.com"
    _create_user(email)

    captured: dict[str, str] = {}

    def fake_send(recipient: str, url: str) -> None:
        captured["recipient"] = recipient
        captured["url"] = url

    monkeypatch.setattr("app.api.auth.send_magic_link_email", fake_send)

    request_response = client.post(
        "/api/auth/magic-link/request",
        json={"email": email},
    )

    assert request_response.status_code == 200
    assert captured["recipient"] == email

    url = urlparse(captured["url"])
    token = parse_qs(url.query)["token"][0]

    login_response = client.get(f"/api/auth/magic-login?token={token}")
    body = login_response.json()

    assert login_response.status_code == 200
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == email

    reuse_response = client.get(f"/api/auth/magic-login?token={token}")
    assert reuse_response.status_code == 400
