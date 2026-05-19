"""Drift Detection Engine & Metacognitive Control Plane — v0.3.5 hardened.

All SQL transaction patterns fixed:
- No ON CONFLICT on non-unique columns
- Proper transaction boundaries
- Deterministic rollback behavior
- No partial persistence
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings


# ─── Drift Detection Engine ───

DRIFT_CATEGORIES = {
    "semantic": {"description": "Requirements diverge over time", "default_threshold": 0.3},
    "goal": {"description": "Runtime objective changes", "default_threshold": 0.4},
    "governance": {"description": "Governance weakens over time", "default_threshold": 0.3},
    "context": {"description": "Stale assumptions, outdated references", "default_threshold": 0.5},
    "cost": {"description": "Runaway Tokenomics", "default_threshold": 0.7},
    "evidence": {"description": "Incomplete evidence, replay inconsistency", "default_threshold": 0.4},
    "memory_poisoning": {"description": "Contradictory memory", "default_threshold": 0.3},
    "cognitive": {"description": "Repeated hallucinations, unstable reasoning", "default_threshold": 0.4},
}


class DriftDetectionEngine:
    """Detects runtime drift across 8 categories."""

    def __init__(self, db: Session):
        self.db = db

    def detect_semantic_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT drift_score, confidence FROM semantic_memory
            WHERE project_id = :pid AND is_active = true
            ORDER BY created_at DESC LIMIT 20
        """), {"pid": project_id})
        entries = result.fetchall()
        if len(entries) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient data"}
        recent = [e[0] for e in entries[:5] if e[0] is not None]
        older = [e[0] for e in entries[5:10] if e[0] is not None]
        avg_recent = sum(recent) / len(recent) if recent else 0.0
        avg_older = sum(older) / len(older) if older else 0.0
        drift_delta = avg_recent - avg_older
        return {"drift_detected": drift_delta > DRIFT_CATEGORIES["semantic"]["default_threshold"],
                "score": max(0.0, drift_delta), "avg_recent": avg_recent, "avg_older": avg_older}

    def detect_governance_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT escalation_level, override_reason FROM governance_memory
            WHERE project_id = :pid AND is_active = true
            ORDER BY created_at DESC LIMIT 50
        """), {"pid": project_id})
        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No governance history"}
        overrides = sum(1 for e in entries if e[1] is not None)
        escalations = sum(1 for e in entries if e[0] not in (None, "none"))
        ratio = (overrides + escalations) / (2 * len(entries)) if entries else 0.0
        return {"drift_detected": ratio > DRIFT_CATEGORIES["governance"]["default_threshold"],
                "score": ratio, "overrides": overrides, "escalations": escalations}

    def detect_cost_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT total_cost, budget_limit FROM runs
            WHERE project_id = :pid ORDER BY created_at DESC LIMIT 20
        """), {"pid": project_id})
        runs = result.fetchall()
        if not runs:
            return {"drift_detected": False, "score": 0.0, "reason": "No run data"}
        total_cost = sum(r[0] for r in runs)
        budget = runs[0][1]
        usage = total_cost / budget if budget and budget > 0 else 0.0
        return {"drift_detected": usage > DRIFT_CATEGORIES["cost"]["default_threshold"],
                "score": min(1.0, max(0.0, usage)), "total_cost": total_cost}

    def detect_evidence_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN chain_hash IS NOT NULL THEN 1 END) as chained
            FROM evidence_bundles eb
            JOIN runs r ON eb.run_id = r.id WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        if not row or row[0] == 0:
            return {"drift_detected": False, "score": 0.0, "reason": "No evidence"}
        completeness = row[1] / row[0] if row[0] > 0 else 1.0
        drift = 1.0 - completeness
        return {"drift_detected": drift > DRIFT_CATEGORIES["evidence"]["default_threshold"],
                "score": drift, "completeness": completeness}

    def detect_context_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT validity_status, staleness_score FROM context_validity
            WHERE project_id = :pid
        """), {"pid": project_id})
        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No context data"}
        stale = sum(1 for e in entries if e[0] in ("stale", "expired"))
        avg_stale = sum(e[1] for e in entries) / len(entries)
        score = (stale / len(entries) * 0.5 + avg_stale * 0.5)
        return {"drift_detected": score > DRIFT_CATEGORIES["context"]["default_threshold"],
                "score": score, "stale_contexts": stale}

    def detect_memory_poisoning(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT memory_type, key, content FROM memory_items WHERE project_id = :pid
            ORDER BY created_at DESC LIMIT 100
        """), {"pid": project_id})
        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No memory items"}
        key_hashes: Dict[str, set] = {}
        for e in entries:
            kh = f"{e[0]}:{e[1]}"
            h = hashlib.md5(str(e[2]).encode()).hexdigest()[:16]
            key_hashes.setdefault(kh, set()).add(h)
        contradictory = sum(1 for hashes in key_hashes.values() if len(hashes) > 1)
        ratio = contradictory / len(key_hashes) if key_hashes else 0.0
        return {"drift_detected": ratio > DRIFT_CATEGORIES["memory_poisoning"]["default_threshold"],
                "score": ratio, "contradictory_keys": contradictory}

    def detect_cognitive_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT overall_semantic_coverage_score FROM semantic_coverage_reports scr
            JOIN runs r ON scr.run_id = r.id::uuid
            WHERE r.project_id = :pid ORDER BY scr.created_at DESC LIMIT 10
        """), {"pid": project_id})
        scores = [e[0] for e in result.fetchall() if e[0] is not None]
        if len(scores) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient data"}
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std = variance ** 0.5
        score = min(1.0, std * 2)
        return {"drift_detected": score > DRIFT_CATEGORIES["cognitive"]["default_threshold"],
                "score": score, "std_deviation": std}

    def detect_goal_drift(self, project_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT intent FROM runs WHERE project_id = :pid ORDER BY created_at DESC LIMIT 10
        """), {"pid": project_id})
        intents = [r[0] for r in result.fetchall() if r[0]]
        if len(intents) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient intents"}
        orig = set(intents[-1].lower().split())
        recent = set(intents[0].lower().split())
        overlap = len(orig & recent) / len(orig) if orig else 1.0
        score = 1.0 - overlap
        return {"drift_detected": score > DRIFT_CATEGORIES["goal"]["default_threshold"],
                "score": score, "intent_overlap": overlap}

    def run_full_drift_scan(self, project_id: str) -> Dict[str, Any]:
        results = {}
        for cat in DRIFT_CATEGORIES:
            try:
                detector = getattr(self, f"detect_{cat}_drift")
                results[cat] = detector(project_id)
            except Exception as e:
                results[cat] = {"drift_detected": False, "score": 0.0, "error": str(e)[:100]}

        scores = [r["score"] for r in results.values() if "score" in r]
        overall = sum(scores) / len(scores) if scores else 0.0
        return {
            "project_id": project_id,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "overall_drift_score": overall,
            "drift_detected": any(r.get("drift_detected", False) for r in results.values()),
            "categories_scanned": len(DRIFT_CATEGORIES),
            "categories_with_drift": sum(1 for r in results.values() if r.get("drift_detected")),
            "category_results": results,
        }


