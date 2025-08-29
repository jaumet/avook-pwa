import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import models
import auth

def test_password_hashing():
    password = "testpassword"
    hashed_password = auth.get_password_hash(password)
    assert hashed_password != password
    assert auth.verify_password(password, hashed_password) is True
    assert auth.verify_password("wrongpassword", hashed_password) is False

def test_admin_login_wrong_password(client: TestClient, db_session: Session):
    # Create an admin user
    hashed_password = auth.get_password_hash("correctpassword")
    admin_user = models.AdminUser(email="admin@test.com", password_hash=hashed_password, role="owner")
    db_session.add(admin_user)
    db_session.commit()

    response = client.post(
        "/api/v1/admin/login",
        data={"username": "admin@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_admin_login_success(client: TestClient, db_session: Session):
    # Create an admin user
    hashed_password = auth.get_password_hash("correctpassword")
    admin_user = models.AdminUser(email="admin2@test.com", password_hash=hashed_password, role="owner")
    db_session.add(admin_user)
    db_session.commit()

    response = client.post(
        "/api/v1/admin/login",
        data={"username": "admin2@test.com", "password": "correctpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
