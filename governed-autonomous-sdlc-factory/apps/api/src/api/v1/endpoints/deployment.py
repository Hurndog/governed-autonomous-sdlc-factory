"""Deployment endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Deployment

router = APIRouter()


@router.post("/{run_id}")
async def deploy_run(run_id: str, db: AsyncSession = Depends(get_db)):
    deployment = Deployment(
        run_id=run_id,
        status="deploying",
        localhost_url=f"http://localhost:9000/projects/{run_id}",
    )
    db.add(deployment)
    await db.flush()
    await db.refresh(deployment)
    return {"status": "deployed", "run_id": run_id, "deployment_id": deployment.id,
            "url": deployment.localhost_url, "message": "Deployment initiated"}


@router.get("/status/{run_id}")
async def deployment_status(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).where(Deployment.run_id == run_id).order_by(Deployment.created_at.desc())
    )
    deployment = result.scalars().first()
    if not deployment:
        raise HTTPException(status_code=404, detail="No deployment found for this run")
    return {
        "run_id": run_id,
        "deployment_id": deployment.id,
        "status": deployment.status,
        "health": deployment.health_status,
        "url": deployment.localhost_url,
    }


@router.post("/shutdown/{run_id}")
async def shutdown_deployment(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).where(Deployment.run_id == run_id).order_by(Deployment.created_at.desc())
    )
    deployment = result.scalars().first()
    if deployment:
        deployment.status = "shutdown"
        await db.flush()
    return {"status": "shutdown", "run_id": run_id}


@router.post("/restart/{run_id}")
async def restart_deployment(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).where(Deployment.run_id == run_id).order_by(Deployment.created_at.desc())
    )
    deployment = result.scalars().first()
    if deployment:
        deployment.status = "restarting"
        await db.flush()
    return {"status": "restarted", "run_id": run_id}


@router.post("/rollback/{run_id}")
async def rollback_deployment(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).where(Deployment.run_id == run_id).order_by(Deployment.created_at.desc())
    )
    deployment = result.scalars().first()
    if deployment:
        deployment.status = "rolling_back"
        await db.flush()
    return {"status": "rolling_back", "run_id": run_id}