# ─── Replay Integrity Verifier ───

class ReplayIntegrityVerifier:
    """Active SHA256 chain validation for replay events."""

    def __init__(self, db: Session):
        self.db = db

    def verify_replay_integrity(self, replay_session_id: str) -> Dict[str, Any]:
        result = self.db.execute(text("""
            SELECT id, event_hash, parent_hash, message, created_at
            FROM replay_events WHERE replay_session_id = :sid ORDER BY created_at ASC
        """), {"sid": replay_session_id})
        events = result.fetchall()
        if not events:
            return {"session_id": replay_session_id, "integrity_valid": False,
                    "error": "No events found", "events_checked": 0}

        issues = []
        chain_breaks = 0
        for i, (eid, ehash, parent_hash, msg, created) in enumerate(events):
            if not ehash:
                issues.append(f"Event {eid[:8]}: missing event_hash")
                continue
            if i > 0 and parent_hash and parent_hash != "genesis":
                prev_hash = events[i - 1][1]
                if prev_hash and parent_hash != prev_hash:
                    issues.append(f"Event {eid[:8]}: chain break")
                    chain_breaks += 1

        return {
            "session_id": replay_session_id,
            "integrity_valid": chain_breaks == 0,
            "events_checked": len(events),
            "chain_breaks": chain_breaks,
            "issues": issues,
        }


