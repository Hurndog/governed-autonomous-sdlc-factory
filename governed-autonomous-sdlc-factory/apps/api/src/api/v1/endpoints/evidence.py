"""Evidence endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import EvidenceBundle

router = APIRouter()


@router.get("/by-run/{run_id}")
async def get_evidence_by_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EvidenceBundle).where(EvidenceBundle.run_id == run_id).order_by(EvidenceBundle.created_at.desc())
    )
    bundles = result.scalars().all()
    return {"bundles": [
        {"id": b.id, "path": b.bundle_path, "size": b.size_bytes,
         "hash": b.bundle_hash, "artifact_count": b.artifact_count,
         "created_at": b.created_at.isoformat() if b.created_at else None}
        for b in bundles
    ]}


@router.post("/create/{run_id}")
async def create_evidence_bundle(run_id: str, db: AsyncSession = Depends(get_db)):
    bundle = EvidenceBundle(run_id=run_id)
    db.add(bundle)
    await db.flush()
    await db.refresh(bundle)
    return {"id": bundle.id, "run_id": run_id, "status": "created"}


@router.get("/download/{bundle_id}")
async def download_evidence(bundle_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EvidenceBundle).where(EvidenceBundle.id == bundle_id))
    bundle = result.scalar_one_or_none()
    if not bundle:
        raise HTTPException(status_code=404, detail="Evidence bundle not found")
    return {"bundle_path": bundle.bundle_path, "message": "Serve file from bundle_path"}
