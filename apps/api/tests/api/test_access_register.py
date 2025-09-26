"""Tests for the access registration and re-registration flows."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import get_engine
from app.models import Device, QrBinding, QrCode, QrStatus


def _get_session() -> Session:
    return Session(get_engine())


def _post_json(client: TestClient, path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    response = client.post(path, json=payload)
    data = response.json() if response.content else {}
    return response.status_code, data


def test_register_creates_binding_and_updates_qr(client: TestClient) -> None:
    token = "DEMO-NEW"
    device_id = uuid.uuid4()

    status_code, payload = _post_json(
        client,
        "/api/access/register",
        {"token": token, "device_id": str(device_id)},
    )

    assert status_code == 200
    assert payload["status"] == "registered"

    with _get_session() as session:
        qr_code = session.exec(select(QrCode).where(QrCode.token == token)).one()
        assert qr_code.status is QrStatus.ACTIVE
        assert qr_code.registered_at is not None

        binding = session.exec(
            select(QrBinding).where(QrBinding.qr_id == qr_code.id)
        ).one()
        assert binding.active is True
        assert binding.device_id == device_id


def test_register_conflict_when_already_bound(client: TestClient) -> None:
    token = "DEMO-NEW"
    original_device = uuid.uuid4()
    _post_json(client, "/api/access/register", {"token": token, "device_id": str(original_device)})

    new_device = uuid.uuid4()
    status_code, payload = _post_json(
        client,
        "/api/access/register",
        {"token": token, "device_id": str(new_device)},
    )

    assert status_code == 409
    assert payload["detail"] == "Token already bound to a different device"


def test_register_is_idempotent_and_updates_account(client: TestClient) -> None:
    token = "DEMO-NEW"
    device_id = uuid.uuid4()
    account_id = uuid.uuid4()

    _post_json(client, "/api/access/register", {"token": token, "device_id": str(device_id)})

    status_code, _ = _post_json(
        client,
        "/api/access/register",
        {"token": token, "device_id": str(device_id), "account_id": str(account_id)},
    )

    assert status_code == 200

    with _get_session() as session:
        qr_code = session.exec(select(QrCode).where(QrCode.token == token)).one()
        binding = session.exec(
            select(QrBinding).where(QrBinding.qr_id == qr_code.id)
        ).one()
        assert binding.account_id == account_id


def test_reregister_moves_binding_to_new_device(client: TestClient) -> None:
    token = "DEMO-NEW"
    device_a = uuid.uuid4()
    device_b = uuid.uuid4()

    _post_json(client, "/api/access/register", {"token": token, "device_id": str(device_a)})

    status_code, payload = _post_json(
        client,
        "/api/access/reregister",
        {"token": token, "new_device_id": str(device_b)},
    )

    assert status_code == 200
    assert payload["status"] == "registered"

    with _get_session() as session:
        qr_code = session.exec(select(QrCode).where(QrCode.token == token)).one()
        bindings = session.exec(
            select(QrBinding).where(QrBinding.qr_id == qr_code.id)
        ).all()
        assert len(bindings) == 2

        active_binding = next(binding for binding in bindings if binding.active)
        inactive_binding = next(binding for binding in bindings if not binding.active)

        assert active_binding.device_id == device_b
        assert inactive_binding.device_id == device_a
        assert inactive_binding.revoked_at is not None


def test_reregister_reuses_existing_account_when_not_provided(
    client: TestClient,
) -> None:
    token = "DEMO-NEW"
    account_id = uuid.uuid4()
    device_a = uuid.uuid4()
    device_b = uuid.uuid4()

    _post_json(
        client,
        "/api/access/register",
        {
            "token": token,
            "device_id": str(device_a),
            "account_id": str(account_id),
        },
    )

    status_code, _ = _post_json(
        client,
        "/api/access/reregister",
        {"token": token, "new_device_id": str(device_b)},
    )

    assert status_code == 200

    with _get_session() as session:
        qr_code = session.exec(select(QrCode).where(QrCode.token == token)).one()

        active_binding = session.exec(
            select(QrBinding)
            .where(QrBinding.qr_id == qr_code.id)
            .where(QrBinding.active.is_(True))
        ).one()
        assert active_binding.account_id == account_id

        device = session.exec(select(Device).where(Device.id == device_b)).one()
        assert device.account_id == account_id


def test_reregister_respects_max_reactivations(client: TestClient) -> None:
    token = "LIMITED-TOKEN"
    device_a = uuid.uuid4()
    device_b = uuid.uuid4()

    with _get_session() as session:
        qr_code = QrCode(token=token, status=QrStatus.NEW, max_reactivations=0)
        session.add(qr_code)
        session.commit()

    _post_json(client, "/api/access/register", {"token": token, "device_id": str(device_a)})

    status_code, payload = _post_json(
        client,
        "/api/access/reregister",
        {"token": token, "new_device_id": str(device_b)},
    )

    assert status_code == 403
    assert payload["detail"] == "Maximum number of re-registrations reached"


def test_reregister_triggers_cooldown_after_multiple_events(client: TestClient) -> None:
    token = "DEMO-NEW"
    devices = [uuid.uuid4() for _ in range(6)]

    _post_json(client, "/api/access/register", {"token": token, "device_id": str(devices[0])})

    for index in range(1, 5):
        status_code, _ = _post_json(
            client,
            "/api/access/reregister",
            {"token": token, "new_device_id": str(devices[index])},
        )
        assert status_code == 200

    with _get_session() as session:
        qr_code = session.exec(select(QrCode).where(QrCode.token == token)).one()
        assert qr_code.cooldown_until is not None
        assert qr_code.cooldown_until > datetime.utcnow()

    status_code, payload = _post_json(
        client,
        "/api/access/validate",
        {"token": token},
    )

    assert status_code == 200
    assert payload["can_reregister"] is False


def test_rate_limit_blocks_after_threshold(client: TestClient) -> None:
    for _ in range(30):
        status_code, _ = _post_json(client, "/api/access/validate", {"token": "DEMO-NEW"})
        assert status_code == 200

    response = client.post("/api/access/validate", json={"token": "DEMO-NEW"})
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_register_logs_hashed_token(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="app.access")
    token = "DEMO-NEW"
    device_id = uuid.uuid4()

    expected_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    status_code, _ = _post_json(
        client,
        "/api/access/register",
        {"token": token, "device_id": str(device_id)},
    )

    assert status_code == 200
    assert expected_hash in caplog.text
    assert token not in caplog.text
