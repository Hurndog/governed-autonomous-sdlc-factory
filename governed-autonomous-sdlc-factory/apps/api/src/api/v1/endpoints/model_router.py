"""
Model Router API Endpoints — v0.5.

Provides:
- GET  /api/v1/models/capabilities — list all model capabilities
- POST /api/v1/models/route — route a task to a model
- POST /api/v1/models/arbitrate — run multi-model arbitration
- GET  /api/v1/models/health — provider health check
- GET  /api/v1/models/sovereignty — sovereignty dashboard data
"""

import time
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_permission
from src.core.database import get_db
from src.core.logging import get_logger
from src.engines.cognitive_governance import (
    ModelCapabilityRegistry, CognitiveModelRouter, CognitiveArbitrationEngine,
    RoutingRequest, TaskType, SovereigntyLevel,
    get_capability_registry, get_model_router, get_arbitration_engine,
)

logger = get_logger("model-router-api")

router = APIRouter(prefix="/models", tags=["model-router"])


# ── Schemas ─────────────────────────────────────────────────────────────────

class RouteRequestSchema(BaseModel):
    task_type: str = Field(..., description="Task type (e.g., code_generation, governance_analysis)")
    governance_level: str = Field(default="standard", description="minimal, standard, strict")
    sovereignty_requirement: str = Field(default="hybrid", description="frontier_only, sovereign_preferred, sovereign_required, local_only, hybrid")
    latency_budget_ms: int = Field(default=30000)
    cost_budget_usd: float = Field(default=1.0)
    hallucination_tolerance: float = Field(default=0.3)
    replay_sensitivity: str = Field(default="standard", description="low, standard, high")
    context_size: int = Field(default=4096)
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None


class ArbitrateRequestSchema(BaseModel):
    task_type: str = Field(..., description="Task type")
    prompt: str = Field(..., description="The prompt to send to multiple models")
    models: List[dict] = Field(default_factory=list, description="List of {provider, model} to use. If empty, router selects.")
    governance_level: str = Field(default="standard")
    sovereignty_requirement: str = Field(default="hybrid")


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/capabilities")
async def list_model_capabilities(
    current_user=Depends(require_permission("operations.view")),
):
    """List all registered model capabilities."""
    registry = get_capability_registry()
    capabilities = registry.list_capabilities()
    return {
        "models": [
            {
                "provider": c.provider,
                "model": c.model,
                "coding_quality": c.coding_quality,
                "reasoning_quality": c.reasoning_quality,
                "governance_reliability": c.governance_reliability,
                "hallucination_risk": c.hallucination_risk,
                "latency_score": c.latency_score,
                "cost_score": c.cost_score,
                "context_window": c.context_window,
                "structured_output_reliability": c.structured_output_reliability,
                "replay_stability": c.replay_stability,
                "semantic_consistency": c.semantic_consistency,
                "sovereignty_level": c.sovereignty_level.value,
                "availability": c.availability,
                "operator_trust": c.operator_trust,
                "historical_failure_rate": c.historical_failure_rate,
                "updated_at": c.updated_at,
            }
            for c in capabilities
        ],
        "total": len(capabilities),
    }


@router.post("/route")
async def route_task(
    request: RouteRequestSchema,
    current_user=Depends(require_permission("operations.view")),
):
    """Route a task to the best model based on requirements."""
    try:
        task_type = TaskType(request.task_type)
    except ValueError:
        valid = [t.value for t in TaskType]
        raise HTTPException(status_code=400, detail=f"Invalid task_type. Valid: {valid}")

    try:
        sovereignty = SovereigntyLevel(request.sovereignty_requirement)
    except ValueError:
        valid = [s.value for s in SovereigntyLevel]
        raise HTTPException(status_code=400, detail=f"Invalid sovereignty_requirement. Valid: {valid}")

    routing_request = RoutingRequest(
        task_type=task_type,
        governance_level=request.governance_level,
        sovereignty_requirement=sovereignty,
        latency_budget_ms=request.latency_budget_ms,
        cost_budget_usd=request.cost_budget_usd,
        hallucination_tolerance=request.hallucination_tolerance,
        replay_sensitivity=request.replay_sensitivity,
        context_size=request.context_size,
        workspace_id=request.workspace_id,
        project_id=request.project_id,
    )

    router = get_model_router()
    decision = router.route(routing_request)

    return {
        "selected_provider": decision.selected_provider,
        "selected_model": decision.selected_model,
        "routing_reason": decision.routing_reason,
        "trust_score": decision.trust_score,
        "governance_score": decision.governance_score,
        "sovereignty_score": decision.sovereignty_score,
        "cost_estimate": round(decision.cost_estimate, 6),
        "fallback_chain": decision.fallback_chain,
        "arbitration_required": decision.arbitration_required,
        "rejected_models": decision.rejected_models,
    }


