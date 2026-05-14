"""Phase endpoints."""
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Phase
from src.schemas.phase import PhaseResponse

router = APIRouter()


@router.get("/by-run/{run_id}", response_model=List[PhaseResponse])
async def list_phases_by_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Phase).where(Phase.run_id == run_id).order_by(Phase.order_index)
    )
    return list(result.scalars().all())


@router.get("/{phase_id}", response_model=PhaseResponse)
async def get_phase(phase_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Phase).where(Phase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    return phase


@router.post("/")
async def create_phase(
    run_id: str,
    name: str,
    order_index: int = 0,
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    phase = Phase(run_id=run_id, name=name, order_index=order_index, agent_id=agent_id)
    db.add(phase)
    await db.flush()
    await db.refresh(phase)
    return phase


@router.patch("/{phase_id}")
async def update_phase(
    phase_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    order_index: Optional[int] = None,
    agent_id: Optional[str] = None,
    model_used: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Phase).where(Phase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    if name is not None:
        phase.name = name
    if status is not None:
        phase.status = status
    if order_index is not None:
        phase.order_index = order_index
    if agent_id is not None:
        phase.agent_id = agent_id
    if model_used is not None:
        phase.model_used = model_used
    await db.flush()
    await db.refresh(phase)
    return phase


@router.post("/{phase_id}/complete")
async def complete_phase(
    phase_id: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost: float = 0.0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Phase).where(Phase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    phase.status = "completed"
    phase.tokens_in = tokens_in
    phase.tokens_out = tokens_out
    phase.cost = cost
    phase.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(phase)
    return phase


@router.post("/{phase_id}/fail")
async def fail_phase(phase_id: str, error_message: str = "", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Phase).where(Phase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    phase.status = "failed"
    phase.error_message = error_message
    phase.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(phase)
    return phase
