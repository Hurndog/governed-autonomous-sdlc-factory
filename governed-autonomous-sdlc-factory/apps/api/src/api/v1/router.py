"""Main API router — with default auth on all endpoints."""
from fastapi import APIRouter, Depends

from src.core.auth import get_current_user, require_permission
from src.api.v1.endpoints import (
    projects, runs, phases, agents, tasks, artifacts, approvals,
    logs, evidence, costs, patterns, memory,
    github as github_endpoints, deployment, settings, engines, pipeline, cognitive,
    semantic_coverage, auth, workspaces, operations, operator_intervention, memory_lifecycle,
    explainability, model_router,
)

api_router = APIRouter(prefix="/api/v1")

# Auth endpoints (public — handle their own auth internally)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Workspaces (protected by endpoint-level dependencies)
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])

# All other endpoints require authentication
api_router.include_router(
    projects.router, prefix="/projects", tags=["projects"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    runs.router, prefix="/runs", tags=["runs"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    phases.router, prefix="/phases", tags=["phases"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    agents.router, prefix="/agents", tags=["agents"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    tasks.router, prefix="/tasks", tags=["tasks"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    artifacts.router, prefix="/artifacts", tags=["artifacts"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    approvals.router, prefix="/approvals", tags=["approvals"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    logs.router, prefix="/logs", tags=["logs"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    evidence.router, prefix="/evidence", tags=["evidence"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    costs.router, prefix="/costs", tags=["costs"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    patterns.router, prefix="/patterns", tags=["patterns"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    memory.router, prefix="/memory", tags=["memory"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    github_endpoints.router, prefix="/github", tags=["github"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    deployment.router, prefix="/deployment", tags=["deployment"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    settings.router, prefix="/settings", tags=["settings"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    engines.router, tags=["engines"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    pipeline.router, tags=["pipeline"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    cognitive.router, tags=["cognitive"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    semantic_coverage.router, tags=["semantic-coverage"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    operations.router, tags=["operations"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    operator_intervention.router, tags=["operator-intervention"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    memory_lifecycle.router, tags=["memory-lifecycle"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    explainability.router, tags=["explainability"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    model_router.router, tags=["model-router"],
    dependencies=[Depends(get_current_user)],
)
