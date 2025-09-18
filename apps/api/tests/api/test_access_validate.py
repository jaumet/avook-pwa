"""Tests for the access validation endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.database import configure_engine
from app.models import QrCode, QrStatus, metadata


@pytest.fixture()
def client() -> TestClient:
    """Provide a FastAPI test client backed by an in-memory database."""

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    configure_engine(engine)

    with Session(engine) as session:
        session.add(QrCode(token="DEMO-NEW", status=QrStatus.NEW, product_id=1))
        session.add(QrCode(token="DEMO-ACTIVE", status=QrStatus.ACTIVE, product_id=2))
        session.add(QrCode(token="DEMO-BLOCKED", status=QrStatus.BLOCKED, product_id=3))
        session.commit()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    metadata.drop_all(engine)


def _post_validate(client: TestClient, token: str) -> dict[str, object]:
    response = client.post("/api/access/validate", json={"token": token})
    assert response.status_code == 200
    return response.json()


def test_invalid_token_returns_invalid_status(client: TestClient) -> None:
    """Unknown tokens should return the "invalid" status."""

    payload = _post_validate(client, "UNKNOWN-TOKEN")
    assert payload["status"] == "invalid"
    assert payload["preview_available"] is False
    assert payload["can_reregister"] is False


def test_new_token_reports_registration_ready(client: TestClient) -> None:
    """Seeded new tokens report that registration can proceed."""

    payload = _post_validate(client, "DEMO-NEW")
    assert payload["status"] == "new"
    assert payload["can_reregister"] is True
    assert payload["preview_available"] is True
    assert payload["product"] == {"id": 1, "title": "Product #1"}


def test_active_token_maps_to_registered_status(client: TestClient) -> None:
    """Active tokens surface as registered to the caller."""

    payload = _post_validate(client, "DEMO-ACTIVE")
    assert payload["status"] == "registered"
    assert payload["can_reregister"] is True
    assert payload["preview_available"] is True


def test_blocked_token_disables_preview(client: TestClient) -> None:
    """Blocked tokens should not offer preview or reregistration."""

    payload = _post_validate(client, "DEMO-BLOCKED")
    assert payload["status"] == "blocked"
    assert payload["preview_available"] is False
    assert payload["can_reregister"] is False
