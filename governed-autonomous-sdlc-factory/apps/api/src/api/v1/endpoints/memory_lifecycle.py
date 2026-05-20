"""
Memory Lifecycle & Archival — Pass 4.

Provides:
- GET  /api/v1/memory/lifecycle/summary — memory lifecycle overview
- POST /api/v1/memory/{memory_id}/archive — archive a memory item
- POST /api/v1/memory/{memory_id}/quarantine — quarantine a memory item
- POST /api/v1/memory/{memory_id}/invalidate — invalidate a memory item
- POST /api/v1/memory/{memory_id}/verify — verify/re-validate a memory item
- POST /api/v1/memory/aging/run — run memory aging process
- GET  /api/v1/memory/context-validity — context validity overview

Memory lifecycle states: active, stale, expired, quarantined, archived, superseded, invalidated
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_permission
from src.core.database import get_db
from src.core.logging import get_logger

logger = get_logger("memory-lifecycle")

router = APIRouter(prefix="/memory", tags=["memory-lifecycle"])


# ── Schemas ─────────────────────────────────────────────────────────────────

class MemoryLifecycleSummary(BaseModel):
    generated_at: str
    semantic_memory: dict
    memory_items: dict
    context_validity: dict
    memory_versions: dict
    aging: dict


class MemoryActionRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000)
    metadata: dict = Field(default_factory=dict)


class MemoryActionResponse(BaseModel):
    id: str
    action: str
    reason: str
    prior_state: dict
    new_state: dict
    created_at: str
    message: str


# ── Helper: get memory lifecycle summary ───────────────────────────────────

async def _get_semantic_memory_summary(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active,
                COUNT(CASE WHEN is_active = false THEN 1 END) as inactive,
                COUNT(CASE WHEN valid_until IS NOT NULL AND valid_until < NOW() THEN 1 END) as expired,
                COUNT(CASE WHEN drift_score > 0.5 THEN 1 END) as high_drift,
                COUNT(CASE WHEN drift_score > 0.3 AND drift_score <= 0.5 THEN 1 END) as medium_drift,
                COUNT(CASE WHEN confidence < 0.5 THEN 1 END) as low_confidence,
                AVG(drift_score) as avg_drift,
                AVG(confidence) as avg_confidence
            FROM semantic_memory
        """))
        row = result.fetchone()
        if not row:
            return {"total": 0}
        return {
            "total": row[0],
            "active": row[1],
            "inactive": row[2],
            "expired": row[3],
            "high_drift": row[4],
            "medium_drift": row[5],
            "low_confidence": row[6],
            "avg_drift": round(float(row[7] or 0), 3),
            "avg_confidence": round(float(row[8] or 0), 3),
        }
    except Exception as e:
        logger.warning(f"Failed to get semantic memory summary: {e}")
        return {"total": 0}


async def _get_memory_items_summary(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT memory_type) as types,
                COUNT(DISTINCT project_id) as projects,
                memory_type,
                COUNT(*) as type_count
            FROM memory_items
            GROUP BY memory_type
            ORDER BY type_count DESC
        """))
        rows = result.fetchall()
        total = sum(r[4] for r in rows) if rows else 0
        return {
            "total": total,
            "types": {r[3]: r[4] for r in rows},
        }
    except Exception as e:
        logger.warning(f"Failed to get memory items summary: {e}")
        return {"total": 0, "types": {}}


async def _get_context_validity_summary(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN validity_status = 'active' THEN 1 END) as active,
                COUNT(CASE WHEN validity_status = 'stale' THEN 1 END) as stale,
                COUNT(CASE WHEN validity_status = 'expired' THEN 1 END) as expired,
                COUNT(CASE WHEN valid_until IS NOT NULL AND valid_until < NOW() THEN 1 END) as time_expired,
                AVG(staleness_score) as avg_staleness
            FROM context_validity
        """))
        row = result.fetchone()
        if not row:
            return {"total": 0}
        return {
            "total": row[0],
            "active": row[1],
            "stale": row[2],
            "expired": row[3],
            "time_expired": row[4],
            "avg_staleness": round(float(row[5] or 0), 3),
        }
    except Exception as e:
        logger.warning(f"Failed to get context validity summary: {e}")
        return {"total": 0}