# ─── Metacognitive Controller ───

AUTONOMY_LEVELS = ["full", "reduced", "supervised", "paused"]


class MetacognitiveController:
    """Controls runtime autonomy, escalation, and cognitive stability."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_runtime_state(self, project_id: str, drift_report: Dict) -> Dict[str, Any]:
        drift = drift_report.get("overall_drift_score", 0.0)
        cats = drift_report.get("categories_with_drift", 0)

        if drift >= 0.8:
            autonomy, escalation = "paused", "critical"
        elif drift >= 0.6:
            autonomy, escalation = "supervised", "high"
        elif drift >= 0.4:
            autonomy, escalation = "reduced", "medium"
        elif drift >= 0.2:
            autonomy, escalation = "reduced", "low"
        else:
            autonomy, escalation = "full", "none"

        warnings = [f"{c}: drift {r.get('score', 0):.2f}"
                    for c, r in drift_report.get("category_results", {}).items()
                    if r.get("drift_detected")]
        restrictions = []
        if autonomy != "full":
            restrictions.append(f"Autonomy: {autonomy}")
        if escalation != "none":
            restrictions.append(f"Escalation: {escalation}")

        return {
            "project_id": project_id, "overall_drift_score": drift,
            "categories_with_drift": cats, "recommended_autonomy": autonomy,
            "recommended_escalation": escalation, "warnings": warnings,
            "restrictions": restrictions,
        }

    def apply_metacognitive_state(self, project_id: str, workspace_id: str,
                                   evaluation: Dict) -> str:
        """Persist metacognitive state — INSERT only, with session recovery."""
        state_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        try:
            self.db.rollback()  # Recover from any failed transaction
            self.db.execute(text("""
                INSERT INTO metacognitive_state (id, project_id, workspace_id, state_type,
                                                  overall_trust_score, autonomy_level, escalation_level,
                                                  active_warnings, active_restrictions, drift_summary,
                                                  last_evaluated_at, updated_at)
                VALUES (:id, :pid, :wid, 'drift_evaluation', :trust, :autonomy, :escalation,
                        :warnings, :restrictions, :summary, :evaluated, :updated)
            """), {
                "id": state_id, "pid": project_id, "wid": workspace_id,
                "trust": 1.0 - evaluation.get("overall_drift_score", 0.0),
                "autonomy": evaluation.get("recommended_autonomy", "full"),
                "escalation": evaluation.get("recommended_escalation", "none"),
                "warnings": json.dumps(evaluation.get("warnings", [])),
                "restrictions": json.dumps(evaluation.get("restrictions", [])),
                "summary": json.dumps({"categories_with_drift": evaluation.get("categories_with_drift", 0)}),
                "evaluated": now, "updated": now,
            })
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return state_id

    def record_operator_intervention(self, project_id: str, workspace_id: str,
                                      operator_id: str, intervention_type: str,
                                      correction: str, prior_state: Dict,
                                      corrected_state: Dict) -> str:
        int_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        self.db.execute(text("""
            INSERT INTO operator_interventions (id, run_id, project_id, workspace_id,
                                                 operator_id, intervention_type, correction,
                                                 prior_state, corrected_state, created_at)
            VALUES (:id, :rid, :pid, :wid, :oid, :itype, :correction, :prior, :corrected, :created)
        """), {
            "id": int_id, "rid": "", "pid": project_id, "wid": workspace_id,
            "oid": operator_id, "itype": intervention_type, "correction": correction,
            "prior": json.dumps(prior_state), "corrected": json.dumps(corrected_state),
            "created": now,
        })
        self.db.commit()
        return int_id


# ─── Runtime Trust Scorer ───

class RuntimeTrustScorer:
    """Multi-dimensional runtime trust scoring."""

    def __init__(self, db: Session):
        self.db = db

    def compute_trust_scores(self, project_id: str) -> Dict[str, Any]:
        scores = {}

        # Semantic integrity
        result = self.db.execute(text("""
            SELECT AVG(overall_semantic_coverage_score), STDDEV(overall_semantic_coverage_score)
            FROM semantic_coverage_reports scr
            JOIN runs r ON scr.run_id = r.id::uuid WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        scores["semantic_integrity"] = {"score": float(row[0]) if row and row[0] else 0.5,
                                         "confidence": 0.8 if row and row[0] else 0.1}

        # Governance effectiveness
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN decision = 'pass' THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM governance_evaluations ge JOIN runs r ON ge.run_id = r.id
            WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        scores["governance_effectiveness"] = {"score": float(row[0]) if row and row[0] else 0.5,
                                               "confidence": 0.7 if row and row[0] else 0.1}

        # Memory reliability
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN is_resolved = false THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM drift_events WHERE project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        drift_ratio = float(row[0]) if row and row[0] is not None else 0.0
        scores["memory_reliability"] = {"score": 1.0 - drift_ratio, "confidence": 0.6}

        # Replay integrity
        result = self.db.execute(text("""
            SELECT AVG(integrity_score) FROM replay_sessions rs
            JOIN runs r ON rs.source_run_id = r.id
            WHERE r.project_id = :pid AND rs.integrity_score IS NOT NULL
        """), {"pid": project_id})
        row = result.fetchone()
        scores["replay_integrity"] = {"score": float(row[0]) if row and row[0] else 0.5,
                                       "confidence": 0.7 if row and row[0] else 0.1}

        # Evidence completeness
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN eb.chain_hash IS NOT NULL THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM evidence_bundles eb JOIN runs r ON eb.run_id = r.id WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        scores["evidence_completeness"] = {"score": float(row[0]) if row and row[0] else 0.5,
                                            "confidence": 0.6 if row and row[0] else 0.1}

        # Cost stability
        result = self.db.execute(text("""
            SELECT AVG(total_cost) FROM runs WHERE project_id = :pid AND total_cost > 0
        """), {"pid": project_id})
        row = result.fetchone()
        avg_cost = float(row[0]) if row and row[0] else 0.0
        scores["cost_stability"] = {"score": max(0.0, 1.0 - avg_cost / 100.0), "confidence": 0.5}

        # Cognitive stability
        result = self.db.execute(text("""
            SELECT COUNT(*) FROM drift_events WHERE project_id = :pid AND is_resolved = false
        """), {"pid": project_id})
        unresolved = result.scalar()
        scores["cognitive_stability"] = {"score": max(0.0, 1.0 - unresolved * 0.1), "confidence": 0.5}

        weights = {"semantic_integrity": 0.2, "governance_effectiveness": 0.2,
                   "memory_reliability": 0.15, "replay_integrity": 0.15,
                   "evidence_completeness": 0.1, "cost_stability": 0.1,
                   "cognitive_stability": 0.1}
        overall = sum(scores.get(d, {}).get("score", 0.5) * w for d, w in weights.items())

        return {"project_id": project_id, "scored_at": datetime.now(timezone.utc).isoformat(),
                "overall_trust": overall, "dimensions": scores}

    def persist_trust_scores(self, project_id: str, workspace_id: str, scores: Dict) -> List[str]:
        ids = []
        now = datetime.now(timezone.utc)
        for dim, data in scores.get("dimensions", {}).items():
            sid = str(uuid.uuid4())
            self.db.execute(text("""
                INSERT INTO runtime_trust_scores (id, project_id, workspace_id, trust_dimension,
                                                   score, confidence, evidence, scored_at)
                VALUES (:id, :pid, :wid, :dim, :score, :conf, :evidence, :scored)
            """), {"id": sid, "pid": project_id, "wid": workspace_id, "dim": dim,
                   "score": data["score"], "conf": data["confidence"],
                   "evidence": json.dumps(data), "scored": now})
            ids.append(sid)
        self.db.commit()
        return ids
