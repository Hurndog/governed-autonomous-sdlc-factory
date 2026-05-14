"""Run endpoints."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.observability import RUNS_CREATED, RUNS_COMPLETED, ACTIVE_RUNS
from src.models import Run, RunStatus
from src.schemas.run import RunCreate, RunUpdate, RunResponse, RunStatusResponse
from src.schemas.common import PaginatedResponse

router = APIRouter()


VALID_TRANSITIONS = {
    RunStatus.PENDING.value: [RunStatus.RUNNING.value, RunStatus.CANCELLED.value],
    RunStatus.RUNNING.value: [RunStatus.PAUSED.value, RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value],
    RunStatus.PAUSED.value: [RunStatus.RUNNING.value, RunStatus.CANCELLED.value],
    RunStatus.COMPLETED.value: [],
    RunStatus.FAILED.value: [RunStatus.PENDING.value],
    RunStatus.CANCELLED.value: [RunStatus.PENDING.value],
}


@router.post("/", response_model=RunResponse)
async def create_run(body: RunCreate, db: AsyncSession = Depends(get_db)):
    run = Run(
        project_id=body.project_id,
        name=body.name,
        budget_limit=body.budget_limit,
        is_demo=body.is_demo,
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)
    RUNS_CREATED.inc()
    return run


@router.get("/", response_model=PaginatedResponse[RunResponse])
async def list_runs(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Run)
    if project_id:
        query = query.where(Run.project_id == project_id)
    if status:
        query = query.where(Run.status == status)

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    count = total.scalar()

    result = await db.execute(
        query.order_by(Run.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=list(items),
        total=count,
        page=page,
        page_size=page_size,
        has_next=count > page * page_size,
        has_prev=page > 1,
    )


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatusResponse(
        id=run.id,
        status=run.status,
        current_phase=run.current_phase,
        total_cost=run.total_cost,
        deployment_status=None,
    )


@router.patch("/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: str, body: RunUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if body.status and body.status != run.status:
        allowed = VALID_TRANSITIONS.get(run.status, [])
        if body.status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transition from {run.status} to {body.status}. Allowed: {allowed}",
            )
        run.status = body.status
        if body.status == RunStatus.RUNNING.value and not run.started_at:
            run.started_at = datetime.now(timezone.utc)
        if body.status in (RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value):
            run.completed_at = datetime.now(timezone.utc)
            RUNS_COMPLETED.labels(status=body.status).inc()
            if body.status == RunStatus.COMPLETED.value:
                ACTIVE_RUNS.dec()

    update_data = body.model_dump(exclude_unset=True, exclude={"status"})
    for key, value in update_data.items():
        setattr(run, key, value)

    await db.flush()
    await db.refresh(run)
    return run


@router.post("/{run_id}/pause", response_model=RunResponse)
async def pause_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != RunStatus.RUNNING.value:
        raise HTTPException(status_code=400, detail="Can only pause running runs")
    run.status = RunStatus.PAUSED.value
    await db.flush()
    await db.refresh(run)
    return run


@router.post("/{run_id}/resume", response_model=RunResponse)
async def resume_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != RunStatus.PAUSED.value:
        raise HTTPException(status_code=400, detail="Can only resume paused runs")
    run.status = RunStatus.RUNNING.value
    await db.flush()
    await db.refresh(run)
    return run


@router.post("/{run_id}/cancel", response_model=RunResponse)
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.status = RunStatus.CANCELLED.value
    run.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(run)
    return run


@router.post("/{run_id}/start", response_model=RunResponse)
async def start_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Start a run — triggers the SDLC workflow."""
    import asyncio
    from src.services.run_orchestrator import orchestrator
    from src.models import Project

    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    proj_result = await db.execute(select(Project).where(Project.id == run.project_id))
    project = proj_result.scalar_one_or_none()
    idea_text = project.idea_text if project else ""

    asyncio.create_task(
        orchestrator.start_run(
            project_id=run.project_id,
            name=run.name,
            idea_text=idea_text or "",
            budget_limit=run.budget_limit,
            is_demo=run.is_demo,
        )
    )

    return run
