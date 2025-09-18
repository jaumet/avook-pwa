"""Placeholder module for the \"play\" API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/play")


@router.get("/placeholder")
async def placeholder() -> dict[str, str]:
    """Temporary endpoint that confirms the module is wired."""

    return {"module": "play", "status": "pending"}
