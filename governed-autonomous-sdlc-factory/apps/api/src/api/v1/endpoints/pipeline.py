"""Full Pipeline API endpoints and replay/timeline endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import get_current_auth as get_current_user
from src.models import Run, RunStatus, Project, Artifact, LogEvent, CostEvent, RunSnapshot
from src.services.full_pipeline_orchestrator import full_pipeline
from src.engines.snapshots import SnapshotManager
from src.engines.traceability import TraceabilityManager
from src.core.logging import get_logger

logger = get_logger("api.pipeline")

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run-full-pipeline")
async def run_full_pipeline(
    project_id: str = Query(...),
    intent: str = Query(..., description="User intent / project description"),
    project_name: str = Query(default=""),
    budget_limit: Optional[float] = None,
    is_demo: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Execute the full cognitive pipeline: intent → spec → arch → governance → test → trace → snapshot → evidence."""
    import asyncio

    # Create a new run
    run = Run(
        project_id=project_id,
        name=f"Pipeline Run: {project_name or 'Untitled'}",
        budget_limit=budget_limit,
        is_demo=is_demo,
    )
    db.add(run)
    await db.flush()

    # Get project name if not provided
    if not project_name:
        proj = await db.get(Project, project_id)
        project_name = proj.name if proj else "Untitled"

    await db.commit()
    await db.refresh(run)

    # Start pipeline in background
    asyncio.create_task(
        full_pipeline.execute_full_pipeline(
            project_id=project_id,
            run_id=run.id,
            intent=intent,
            project_name=project_name,
            budget_limit=budget_limit,
            is_demo=is_demo,
        )
    )

    return {
        "run_id": run.id,
        "status": "started",
        "message": "Full pipeline started. Connect to WebSocket for live events.",
        "ws_url": f"/ws/runs/{run.id}",
    }


# ── Replay & Timeline Endpoints ─────────────────────────────────────────

@router.get("/runs/{run_id}/snapshot")
async def get_run_snapshot(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the latest snapshot for a run."""
    result = await db.execute(
        select(RunSnapshot)
        .where(RunSnapshot.run_id == run_id)
        .order_by(RunSnapshot.created_at.desc())
    )
    snapshot = result.scalars().first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found for this run")
    return {
        "id": snapshot.id,
        "type": snapshot.snapshot_type,
        "state": snapshot.state_data,
        "phases": snapshot.phase_states,
        "artifacts": snapshot.artifact_states,
        "costs": snapshot.cost_summary,
        "governance": snapshot.governance_summary,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
    }


@router.post("/runs/{run_id}/replay")
async def replay_run(
    run_id: str,
    from_timestamp: Optional[str] = Query(None, description="ISO timestamp to replay from"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Replay a run — returns all events in chronological order for reconstruction."""
    # Get run
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Get all events
    events_query = select(LogEvent).where(LogEvent.run_id == run_id)
    if from_timestamp:
        events_query = events_query.where(LogEvent.created_at >= from_timestamp)
    events_query = events_query.order_by(LogEvent.created_at)
    events_result = await db.execute(events_query)
    events = events_result.scalars().all()

    # Get all artifacts
    artifacts_query = select(Artifact).where(Artifact.run_id == run_id).order_by(Artifact.created_at)
    artifacts_result = await db.execute(artifacts_query)
    artifacts = artifacts_result.scalars().all()

    # Get all costs
    costs_query = select(CostEvent).where(CostEvent.run_id == run_id).order_by(CostEvent.created_at)
    costs_result = await db.execute(costs_query)
    costs = costs_result.scalars().all()

    # Get snapshots
    snaps_query = select(RunSnapshot).where(RunSnapshot.run_id == run_id).order_by(RunSnapshot.created_at)
    snaps_result = await db.execute(snaps_query)
    snaps = snaps_result.scalars().all()

    return {
        "run": {
            "id": run.id,
            "name": run.name,
            "status": str(run.status),
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "total_cost": run.total_cost,
        },
        "events": [
            {
                "id": e.id,
                "severity": e.severity,
                "message": e.message,
                "source_file": e.source_file,
                "timestamp": e.created_at.isoformat() if e.created_at else None,
                "metadata": e.metadata_,
            }
            for e in events
        ],
        "artifacts": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.artifact_type,
                "phase": a.phase_name,
                "file_path": a.file_path,
                "content_hash": a.metadata_.get("content_hash") if a.metadata_ else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in artifacts
        ],
        "costs": [
            {
                "model": c.model_name,
                "tokens_in": c.tokens_in,
                "tokens_out": c.tokens_out,
                "cost": c.estimated_cost,
                "timestamp": c.created_at.isoformat() if c.created_at else None,
            }
            for c in costs
        ],
        "snapshots": [
            {
                "id": s.id,
                "type": s.snapshot_type,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in snaps
        ],
        "replay_metadata": {
            "total_events": len(events),
            "total_artifacts": len(artifacts),
            "total_cost_entries": len(costs),
            "total_snapshots": len(snaps),
            "replayed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        },
    }


@router.get("/runs/{run_id}/timeline")
async def get_run_timeline(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get a chronological timeline of all run events for playback."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    events_query = select(LogEvent).where(LogEvent.run_id == run_id).order_by(LogEvent.created_at)
    events_result = await db.execute(events_query)
    events = events_result.scalars().all()

    timeline = []
    for e in events:
        timeline.append({
            "timestamp": e.created_at.isoformat() if e.created_at else None,
            "severity": e.severity,
            "message": e.message,
            "source": e.source_file or "system",
            "phase": e.phase_id or "global",
            "trace_id": e.trace_id,
        })

    return {
        "run_id": run_id,
        "run_status": str(run.status),
        "total_events": len(timeline),
        "timeline": timeline,
    }


@router.get("/traceability/lineage/{artifact_id}")
async def get_artifact_lineage(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the full lineage chain for an artifact."""
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    trace_mgr = TraceabilityManager(artifact.run_id)
    chain = await trace_mgr.get_chain(session=db, source_type="artifact", source_id=artifact_id)

    return {
        "artifact": {
            "id": artifact.id,
            "name": artifact.name,
            "type": artifact.artifact_type,
            "phase": artifact.phase_name,
            "file_path": artifact.file_path,
            "content_hash": artifact.metadata_.get("content_hash") if artifact.metadata_ else None,
        },
        "lineage": chain,
    }
