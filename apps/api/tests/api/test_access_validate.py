"""Tests for the access validation endpoint."""

from __future__ import annotations

import hashlib
import logging

import pytest

from fastapi.testclient import TestClient


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


def test_validate_logs_structured_event(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Validation events are logged with hashed identifiers."""

    caplog.set_level(logging.INFO, logger="app.access")

    token = "DEMO-NEW"
    hashed = hashlib.sha256(token.encode("utf-8")).hexdigest()

    payload = _post_validate(client, token)
    assert payload["status"] == "new"

    assert hashed in caplog.text
    assert token not in caplog.text
