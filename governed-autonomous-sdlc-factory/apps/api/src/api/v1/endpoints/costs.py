"""Cost endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import CostEvent, Run
from src.schemas.phase import CostEventCreate, CostReportResponse

router = APIRouter()


@router.post("/")
async def record_cost_event(body: CostEventCreate, db: AsyncSession = Depends(get_db)):
    event = CostEvent(
        run_id=body.run_id,
        phase_id=body.phase_id,
        agent_id=body.agent_id,
        event_type=body.event_type,
        model_name=body.model_name,
        provider=body.provider,
        tokens_in=body.tokens_in,
        tokens_out=body.tokens_out,
        estimated_cost=body.estimated_cost,
        actual_cost=body.actual_cost,
        is_local=body.is_local,
        latency_ms=body.latency_ms,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return {"id": event.id, "status": "recorded"}


@router.get("/report/{run_id}", response_model=CostReportResponse)
async def get_cost_report(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostEvent).where(CostEvent.run_id == run_id))
    events = result.scalars().all()

    total_cost = sum(e.estimated_cost for e in events)
    local_cost = sum(e.estimated_cost for e in events if e.is_local)
    paid_cost = sum(e.estimated_cost for e in events if not e.is_local)

    by_phase = {}
    by_agent = {}
    by_model = {}
    for e in events:
        phase_key = e.phase_id or "unknown"
        by_phase[phase_key] = by_phase.get(phase_key, 0) + e.estimated_cost
        agent_key = e.agent_id or "unknown"
        by_agent[agent_key] = by_agent.get(agent_key, 0) + e.estimated_cost
        model_key = e.model_name or "unknown"
        by_model[model_key] = by_model.get(model_key, 0) + e.estimated_cost

    run_result = await db.execute(select(Run).where(Run.id == run_id))
    run = run_result.scalar_one_or_none()
    budget_limit = run.budget_limit if run else None

    warning_threshold = 0.8
    is_near_limit = budget_limit is not None and total_cost >= budget_limit * warning_threshold if budget_limit else False
    is_hard_limit = budget_limit is not None and total_cost >= budget_limit if budget_limit else False

    return CostReportResponse(
        run_id=run_id,
        total_cost=round(total_cost, 4),
        budget_limit=budget_limit,
        remaining_budget=round(budget_limit - total_cost, 4) if budget_limit else None,
        warning_threshold=warning_threshold,
        is_near_limit=is_near_limit,
        is_hard_limit_reached=is_hard_limit,
        local_cost=round(local_cost, 4),
        paid_cost=round(paid_cost, 4),
        estimated_savings=round(paid_cost * 0.9, 4),
        by_phase={k: round(v, 4) for k, v in by_phase.items()},
        by_agent={k: round(v, 4) for k, v in by_agent.items()},
        by_model={k: round(v, 4) for k, v in by_model.items()},
    )


@router.get("/events/{run_id}")
async def list_cost_events(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CostEvent).where(CostEvent.run_id == run_id).order_by(CostEvent.created_at)
    )
    events = result.scalars().all()
    return {"events": [
        {
            "id": e.id, "event_type": e.event_type, "model": e.model_name,
            "provider": e.provider, "tokens_in": e.tokens_in, "tokens_out": e.tokens_out,
            "cost": e.estimated_cost, "is_local": e.is_local, "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]}
