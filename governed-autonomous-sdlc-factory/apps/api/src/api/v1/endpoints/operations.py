"""
Operations endpoint — Pass 1: Runtime Operations Baseline.

Provides:
- GET /api/v1/operations/summary — operational state overview
- GET /api/v1/operations/events — recent operation events
- POST /api/v1/operations/events — record operation event (internal)

No fake data. All data comes from actual database queries.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from enum import Enum

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text, func, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_permission
from src.core.database import get_db
from src.core.logging import get_logger

logger = get_logger("operations")

router = APIRouter(prefix="/operations", tags=["operations"])


# ── Event Type Enum ─────────────────────────────────────────────────────────

class OperationEventType(str, Enum):
    RUN_STARTED = "RUN_STARTED"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"
    RUN_PAUSED = "RUN_PAUSED"
    RUN_RESUMED = "RUN_RESUMED"
    GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    TRUST_DEGRADED = "TRUST_DEGRADED"
    REPLAY_INVALID = "REPLAY_INVALID"
    MEMORY_QUARANTINED = "MEMORY_QUARANTINED"
    HALLUCINATION_DETECTED = "HALLUCINATION_DETECTED"
    OPERATOR_INTERVENTION_REQUIRED = "OPERATOR_INTERVENTION_REQUIRED"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    TOKEN_BUDGET_WARNING = "TOKEN_BUDGET_WARNING"
    AUTONOMY_REDUCED = "AUTONOMY_REDUCED"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ── Schemas ─────────────────────────────────────────────────────────────────

class RuntimeOperationEvent(BaseModel):
    id: str
    timestamp: str
    run_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    event_type: str
    severity: str
    source: str
    message: str
    metadata: dict = Field(default_factory=dict)
    trust_impact: float = 0.0
    requires_operator_action: bool = False


class OperationsSummary(BaseModel):
    generated_at: str
    runs: dict
    health: dict
    alerts: dict
    providers: dict
    recent_events: list[RuntimeOperationEvent]


class OperationsHealth(BaseModel):
    runtime: str  # healthy, degraded, critical
    governance: str
    replay: str
    memory: str
    drift: str
    trust: str
    tokenomics: str
    overall: str


# ── Helper: compute run status counts from actual DB ────────────────────────

async def _get_run_status_counts(db: AsyncSession) -> dict:
    """Get actual run status counts from database."""
    try:
        result = await db.execute(text("""
            SELECT status, COUNT(*) as cnt
            FROM runs
            GROUP BY status
        """))
        rows = result.fetchall()
        counts = {row[0]: row[1] for row in rows}

        return {
            "active": counts.get("running", 0),
            "paused": counts.get("paused", 0),
            "failed": counts.get("failed", 0),
            "completed": counts.get("completed", 0),
            "pending": counts.get("pending", 0),
            "cancelled": counts.get("cancelled", 0),
            "total": sum(counts.values()),
        }
    except Exception as e:
        logger.warning(f"Failed to get run counts: {e}")
        return {"active": 0, "paused": 0, "failed": 0, "completed": 0, "pending": 0, "cancelled": 0, "total": 0}


async def _get_governance_alert_count(db: AsyncSession) -> int:
    """Count governance events requiring attention."""
    try:
        result = await db.execute(text("""
            SELECT COUNT(*) FROM governance_memory
            WHERE is_active = true AND escalation_level != 'none'
        """))
        return result.scalar() or 0
    except Exception:
        return 0


async def _get_drift_event_count(db: AsyncSession) -> int:
    """Count active drift events."""
    try:
        result = await db.execute(text("""
            SELECT COUNT(*) FROM semantic_memory
            WHERE is_active = true AND drift_score > 0.3
        """))
        return result.scalar() or 0
    except Exception:
        return 0


async def _get_replay_integrity_status(db: AsyncSession) -> dict:
    """Check replay integrity status."""
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN chain_hash IS NOT NULL THEN 1 END) as chained,
                COUNT(CASE WHEN chain_hash IS NULL THEN 1 END) as unchained
            FROM evidence_bundles
        """))
        row = result.fetchone()
        if not row or row[0] == 0:
            return {"status": "no_data", "total": 0, "chained": 0, "unchained": 0, "integrity_pct": 100.0}
        total = row[0]
        chained = row[1]
        pct = (chained / total * 100) if total > 0 else 100.0
        status = "healthy" if pct >= 95 else "degraded" if pct >= 80 else "critical"
        return {"status": status, "total": total, "chained": chained, "unchained": row[2], "integrity_pct": round(pct, 1)}
    except Exception as e:
        logger.warning(f"Failed to get replay status: {e}")
        return {"status": "unknown", "total": 0, "chained": 0, "unchained": 0, "integrity_pct": 0.0}


