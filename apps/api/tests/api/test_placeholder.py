"""Smoke tests for the placeholder API application."""

import pytest

fastapi = pytest.importorskip('fastapi')
from fastapi.testclient import TestClient

from app import create_app


def test_health_endpoint_returns_ok() -> None:
    """The health endpoint should return a healthy status."""

    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
