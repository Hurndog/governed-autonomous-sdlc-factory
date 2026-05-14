"""Task endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Task

router = APIRouter()


@router.get("/by-phase/{phase_id}")
async def list_tasks_by_phase(phase_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task).where(Task.phase_id == phase_id).order_by(Task.created_at)
    )
    return list(result.scalars().all())


@router.get("/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/")
async def create_task(
    phase_id: str,
    name: str,
    description: str = "",
    requirement_ids: Optional[List[str]] = None,
    acceptance_criteria_ids: Optional[List[str]] = None,
    expected_artifacts: Optional[List[str]] = None,
    test_ids: Optional[List[str]] = None,
    governance_check_ids: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        phase_id=phase_id, name=name, description=description,
        requirement_ids=requirement_ids or [],
        acceptance_criteria_ids=acceptance_criteria_ids or [],
        expected_artifacts=expected_artifacts or [],
        test_ids=test_ids or [],
        governance_check_ids=governance_check_ids or [],
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.patch("/{task_id}")
async def update_task(task_id: str, status: Optional[str] = None, name: Optional[str] = None,
                       description: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if status is not None:
        task.status = status
    if name is not None:
        task.name = name
    if description is not None:
        task.description = description
    await db.flush()
    return task
