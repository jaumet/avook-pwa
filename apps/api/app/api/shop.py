"""Placeholder module for the \"shop\" API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/shop")


@router.get("/placeholder")
async def placeholder() -> dict[str, str]:
    """Temporary endpoint that confirms the module is wired."""

    return {"module": "shop", "status": "pending"}
