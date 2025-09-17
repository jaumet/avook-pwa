"""Core application package for the Audiovook API."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create a FastAPI application instance.

    This placeholder will be replaced with the fully configured
    application as the project evolves.
    """

    app = FastAPI(title="Audiovook API", version="0.1.0-dev")

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        """Return a basic health status payload."""

        return {"status": "ok"}

    return app
