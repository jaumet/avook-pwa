"""Placeholder module for the \"access\" API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/access")


@router.get("/placeholder")
async def placeholder() -> dict[str, str]:
    """Temporary endpoint that confirms the module is wired."""

    return {"module": "access", "status": "pending"}
