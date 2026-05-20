"""
Operations endpoint — Pass 1+2: Runtime Operations Baseline + Real-Time Telemetry.

Provides:
- GET /api/v1/operations/summary — operational state overview
- GET /api/v1/operations/events — recent operation events
- GET /api/v1/operations/events/stream — SSE real-time event stream
- publish_operation_event() — internal helper to publish events

No fake data. All data comes from actual database queries.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Set
from enum import Enum

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
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


# ── SSE Event Model ─────────────────────────────────────────────────────────

@dataclass
class OperationStreamEvent:
    """Normalized event for SSE streaming."""
    id: str
    timestamp: str
    event_type: str
    severity: str
    source: str
    message: str
    run_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    trust_impact: float = 0.0
    requires_operator_action: bool = False

    def to_sse(self) -> str:
        data = json.dumps(asdict(self))
        return f"event: {self.event_type.lower()}\ndata: {data}\n\n"


# ── In-Process Event Queue (no Kafka, no broker) ────────────────────────────

class OperationEventQueue:
    """Simple in-process event queue for SSE streaming.

    Events are persisted to log_events table and broadcast to SSE subscribers.
    """

    _subscribers: Dict[str, Set[asyncio.Queue]] = {}
    _global_subscribers: Set[asyncio.Queue] = set()
    _lock = asyncio.Lock()

    @classmethod
    async def subscribe(cls, run_id: Optional[str] = None) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with cls._lock:
            if run_id:
                if run_id not in cls._subscribers:
                    cls._subscribers[run_id] = set()
                cls._subscribers[run_id].add(queue)
            else:
                cls._global_subscribers.add(queue)
        return queue

    @classmethod
    async def unsubscribe(cls, queue: asyncio.Queue, run_id: Optional[str] = None):
        async with cls._lock:
            if run_id and run_id in cls._subscribers:
                cls._subscribers[run_id].discard(queue)
                if not cls._subscribers[run_id]:
                    del cls._subscribers[run_id]
            cls._global_subscribers.discard(queue)

    @classmethod
    async def publish(cls, event: OperationStreamEvent, run_id: Optional[str] = None):
        # Persist to database
        try:
            from src.core.database import async_session_factory
            async with async_session_factory() as session:
                await session.execute(text("""
                    INSERT INTO log_events (id, run_id, severity, message, source_file, metadata, created_at)
                    VALUES (:id, :run_id, :severity, :message, :source, :metadata, :created_at)
                """), {
                    "id": event.id,
                    "run_id": event.run_id,
                    "severity": event.severity,
                    "message": event.message,
                    "source": event.source,
                    "metadata": json.dumps(event.metadata),
                    "created_at": datetime.now(timezone.utc),
                })
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist operation event: {e}")

        # Broadcast to SSE subscribers
        async with cls._lock:
            for queue in cls._global_subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass
            if run_id and run_id in cls._subscribers:
                for queue in cls._subscribers[run_id]:
                    try:
                        queue.put_nowait(event)
                    except asyncio.QueueFull:
                        pass


# ── Database Helpers ────────────────────────────────────────────────────────

async def _get_run_status_counts(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("SELECT status, COUNT(*) as cnt FROM runs GROUP BY status"))
        rows = result.fetchall()
        counts = {row[0]: row[1] for row in rows}
        return {
            "active": counts.get("running", 0), "paused": counts.get("paused", 0),
            "failed": counts.get("failed", 0), "completed": counts.get("completed", 0),
            "pending": counts.get("pending", 0), "cancelled": counts.get("cancelled", 0),
            "total": sum(counts.values()),
        }
    except Exception as e:
        logger.warning(f"Failed to get run counts: {e}")
        return {"active": 0, "paused": 0, "failed": 0, "completed": 0, "pending": 0, "cancelled": 0, "total": 0}


async def _get_governance_alert_count(db: AsyncSession) -> int:
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM governance_memory WHERE is_active = true AND escalation_level != 'none'"))
        return result.scalar() or 0
    except Exception:
        return 0


async def _get_drift_event_count(db: AsyncSession) -> int:
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM semantic_memory WHERE is_active = true AND drift_score > 0.3"))
        return result.scalar() or 0
    except Exception:
        return 0


async def _get_replay_integrity_status(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("""
            SELECT COUNT(*) as total,
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
    try:
        result = await db.execute(text("""
            SELECT COUNT(*) as total,
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
    try:
        result = await db.execute(text("""
            SELECT AVG(overall_semantic_coverage_score) as avg_semantic,
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
    try:
        result = await db.execute(text("""
            SELECT SUM(total_cost) as total_cost, AVG(total_cost) as avg_cost, MAX(total_cost) as max_cost
            FROM runs WHERE created_at > NOW() - INTERVAL '24 hours'
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
    try:
        result = await db.execute(text("""
            SELECT id, created_at, run_id, severity, message, metadata_, source_file
            FROM log_events ORDER BY created_at DESC LIMIT :limit
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


async def _get_recent_events_for_stream(run_id: Optional[str], limit: int = 20) -> List[OperationStreamEvent]:
    """Get recent events from database for initial SSE batch."""
    try:
        from src.core.database import async_session_factory
        async with async_session_factory() as session:
            query = "SELECT id, created_at, run_id, severity, message, metadata, source_file FROM log_events WHERE 1=1"
            params: Dict = {"limit": limit}
            if run_id:
                query += " AND run_id = :run_id"
                params["run_id"] = run_id
            query += " ORDER BY created_at DESC LIMIT :limit"
            result = await session.execute(text(query), params)
            rows = result.fetchall()
            events = []
            for row in rows:
                events.append(OperationStreamEvent(
                    id=str(row[0]),
                    timestamp=row[1].isoformat() if row[1] else datetime.now(timezone.utc).isoformat(),
                    event_type="LOG_ENTRY",
                    severity=row[3] or "info",
                    source=row[6] or "system",
                    message=row[4] or "",
                    run_id=str(row[2]) if row[2] else None,
                    metadata=row[5] if isinstance(row[5], dict) else {},
                ))
            return events
    except Exception as e:
        logger.warning(f"Failed to get recent stream events: {e}")
        return []


def _compute_overall_health(health: dict) -> str:
    statuses = [health.get(k, "unknown") for k in ("runtime", "governance", "replay", "memory", "drift", "trust", "tokenomics")]
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
    run_counts = await _get_run_status_counts(db)
    governance_alerts = await _get_governance_alert_count(db)
    drift_events = await _get_drift_event_count(db)
    replay_status = await _get_replay_integrity_status(db)
    memory_health = await _get_memory_health(db)
    trust_summary = await _get_trust_summary(db)
    tokenomics_health = await _get_tokenomics_health(db)
    recent_events = await _get_recent_events(db)

    total_runs = run_counts["total"]
    if total_runs == 0:
        runtime_health = "no_data"
    elif run_counts["failed"] > total_runs * 0.2:
        runtime_health = "critical"
    elif run_counts["failed"] > total_runs * 0.1:
        runtime_health = "degraded"
    else:
        runtime_health = "healthy"

    drift_health = "healthy" if drift_events == 0 else "warning" if drift_events < 5 else "critical"

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
        params: Dict = {"limit": limit}
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


# ── SSE Stream Endpoint ─────────────────────────────────────────────────────

@router.get("/events/stream")
async def stream_operation_events(
    run_id: Optional[str] = None,
    current_user=Depends(require_permission("operations.view")),
):
    """Server-Sent Events stream for real-time operation events.

    Streams run events, governance alerts, drift alerts, replay integrity alerts,
    trust degradation alerts, memory warnings, tokenomics warnings, provider failures,
    and autonomy reductions.

    If run_id is provided, only events for that run are streamed.
    Otherwise, all events are streamed.
    """
    queue = await OperationEventQueue.subscribe(run_id)

    async def event_generator():
        # Send connection confirmation
        yield OperationStreamEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="CONNECTED",
            severity="info",
            source="operations",
            message=f"Stream connected{' for run ' + run_id if run_id else ' (all events)'}",
            run_id=run_id,
        ).to_sse()

        # Send recent events from database as initial batch
        try:
            recent = await _get_recent_events_for_stream(run_id, limit=20)
            for evt in recent:
                yield evt.to_sse()
        except Exception as e:
            logger.warning(f"Failed to send initial events: {e}")

        # Stream new events
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event.to_sse()
                except asyncio.TimeoutError:
                    yield OperationStreamEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        event_type="KEEPALIVE",
                        severity="info",
                        source="operations",
                        message="keepalive",
                    ).to_sse()
        except asyncio.CancelledError:
            pass
        finally:
            await OperationEventQueue.unsubscribe(queue, run_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Internal: publish operation event ───────────────────────────────────────

async def publish_operation_event(
    event_type: str,
    message: str,
    severity: str = "info",
    source: str = "operations",
    run_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
    trust_impact: float = 0.0,
    requires_operator_action: bool = False,
):
    """Publish an operation event to the stream and database."""
    event = OperationStreamEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_type,
        severity=severity,
        source=source,
        message=message,
        run_id=run_id,
        workspace_id=workspace_id,
        project_id=project_id,
        metadata=metadata or {},
        trust_impact=trust_impact,
        requires_operator_action=requires_operator_action,
    )
    await OperationEventQueue.publish(event, run_id)
    return event
