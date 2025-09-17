"""Placeholder module for the \"preview\" API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/preview")


@router.get("/placeholder")
async def placeholder() -> dict[str, str]:
    """Temporary endpoint that confirms the module is wired."""

    return {"module": "preview", "status": "pending"}
