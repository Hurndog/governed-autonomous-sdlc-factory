"""Full Pipeline API endpoints and replay/timeline endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_no_autoflush
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
    db: AsyncSession = Depends(get_db_no_autoflush),
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
    db: AsyncSession = Depends(get_db_no_autoflush),
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


@router.get("/runs/{run_id}/timeline")
async def get_run_timeline(
    run_id: str,
    db: AsyncSession = Depends(get_db_no_autoflush),
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
    db: AsyncSession = Depends(get_db_no_autoflush),
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


# ── PHASE G: Replay & Integrity API Endpoints ─────────────────────────────

from src.core.integrity import IntegrityManager
from src.engines.replay_engine import ReplayEngine
from src.engines.divergence import DivergenceAnalyzer
from src.models import (
    ReplaySession, IntegrityVerification, DivergenceRecord,
    ReplayManifest, ExecutionBaseline,
)


@router.get("/runs/{run_id}/integrity")
async def get_run_integrity(
    run_id: str,
    user=Depends(get_current_user),
):
    """Get integrity verification for a run."""
    import asyncio
    from src.engines.integrity_runtime_sync import verify_integrity_sync

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,  # Uses default executor
        verify_integrity_sync,
        run_id,
    )
    return result


@router.post("/runs/{run_id}/verify-integrity")
async def verify_run_integrity(
    run_id: str,
    user=Depends(get_current_user),
):
    """Run full integrity verification on a run."""
    import asyncio
    from src.engines.integrity_runtime_sync import verify_integrity_sync

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,  # Uses default executor
        verify_integrity_sync,
        run_id,
    )

    return {
        "run_id": run_id,
        "integrity_score": result.get("overall_score", 0.0),
        "status": (
            "pass" if result.get("overall_score", 0) >= 0.8
            else "warning" if result.get("overall_score", 0) >= 0.5
            else "fail"
        ),
        "checks": result.get("total_checks", 0),
        "passed": result.get("passed_checks", 0),
        "failed": result.get("failed_checks", 0),
        "warnings": result.get("warning_checks", 0),
        "report": result,
    }


@router.post("/runs/{run_id}/replay")
async def replay_run_full(
    run_id: str,
    replay_mode: str = Query(default="full", description="Replay mode: full, phase, event, snapshot, semantic"),
    from_timestamp: Optional[str] = Query(None, description="ISO timestamp to replay from"),
    phase_name: Optional[str] = Query(None, description="Phase name for phase-mode replay"),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Execute a deterministic replay of a run using synchronous replay runtime.

    The replay runs in a dedicated thread pool with a completely independent
    sync SQLAlchemy session. No async/greenlet conflicts. No shared state.
    """
    import asyncio
    from src.engines.replay_runtime_sync import _replay_executor, run_sync_replay

    # Verify run exists first (using the async session)
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Execute sync replay in thread pool
    loop = asyncio.get_running_loop()
    try:
        ctx = await loop.run_in_executor(
            _replay_executor,
            run_sync_replay,
            run_id,
            replay_mode,
            from_timestamp,
            phase_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if ctx.error:
        raise HTTPException(status_code=500, detail=f"Replay failed: {ctx.error}")

    return {
        "replay_session_id": ctx.replay_id,
        "run_id": ctx.run_id,
        "replay_mode": ctx.replay_mode,
        "status": ctx.phase,
        "events_replayed": ctx.events_replayed,
        "artifacts_replayed": ctx.artifacts_replayed,
        "governance_replayed": ctx.governance_replayed,
        "snapshots_replayed": ctx.snapshots_replayed,
        "traceability_replayed": ctx.traceability_replayed,
        "divergence_count": ctx.divergence_count,
        "integrity_score": ctx.integrity_score,
        "chain_continuity_valid": ctx.chain_continuity_valid,
        "replay_hash": ctx.replay_hash,
        "checkpoints": ctx.checkpoints,
        "started_at": ctx.started_at.isoformat() if ctx.started_at else None,
        "completed_at": ctx.completed_at.isoformat() if ctx.completed_at else None,
    }


@router.get("/runs/{run_id}/replay")
async def get_replay_sessions(
    run_id: str,
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Get all replay sessions for a run."""
    engine = ReplayEngine(run_id)
    sessions = await engine.get_replay_sessions(db)
    return {
        "run_id": run_id,
        "replay_sessions": [
            {
                "id": s.id,
                "mode": s.replay_mode,
                "status": s.status,
                "events_replayed": s.total_events_replayed,
                "artifacts_replayed": s.total_artifacts_replayed,
                "divergence_count": s.divergence_count,
                "integrity_score": s.integrity_score,
                "replay_hash": s.replay_hash,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in sessions
        ],
    }


@router.get("/runs/{run_id}/divergence")
async def get_divergence_records(
    run_id: str,
    replay_session_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Get divergence records for a run."""
    query = select(DivergenceRecord).where(DivergenceRecord.run_id == run_id)
    if replay_session_id:
        query = query.where(DivergenceRecord.replay_session_id == replay_session_id)
    query = query.order_by(DivergenceRecord.detected_at.desc())
    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "run_id": run_id,
        "total_divergences": len(records),
        "records": [
            {
                "id": r.id,
                "type": r.divergence_type,
                "severity": r.severity,
                "location": r.divergence_location,
                "expected": r.expected_value,
                "actual": r.actual_value,
                "causal_impact": r.causal_impact,
                "detected_at": r.detected_at.isoformat() if r.detected_at else None,
            }
            for r in records
        ],
    }


@router.post("/runs/{run_id}/compare")
async def compare_run_replay(
    run_id: str,
    replay_session_id: str = Query(..., description="Replay session ID to compare against"),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Compare original run with replay and generate divergence analysis."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    replay_session = await db.get(ReplaySession, replay_session_id)
    if not replay_session:
        raise HTTPException(status_code=404, detail="Replay session not found")

    analyzer = DivergenceAnalyzer(run_id)
    report = await analyzer.analyze(db, replay_session_id)

    return report.to_dict()


@router.get("/runs/{run_id}/semantic-graph")
async def get_semantic_graph(
    run_id: str,
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Get the semantic execution graph for a run."""
    from src.models import SemanticGraphNode, SemanticGraphEdge

    nodes_result = await db.execute(
        select(SemanticGraphNode).where(SemanticGraphNode.run_id == run_id).order_by(SemanticGraphNode.created_at)
    )
    nodes = nodes_result.scalars().all()

    edges_result = await db.execute(
        select(SemanticGraphEdge).where(SemanticGraphEdge.run_id == run_id)
    )
    edges = edges_result.scalars().all()

    return {
        "run_id": run_id,
        "nodes": [
            {
                "id": n.id,
                "type": n.node_type,
                "entity_id": n.entity_id,
                "entity_name": n.entity_name,
                "semantic_type": n.semantic_type,
                "from_state": n.from_state,
                "to_state": n.to_state,
                "transition_reason": n.transition_reason,
                "node_hash": n.node_hash,
            }
            for n in nodes
        ],
        "edges": [
            {
                "id": e.id,
                "source": e.source_node_id,
                "target": e.target_node_id,
                "type": e.edge_type,
                "label": e.edge_label,
                "weight": e.edge_weight,
                "edge_hash": e.edge_hash,
            }
            for e in edges
        ],
    }


@router.get("/runs/{run_id}/snapshot/{snapshot_id}")
async def get_snapshot_detail(
    run_id: str,
    snapshot_id: str,
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Get detailed snapshot data."""
    snapshot = await db.get(RunSnapshot, snapshot_id)
    if not snapshot or snapshot.run_id != run_id:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return {
        "id": snapshot.id,
        "run_id": snapshot.run_id,
        "type": snapshot.snapshot_type,
        "state": snapshot.state_data,
        "phases": snapshot.phase_states,
        "artifacts": snapshot.artifact_states,
        "costs": snapshot.cost_summary,
        "governance": snapshot.governance_summary,
        "snapshot_hash": snapshot.snapshot_hash,
        "chain_hash": snapshot.chain_hash,
        "parent_hash": snapshot.parent_hash,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
    }
