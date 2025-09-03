import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import csv
import io

import models
import auth

@pytest.fixture()
def owner_user(db_session: Session):
    password = "ownerpassword"
    hashed_password = auth.get_password_hash(password)
    user = models.AdminUser(email="owner@test.com", password_hash=hashed_password, role="owner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Add plain password for login
    user.plain_password = password
    return user

@pytest.fixture()
def editor_user(db_session: Session):
    password = "editorpassword"
    hashed_password = auth.get_password_hash(password)
    user = models.AdminUser(email="editor@test.com", password_hash=hashed_password, role="editor")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Add plain password for login
    user.plain_password = password
    return user

@pytest.fixture()
def owner_auth_headers(client: TestClient, owner_user: models.AdminUser):
    response = client.post(
        "/api/v1/admin/login",
        data={"username": owner_user.email, "password": owner_user.plain_password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def editor_auth_headers(client: TestClient, editor_user: models.AdminUser):
    response = client.post(
        "/api/v1/admin/login",
        data={"username": editor_user.email, "password": editor_user.plain_password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_password_hashing():
    password = "testpassword"
    hashed_password = auth.get_password_hash(password)
    assert hashed_password != password
    assert auth.verify_password(password, hashed_password) is True
    assert auth.verify_password("wrongpassword", hashed_password) is False

def test_admin_login_success(client: TestClient, owner_user: models.AdminUser):
    response = client.post(
        "/api/v1/admin/login",
        data={"username": owner_user.email, "password": owner_user.plain_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# --- Test Admin User Management ---

def test_owner_can_create_editor(client: TestClient, owner_auth_headers: dict):
    response = client.post(
        "/api/v1/admin/users",
        headers=owner_auth_headers,
        json={"email": "neweditor@test.com", "password": "newpassword", "role": "editor"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "neweditor@test.com"
    assert response.json()["role"] == "editor"

def test_editor_cannot_create_user(client: TestClient, editor_auth_headers: dict):
    response = client.post(
        "/api/v1/admin/users",
        headers=editor_auth_headers,
        json={"email": "anothereditor@test.com", "password": "newpassword", "role": "editor"}
    )
    assert response.status_code == 403

def test_owner_can_list_users(client: TestClient, owner_auth_headers: dict):
    response = client.get("/api/v1/admin/users", headers=owner_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# --- Test Title and Product Management ---

@pytest.fixture()
def sample_title(db_session: Session):
    title = models.Title(slug="sample-title", title="Sample Title", author="Test Author")
    db_session.add(title)
    db_session.commit()
    return title

def test_admin_can_create_title(client: TestClient, editor_auth_headers: dict):
    response = client.post(
        "/api/v1/admin/titles",
        headers=editor_auth_headers,
        json={"slug": "new-title", "title": "New Title", "author": "Author"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Title"

def test_admin_can_create_product(client: TestClient, editor_auth_headers: dict, sample_title: models.Title):
    response = client.post(
        "/api/v1/admin/products",
        headers=editor_auth_headers,
        json={"title_id": sample_title.id, "sku_ean": "1234567890123"}
    )
    assert response.status_code == 201
    assert response.json()["sku_ean"] == "1234567890123"

# --- Test QR Code Generation and Management ---

@pytest.fixture()
def sample_product(db_session: Session, sample_title: models.Title):
    product = models.Product(title_id=sample_title.id, sku_ean="product-for-qrs")
    db_session.add(product)
    db_session.commit()
    return product

def test_generate_qr_codes_csv(client: TestClient, owner_auth_headers: dict, sample_product: models.Product):
    quantity = 5
    batch_name = "Test Batch"
    response = client.post(
        f"/api/v1/admin/products/{sample_product.id}/batches",
        headers=owner_auth_headers,
        json={"quantity": quantity, "name": batch_name}
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

    # Verify CSV content
    content = response.content.decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == quantity + 1 # header + rows
    assert rows[0] == ["qr_code", "pin"]
    assert len(rows[1][0]) > 10 # QR code is a UUID
    assert len(rows[1][1]) == 4 # PIN is 4 digits

def test_get_qr_code_details(client: TestClient, owner_auth_headers: dict, db_session: Session):
    # Create a QR code to fetch
    qr_code = models.QRCode(product_id=1, qr="test-qr-code", owner_pin_hash="hashed_pin")
    db_session.add(qr_code)
    db_session.commit()

    response = client.get(f"/api/v1/admin/qrcodes/{qr_code.qr}", headers=owner_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["qr"] == "test-qr-code"
    assert "device_bindings" in data

def test_reset_qr_code(client: TestClient, owner_auth_headers: dict, db_session: Session):
    # Create a QR code and a device binding to reset
    qr_code = models.QRCode(product_id=1, qr="reset-me", state="active", owner_pin_hash="hashed_pin")
    db_session.add(qr_code)
    db_session.commit()
    binding = models.DeviceBinding(qr_code_id=qr_code.id, device_id="test-device")
    db_session.add(binding)
    db_session.commit()

    response = client.post(f"/api/v1/admin/qrcodes/{qr_code.qr}/reset", headers=owner_auth_headers)
    assert response.status_code == 204

    # Verify reset
    db_session.refresh(qr_code)
    assert qr_code.state == "new"
    bindings = db_session.query(models.DeviceBinding).filter_by(qr_code_id=qr_code.id).count()
    assert bindings == 0
