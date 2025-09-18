"""Tests for the SQLModel schema definitions."""

from __future__ import annotations

from sqlalchemy import Enum
from sqlalchemy.dialects import postgresql

from app import models


def test_required_tables_are_registered() -> None:
    """The metadata should include all mandated tables."""

    expected_tables = {
        "qr_code",
        "account",
        "device",
        "qr_binding",
        "play_session",
        "listening_progress",
    }
    assert expected_tables.issubset(set(models.metadata.tables))


def test_qr_code_schema_matches_spec() -> None:
    """Ensure the qr_code table exposes the expected columns and defaults."""

    qr_table = models.metadata.tables["qr_code"]
    assert isinstance(qr_table.c.id.type, postgresql.UUID)
    assert qr_table.c.token.unique is True

    status_type = qr_table.c.status.type
    assert isinstance(status_type, Enum)
    assert {value.lower() for value in status_type.enums} == {"new", "active", "blocked"}

    default_clause = qr_table.c.max_reactivations.server_default
    assert default_clause is not None
    assert str(default_clause.arg) == "999"

    assert any(index.name == "idx_qr_token" for index in qr_table.indexes)


def test_listening_progress_primary_key_and_index() -> None:
    """The listening_progress table should use the composite key and timestamp index."""

    progress_table = models.metadata.tables["listening_progress"]
    pk_columns = list(progress_table.primary_key.columns.keys())
    assert pk_columns == ["qr_id", "device_id", "track_id"]

    assert any(index.name == "idx_progress_updated_at" for index in progress_table.indexes)


def test_qr_binding_index_and_defaults() -> None:
    """Check that the qr_binding table includes the active index and defaults."""

    binding_table = models.metadata.tables["qr_binding"]
    assert any(index.name == "idx_binding_qr_active" for index in binding_table.indexes)
    default_clause = binding_table.c.active.server_default
    assert default_clause is not None
    assert str(default_clause.arg).lower() == "true"
