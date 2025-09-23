"""Utilities for applying database migrations on application startup."""

from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.models import metadata as model_metadata

from .database import get_engine

logger = logging.getLogger("app.migrations")

_migration_lock = Lock()
_migrations_applied = False


def _build_alembic_config(engine: Engine) -> Config:
    """Return an Alembic configuration bound to the current environment."""

    base_path = Path(__file__).resolve().parents[2]
    config = Config(str(base_path / "alembic.ini"))

    # Ensure Alembic resolves script locations using absolute paths so the
    # command works regardless of the current working directory.
    config.set_main_option("script_location", str(base_path / "alembic"))

    config.set_main_option(
        "sqlalchemy.url", engine.url.render_as_string(hide_password=False)
    )

    return config


def _database_at_head(engine: Engine, script: ScriptDirectory) -> bool:
    """Return True if the database already matches the latest revision."""

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_revision = context.get_current_revision()

    head_revision = script.get_current_head()
    return current_revision == head_revision


EXPECTED_TABLES = set(model_metadata.tables.keys())


def _needs_stamp(engine: Engine) -> bool:
    """Return True when the schema exists but Alembic hasn't recorded a revision."""

    inspector = inspect(engine)
    if inspector.has_table("alembic_version"):
        return False

    table_names = set(inspector.get_table_names())

    # If the target schema already exists (likely from a previous manual migration
    # run) but the Alembic version table is missing, we can stamp the database at
    # head instead of trying to apply migrations that would re-create the objects
    # and fail with DuplicateObject errors.
    return EXPECTED_TABLES.issubset(table_names)


def run_migrations() -> None:
    """Apply pending Alembic migrations if the target database requires them."""

    global _migrations_applied

    if _migrations_applied:
        return

    with _migration_lock:
        if _migrations_applied:
            return

        engine = get_engine()

        # SQLite is only used in tests where tables are created via metadata.
        if engine.dialect.name == "sqlite":
            logger.info("Skipping automatic migrations for SQLite engine")
            _migrations_applied = True
            return

        config = _build_alembic_config(engine)
        script = ScriptDirectory.from_config(config)

        if _database_at_head(engine, script):
            logger.info("Database already at latest Alembic revision")
            _migrations_applied = True
            return

        if _needs_stamp(engine):
            logger.warning(
                "Database schema detected without Alembic version; stamping to head"
            )
            with engine.begin() as connection:
                config.attributes["connection"] = connection
                command.stamp(config, script.get_current_head())
            config.attributes.pop("connection", None)
            _migrations_applied = True
            return

        try:
            with engine.begin() as connection:
                config.attributes["connection"] = connection
                command.upgrade(config, "head")
        finally:
            config.attributes.pop("connection", None)

        logger.info("Applied pending Alembic migrations")
        _migrations_applied = True


__all__ = ["run_migrations"]

