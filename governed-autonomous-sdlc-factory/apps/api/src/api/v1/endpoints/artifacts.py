"""Artifact endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Artifact
from src.schemas.phase import ArtifactCreate, ArtifactResponse

router = APIRouter()


@router.post("/", response_model=ArtifactResponse)
async def create_artifact(body: ArtifactCreate, db: AsyncSession = Depends(get_db)):
    artifact = Artifact(
        task_id=body.task_id,
        run_id=body.run_id,
        name=body.name,
        artifact_type=body.artifact_type,
        content=body.content,
        file_path=body.file_path,
        metadata_=body.metadata or {},
    )
    db.add(artifact)
    await db.flush()
    await db.refresh(artifact)
    return artifact


@router.get("/by-run/{run_id}", response_model=List[ArtifactResponse])
async def list_artifacts_by_run(
    run_id: str,
    artifact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Artifact).where(Artifact.run_id == run_id)
    if artifact_type:
        query = query.where(Artifact.artifact_type == artifact_type)
    result = await db.execute(query.order_by(Artifact.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.patch("/{artifact_id}/lock")
async def lock_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    artifact.is_locked = True
    artifact.is_baseline = True
    await db.flush()
    return {"id": artifact_id, "locked": True, "baseline": True}
