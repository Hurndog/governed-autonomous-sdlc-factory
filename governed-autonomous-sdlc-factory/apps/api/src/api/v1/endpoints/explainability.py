"""
Runtime Explainability Engine — Pass 5.

Provides human-comprehensible cognitive runtime narratives.
All explanations are grounded in actual database records.

Endpoints:
- GET /api/v1/explain/runtime/{run_id} — full runtime explanation
- GET /api/v1/explain/trust/{run_id} — trust evolution narrative
- GET /api/v1/explain/drift/{run_id} — drift lineage narrative
- GET /api/v1/explain/replay/{run_id} — replay integrity narrative
- GET /api/v1/explain/governance/{run_id} — governance rationale narrative
- GET /api/v1/explain/memory/{run_id} — memory lifecycle narrative
- GET /api/v1/explain/interventions/{run_id} — intervention narrative
- GET /api/v1/explain/autonomy/{run_id} — autonomy transition narrative
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_permission
from src.core.database import get_db
from src.core.logging import get_logger

logger = get_logger("explainability")

router = APIRouter(prefix="/explain", tags=["explainability"])


# ── Schemas ─────────────────────────────────────────────────────────────────

class EvidenceReference(BaseModel):
    id: str
    type: str
    description: str
    timestamp: Optional[str] = None

class CausalLink(BaseModel):
    from_event: str
    to_event: str
    relationship: str  # "caused", "contributed_to", "triggered", "preceded"
    confidence: float  # 0.0-1.0
    evidence_ids: list[str] = []

class NarrativeSegment(BaseModel):
    timestamp: str
    event_type: str
    description: str
    severity: str
    trust_impact: float = 0.0
    evidence_references: list[EvidenceReference] = []
    causal_links: list[CausalLink] = []
    uncertainty: Optional[str] = None

class TrustDimensionEvolution(BaseModel):
    dimension: str
    initial_score: Optional[float] = None
    current_score: Optional[float] = None
    change: Optional[float] = None
    trend: str = "stable"  # improving, degrading, stable, unknown
    contributing_events: list[str] = []
    uncertainty: Optional[str] = None

class RuntimeExplanation(BaseModel):
    run_id: str
    generated_at: str
    run_info: dict
    timeline: list[NarrativeSegment]
    trust_evolution: list[TrustDimensionEvolution]
    drift_lineage: list[dict]
    governance_narrative: list[dict]
    replay_integrity: dict
    memory_lifecycle: list[dict]
    interventions: list[dict]
    autonomy_transitions: list[dict]
    causal_chains: list[dict]
    overall_assessment: dict
    recommendations: list[str]
    uncertainty_disclosures: list[str]

class TrustExplanation(BaseModel):
    run_id: str
    generated_at: str
    dimensions: list[TrustDimensionEvolution]
    overall_trend: str
    degradation_events: list[dict]
    recovery_events: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class DriftExplanation(BaseModel):
    run_id: str
    generated_at: str
    drift_events: list[dict]
    lineage: list[dict]
    propagation: list[dict]
    trust_impact: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class ReplayExplanation(BaseModel):
    run_id: str
    generated_at: str
    integrity_status: str
    total_events: int
    chained_events: int
    chain_breaks: list[dict]
    orphaned_events: list[dict]
    corruption_markers: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class GovernanceExplanation(BaseModel):
    run_id: str
    generated_at: str
    decisions: list[dict]
    triggered_policies: list[dict]
    blocked_actions: list[dict]
    operator_overrides: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class MemoryExplanation(BaseModel):
    run_id: str
    generated_at: str
    lifecycle_events: list[dict]
    quarantined_items: list[dict]
    archived_items: list[dict]
    confidence_decay: list[dict]
    poisoning_suspected: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class InterventionExplanation(BaseModel):
    run_id: str
    generated_at: str
    interventions: list[dict]
    autonomy_changes: list[dict]
    trust_impact: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]

class AutonomyExplanation(BaseModel):
    run_id: str
    generated_at: str
    transitions: list[dict]
    current_level: str
    triggers: list[dict]
    trust_thresholds: list[dict]
    narrative: str
    uncertainty_disclosures: list[str]


# ── Helper: get run info ────────────────────────────────────────────────────

async def _get_run_info(db: AsyncSession, run_id: str) -> dict:
    result = await db.execute(text("""
        SELECT id, name, status, project_id, workspace_id, total_cost, budget_limit,
               created_at, updated_at, started_at, completed_at
        FROM runs WHERE id = :rid
    """), {"rid": run_id})
    row = result.fetchone()
    if not row:
        return {}
    return {
        "id": str(row[0]), "name": row[1], "status": row[2],
        "project_id": str(row[3]) if row[3] else None,
        "workspace_id": str(row[4]) if row[4] else None,
        "total_cost": float(row[5] or 0), "budget_limit": float(row[6] or 0),
        "created_at": row[7].isoformat() if row[7] else None,
        "updated_at": row[8].isoformat() if row[8] else None,
        "started_at": row[9].isoformat() if row[9] else None,
        "completed_at": row[10].isoformat() if row[10] else None,
    }


# ── Helper: get timeline events ─────────────────────────────────────────────

async def _get_timeline_events(db: AsyncSession, run_id: str) -> list[dict]:
    """Get all events for a run from log_events, ordered chronologically."""
    result = await db.execute(text("""
        SELECT id, created_at, severity, message, metadata, source_file, phase_id, agent_id
        FROM log_events
        WHERE run_id = :rid
        ORDER BY created_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "id": str(r[0]),
        "timestamp": r[1].isoformat() if r[1] else None,
        "severity": r[2] or "info",
        "message": r[3] or "",
        "metadata": r[4] if isinstance(r[4], dict) else {},
        "source": r[5] or "system",
        "phase_id": str(r[6]) if r[6] else None,
        "agent_id": str(r[7]) if r[7] else None,
    } for r in rows]