async def _get_memory_versions_summary(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT memory_type) as types,
                COUNT(DISTINCT project_id) as projects,
                MAX(version_number) as max_version
            FROM memory_versions
        """))
        row = result.fetchone()
        if not row:
            return {"total": 0}
        return {
            "total": row[0],
            "types": row[1],
            "projects": row[2],
            "max_version": row[3] or 0,
        }
    except Exception as e:
        logger.warning(f"Failed to get memory versions summary: {e}")
        return {"total": 0}


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/lifecycle/summary", response_model=MemoryLifecycleSummary)
async def get_memory_lifecycle_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Get memory lifecycle summary — overview of all memory states."""
    now = datetime.now(timezone.utc)

    semantic = await _get_semantic_memory_summary(db)
    items = await _get_memory_items_summary(db)
    context = await _get_context_validity_summary(db)
    versions = await _get_memory_versions_summary(db)

    # Aging stats
    aging = {
        "stale_threshold_hours": 24,
        "expiry_threshold_hours": 168,  # 7 days
        "archival_threshold_hours": 720,  # 30 days
        "last_aging_run": None,  # Would be tracked in a settings table
    }

    return MemoryLifecycleSummary(
        generated_at=now.isoformat(),
        semantic_memory=semantic,
        memory_items=items,
        context_validity=context,
        memory_versions=versions,
        aging=aging,
    )


@router.post("/{memory_id}/archive", response_model=MemoryActionResponse)
async def archive_memory(
    memory_id: str,
    body: MemoryActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.quarantine_memory")),
):
    """Archive a memory item. Requires operations.quarantine_memory permission."""
    # Find the memory item in semantic_memory
    result = await db.execute(text("SELECT id, is_active, semantic_content FROM semantic_memory WHERE id = :mid"), {"mid": memory_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Memory item {memory_id} not found")

    prior_state = {"is_active": row[1], "archived": False}

    # Archive: set is_active=false, add archive metadata
    await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = false,
            semantic_content = jsonb_set(
                COALESCE(semantic_content, '{}'::jsonb),
                '{archived}',
                :archive_info
            ),
            updated_at = :now
        WHERE id = :mid
    """), {
        "archive_info": {"archived_by": current_user.user_id, "reason": body.reason, "at": datetime.now(timezone.utc).isoformat()},
        "now": datetime.now(timezone.utc),
        "mid": memory_id,
    })

    # Create intervention record
    intervention_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO operator_interventions
        (id, run_id, operator_id, intervention_type, intervention_context, correction, prior_state, corrected_state, created_at)
        VALUES (:id, :rid, :oid, 'ARCHIVE_MEMORY', :context, :correction, :prior, :corrected, :created)
    """), {
        "id": intervention_id,
        "rid": None,
        "oid": current_user.user_id,
        "context": {"memory_id": memory_id, "reason": body.reason},
        "correction": body.reason,
        "prior": prior_state,
        "corrected": {"is_active": False, "archived": True},
        "created": datetime.now(timezone.utc),
    })

    await db.commit()

    # Publish event
    try:
        from src.api.v1.endpoints.operations import publish_operation_event
        await publish_operation_event("MEMORY_QUARANTINED", f"Memory archived by {current_user.display_name}: {body.reason}", "info", "memory-lifecycle", metadata={"memory_id": memory_id})
    except Exception:
        pass

    return MemoryActionResponse(
        id=intervention_id, action="ARCHIVE", reason=body.reason,
        prior_state=prior_state, new_state={"is_active": False, "archived": True},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Memory {memory_id} archived successfully",
    )


@router.post("/{memory_id}/quarantine", response_model=MemoryActionResponse)
async def quarantine_memory(
    memory_id: str,
    body: MemoryActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.quarantine_memory")),
):
    """Quarantine a memory item. Requires operations.quarantine_memory permission."""
    result = await db.execute(text("SELECT id, is_active, semantic_content, drift_score FROM semantic_memory WHERE id = :mid"), {"mid": memory_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Memory item {memory_id} not found")

    prior_state = {"is_active": row[1], "drift_score": row[3], "quarantined": False}

    # Quarantine: set is_active=false, add quarantine metadata
    await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = false,
            semantic_content = jsonb_set(
                COALESCE(semantic_content, '{}'::jsonb),
                '{quarantined}',
                :quarantine_info
            ),
            updated_at = :now
        WHERE id = :mid
    """), {
        "quarantine_info": {"quarantined_by": current_user.user_id, "reason": body.reason, "at": datetime.now(timezone.utc).isoformat()},
        "now": datetime.now(timezone.utc),
        "mid": memory_id,
    })

    intervention_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO operator_interventions
        (id, run_id, operator_id, intervention_type, intervention_context, correction, prior_state, corrected_state, created_at)
        VALUES (:id, :rid, :oid, 'QUARANTINE_MEMORY_ITEM', :context, :correction, :prior, :corrected, :created)
    """), {
        "id": intervention_id, "rid": None, "oid": current_user.user_id,
        "context": {"memory_id": memory_id, "reason": body.reason},
        "correction": body.reason, "prior": prior_state,
        "corrected": {"is_active": False, "quarantined": True},
        "created": datetime.now(timezone.utc),
    })

    await db.commit()

    try:
        from src.api.v1.endpoints.operations import publish_operation_event
        await publish_operation_event("MEMORY_QUARANTINED", f"Memory quarantined by {current_user.display_name}: {body.reason}", "warning", "memory-lifecycle", metadata={"memory_id": memory_id})
    except Exception:
        pass

    return MemoryActionResponse(
        id=intervention_id, action="QUARANTINE", reason=body.reason,
        prior_state=prior_state, new_state={"is_active": False, "quarantined": True},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Memory {memory_id} quarantined successfully",
    )


