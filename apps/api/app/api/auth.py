"""Placeholder module for the \"auth\" API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.get("/placeholder")
async def placeholder() -> dict[str, str]:
    """Temporary endpoint that confirms the module is wired."""

    return {"module": "auth", "status": "pending"}