# ── Helper: get trust evolution ─────────────────────────────────────────────

async def _get_trust_evolution(db: AsyncSession, run_id: str) -> list[dict]:
    """Get trust score evolution for a run."""
    result = await db.execute(text("""
        SELECT trust_dimension, score, confidence, evidence, degradation_factors, scored_at
        FROM runtime_trust_scores
        WHERE run_id = :rid
        ORDER BY scored_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "dimension": r[0],
        "score": float(r[1] or 0),
        "confidence": float(r[2] or 0),
        "evidence": r[3] if isinstance(r[3], dict) else {},
        "degradation_factors": r[4] if isinstance(r[4], list) else [],
        "scored_at": r[5].isoformat() if r[5] else None,
    } for r in rows]


# ── Helper: get drift events ────────────────────────────────────────────────

async def _get_drift_events(db: AsyncSession, run_id: str) -> list[dict]:
    """Get drift events for a run."""
    result = await db.execute(text("""
        SELECT id, drift_type, drift_category, severity, drift_score, threshold,
               detection_context, evidence, prior_state, current_state,
               recommended_action, action_taken, autonomy_impact, detected_at, resolved_at, is_resolved
        FROM drift_events
        WHERE project_id = (SELECT project_id FROM runs WHERE id = :rid)
        ORDER BY detected_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "id": str(r[0]), "drift_type": r[1], "drift_category": r[2],
        "severity": r[3], "drift_score": float(r[4] or 0),
        "threshold": float(r[5] or 0), "detection_context": r[6],
        "evidence": r[7], "prior_state": r[8], "current_state": r[9],
        "recommended_action": r[10], "action_taken": r[11],
        "autonomy_impact": r[12],
        "detected_at": r[13].isoformat() if r[13] else None,
        "resolved_at": r[14].isoformat() if r[14] else None,
        "is_resolved": r[15],
    } for r in rows]


# ── Helper: get governance decisions ────────────────────────────────────────