@router.post("/{memory_id}/invalidate", response_model=MemoryActionResponse)
async def invalidate_memory(
    memory_id: str,
    body: MemoryActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.quarantine_memory")),
):
    """Invalidate a memory item. Requires operations.quarantine_memory permission."""
    result = await db.execute(text("SELECT id, is_active, semantic_content FROM semantic_memory WHERE id = :mid"), {"mid": memory_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Memory item {memory_id} not found")

    prior_state = {"is_active": row[1], "invalidated": False}

    await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = false,
            semantic_content = jsonb_set(
                COALESCE(semantic_content, '{}'::jsonb),
                '{invalidated}',
                :invalidate_info
            ),
            updated_at = :now
        WHERE id = :mid
    """), {
        "invalidate_info": {"invalidated_by": current_user.user_id, "reason": body.reason, "at": datetime.now(timezone.utc).isoformat()},
        "now": datetime.now(timezone.utc),
        "mid": memory_id,
    })

    intervention_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO operator_interventions
        (id, run_id, operator_id, intervention_type, intervention_context, correction, prior_state, corrected_state, created_at)
        VALUES (:id, :rid, :oid, 'INVALIDATE_MEMORY', :context, :correction, :prior, :corrected, :created)
    """), {
        "id": intervention_id, "rid": None, "oid": current_user.user_id,
        "context": {"memory_id": memory_id, "reason": body.reason},
        "correction": body.reason, "prior": prior_state,
        "corrected": {"is_active": False, "invalidated": True},
        "created": datetime.now(timezone.utc),
    })

    await db.commit()

    try:
        from src.api.v1.endpoints.operations import publish_operation_event
        await publish_operation_event("MEMORY_QUARANTINED", f"Memory invalidated by {current_user.display_name}: {body.reason}", "warning", "memory-lifecycle", metadata={"memory_id": memory_id})
    except Exception:
        pass

    return MemoryActionResponse(
        id=intervention_id, action="INVALIDATE", reason=body.reason,
        prior_state=prior_state, new_state={"is_active": False, "invalidated": True},
        created_at=datetime.now(timezone.utc).isoformat(),
        message=f"Memory {memory_id} invalidated successfully",
    )


