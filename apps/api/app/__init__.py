"""Core application package for the Audiovook API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import access, auth, play, preview, shop
from .core.config import get_settings
from .core.migrations import run_migrations


API_PREFIX = "/api"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = get_settings()

    app = FastAPI(
        title="Audiovook API",
        version="0.1.0",
        debug=settings.debug,
    )

    run_migrations()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(access.router, prefix=API_PREFIX)
    app.include_router(auth.router, prefix=API_PREFIX)
    app.include_router(play.router, prefix=API_PREFIX)
    app.include_router(preview.router, prefix=API_PREFIX)
    app.include_router(shop.router, prefix=API_PREFIX)

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        """Return a basic health status payload."""

        return {"status": "ok"}

    return app


__all__ = ["create_app"]
