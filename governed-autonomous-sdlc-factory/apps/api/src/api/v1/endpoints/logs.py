"""Log endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import LogEvent
from src.schemas.phase import LogEventResponse, LogFilterParams
from src.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[LogEventResponse])
async def list_logs(
    run_id: Optional[str] = None,
    phase_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    error_only: bool = False,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(LogEvent)
    if run_id:
        query = query.where(LogEvent.run_id == run_id)
    if phase_id:
        query = query.where(LogEvent.phase_id == phase_id)
    if agent_id:
        query = query.where(LogEvent.agent_id == agent_id)
    if severity:
        query = query.where(LogEvent.severity == severity)
    if error_only:
        query = query.where(LogEvent.severity.in_(["error", "critical"]))
    if from_time:
        query = query.where(LogEvent.created_at >= from_time)
    if to_time:
        query = query.where(LogEvent.created_at <= to_time)

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    count = total.scalar()

    result = await db.execute(
        query.order_by(LogEvent.created_at.desc()).offset(offset).limit(limit)
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=list(items),
        total=count,
        page=(offset // limit) + 1 if limit > 0 else 1,
        page_size=limit,
        has_next=count > offset + limit,
        has_prev=offset > 0,
    )


@router.post("/export")
async def export_logs(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LogEvent).where(LogEvent.run_id == run_id).order_by(LogEvent.created_at)
    )
    events = result.scalars().all()
    lines = []
    for e in events:
        lines.append(
            f'{{"timestamp":"{e.created_at.isoformat()}","severity":"{e.severity}",'
            f'"message":"{e.message}","run_id":"{e.run_id}","trace_id":"{e.trace_id or ""}"}}'
        )
    return {"content": "\n".join(lines), "count": len(lines)}