@router.post("/arbitrate")
async def arbitrate_task(
    request: ArbitrateRequestSchema,
    current_user=Depends(require_permission("operations.intervene")),
):
    """Run multi-model arbitration — send prompt to multiple models and analyze disagreement."""
    registry = get_capability_registry()
    arb_engine = get_arbitration_engine()

    # Determine which models to use
    if request.models:
        model_configs = request.models
    else:
        # Auto-select based on task type and sovereignty
        try:
            task_type = TaskType(request.task_type)
            sovereignty = SovereigntyLevel(request.sovereignty_requirement)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        candidates = registry.get_models_for_task(task_type, sovereignty)
        model_configs = [{"provider": c.provider, "model": c.model} for c in candidates[:3]]

    if len(model_configs) < 2:
        return {
            "status": "skipped",
            "reason": "Fewer than 2 suitable models found. Arbitration requires at least 2 models.",
            "models_considered": model_configs,
        }

    # For now, return the arbitration plan (actual multi-model execution would require provider API keys)
    # In production, this would call each provider and collect responses
    return {
        "status": "arbitration_plan",
        "models": model_configs,
        "task_type": request.task_type,
        "sovereignty_requirement": request.sovereignty_requirement,
        "governance_level": request.governance_level,
        "note": "Multi-model execution requires configured provider API keys. This endpoint returns the arbitration plan.",
        "next_steps": "Configure provider API keys and call each provider's complete() method, then submit outputs to /arbitrate/analyze.",
    }


@router.get("/health")
async def check_model_health(
    current_user=Depends(require_permission("operations.view")),
):
    """Check health of all configured model providers."""
    registry = get_capability_registry()
    capabilities = registry.list_capabilities()

    health = []
    for cap in capabilities:
        # In production, this would actually ping each provider
        health.append({
            "provider": cap.provider,
            "model": cap.model,
            "status": "configured" if cap.availability > 0 else "unavailable",
            "availability": cap.availability,
            "historical_failure_rate": cap.historical_failure_rate,
            "last_checked": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        })

    return {"providers": health, "total": len(health)}


@router.get("/sovereignty")
async def get_sovereignty_dashboard(
    current_user=Depends(require_permission("operations.view")),
):
    """Get sovereignty dashboard data — local vs frontier usage analysis."""
    registry = get_capability_registry()
    capabilities = registry.list_capabilities()

    local_models = [c for c in capabilities if c.sovereignty_level == SovereigntyLevel.LOCAL_ONLY]
    sovereign_models = [c for c in capabilities if c.sovereignty_level == SovereigntyLevel.SOVEREIGN_PREFERRED]
    frontier_models = [c for c in capabilities if c.sovereignty_level == SovereigntyLevel.FRONTIER_ONLY]
    hybrid_models = [c for c in capabilities if c.sovereignty_level == SovereigntyLevel.HYBRID]

    return {
        "summary": {
            "total_models": len(capabilities),
            "local_only": len(local_models),
            "sovereign_preferred": len(sovereign_models),
            "frontier_only": len(frontier_models),
            "hybrid": len(hybrid_models),
        },
        "sovereignty_ratio": {
            "local": len(local_models) / len(capabilities) if capabilities else 0,
            "sovereign": len(sovereign_models) / len(capabilities) if capabilities else 0,
            "frontier": len(frontier_models) / len(capabilities) if capabilities else 0,
        },
        "models": {
            "local": [{"provider": c.provider, "model": c.model} for c in local_models],
            "sovereign": [{"provider": c.provider, "model": c.model} for c in sovereign_models],
            "frontier": [{"provider": c.provider, "model": c.model} for c in frontier_models],
            "hybrid": [{"provider": c.provider, "model": c.model} for c in hybrid_models],
        },
        "provider_concentration": _compute_provider_concentration(capabilities),
    }


def _compute_provider_concentration(capabilities: list) -> dict:
    """Compute provider concentration risk."""
    if not capabilities:
        return {"risk": "none", "providers": {}}

    provider_counts = {}
    for c in capabilities:
        provider_counts[c.provider] = provider_counts.get(c.provider, 0) + 1

    total = len(capabilities)
    concentration = {p: round(c / total, 2) for p, c in provider_counts.items()}

    max_conc = max(concentration.values()) if concentration else 0
    risk = "low" if max_conc < 0.5 else "medium" if max_conc < 0.8 else "high"

    return {"risk": risk, "providers": concentration}