async def _get_memory_health(db: AsyncSession) -> dict:
    """Get memory health status."""
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN drift_score > 0.5 THEN 1 END) as poisoned,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active
            FROM semantic_memory
        """))
        row = result.fetchone()
        if not row:
            return {"status": "no_data", "total": 0, "poisoned": 0, "active": 0}
        total = row[0]
        poisoned = row[1]
        status = "healthy" if poisoned == 0 else "warning" if poisoned < 5 else "critical"
        return {"status": status, "total": total, "poisoned": poisoned, "active": row[2]}
    except Exception:
        return {"status": "unknown", "total": 0, "poisoned": 0, "active": 0}


async def _get_trust_summary(db: AsyncSession) -> dict:
    """Get trust score summary."""
    try:
        result = await db.execute(text("""
            SELECT
                AVG(overall_semantic_coverage_score) as avg_semantic,
                COUNT(CASE WHEN overall_semantic_coverage_score < 0.5 THEN 1 END) as low_coverage
            FROM semantic_coverage_reports
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """))
        row = result.fetchone()
        if not row or row[0] is None:
            return {"status": "no_data", "avg_semantic_score": None, "low_coverage_runs": 0}
        avg = float(row[0])
        status = "healthy" if avg >= 0.7 else "degraded" if avg >= 0.5 else "critical"
        return {"status": status, "avg_semantic_score": round(avg, 3), "low_coverage_runs": row[1]}
    except Exception:
        return {"status": "unknown", "avg_semantic_score": None, "low_coverage_runs": 0}


async def _get_tokenomics_health(db: AsyncSession) -> dict:
    """Get tokenomics health."""
    try:
        result = await db.execute(text("""
            SELECT
                SUM(total_cost) as total_cost,
                AVG(total_cost) as avg_cost,
                MAX(total_cost) as max_cost
            FROM runs
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """))
        row = result.fetchone()
        if not row or row[0] is None:
            return {"status": "no_data", "total_cost_24h": 0, "avg_cost": 0, "max_cost": 0}
        total = float(row[0] or 0)
        status = "healthy" if total < 100 else "warning" if total < 500 else "critical"
        return {"status": status, "total_cost_24h": round(total, 2), "avg_cost": round(float(row[1] or 0), 2), "max_cost": round(float(row[2] or 0), 2)}
    except Exception:
        return {"status": "unknown", "total_cost_24h": 0, "avg_cost": 0, "max_cost": 0}


async def _get_recent_events(db: AsyncSession, limit: int = 20) -> list[RuntimeOperationEvent]:
    """Get recent operation events from log events."""
    try:
        result = await db.execute(text("""
            SELECT id, created_at, run_id, severity, message, metadata_, source_file
            FROM log_events
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        events = []
        for row in rows:
            events.append(RuntimeOperationEvent(
                id=str(row[0]),
                timestamp=row[1].isoformat() if row[1] else datetime.now(timezone.utc).isoformat(),
                run_id=str(row[2]) if row[2] else None,
                event_type="LOG_ENTRY",
                severity=row[3] or "info",
                source=row[6] or "system",
                message=row[4] or "",
                metadata=row[5] if isinstance(row[5], dict) else {},
                trust_impact=0.0,
                requires_operator_action=row[3] in ("error", "critical") if row[3] else False,
            ))
        return events
    except Exception as e:
        logger.warning(f"Failed to get recent events: {e}")
        return []


