"""Shared pytest fixtures for API tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from app import create_app
from app.api.access import rate_limiter
from app.core.database import configure_engine
from app.models import QrCode, QrStatus, metadata


@pytest.fixture()
def client() -> TestClient:
    """Provide a FastAPI test client backed by an in-memory database."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    configure_engine(engine)
    rate_limiter.reset()

    with Session(engine) as session:
        session.add(QrCode(token="DEMO-NEW", status=QrStatus.NEW, product_id=1))
        session.add(QrCode(token="DEMO-ACTIVE", status=QrStatus.ACTIVE, product_id=2))
        session.add(QrCode(token="DEMO-BLOCKED", status=QrStatus.BLOCKED, product_id=3))
        session.commit()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    metadata.drop_all(engine)
