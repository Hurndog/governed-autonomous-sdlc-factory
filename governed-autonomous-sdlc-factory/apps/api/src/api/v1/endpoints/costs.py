"""Cost endpoints with enhanced tokenomics aggregation."""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import CostEvent, Run, Phase, Agent, ModelCall
from src.schemas.phase import CostEventCreate

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


@router.get("/report/{run_id}")
async def get_cost_report(run_id: str, db: AsyncSession = Depends(get_db)):
    """Enhanced cost report with full tokenomics aggregation."""
    result = await db.execute(select(CostEvent).where(CostEvent.run_id == run_id))
    events = result.scalars().all()

    # Also query model_calls for call-level stats
    mc_result = await db.execute(
        select(ModelCall).where(ModelCall.run_id == run_id)
    )
    model_calls = mc_result.scalars().all()

    # --- Core totals ---
    total_cost = sum(e.estimated_cost for e in events)
    total_input_tokens = sum(e.tokens_in for e in events)
    total_output_tokens = sum(e.tokens_out for e in events)
    total_tokens = total_input_tokens + total_output_tokens

    # --- Model call stats ---
    total_calls = len(model_calls)
    total_errors = sum(1 for mc in model_calls if not mc.is_success)
    total_retries = sum(mc.retry_count for mc in model_calls)

    # --- Budget ---
    run_result = await db.execute(select(Run).where(Run.id == run_id))
    run = run_result.scalar_one_or_none()
    budget_limit = run.budget_limit if run else None
    warning_threshold = 0.8
    is_near_limit = budget_limit is not None and total_cost >= budget_limit * warning_threshold if budget_limit else False
    is_hard_limit = budget_limit is not None and total_cost >= budget_limit if budget_limit else False
    local_cost = sum(e.estimated_cost for e in events if e.is_local)
    paid_cost = sum(e.estimated_cost for e in events if not e.is_local)

    # --- by_phase: resolve phase_id → phase name ---
    phase_ids = list(set(e.phase_id for e in events if e.phase_id))
    phase_name_map = {}
    if phase_ids:
        phase_result = await db.execute(select(Phase.id, Phase.name).where(Phase.id.in_(phase_ids)))
        phase_name_map = {pid: name for pid, name in phase_result.all()}

    by_phase = {}
    for e in events:
        phase_key = phase_name_map.get(e.phase_id, e.phase_id or "unknown")
        if phase_key not in by_phase:
            by_phase[phase_key] = {
                "key": phase_key, "label": phase_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_phase[phase_key]
        entry["input_tokens"] += e.tokens_in
        entry["output_tokens"] += e.tokens_out
        entry["total_tokens"] += e.tokens_in + e.tokens_out
        entry["cost"] += e.estimated_cost

    # Add call counts from model_calls per phase
    for mc in model_calls:
        phase_key = phase_name_map.get(mc.phase_id, mc.phase_id or "unknown")
        if phase_key not in by_phase:
            by_phase[phase_key] = {
                "key": phase_key, "label": phase_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_phase[phase_key]
        entry["call_count"] += 1
        if not mc.is_success:
            entry["error_count"] += 1
        entry["retry_count"] += mc.retry_count

    # --- by_model ---
    by_model = {}
    for e in events:
        model_key = e.model_name or "unknown"
        if model_key not in by_model:
            by_model[model_key] = {
                "key": model_key, "label": model_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_model[model_key]
        entry["input_tokens"] += e.tokens_in
        entry["output_tokens"] += e.tokens_out
        entry["total_tokens"] += e.tokens_in + e.tokens_out
        entry["cost"] += e.estimated_cost

    for mc in model_calls:
        model_key = mc.model_name or "unknown"
        if model_key not in by_model:
            by_model[model_key] = {
                "key": model_key, "label": model_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_model[model_key]
        entry["call_count"] += 1
        if not mc.is_success:
            entry["error_count"] += 1
        entry["retry_count"] += mc.retry_count

    # --- by_provider ---
    by_provider = {}
    for e in events:
        provider_key = e.provider or "unknown"
        if provider_key not in by_provider:
            by_provider[provider_key] = {
                "key": provider_key, "label": provider_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_provider[provider_key]
        entry["input_tokens"] += e.tokens_in
        entry["output_tokens"] += e.tokens_out
        entry["total_tokens"] += e.tokens_in + e.tokens_out
        entry["cost"] += e.estimated_cost

    for mc in model_calls:
        provider_key = mc.provider or "unknown"
        if provider_key not in by_provider:
            by_provider[provider_key] = {
                "key": provider_key, "label": provider_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_provider[provider_key]
        entry["call_count"] += 1
        if not mc.is_success:
            entry["error_count"] += 1
        entry["retry_count"] += mc.retry_count

    # --- by_agent: resolve agent_id → agent name ---
    agent_ids = list(set(e.agent_id for e in events if e.agent_id))
    agent_name_map = {}
    if agent_ids:
        agent_result = await db.execute(select(Agent.id, Agent.name).where(Agent.id.in_(agent_ids)))
        agent_name_map = {aid: name for aid, name in agent_result.all()}

    by_agent = {}
    for e in events:
        if not e.agent_id:
            continue
        agent_key = agent_name_map.get(e.agent_id, e.agent_id)
        if agent_key not in by_agent:
            by_agent[agent_key] = {
                "key": agent_key, "label": agent_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_agent[agent_key]
        entry["input_tokens"] += e.tokens_in
        entry["output_tokens"] += e.tokens_out
        entry["total_tokens"] += e.tokens_in + e.tokens_out
        entry["cost"] += e.estimated_cost

    for mc in model_calls:
        if not mc.agent_id:
            continue
        agent_key = agent_name_map.get(mc.agent_id, mc.agent_id)
        if agent_key not in by_agent:
            by_agent[agent_key] = {
                "key": agent_key, "label": agent_key,
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "call_count": 0, "error_count": 0, "retry_count": 0,
                "percentage_of_total": 0.0, "is_estimated": False,
            }
        entry = by_agent[agent_key]
        entry["call_count"] += 1
        if not mc.is_success:
            entry["error_count"] += 1
        entry["retry_count"] += mc.retry_count

    # --- Percentages ---
    for agg in [by_phase, by_model, by_provider, by_agent]:
        for key, entry in agg.items():
            entry["percentage_of_total"] = round(entry["total_tokens"] / max(total_tokens, 1) * 100, 2)
            entry["cost"] = round(entry["cost"], 4)

    # --- Waste summary (derived) ---
    retry_tokens = sum(
        e.tokens_in + e.tokens_out
        for e in events
        if e.event_type in ("retry", "rework")
    )
    failed_call_tokens = sum(
        mc.tokens_in + mc.tokens_out
        for mc in model_calls
        if not mc.is_success
    )
    waste_summary = {
        "retry_tokens": retry_tokens,
        "failed_call_tokens": failed_call_tokens,
        "oversized_prompt_tokens": None,
        "unused_context_tokens": None,
        "unknown_waste_tokens": None,
        "notes": "retry_tokens derived from event_type='retry'/'rework'; failed_call_tokens from model_calls.is_success=false",
    }

    # --- Missing fields & data quality ---
    missing_fields = []
    data_quality_warnings = []

    if not agent_ids and not any(mc.agent_id for mc in model_calls):
        missing_fields.append("agent")
        data_quality_warnings.append("No agent_id found in cost_events or model_calls; by_agent aggregation is empty")

    if not events:
        data_quality_warnings.append("No cost events found for this run")

    if total_cost == 0 and total_tokens > 0:
        data_quality_warnings.append("Total cost is 0 but tokens were consumed; likely using local/free inference")

    # Check for null model/provider
    null_models = sum(1 for e in events if not e.model_name)
    if null_models > 0:
        data_quality_warnings.append(f"{null_models} cost events have null model_name")

    null_providers = sum(1 for e in events if not e.provider)
    if null_providers > 0:
        data_quality_warnings.append(f"{null_providers} cost events have null provider")

    # --- Aggregation confidence ---
    aggregation_confidence = "high"
    if missing_fields:
        aggregation_confidence = "partial"
    if not events and not model_calls:
        aggregation_confidence = "none"

    return {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aggregation_confidence": aggregation_confidence,
        "total_cost": round(total_cost, 4),
        "total_tokens": total_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_calls": total_calls,
        "total_errors": total_errors,
        "total_retries": total_retries,
        "budget_limit": budget_limit,
        "remaining_budget": round(budget_limit - total_cost, 4) if budget_limit else None,
        "warning_threshold": warning_threshold,
        "is_near_limit": is_near_limit,
        "is_hard_limit_reached": is_hard_limit,
        "local_cost": round(local_cost, 4),
        "paid_cost": round(paid_cost, 4),
        "estimated_savings": round(paid_cost * 0.9, 4),
        "by_phase": {k: v for k, v in by_phase.items()},
        "by_model": {k: v for k, v in by_model.items()},
        "by_provider": {k: v for k, v in by_provider.items()},
        "by_agent": {k: v for k, v in by_agent.items()},
        "waste_summary": waste_summary,
        "missing_fields": missing_fields,
        "data_quality_warnings": data_quality_warnings,
    }


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
