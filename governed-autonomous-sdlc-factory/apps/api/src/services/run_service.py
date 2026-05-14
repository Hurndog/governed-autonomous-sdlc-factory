"""Run service with state machine."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Run, RunStatus

VALID_TRANSITIONS = {
    RunStatus.PENDING.value: [RunStatus.RUNNING.value, RunStatus.CANCELLED.value],
    RunStatus.RUNNING.value: [RunStatus.PAUSED.value, RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value],
    RunStatus.PAUSED.value: [RunStatus.RUNNING.value, RunStatus.CANCELLED.value],
    RunStatus.COMPLETED.value: [],
    RunStatus.FAILED.value: [RunStatus.PENDING.value],
    RunStatus.CANCELLED.value: [RunStatus.PENDING.value],
}


class RunService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, project_id: str, name: str, budget_limit: float = None, is_demo: bool = False) -> Run:
        run = Run(
            project_id=project_id,
            name=name,
            budget_limit=budget_limit,
            is_demo=is_demo,
        )
        self.db.add(run)
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def get(self, run_id: str) -> Optional[Run]:
        result = await self.db.execute(select(Run).where(Run.id == run_id))
        return result.scalar_one_or_none()

    async def transition(self, run_id: str, new_status: str) -> Optional[Run]:
        run = await self.get(run_id)
        if not run:
            return None
        allowed = VALID_TRANSITIONS.get(run.status, [])
        if new_status not in allowed:
            raise ValueError(f"Invalid transition from {run.status} to {new_status}. Allowed: {allowed}")
        run.status = new_status
        if new_status == RunStatus.RUNNING.value and not run.started_at:
            run.started_at = datetime.now(timezone.utc)
        if new_status in (RunStatus.COMPLETED.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value):
            run.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def update(self, run_id: str, **kwargs) -> Optional[Run]:
        run = await self.get(run_id)
        if not run:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(run, key, value)
        await self.db.flush()
        await self.db.refresh(run)
        return run