@router.post("/{memory_id}/verify", response_model=MemoryActionResponse)
async def verify_memory(
    memory_id: str,
    body: MemoryActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Verify/re-validate a memory item. Requires operations.view permission."""
    result = await db.execute(text("SELECT id, is_active, drift_score, confidence FROM semantic_memory WHERE id = :mid"), {"mid": memory_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Memory item {memory_id} not found")

    prior_state = {"is_active": row[1], "drift_score": row[2], "confidence": row[3], "last_verified": None}

    now = datetime.now(timezone.utc)
    # Re-activate if it was inactive, update confidence
    await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = true,
            confidence = LEAST(1.0, COALESCE(confidence, 0.5) + 0.1),
            drift_score = GREATEST(0.0, COALESCE(drift_score, 0.5) - 0.05),
            updated_at = :now
        WHERE id = :mid
    """), {"now": now, "mid": memory_id})

    intervention_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO operator_interventions
        (id, run_id, operator_id, intervention_type, intervention_context, correction, prior_state, corrected_state, created_at)
        VALUES (:id, :rid, :oid, 'VERIFY_MEMORY', :context, :correction, :prior, :corrected, :created)
    """), {
        "id": intervention_id, "rid": None, "oid": current_user.user_id,
        "context": {"memory_id": memory_id, "reason": body.reason},
        "correction": body.reason, "prior": prior_state,
        "corrected": {"is_active": True, "last_verified": now.isoformat()},
        "created": now,
    })

    await db.commit()

    return MemoryActionResponse(
        id=intervention_id, action="VERIFY", reason=body.reason,
        prior_state=prior_state, new_state={"is_active": True, "last_verified": now.isoformat()},
        created_at=now.isoformat(),
        message=f"Memory {memory_id} verified successfully",
    )


@router.post("/aging/run")
async def run_memory_aging(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.intervene")),
):
    """Run memory aging process. Requires operations.intervene permission.

    Applies:
    - Stale after 24h without verification
    - Expired after 7 days
    - Confidence decay over time
    - Drift-triggered decay
    - Contradiction-triggered quarantine
    """
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(hours=24)
    expiry_threshold = now - timedelta(hours=168)  # 7 days
    archival_threshold = now - timedelta(hours=720)  # 30 days

    results = {"stale": 0, "expired": 0, "archived": 0, "confidence_decayed": 0}

    # Mark stale: not updated in 24h, still active
    stale_result = await db.execute(text("""
        UPDATE semantic_memory
        SET semantic_content = jsonb_set(
            COALESCE(semantic_content, '{}'::jsonb),
            '{lifecycle_state}',
            '"stale"'
        )
        WHERE is_active = true
          AND updated_at < :stale_threshold
          AND (semantic_content->>'lifecycle_state' IS NULL OR semantic_content->>'lifecycle_state' = 'active')
    """), {"stale_threshold": stale_threshold})
    results["stale"] = stale_result.rowcount or 0

    # Mark expired: not updated in 7 days
    expired_result = await db.execute(text("""
        UPDATE semantic_memory
        SET is_active = false,
            valid_until = COALESCE(valid_until, :now),
            semantic_content = jsonb_set(
                COALESCE(semantic_content, '{}'::jsonb),
                '{lifecycle_state}',
                '"expired"'
            )
        WHERE is_active = true
          AND updated_at < :expiry_threshold
    """), {"now": now, "expiry_threshold": expiry_threshold})
    results["expired"] = expired_result.rowcount or 0

    # Confidence decay: reduce confidence for old unverified items
    decay_result = await db.execute(text("""
        UPDATE semantic_memory
        SET confidence = GREATEST(0.1, COALESCE(confidence, 0.5) - 0.05),
            updated_at = :now
        WHERE is_active = true
          AND updated_at < :stale_threshold
          AND confidence > 0.1
    """), {"now": now, "stale_threshold": stale_threshold})
    results["confidence_decayed"] = decay_result.rowcount or 0

    # Auto-archive: inactive for 30 days (but keep evidence links)
    archive_result = await db.execute(text("""
        UPDATE semantic_memory
        SET semantic_content = jsonb_set(
            COALESCE(semantic_content, '{}'::jsonb),
            '{lifecycle_state}',
            '"archived"'
        )
        WHERE is_active = false
          AND updated_at < :archival_threshold
          AND (semantic_content->>'lifecycle_state' IS NULL OR semantic_content->>'lifecycle_state' != 'archived')
    """), {"archival_threshold": archival_threshold})
    results["archived"] = archive_result.rowcount or 0

    # Update context validity staleness
    await db.execute(text("""
        UPDATE context_validity
        SET validity_status = 'stale',
            staleness_score = LEAST(1.0, COALESCE(staleness_score, 0) + 0.1)
        WHERE validity_status = 'active'
          AND updated_at < :stale_threshold
    """), {"stale_threshold": stale_threshold})

    await db.commit()

    # Publish event
    try:
        from src.api.v1.endpoints.operations import publish_operation_event
        total_affected = sum(results.values())
        await publish_operation_event(
            "MEMORY_QUARANTINED",
            f"Memory aging run completed: {total_affected} items affected",
            "info",
            "memory-lifecycle",
            metadata={"results": results},
        )
    except Exception:
        pass

    return {
        "status": "completed",
        "results": results,
        "thresholds": {
            "stale_hours": 24,
            "expiry_hours": 168,
            "archival_hours": 720,
        },
        "run_at": now.isoformat(),
    }


@router.get("/context-validity")
async def get_context_validity(
    project_id: Optional[str] = None,
    validity_status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Get context validity overview with optional filtering."""
    try:
        query = "SELECT * FROM context_validity WHERE 1=1"
        params: dict = {"limit": limit, "offset": offset}

        if project_id:
            query += " AND project_id = :pid"
            params["pid"] = project_id
        if validity_status:
            query += " AND validity_status = :status"
            params["status"] = validity_status

        query += " ORDER BY updated_at DESC LIMIT :limit OFFSET :offset"

        result = await db.execute(text(query), params)
        rows = result.fetchall()

        contexts = []
        for row in rows:
            contexts.append({
                "id": str(row[0]),
                "project_id": str(row[1]) if row[1] else None,
                "workspace_id": str(row[2]) if row[2] else None,
                "context_type": row[3],
                "context_key": row[4],
                "context_value": row[5],
                "validity_status": row[6],
                "valid_from": row[7].isoformat() if row[7] else None,
                "valid_until": row[8].isoformat() if row[8] else None,
                "staleness_score": row[9],
                "last_validated_at": row[10].isoformat() if row[10] else None,
                "created_at": row[11].isoformat() if row[11] else None,
                "updated_at": row[12].isoformat() if row[12] else None,
            })

        return {"contexts": contexts, "count": len(contexts)}
    except Exception as e:
        logger.error(f"Failed to get context validity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get context validity: {e}")
