"""Main API router."""
from fastapi import APIRouter
from src.api.v1.endpoints import (
    projects, runs, phases, agents, tasks, artifacts, approvals,
    logs, evidence, costs, patterns, memory,
    github as github_endpoints, deployment, settings, engines,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(artifacts.router, prefix="/artifacts", tags=["artifacts"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
api_router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(github_endpoints.router, prefix="/github", tags=["github"])
api_router.include_router(deployment.router, prefix="/deployment", tags=["deployment"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(engines.router, tags=["engines"])