async def _get_governance_decisions(db: AsyncSession, run_id: str) -> list[dict]:
    """Get governance decisions for a run."""
    result = await db.execute(text("""
        SELECT id, policy_name, decision, severity, evidence, created_at
        FROM governance_findings
        WHERE project_id = (SELECT project_id FROM runs WHERE id = :rid)
        ORDER BY created_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "id": str(r[0]), "policy_name": r[1], "decision": r[2],
        "severity": r[3], "evidence": r[4],
        "created_at": r[5].isoformat() if r[5] else None,
    } for r in rows]


# ── Helper: get replay integrity ────────────────────────────────────────────

async def _get_replay_integrity(db: AsyncSession, run_id: str) -> dict:
    """Get replay integrity status for a run."""
    result = await db.execute(text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN chain_hash IS NOT NULL AND chain_hash NOT LIKE 'INVALIDATED:%' THEN 1 END) as chained,
            COUNT(CASE WHEN chain_hash IS NULL THEN 1 END) as unchained,
            COUNT(CASE WHEN chain_hash LIKE 'INVALIDATED:%' THEN 1 END) as invalidated
        FROM evidence_bundles
        WHERE run_id = :rid
    """), {"rid": run_id})
    row = result.fetchone()
    if not row:
        return {"status": "no_data", "total": 0, "chained": 0, "unchained": 0, "invalidated": 0}

    total = row[0]
    chained = row[1]
    unchained = row[2]
    invalidated = row[3]

    if total == 0:
        integrity_pct = 100.0
        status = "no_data"
    else:
        integrity_pct = (chained / total * 100) if total > 0 else 0.0
        status = "healthy" if integrity_pct >= 95 else "degraded" if integrity_pct >= 80 else "critical"

    # Get chain breaks
    chain_breaks = []
    if total > 0:
        cb_result = await db.execute(text("""
            SELECT id, bundle_hash, chain_hash, bundle_path, created_at
            FROM evidence_bundles
            WHERE run_id = :rid AND (chain_hash IS NULL OR chain_hash LIKE 'INVALIDATED:%')
            ORDER BY created_at ASC
        """), {"rid": run_id})
        for r in cb_result.fetchall():
            chain_breaks.append({
                "id": str(r[0]), "bundle_hash": r[1], "chain_hash": r[2],
                "path": r[3], "created_at": r[4].isoformat() if r[4] else None,
            })

    return {
        "status": status, "total": total, "chained": chained,
        "unchained": unchained, "invalidated": invalidated,
        "integrity_pct": round(integrity_pct, 1),
        "chain_breaks": chain_breaks,
    }


# ── Helper: get memory lifecycle ─────────────────────────────────────────────