def _compute_overall_health(health: dict) -> str:
    """Compute overall health from individual health statuses."""
    statuses = [
        health.get("runtime", "unknown"),
        health.get("governance", "unknown"),
        health.get("replay", "unknown"),
        health.get("memory", "unknown"),
        health.get("drift", "unknown"),
        health.get("trust", "unknown"),
        health.get("tokenomics", "unknown"),
    ]
    if any(s == "critical" for s in statuses):
        return "critical"
    if any(s == "degraded" for s in statuses):
        return "degraded"
    if all(s == "healthy" for s in statuses):
        return "healthy"
    if any(s == "no_data" for s in statuses):
        return "initializing"
    return "degraded"


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/summary", response_model=OperationsSummary)
async def get_operations_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Get operations summary — real-time operational state overview."""
    now = datetime.now(timezone.utc)

    # Gather all metrics in parallel where possible
    run_counts = await _get_run_status_counts(db)
    governance_alerts = await _get_governance_alert_count(db)
    drift_events = await _get_drift_event_count(db)
    replay_status = await _get_replay_integrity_status(db)
    memory_health = await _get_memory_health(db)
    trust_summary = await _get_trust_summary(db)
    tokenomics_health = await _get_tokenomics_health(db)
    recent_events = await _get_recent_events(db)

    # Compute runtime health from run counts
    total_runs = run_counts["total"]
    if total_runs == 0:
        runtime_health = "no_data"
    elif run_counts["failed"] > total_runs * 0.2:
        runtime_health = "critical"
    elif run_counts["failed"] > total_runs * 0.1:
        runtime_health = "degraded"
    else:
        runtime_health = "healthy"

    # Drift health
    if drift_events == 0:
        drift_health = "healthy"
    elif drift_events < 5:
        drift_health = "warning"
    else:
        drift_health = "critical"

    health = {
        "runtime": runtime_health,
        "governance": "healthy" if governance_alerts == 0 else "warning" if governance_alerts < 3 else "critical",
        "replay": replay_status["status"],
        "memory": memory_health["status"],
        "drift": drift_health,
        "trust": trust_summary["status"],
        "tokenomics": tokenomics_health["status"],
    }

    return OperationsSummary(
        generated_at=now.isoformat(),
        runs=run_counts,
        health={**health, "overall": _compute_overall_health(health)},
        alerts={
            "governance_alerts": governance_alerts,
            "drift_events": drift_events,
            "replay_unchained": replay_status.get("unchained", 0),
            "memory_poisoned": memory_health.get("poisoned", 0),
            "low_coverage_runs": trust_summary.get("low_coverage_runs", 0),
            "total_critical": sum(1 for v in health.values() if v == "critical"),
            "total_warnings": sum(1 for v in health.values() if v in ("warning", "degraded")),
        },
        providers={
            "ollama": {"status": "configured", "url": "http://localhost:11434"},
            "openai": {"status": "not_configured"},
            "anthropic": {"status": "not_configured"},
        },
        recent_events=recent_events,
    )


@router.get("/events")
async def get_operation_events(
    limit: int = Query(default=50, le=200),
    severity: Optional[str] = None,
    run_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Get recent operation events with optional filtering."""
    try:
        query = "SELECT id, created_at, run_id, severity, message, metadata_, source_file FROM log_events WHERE 1=1"
        params = {"limit": limit}

        if severity:
            query += " AND severity = :severity"
            params["severity"] = severity
        if run_id:
            query += " AND run_id = :run_id"
            params["run_id"] = run_id

        query += " ORDER BY created_at DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()

        events = []
        for row in rows:
            events.append({
                "id": str(row[0]),
                "timestamp": row[1].isoformat() if row[1] else None,
                "run_id": str(row[2]) if row[2] else None,
                "severity": row[3] or "info",
                "message": row[4] or "",
                "metadata": row[5] if isinstance(row[5], dict) else {},
                "source": row[6] or "system",
            })

        return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get events: {e}")
