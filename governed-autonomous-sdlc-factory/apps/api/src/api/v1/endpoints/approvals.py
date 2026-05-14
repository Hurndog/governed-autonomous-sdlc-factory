"""Approval endpoints."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Approval, ApprovalStatus
from src.schemas.phase import ApprovalCreate, ApprovalResponse

router = APIRouter()


@router.post("/", response_model=ApprovalResponse)
async def create_approval(body: ApprovalCreate, db: AsyncSession = Depends(get_db)):
    status = ApprovalStatus.AUTO_APPROVED.value if body.is_demo else ApprovalStatus.PENDING.value
    approval = Approval(
        run_id=body.run_id,
        artifact_id=body.artifact_id,
        approval_type=body.approval_type,
        status=status,
        is_demo=body.is_demo,
        notes=body.notes,
    )
    if body.is_demo:
        approval.approver = "demo-auto-approver"
        approval.approved_at = datetime.now(timezone.utc)
    db.add(approval)
    await db.flush()
    await db.refresh(approval)
    return approval


@router.get("/by-run/{run_id}", response_model=List[ApprovalResponse])
async def list_approvals_by_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Approval).where(Approval.run_id == run_id).order_by(Approval.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve(approval_id: str, approver: str = "manual", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = ApprovalStatus.APPROVED.value
    approval.approver = approver
    approval.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(approval)
    return approval


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject(approval_id: str, approver: str = "manual", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = ApprovalStatus.REJECTED.value
    approval.approver = approver
    approval.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(approval)
    return approval