async def _get_memory_lifecycle(db: AsyncSession, run_id: str) -> list[dict]:
    """Get memory lifecycle events for a run."""
    result = await db.execute(text("""
        SELECT id, memory_type, entity_type, entity_id, drift_score, confidence,
               is_active, valid_until, created_at, updated_at, semantic_content
        FROM semantic_memory
        WHERE project_id = (SELECT project_id FROM runs WHERE id = :rid)
        ORDER BY updated_at DESC
        LIMIT 100
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "id": str(r[0]), "memory_type": r[1], "entity_type": r[2],
        "entity_id": str(r[3]) if r[3] else None,
        "drift_score": float(r[4] or 0), "confidence": float(r[5] or 0),
        "is_active": r[6], "valid_until": r[7].isoformat() if r[7] else None,
        "created_at": r[8].isoformat() if r[8] else None,
        "updated_at": r[9].isoformat() if r[9] else None,
        "lifecycle_state": (r[10] or {}).get("lifecycle_state", "unknown") if isinstance(r[10], dict) else "unknown",
    } for r in rows]


# ── Helper: get interventions ───────────────────────────────────────────────

async def _get_interventions(db: AsyncSession, run_id: str) -> list[dict]:
    """Get operator interventions for a run."""
    result = await db.execute(text("""
        SELECT id, operator_id, intervention_type, correction, prior_state,
               corrected_state, governance_impact, created_at
        FROM operator_interventions
        WHERE run_id = :rid
        ORDER BY created_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    return [{
        "id": str(r[0]), "operator_id": str(r[1]) if r[1] else None,
        "intervention_type": r[2], "correction": r[3],
        "prior_state": r[4], "corrected_state": r[5],
        "governance_impact": r[6],
        "created_at": r[7].isoformat() if r[7] else None,
    } for r in rows]


# ── Helper: get autonomy transitions ────────────────────────────────────────

async def _get_autonomy_transitions(db: AsyncSession, run_id: str) -> list[dict]:
    """Get autonomy level transitions for a run."""
    result = await db.execute(text("""
        SELECT autonomy_level, escalation_level, active_restrictions, drift_summary,
               last_evaluated_at, updated_at
        FROM metacognitive_state
        WHERE project_id = (SELECT project_id FROM runs WHERE id = :rid)
        ORDER BY updated_at ASC
    """), {"rid": run_id})
    rows = result.fetchall()
    transitions = []
    prev_level = None
    for r in rows:
        current_level = r[0] or "full"
        if current_level != prev_level:
            transitions.append({
                "from_level": prev_level or "unknown",
                "to_level": current_level,
                "escalation_level": r[1],
                "active_restrictions": r[2] if isinstance(r[2], list) else [],
                "drift_summary": r[3] if isinstance(r[3], dict) else {},
                "evaluated_at": r[4].isoformat() if r[4] else None,
                "updated_at": r[5].isoformat() if r[5] else None,
            })
            prev_level = current_level
    return transitions


# ── Helper: build narrative from events ─────────────────────────────────────

def _build_narrative(events: list[dict], title: str) -> str:
    """Build a human-readable narrative from a list of events."""
    if not events:
        return f"No {title} events recorded for this run."

    parts = []
    for evt in events:
        ts = evt.get("timestamp", "unknown time")
        if ts and isinstance(ts, str) and "T" in ts:
            try:
                ts = ts[:19].replace("T", " ")
            except Exception:
                pass
        severity = evt.get("severity", "info")
        message = evt.get("message", evt.get("correction", evt.get("intervention_type", "Unknown event")))
        parts.append(f"[{ts}] ({severity.upper()}) {message}")

    return "\n".join(parts)


# ── Helper: compute uncertainty disclosures ─────────────────────────────────

def _compute_uncertainty(
    events: list[dict],
    trust_scores: list[dict],
    drift_events: list[dict],
    interventions: list[dict],
) -> list[str]:
    """Compute uncertainty disclosures — be honest about what we don't know."""
    disclosures = []

    if not events:
        disclosures.append("No runtime events were recorded. The timeline may be incomplete.")

    if not trust_scores:
        disclosures.append("No trust scores were computed for this run. Trust evolution is unknown.")

    unresolved_drift = [d for d in drift_events if not d.get("is_resolved")]
    if unresolved_drift:
        disclosures.append(f"{len(unresolved_drift)} drift event(s) remain unresolved. Causal impact may be incomplete.")

    if not interventions:
        disclosures.append("No operator interventions were recorded. The run may have completed autonomously.")

    # Check for gaps in event timeline
    if len(events) >= 2:
        try:
            timestamps = [e["timestamp"] for e in events if e.get("timestamp")]
            if len(timestamps) >= 2:
                from datetime import datetime as dt
                parsed = [dt.fromisoformat(t.replace("Z", "+00:00")) for t in timestamps if t]
                parsed.sort()
                for i in range(1, len(parsed)):
                    gap = (parsed[i] - parsed[i-1]).total_seconds()
                    if gap > 3600:  # 1 hour gap
                        disclosures.append(f"Event timeline has a {gap/3600:.1f}h gap between {parsed[i-1]} and {parsed[i]}. Events may be missing.")
        except Exception:
            pass

    return disclosures


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/runtime/{run_id}", response_model=RuntimeExplanation)
async def explain_runtime(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Full runtime explanation — cognitive reconstruction of what happened."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Gather all data
    timeline_events = await _get_timeline_events(db, run_id)
    trust_scores = await _get_trust_evolution(db, run_id)
    drift_events = await _get_drift_events(db, run_id)
    governance_decisions = await _get_governance_decisions(db, run_id)
    replay_integrity = await _get_replay_integrity(db, run_id)
    memory_lifecycle = await _get_memory_lifecycle(db, run_id)
    interventions = await _get_interventions(db, run_id)
    autonomy_transitions = await _get_autonomy_transitions(db, run_id)

    # Build timeline narrative segments
    timeline = []
    for evt in timeline_events:
        segment = NarrativeSegment(
            timestamp=evt["timestamp"] or datetime.now(timezone.utc).isoformat(),
            event_type="LOG_ENTRY",
            description=evt["message"],
            severity=evt["severity"],
            trust_impact=0.0,
            evidence_references=[EvidenceReference(
                id=evt["id"], type="log_event", description=evt["message"][:100],
                timestamp=evt["timestamp"],
            )],
            uncertainty=None,
        )
        timeline.append(segment)

    # Build trust evolution
    trust_evolution = []
    dimensions_seen = {}
    for ts in trust_scores:
        dim = ts["dimension"]
        if dim not in dimensions_seen:
            dimensions_seen[dim] = {"initial": ts["score"], "current": ts["score"], "events": []}
        dimensions_seen[dim]["current"] = ts["score"]
        dimensions_seen[dim]["events"].append(ts["scored_at"])

    for dim, data in dimensions_seen.items():
        change = data["current"] - data["initial"]
        trend = "improving" if change > 0.05 else "degrading" if change < -0.05 else "stable"
        trust_evolution.append(TrustDimensionEvolution(
            dimension=dim, initial_score=data["initial"], current_score=data["current"],
            change=round(change, 3), trend=trend, contributing_events=data["events"],
        ))

    # Build causal chains
    causal_chains = []
    for drift in drift_events:
        chain = {
            "type": "drift_propagation",
            "root_cause": f"Drift detected: {drift['drift_category']} ({drift['drift_type']})",
            "score": drift["drift_score"],
            "propagated_to": [],
        }
        if drift.get("autonomy_impact"):
            chain["propagated_to"].append(f"Autonomy impact: {drift['autonomy_impact']}")
        if drift["drift_score"] > 0.5:
            chain["propagated_to"].append("Trust degradation (high drift)")
        causal_chains.append(chain)

    for intervention in interventions:
        causal_chains.append({
            "type": "operator_intervention",
            "root_cause": f"Operator intervention: {intervention['intervention_type']}",
            "operator": intervention["operator_id"],
            "result": intervention.get("corrected_state", {}),
        })

    # Build recommendations
    recommendations = []
    if replay_integrity.get("status") == "critical":
        recommendations.append("Replay integrity is critical. Consider invalidating and re-running the pipeline.")
    if any(d["severity"] == "critical" for d in drift_events):
        recommendations.append("Critical drift detected. Review semantic memory and consider re-seeding.")
    if any(t.trend == "degrading" for t in trust_evolution):
        degrading = [t.dimension for t in trust_evolution if t.trend == "degrading"]
        recommendations.append(f"Trust degrading in: {', '.join(degrading)}. Investigate root causes.")
    if any(not d.get("is_resolved") for d in drift_events):
        recommendations.append("Unresolved drift events remain. Consider manual review.")
    if not recommendations:
        recommendations.append("No critical issues detected. Runtime appears healthy.")

    # Uncertainty disclosures
    uncertainty = _compute_uncertainty(timeline_events, trust_scores, drift_events, interventions)

    # Overall assessment
    overall_status = "healthy"
    if replay_integrity.get("status") == "critical" or any(d["severity"] == "critical" for d in drift_events):
        overall_status = "critical"
    elif replay_integrity.get("status") == "degraded" or any(t.trend == "degrading" for t in trust_evolution):
        overall_status = "degraded"

    return RuntimeExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        run_info=run_info,
        timeline=timeline,
        trust_evolution=trust_evolution,
        drift_lineage=drift_events,
        governance_narrative=governance_decisions,
        replay_integrity=replay_integrity,
        memory_lifecycle=memory_lifecycle,
        interventions=interventions,
        autonomy_transitions=autonomy_transitions,
        causal_chains=causal_chains,
        overall_assessment={
            "status": overall_status,
            "total_events": len(timeline_events),
            "total_drift_events": len(drift_events),
            "total_interventions": len(interventions),
            "replay_integrity_pct": replay_integrity.get("integrity_pct", 0),
            "trust_trend": "degrading" if any(t.trend == "degrading" for t in trust_evolution) else "stable",
        },
        recommendations=recommendations,
        uncertainty_disclosures=uncertainty,
    )


@router.get("/trust/{run_id}", response_model=TrustExplanation)
async def explain_trust(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Trust evolution narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    trust_scores = await _get_trust_evolution(db, run_id)
    drift_events = await _get_drift_events(db, run_id)

    dimensions = []
    dimensions_seen = {}
    for ts in trust_scores:
        dim = ts["dimension"]
        if dim not in dimensions_seen:
            dimensions_seen[dim] = {"initial": ts["score"], "current": ts["score"], "events": [], "degradation": []}
        dimensions_seen[dim]["current"] = ts["score"]
        dimensions_seen[dim]["events"].append(ts["scored_at"])
        if ts.get("degradation_factors"):
            dimensions_seen[dim]["degradation"].extend(ts["degradation_factors"])

    for dim, data in dimensions_seen.items():
        change = data["current"] - data["initial"]
        trend = "improving" if change > 0.05 else "degrading" if change < -0.05 else "stable"
        dimensions.append(TrustDimensionEvolution(
            dimension=dim, initial_score=data["initial"], current_score=data["current"],
            change=round(change, 3), trend=trend, contributing_events=data["events"],
            uncertainty=f"Degradation factors: {data['degradation']}" if data["degradation"] else None,
        ))

    # Build narrative
    narrative_parts = []
    if not trust_scores:
        narrative_parts.append("No trust scores were computed for this run.")
    else:
        for d in dimensions:
            if d.trend == "degrading":
                narrative_parts.append(f"Trust in '{d.dimension}' degraded from {d.initial_score:.2f} to {d.current_score:.2f} (Δ{d.change:+.2f}).")
            elif d.trend == "improving":
                narrative_parts.append(f"Trust in '{d.dimension}' improved from {d.initial_score:.2f} to {d.current_score:.2f} (Δ{d.change:+.2f}).")
            else:
                narrative_parts.append(f"Trust in '{d.dimension}' remained stable at {d.current_score:.2f}.")

    degradation_events = [d for d in drift_events if d["drift_score"] > 0.3]
    recovery_events = [d for d in drift_events if d.get("is_resolved")]

    uncertainty = []
    if not trust_scores:
        uncertainty.append("No trust data available. Cannot assess trust evolution.")

    return TrustExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        dimensions=dimensions,
        overall_trend="degrading" if any(d.trend == "degrading" for d in dimensions) else "stable",
        degradation_events=degradation_events,
        recovery_events=recovery_events,
        narrative="\n".join(narrative_parts) if narrative_parts else "No trust evolution data available.",
        uncertainty_disclosures=uncertainty,
    )


@router.get("/drift/{run_id}", response_model=DriftExplanation)
async def explain_drift(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Drift lineage narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    drift_events = await _get_drift_events(db, run_id)

    lineage = []
    propagation = []
    trust_impact = []

    for d in drift_events:
        lineage.append({
            "id": d["id"],
            "category": d["drift_category"],
            "type": d["drift_type"],
            "score": d["drift_score"],
            "severity": d["severity"],
            "detected_at": d["detected_at"],
            "resolved_at": d.get("resolved_at"),
            "is_resolved": d.get("is_resolved", False),
        })
        if d["drift_score"] > 0.3:
            propagation.append({
                "from": d["drift_category"],
                "to": "trust_degradation",
                "score": d["drift_score"],
                "detected_at": d["detected_at"],
            })
        if d.get("autonomy_impact"):
            trust_impact.append({
                "drift_type": d["drift_type"],
                "autonomy_impact": d["autonomy_impact"],
                "score": d["drift_score"],
            })

    narrative_parts = []
    if not drift_events:
        narrative_parts.append("No drift events were detected for this run.")
    else:
        unresolved = [d for d in drift_events if not d.get("is_resolved")]
        narrative_parts.append(f"{len(drift_events)} drift event(s) detected, {len(unresolved)} unresolved.")
        for d in drift_events:
            status = "resolved" if d.get("is_resolved") else "UNRESOLVED"
            narrative_parts.append(f"  [{status}] {d['drift_category']} ({d['drift_type']}): score={d['drift_score']:.2f}, severity={d['severity']}")

    uncertainty = []
    if not drift_events:
        uncertainty.append("No drift events recorded. Drift may have occurred but not been detected.")

    return DriftExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        drift_events=drift_events,
        lineage=lineage,
        propagation=propagation,
        trust_impact=trust_impact,
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )


@router.get("/replay/{run_id}", response_model=ReplayExplanation)
async def explain_replay(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Replay integrity narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    replay = await _get_replay_integrity(db, run_id)

    narrative_parts = []
    if replay["total"] == 0:
        narrative_parts.append("No replay events recorded for this run.")
    else:
        narrative_parts.append(f"Replay integrity: {replay['status']} ({replay['integrity_pct']}% chained).")
        narrative_parts.append(f"Total events: {replay['total']}, Chained: {replay['chained']}, Unchained: {replay['unchained']}, Invalidated: {replay['invalidated']}.")
        if replay["chain_breaks"]:
            narrative_parts.append(f"{len(replay['chain_breaks'])} chain break(s) detected:")
            for cb in replay["chain_breaks"][:10]:
                narrative_parts.append(f"  - {cb['id'][:8]}...: {cb['path']}")

    uncertainty = []
    if replay["total"] == 0:
        uncertainty.append("No replay data available. Cannot assess replay integrity.")

    return ReplayExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        integrity_status=replay["status"],
        total_events=replay["total"],
        chained_events=replay["chained"],
        chain_breaks=replay.get("chain_breaks", []),
        orphaned_events=[],
        corruption_markers=[cb for cb in replay.get("chain_breaks", []) if cb.get("chain_hash", "").startswith("INVALIDATED:")],
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )


@router.get("/governance/{run_id}", response_model=GovernanceExplanation)
async def explain_governance(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Governance rationale narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    decisions = await _get_governance_decisions(db, run_id)
    interventions = await _get_interventions(db, run_id)

    triggered_policies = [d for d in decisions if d.get("decision") in ("blocked", "violation", "warning")]
    blocked_actions = [d for d in decisions if d.get("decision") == "blocked"]
    operator_overrides = [i for i in interventions if i.get("intervention_type") in ("RESUME", "FORCE_VERIFIER")]

    narrative_parts = []
    if not decisions:
        narrative_parts.append("No governance decisions were recorded for this run.")
    else:
        narrative_parts.append(f"{len(decisions)} governance decision(s) recorded.")
        if blocked_actions:
            narrative_parts.append(f"{len(blocked_actions)} action(s) blocked by governance policies:")
            for ba in blocked_actions:
                narrative_parts.append(f"  - Policy '{ba['policy_name']}': {ba.get('evidence', 'No evidence recorded')}")
        if triggered_policies:
            narrative_parts.append(f"{len(triggered_policies)} policy threshold(s) exceeded.")

    uncertainty = []
    if not decisions:
        uncertainty.append("No governance decisions recorded. Governance may not have been active for this run.")

    return GovernanceExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        decisions=decisions,
        triggered_policies=triggered_policies,
        blocked_actions=blocked_actions,
        operator_overrides=operator_overrides,
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )


@router.get("/memory/{run_id}", response_model=MemoryExplanation)
async def explain_memory(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Memory lifecycle narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    memory_items = await _get_memory_lifecycle(db, run_id)

    quarantined = [m for m in memory_items if m.get("lifecycle_state") == "quarantined"]
    archived = [m for m in memory_items if m.get("lifecycle_state") == "archived"]
    low_confidence = [m for m in memory_items if m.get("confidence", 1.0) < 0.5 and m.get("is_active")]
    poisoning_suspected = [m for m in memory_items if m.get("drift_score", 0) > 0.5]

    lifecycle_events = []
    for m in memory_items:
        lifecycle_events.append({
            "id": m["id"],
            "type": m["memory_type"],
            "state": m.get("lifecycle_state", "unknown"),
            "is_active": m.get("is_active"),
            "drift_score": m.get("drift_score"),
            "confidence": m.get("confidence"),
            "updated_at": m.get("updated_at"),
        })

    narrative_parts = []
    if not memory_items:
        narrative_parts.append("No memory items found for this run's project.")
    else:
        active = sum(1 for m in memory_items if m.get("is_active"))
        narrative_parts.append(f"{len(memory_items)} memory item(s), {active} active.")
        if quarantined:
            narrative_parts.append(f"{len(quarantined)} item(s) quarantined.")
        if archived:
            narrative_parts.append(f"{len(archived)} item(s) archived.")
        if poisoning_suspected:
            narrative_parts.append(f"{len(poisoning_suspected)} item(s) with high drift (possible poisoning).")

    uncertainty = []
    if not memory_items:
        uncertainty.append("No memory data available.")

    return MemoryExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        lifecycle_events=lifecycle_events,
        quarantined_items=quarantined,
        archived_items=archived,
        confidence_decay=low_confidence,
        poisoning_suspected=poisoning_suspected,
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )


@router.get("/interventions/{run_id}", response_model=InterventionExplanation)
async def explain_interventions(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Intervention narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    interventions = await _get_interventions(db, run_id)
    autonomy_transitions = await _get_autonomy_transitions(db, run_id)

    narrative_parts = []
    if not interventions:
        narrative_parts.append("No operator interventions were recorded for this run.")
    else:
        narrative_parts.append(f"{len(interventions)} operator intervention(s):")
        for iv in interventions:
            narrative_parts.append(f"  - {iv['intervention_type']} by {iv['operator_id'][:8] if iv['operator_id'] else 'unknown'}...: {iv.get('correction', 'No reason recorded')}")

    uncertainty = []
    if not interventions:
        uncertainty.append("No interventions recorded. The run may have completed without operator involvement.")

    return InterventionExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        interventions=interventions,
        autonomy_changes=autonomy_transitions,
        trust_impact=[],
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )


@router.get("/autonomy/{run_id}", response_model=AutonomyExplanation)
async def explain_autonomy(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("operations.view")),
):
    """Autonomy transition narrative for a run."""
    run_info = await _get_run_info(db, run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    transitions = await _get_autonomy_transitions(db, run_id)
    drift_events = await _get_drift_events(db, run_id)
    trust_scores = await _get_trust_evolution(db, run_id)

    current_level = transitions[-1]["to_level"] if transitions else "full"

    triggers = []
    for t in transitions:
        if t["to_level"] != t["from_level"]:
            triggers.append({
                "from": t["from_level"],
                "to": t["to_level"],
                "at": t.get("updated_at"),
                "restrictions": t.get("active_restrictions", []),
            })

    trust_thresholds = []
    for ts in trust_scores:
        if ts["score"] < 0.5:
            trust_thresholds.append({
                "dimension": ts["dimension"],
                "score": ts["score"],
                "threshold": 0.5,
                "breached_at": ts["scored_at"],
            })

    narrative_parts = []
    if not transitions:
        narrative_parts.append("No autonomy transitions recorded. Autonomy remained at default level.")
    else:
        narrative_parts.append(f"Autonomy level: {current_level}")
        for t in triggers:
            narrative_parts.append(f"  Transition: {t['from']} → {t['to']} at {t.get('at', 'unknown time')}")

    uncertainty = []
    if not transitions:
        uncertainty.append("No autonomy data available.")

    return AutonomyExplanation(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        transitions=transitions,
        current_level=current_level,
        triggers=triggers,
        trust_thresholds=trust_thresholds,
        narrative="\n".join(narrative_parts),
        uncertainty_disclosures=uncertainty,
    )
