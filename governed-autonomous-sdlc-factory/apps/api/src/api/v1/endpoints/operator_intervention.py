"""
Operator Intervention Console — Pass 3.

Provides endpoints for humans to control the runtime safely:
- POST /api/v1/operations/runs/{run_id}/pause
- POST /api/v1/operations/runs/{run_id}/resume
- POST /api/v1/operations/runs/{run_id}/quarantine-memory
- POST /api/v1/operations/runs/{run_id}/force-verifier
- POST /api/v1/operations/runs/{run_id}/reduce-autonomy
- POST /api/v1/operations/runs/{run_id}/request-human-review
- POST /api/v1/operations/runs/{run_id}/invalidate-replay
- POST /api/v1/operations/runs/{run_id}/lock-evidence
- GET  /api/v1/operations/interventions — intervention history
- GET  /api/v1/operations/interventions/{intervention_id} — single intervention detail

Each action:
- requires specific RBAC permission
- creates audit log entry
- creates operator_interventions record
- updates metacognitive_state where relevant
- publishes operation event to SSE stream
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_permission, Role, PERMISSIONS, role_has_permission
from src.core.database import get_db
from src.core.logging import get_logger

logger = get_logger("operator")

router = APIRouter(prefix="/operations", tags=["operator-intervention"])


# ── Ensure operations permissions exist ────────────────────────────────────

# Add operations permissions to the PERMISSIONS dict
PERMISSIONS["operations.view"] = {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.EXECUTIVE_VIEWER, Role.AUDITOR, Role.OPERATOR}
PERMISSIONS["operations.intervene"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.pause_run"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.resume_run"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.reduce_autonomy"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.quarantine_memory"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.invalidate_replay"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.lock_evidence"] = {Role.ADMIN, Role.OPERATOR}
PERMISSIONS["operations.force_verifier"] = {Role.ADMIN, Role.OPERATOR, Role.GOVERNANCE_REVIEWER}
PERMISSIONS["operations.request_human_review"] = {Role.ADMIN, Role.OPERATOR, Role.GOVERNANCE_REVIEWER}


# ── Schemas ─────────────────────────────────────────────────────────────────

class InterventionRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000, description="Reason for the intervention")
    metadata: dict = Field(default_factory=dict, description="Additional context")


class InterventionResponse(BaseModel):
    id: str
    run_id: str
    intervention_type: str
    operator_id: str
    reason: str
    prior_state: Optional[dict] = None
    corrected_state: Optional[dict] = None
    governance_impact: Optional[dict] = None
    created_at: str
    message: str


class InterventionHistoryResponse(BaseModel):
    interventions: list[dict]
    total: int
    offset: int
    limit: int


# ── Helper: create intervention record ──────────────────────────────────────

async def _create_intervention(
    db: AsyncSession,
    run_id: str,
    operator_id: str,
    intervention_type: str,
    reason: str,
    prior_state: Optional[dict] = None,
    corrected_state: Optional[dict] = None,
    governance_impact: Optional[dict] = None,
) -> str:
    """Create an operator_interventions record."""
    intervention_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Get project_id and workspace_id from run
    result = await db.execute(text("SELECT project_id, workspace_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    project_id = row[0] if row else None
    workspace_id = row[1] if row else None

    await db.execute(text("""
        INSERT INTO operator_interventions
        (id, run_id, project_id, workspace_id, operator_id, intervention_type,
         intervention_context, correction, prior_state, corrected_state, governance_impact, created_at)
        VALUES (:id, :rid, :pid, :wid, :oid, :itype, :context, :correction, :prior, :corrected, :gimpact, :created)
    """), {
        "id": intervention_id,
        "rid": run_id,
        "pid": project_id,
        "wid": workspace_id,
        "oid": operator_id,
        "itype": intervention_type,
        "context": {"reason": reason, **(governance_impact or {})},
        "correction": reason,
        "prior": prior_state,
        "corrected": corrected_state,
        "gimpact": governance_impact,
        "created": now,
    })

    return intervention_id


# ── Helper: publish intervention event ──────────────────────────────────────

async def _publish_intervention_event(
    run_id: str,
    event_type: str,
    message: str,
    severity: str,
    operator_id: str,
    metadata: Optional[dict] = None,
):
    """Publish intervention event to SSE stream."""
    try:
        from src.api.v1.endpoints.operations import publish_operation_event
        await publish_operation_event(
            event_type=event_type,
            message=message,
            severity=severity,
            source="operator",
            run_id=run_id,
            metadata={"operator_id": operator_id, **(metadata or {})},
            requires_operator_action=False,  # This IS the action
        )
    except Exception as e:
        logger.warning(f"Failed to publish intervention event: {e}")


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/runs/{run_id}/pause", response_model=InterventionResponse)
async def pause_run(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.pause_run")),
):
    """Pause a running run. Requires operations.pause_run permission."""
    # Verify run exists and is running
    result = await db.execute(text("SELECT status, project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if row[0] != "running":
        raise HTTPException(status_code=400, detail=f"Run is not running (status: {row[0]})")

    prior_state = {"status": row[0]}

    # Update run status
    await db.execute(text("UPDATE runs SET status = 'paused', updated_at = :now WHERE id = :rid"), {
        "now": datetime.now(timezone.utc), "rid": run_id,
    })

    # Update metacognitive state
    await db.execute(text("""
        UPDATE metacognitive_state
        SET active_restrictions = COALESCE(active_restrictions, '[]'::jsonb) || :restriction,
            updated_at = :now
        WHERE project_id = :pid
    """), {
        "restriction": [{"type": "operator_paused", "run_id": run_id, "at": datetime.now(timezone.utc).isoformat()}],
        "now": datetime.now(timezone.utc),
        "pid": row[1],
    })

    # Create intervention record
    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "PAUSE", body.reason,
        prior_state=prior_state, corrected_state={"status": "paused"},
        governance_impact={"action": "pause", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "RUN_PAUSED", f"Run paused by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="PAUSE",
        operator_id=current_user.user_id, reason=body.reason,
        prior_state=prior_state, corrected_state={"status": "paused"},
        governance_impact={"action": "pause"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Run {run_id} paused successfully",
    )


@router.post("/runs/{run_id}/resume", response_model=InterventionResponse)
async def resume_run(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.resume_run")),
):
    """Resume a paused run. Requires operations.resume_run permission."""
    result = await db.execute(text("SELECT status, project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if row[0] != "paused":
        raise HTTPException(status_code=400, detail=f"Run is not paused (status: {row[0]})")

    prior_state = {"status": row[0]}

    await db.execute(text("UPDATE runs SET status = 'running', updated_at = :now WHERE id = :rid"), {
        "now": datetime.now(timezone.utc), "rid": run_id,
    })

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "RESUME", body.reason,
        prior_state=prior_state, corrected_state={"status": "running"},
        governance_impact={"action": "resume", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "RUN_RESUMED", f"Run resumed by {current_user.display_name}: {body.reason}", "info", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="RESUME",
        operator_id=current_user.user_id, reason=body.reason,
        prior_state=prior_state, corrected_state={"status": "running"},
        governance_impact={"action": "resume"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Run {run_id} resumed successfully",
    )


@router.post("/runs/{run_id}/quarantine-memory", response_model=InterventionResponse)
async def quarantine_memory(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.quarantine_memory")),
):
    """Quarantine memory items for a run. Requires operations.quarantine_memory permission."""
    result = await db.execute(text("SELECT project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    project_id = row[0]

    # Quarantine active memory items for this run
    await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = false,
            semantic_content = jsonb_set(
                COALESCE(semantic_content, '{}'::jsonb),
                '{quarantined}',
                :quarantine_info
            )
        WHERE project_id = :pid AND is_active = true
          AND (entity_id = :rid OR semantic_content->>'run_id' = :rid2)
    """), {
        "quarantine_info": {"quarantined_by": current_user.user_id, "reason": body.reason, "at": datetime.now(timezone.utc).isoformat()},
        "pid": project_id,
        "rid": run_id,
        "rid2": run_id,
    })

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "QUARANTINE_MEMORY", body.reason,
        governance_impact={"action": "quarantine_memory", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "MEMORY_QUARANTINED", f"Memory quarantined by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="QUARANTINE_MEMORY",
        operator_id=current_user.user_id, reason=body.reason,
        governance_impact={"action": "quarantine_memory"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Memory quarantined for run {run_id}",
    )


@router.post("/runs/{run_id}/force-verifier", response_model=InterventionResponse)
async def force_verifier(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.force_verifier")),
):
    """Force a verifier review for a run. Requires operations.force_verifier permission."""
    result = await db.execute(text("SELECT status, project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "FORCE_VERIFIER", body.reason,
        prior_state={"status": row[0]},
        corrected_state={"status": row[0], "verifier_forced": True},
        governance_impact={"action": "force_verifier", "operator": current_user.user_id},
    )

    # Update metacognitive state
    await db.execute(text("""
        UPDATE metacognitive_state
        SET active_restrictions = COALESCE(active_restrictions, '[]'::jsonb) || :restriction,
            updated_at = :now
        WHERE project_id = :pid
    """), {
        "restriction": [{"type": "verifier_forced", "run_id": run_id, "at": datetime.now(timezone.utc).isoformat()}],
        "now": datetime.now(timezone.utc),
        "pid": row[1],
    })

    await db.commit()

    await _publish_intervention_event(run_id, "OPERATOR_INTERVENTION_REQUIRED", f"Verifier forced by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="FORCE_VERIFIER",
        operator_id=current_user.user_id, reason=body.reason,
        governance_impact={"action": "force_verifier"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Verifier review forced for run {run_id}",
    )


@router.post("/runs/{run_id}/reduce-autonomy", response_model=InterventionResponse)
async def reduce_autonomy(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.reduce_autonomy")),
):
    """Reduce autonomy level for a run. Requires operations.reduce_autonomy permission."""
    result = await db.execute(text("SELECT project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    project_id = row[0]

    # Get current autonomy level
    mc_result = await db.execute(text("SELECT autonomy_level FROM metacognitive_state WHERE project_id = :pid ORDER BY updated_at DESC LIMIT 1"), {"pid": project_id})
    mc_row = mc_result.fetchone()
    current_autonomy = mc_row[0] if mc_row else "full"

    # Reduce autonomy: full -> reduced -> restricted
    new_autonomy = "reduced" if current_autonomy == "full" else "restricted"

    await db.execute(text("""
        UPDATE metacognitive_state
        SET autonomy_level = :new_level,
            active_restrictions = COALESCE(active_restrictions, '[]'::jsonb) || :restriction,
            updated_at = :now
        WHERE project_id = :pid
    """), {
        "new_level": new_autonomy,
        "restriction": [{"type": "autonomy_reduced", "from": current_autonomy, "to": new_autonomy, "by": current_user.user_id, "at": datetime.now(timezone.utc).isoformat()}],
        "now": datetime.now(timezone.utc),
        "pid": project_id,
    })

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "REDUCE_AUTONOMY", body.reason,
        prior_state={"autonomy_level": current_autonomy},
        corrected_state={"autonomy_level": new_autonomy},
        governance_impact={"action": "reduce_autonomy", "from": current_autonomy, "to": new_autonomy, "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "AUTONOMY_REDUCED", f"Autonomy reduced to {new_autonomy} by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="REDUCE_AUTONOMY",
        operator_id=current_user.user_id, reason=body.reason,
        prior_state={"autonomy_level": current_autonomy},
        corrected_state={"autonomy_level": new_autonomy},
        governance_impact={"action": "reduce_autonomy", "from": current_autonomy, "to": new_autonomy},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Autonomy reduced to {new_autonomy} for run {run_id}",
    )


@router.post("/runs/{run_id}/request-human-review", response_model=InterventionResponse)
async def request_human_review(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.request_human_review")),
):
    """Request human review for a run. Requires operations.request_human_review permission."""
    result = await db.execute(text("SELECT status, project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "REQUEST_HUMAN_REVIEW", body.reason,
        prior_state={"status": row[0], "human_review_requested": False},
        corrected_state={"status": row[0], "human_review_requested": True},
        governance_impact={"action": "request_human_review", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "OPERATOR_INTERVENTION_REQUIRED", f"Human review requested by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="REQUEST_HUMAN_REVIEW",
        operator_id=current_user.user_id, reason=body.reason,
        governance_impact={"action": "request_human_review"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Human review requested for run {run_id}",
    )


@router.post("/runs/{run_id}/invalidate-replay", response_model=InterventionResponse)
async def invalidate_replay(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.invalidate_replay")),
):
    """Invalidate replay for a run. Requires operations.invalidate_replay permission."""
    result = await db.execute(text("SELECT project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Mark evidence bundles as invalidated
    await db.execute(text("""
        UPDATE evidence_bundles
        SET chain_hash = 'INVALIDATED:' || COALESCE(chain_hash, 'none'),
            bundle_path = bundle_path || '.invalidated'
        WHERE run_id = :rid
    """), {"rid": run_id})

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "INVALIDATE_REPLAY", body.reason,
        governance_impact={"action": "invalidate_replay", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "REPLAY_INVALID", f"Replay invalidated by {current_user.display_name}: {body.reason}", "error", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="INVALIDATE_REPLAY",
        operator_id=current_user.user_id, reason=body.reason,
        governance_impact={"action": "invalidate_replay"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Replay invalidated for run {run_id}",
    )


@router.post("/runs/{run_id}/lock-evidence", response_model=InterventionResponse)
async def lock_evidence(
    run_id: str,
    body: InterventionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.lock_evidence")),
):
    """Lock evidence for a run. Requires operations.lock_evidence permission."""
    result = await db.execute(text("SELECT project_id FROM runs WHERE id = :rid"), {"rid": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Lock artifacts
    await db.execute(text("""
        UPDATE artifacts SET is_locked = true WHERE run_id = :rid
    """), {"rid": run_id})

    intervention_id = await _create_intervention(
        db, run_id, current_user.user_id, "LOCK_EVIDENCE", body.reason,
        governance_impact={"action": "lock_evidence", "operator": current_user.user_id},
    )

    await db.commit()

    await _publish_intervention_event(run_id, "OPERATOR_INTERVENTION_REQUIRED", f"Evidence locked by {current_user.display_name}: {body.reason}", "warning", current_user.user_id)

    return InterventionResponse(
        id=intervention_id, run_id=run_id, intervention_type="LOCK_EVIDENCE",
        operator_id=current_user.user_id, reason=body.reason,
        governance_impact={"action": "lock_evidence"},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Evidence locked for run {run_id}",
    )


# ── Intervention History ────────────────────────────────────────────────────

@router.get("/interventions")
async def get_intervention_history(
    run_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Get operator intervention history. Requires operations.view permission."""
    try:
        query = "SELECT * FROM operator_interventions WHERE 1=1"
        params: dict = {"limit": limit, "offset": offset}

        if run_id:
            query += " AND run_id = :run_id"
            params["run_id"] = run_id

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        result = await db.execute(text(query), params)
        rows = result.fetchall()

        interventions = []
        for row in rows:
            interventions.append({
                "id": str(row[0]),
                "run_id": str(row[1]) if row[1] else None,
                "project_id": str(row[2]) if row[2] else None,
                "workspace_id": str(row[3]) if row[3] else None,
                "operator_id": str(row[4]) if row[4] else None,
                "intervention_type": row[5],
                "intervention_context": row[6],
                "correction": row[7],
                "prior_state": row[8],
                "corrected_state": row[9],
                "governance_impact": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM operator_interventions WHERE 1=1"
        count_params: dict = {}
        if run_id:
            count_query += " AND run_id = :run_id"
            count_params["run_id"] = run_id
        count_result = await db.execute(text(count_query), count_params)
        total = count_result.scalar() or 0

        return {"interventions": interventions, "total": total, "offset": offset, "limit": limit}
    except Exception as e:
        logger.error(f"Failed to get intervention history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get intervention history: {e}")
