"""Database session management utilities."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Optional

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from .config import get_settings

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def _initialise_engine() -> None:
    """Initialise the SQLModel engine and session factory."""

    global _engine, _session_factory

    if _engine is not None and _session_factory is not None:
        return

    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    _engine = engine
    _session_factory = factory


def get_engine() -> Engine:
    """Return the active SQLModel engine, creating it if necessary."""

    if _engine is None or _session_factory is None:
        _initialise_engine()
    assert _engine is not None  # pragma: no cover - defensive
    return _engine


def configure_engine(engine: Engine) -> None:
    """Override the database engine and rebuild the session factory.

    This is primarily intended for tests that need to swap in an
    in-memory database without touching the production configuration.
    """

    global _engine, _session_factory

    _engine = engine
    _session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """Provide a SQLModel session for request handlers."""

    if _session_factory is None:
        _initialise_engine()
    assert _session_factory is not None  # pragma: no cover - defensive
    with _session_factory() as session:
        yield session


__all__ = ["configure_engine", "get_engine", "get_session"]
