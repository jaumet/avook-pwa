import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import models

def test_play_auth_qr_not_found(client: TestClient):
    response = client.get("/api/v1/abook/non-existent-qr/play-auth?device_id=test-device")
    assert response.status_code == 404
    assert response.json() == {"detail": "QR code not found"}

def test_play_auth_new_qr_new_device(client: TestClient, db_session: Session):
    # Create a product and a title for the QR code to belong to
    new_title = models.Title(slug="test-title", title="Test Title")
    db_session.add(new_title)
    db_session.commit()
    new_product = models.Product(title_id=new_title.id)
    db_session.add(new_product)
    db_session.commit()

    # Create a QR code
    new_qr = models.QRCode(qr="test-qr", product_id=new_product.id)
    db_session.add(new_qr)
    db_session.commit()

    response = client.get("/api/v1/abook/test-qr/play-auth?device_id=new-device")
    assert response.status_code == 200
    data = response.json()
    assert data["start_position"] == 0
    assert "https://placeholder.url/master.m3u8" in data["signed_url"]

    # Check that a new device binding was created
    binding = db_session.query(models.DeviceBinding).filter(
        models.DeviceBinding.qr_code_id == new_qr.id,
        models.DeviceBinding.device_id == "new-device"
    ).first()
    assert binding is not None
    assert binding.active is True

def test_play_auth_device_limit_reached(client: TestClient, db_session: Session):
    # Create data
    new_title = models.Title(slug="test-title-2", title="Test Title 2")
    db_session.add(new_title)
    db_session.commit()
    new_product = models.Product(title_id=new_title.id)
    db_session.add(new_product)
    db_session.commit()
    new_qr = models.QRCode(qr="test-qr-2", product_id=new_product.id)
    db_session.add(new_qr)
    db_session.commit()

    # Create two existing bindings
    binding1 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device1", active=True)
    binding2 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device2", active=True)
    db_session.add_all([binding1, binding2])
    db_session.commit()

    # Try to bind a third device
    response = client.get("/api/v1/abook/test-qr-2/play-auth?device_id=device3")
    assert response.status_code == 403
    assert response.json() == {"detail": "Device limit reached for this QR code"}


def test_update_progress_unauthorized_device(client: TestClient, db_session: Session):
    # Create data
    new_title = models.Title(slug="test-title-3", title="Test Title 3")
    db_session.add(new_title)
    db_session.commit()
    new_product = models.Product(title_id=new_title.id)
    db_session.add(new_product)
    db_session.commit()
    new_qr = models.QRCode(qr="test-qr-3", product_id=new_product.id)
    db_session.add(new_qr)
    db_session.commit()

    response = client.post(
        "/api/v1/abook/test-qr-3/progress",
        json={"device_id": "unauthorized-device", "position_sec": 120}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Device not authorized"}

def test_update_progress_valid(client: TestClient, db_session: Session):
    # Create data
    new_title = models.Title(slug="test-title-4", title="Test Title 4")
    db_session.add(new_title)
    db_session.commit()
    new_product = models.Product(title_id=new_title.id)
    db_session.add(new_product)
    db_session.commit()
    new_qr = models.QRCode(qr="test-qr-4", product_id=new_product.id)
    db_session.add(new_qr)
    db_session.commit()
    binding = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device1", active=True)
    db_session.add(binding)
    db_session.commit()

    # First progress update (creates the record)
    response = client.post(
        "/api/v1/abook/test-qr-4/progress",
        json={"device_id": "device1", "position_sec": 120}
    )
    assert response.status_code == 204

    progress = db_session.query(models.ListeningProgress).filter(
        models.ListeningProgress.qr_code_id == new_qr.id,
        models.ListeningProgress.device_id == "device1"
    ).first()
    assert progress is not None
    assert progress.position_sec == 120

    # Second progress update (updates the record)
    response = client.post(
        "/api/v1/abook/test-qr-4/progress",
        json={"device_id": "device1", "position_sec": 240}
    )
    assert response.status_code == 204

    db_session.refresh(progress)
    assert progress.position_sec == 240
