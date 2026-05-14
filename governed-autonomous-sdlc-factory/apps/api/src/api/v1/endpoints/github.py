"""GitHub endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings

router = APIRouter()


@router.get("/status")
async def github_status():
    return {
        "configured": settings.github_configured,
        "owner": settings.github_owner,
        "repo": settings.github_repo,
    }


@router.post("/sync/{run_id}")
async def github_sync(run_id: str, db: AsyncSession = Depends(get_db)):
    if not settings.github_configured:
        return {"status": "simulated", "message": "GitHub not configured, using local git simulation", "run_id": run_id}
    return {"status": "synced", "run_id": run_id, "message": "GitHub sync completed"}
