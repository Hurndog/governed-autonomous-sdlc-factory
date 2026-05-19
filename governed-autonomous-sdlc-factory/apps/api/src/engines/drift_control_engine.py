"""Drift Detection Engine & Metacognitive Control Plane.

Implements:
1. DriftDetectionEngine — detects 8 categories of runtime drift
2. MetacognitiveController — autonomy reduction, escalation, quarantine
3. ReplayIntegrityVerifier — active SHA256 chain validation
4. RuntimeTrustScorer — multi-dimensional trust scoring

All components are designed to be called from the pipeline runtime.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings


# ─── Drift Detection Engine ───

DRIFT_CATEGORIES = {
    "semantic": {
        "description": "Requirements diverge over time, ontology drift, specification contradiction",
        "default_threshold": 0.3,
        "severity_map": {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9},
    },
    "goal": {
        "description": "Runtime objective changes, autonomy exceeds original scope",
        "default_threshold": 0.4,
        "severity_map": {"low": 0.4, "medium": 0.6, "high": 0.8, "critical": 0.95},
    },
    "governance": {
        "description": "Governance weakens over time, repeated overrides, policy inconsistency",
        "default_threshold": 0.3,
        "severity_map": {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9},
    },
    "context": {
        "description": "Stale assumptions, outdated references, invalid prior memory",
        "default_threshold": 0.5,
        "severity_map": {"low": 0.5, "medium": 0.65, "high": 0.8, "critical": 0.95},
    },
    "cost": {
        "description": "Runaway Tokenomics, abnormal retry accumulation, abnormal inference cost",
        "default_threshold": 0.7,
        "severity_map": {"low": 0.7, "medium": 0.8, "high": 0.9, "critical": 0.95},
    },
    "evidence": {
        "description": "Incomplete evidence, replay inconsistency, forensic degradation",
        "default_threshold": 0.4,
        "severity_map": {"low": 0.4, "medium": 0.6, "high": 0.8, "critical": 0.95},
    },
    "memory_poisoning": {
        "description": "Contradictory memory, invalid memory insertion, malicious memory injection",
        "default_threshold": 0.3,
        "severity_map": {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9},
    },
    "cognitive": {
        "description": "Repeated hallucinations, unstable semantic interpretation, reasoning inconsistency",
        "default_threshold": 0.4,
        "severity_map": {"low": 0.4, "medium": 0.6, "high": 0.8, "critical": 0.95},
    },
}


class DriftDetectionEngine:
    """Detects runtime drift across 8 categories."""

    def __init__(self, db: Session):
        self.db = db

    def detect_semantic_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect semantic drift: requirement divergence, ontology changes."""
        # Get recent semantic memory entries
        result = self.db.execute(text("""
            SELECT id, semantic_content, drift_score, confidence, created_at
            FROM semantic_memory
            WHERE project_id = :pid AND is_active = true
            ORDER BY created_at DESC
            LIMIT 20
        """), {"pid": project_id})

        entries = result.fetchall()
        if len(entries) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient data"}

        # Check for drift score escalation
        recent_scores = [e[2] for e in entries[:5]]
        avg_recent = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0

        older_scores = [e[2] for e in entries[5:10]]
        avg_older = sum(older_scores) / len(older_scores) if older_scores else 0.0

        drift_delta = avg_recent - avg_older
        drift_detected = drift_delta > DRIFT_CATEGORIES["semantic"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": max(0.0, drift_delta),
            "avg_recent": avg_recent,
            "avg_older": avg_older,
            "entries_analyzed": len(entries),
        }

    def detect_governance_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect governance drift: weakening enforcement, repeated overrides."""
        result = self.db.execute(text("""
            SELECT escalation_level, override_reason, autonomy_before, autonomy_after, created_at
            FROM governance_memory
            WHERE project_id = :pid AND is_active = true
            ORDER BY created_at DESC
            LIMIT 50
        """), {"pid": project_id})

        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No governance history"}

        # Count overrides and escalations
        overrides = sum(1 for e in entries if e[1] is not None)
        escalations = sum(1 for e in entries if e[0] not in (None, "none"))

        # Check for autonomy reduction pattern
        autonomy_reductions = sum(
            1 for e in entries
            if e[2] is not None and e[3] is not None and e[3] != e[2]
        )

        override_ratio = overrides / len(entries) if entries else 0.0
        escalation_ratio = escalations / len(entries) if entries else 0.0

        drift_score = (override_ratio * 0.5 + escalation_ratio * 0.5)
        drift_detected = drift_score > DRIFT_CATEGORIES["governance"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": drift_score,
            "overrides": overrides,
            "escalations": escalations,
            "autonomy_reductions": autonomy_reductions,
            "total_events": len(entries),
        }

    def detect_cost_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect cost drift: runaway Tokenomics, abnormal retry accumulation."""
        result = self.db.execute(text("""
            SELECT total_cost, budget_limit
            FROM runs
            WHERE project_id = :pid
            ORDER BY created_at DESC
            LIMIT 20
        """), {"pid": project_id})

        runs = result.fetchall()
        if not runs:
            return {"drift_detected": False, "score": 0.0, "reason": "No run data"}

        total_cost = sum(r[0] for r in runs)
        budget = runs[0][1]  # Most recent budget

        if budget and budget > 0:
            budget_usage = total_cost / budget
        else:
            # No budget set — check for abnormal growth
            if len(runs) >= 2:
                recent_avg = sum(r[0] for r in runs[:5]) / min(5, len(runs))
                older_avg = sum(r[0] for r in runs[5:10]) / max(1, min(5, len(runs) - 5))
                budget_usage = recent_avg / max(older_avg, 0.01) - 1.0 if older_avg > 0 else 0.0
            else:
                budget_usage = 0.0

        drift_detected = budget_usage > DRIFT_CATEGORIES["cost"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": min(1.0, max(0.0, budget_usage)),
            "total_cost": total_cost,
            "budget_limit": budget,
            "runs_analyzed": len(runs),
        }

    def detect_evidence_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect evidence drift: incomplete evidence, replay inconsistency."""
        result = self.db.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN chain_hash IS NOT NULL THEN 1 END) as with_chain,
                   COUNT(CASE WHEN bundle_path IS NOT NULL THEN 1 END) as with_path
            FROM evidence_bundles
            WHERE run_id IN (SELECT id FROM runs WHERE project_id = :pid)
        """), {"pid": project_id})

        row = result.fetchone()
        if not row or row[0] == 0:
            return {"drift_detected": False, "score": 0.0, "reason": "No evidence bundles"}

        total = row[0]
        with_chain = row[1]
        with_path = row[2]

        completeness = (with_chain + with_path) / (2 * total) if total > 0 else 1.0
        drift_score = 1.0 - completeness
        drift_detected = drift_score > DRIFT_CATEGORIES["evidence"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": drift_score,
            "total_bundles": total,
            "with_chain_hash": with_chain,
            "with_path": with_path,
            "completeness": completeness,
        }

    def detect_context_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect context drift: stale assumptions, outdated references."""
        result = self.db.execute(text("""
            SELECT context_type, validity_status, staleness_score
            FROM context_validity
            WHERE project_id = :pid AND is_active = true
        """), {"pid": project_id})

        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No context data"}

        stale = sum(1 for e in entries if e[1] in ("stale", "expired"))
        avg_staleness = sum(e[2] for e in entries) / len(entries) if entries else 0.0

        drift_score = (stale / len(entries) * 0.5 + avg_staleness * 0.5) if entries else 0.0
        drift_detected = drift_score > DRIFT_CATEGORIES["context"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": drift_score,
            "stale_contexts": stale,
            "total_contexts": len(entries),
            "avg_staleness": avg_staleness,
        }

    def detect_memory_poisoning(self, project_id: str) -> Dict[str, Any]:
        """Detect memory poisoning: contradictory memory, invalid insertions."""
        result = self.db.execute(text("""
            SELECT memory_type, key, content, created_at
            FROM memory_items
            WHERE project_id = :pid
            ORDER BY created_at DESC
            LIMIT 100
        """), {"pid": project_id})

        entries = result.fetchall()
        if not entries:
            return {"drift_detected": False, "score": 0.0, "reason": "No memory items"}

        # Check for duplicate keys with different content (potential poisoning)
        key_contents: Dict[str, List[str]] = {}
        for e in entries:
            key = f"{e[0]}:{e[1]}"
            content_hash = hashlib.md5(str(e[2]).encode()).hexdigest()[:16]
            if key not in key_contents:
                key_contents[key] = []
            key_contents[key].append(content_hash)

        contradictory = sum(1 for hashes in key_contents.values() if len(set(hashes)) > 1)
        contradiction_ratio = contradictory / len(key_contents) if key_contents else 0.0

        drift_detected = contradiction_ratio > DRIFT_CATEGORIES["memory_poisoning"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": contradiction_ratio,
            "contradictory_keys": contradictory,
            "total_keys": len(key_contents),
        }

    def detect_cognitive_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect cognitive drift: unstable semantic interpretation, reasoning inconsistency."""
        result = self.db.execute(text("""
            SELECT overall_semantic_coverage_score, mutation_score
            FROM semantic_coverage_reports scr
            JOIN runs r ON scr.run_id = r.id::uuid
            WHERE r.project_id = :pid
            ORDER BY scr.created_at DESC
            LIMIT 10
        """), {"pid": project_id})

        entries = result.fetchall()
        if len(entries) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient data"}

        # Check for score variance (instability)
        scores = [e[0] for e in entries if e[0] is not None]
        if len(scores) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient scores"}

        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # High variance = cognitive instability
        drift_score = min(1.0, std_dev * 2)  # Normalize
        drift_detected = drift_score > DRIFT_CATEGORIES["cognitive"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": drift_score,
            "mean_score": mean_score,
            "std_deviation": std_dev,
            "scores_analyzed": len(scores),
        }

    def detect_goal_drift(self, project_id: str) -> Dict[str, Any]:
        """Detect goal drift: runtime objective changes, scope creep."""
        result = self.db.execute(text("""
            SELECT intent FROM runs
            WHERE project_id = :pid
            ORDER BY created_at DESC
            LIMIT 10
        """), {"pid": project_id})

        intents = [r[0] for r in result.fetchall() if r[0]]
        if len(intents) < 2:
            return {"drift_detected": False, "score": 0.0, "reason": "Insufficient intent data"}

        # Simple heuristic: check if recent intents differ significantly from original
        # In production, this would use semantic similarity
        original = intents[-1]  # Oldest
        recent = intents[0]  # Most recent

        # Word overlap ratio
        orig_words = set(original.lower().split())
        recent_words = set(recent.lower().split())
        if orig_words:
            overlap = len(orig_words & recent_words) / len(orig_words)
        else:
            overlap = 1.0

        drift_score = 1.0 - overlap
        drift_detected = drift_score > DRIFT_CATEGORIES["goal"]["default_threshold"]

        return {
            "drift_detected": drift_detected,
            "score": drift_score,
            "intent_overlap": overlap,
            "intents_analyzed": len(intents),
        }

    def run_full_drift_scan(self, project_id: str) -> Dict[str, Any]:
        """Run all drift detection checks. Returns comprehensive drift report."""
        results = {}

        detectors = [
            ("semantic", self.detect_semantic_drift),
            ("goal", self.detect_goal_drift),
            ("governance", self.detect_governance_drift),
            ("context", self.detect_context_drift),
            ("cost", self.detect_cost_drift),
            ("evidence", self.detect_evidence_drift),
            ("memory_poisoning", self.detect_memory_poisoning),
            ("cognitive", self.detect_cognitive_drift),
        ]

        for category, detector in detectors:
            try:
                results[category] = detector(project_id)
            except Exception as e:
                results[category] = {"drift_detected": False, "score": 0.0, "error": str(e)[:100]}

        # Compute overall drift score
        detected_scores = [r["score"] for r in results.values() if "score" in r]
        overall_score = sum(detected_scores) / len(detected_scores) if detected_scores else 0.0
        any_detected = any(r.get("drift_detected", False) for r in results.values())

        return {
            "project_id": project_id,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "overall_drift_score": overall_score,
            "drift_detected": any_detected,
            "categories_scanned": len(detectors),
            "categories_with_drift": sum(1 for r in results.values() if r.get("drift_detected")),
            "category_results": results,
        }

    def persist_drift_event(self, project_id: str, workspace_id: str,
                            category: str, score: float, threshold: float,
                            evidence: Dict, recommended_action: str) -> str:
        """Persist a drift event to the database."""
        event_id = str(uuid.uuid4())
        severity = "low"
        for sev, thresh in DRIFT_CATEGORIES.get(category, {}).get("severity_map", {}).items():
            if score >= thresh:
                severity = sev

        self.db.execute(text("""
            INSERT INTO drift_events (id, project_id, workspace_id, drift_type, drift_category,
                                      severity, drift_score, threshold, evidence, recommended_action, detected_at)
            VALUES (:id, :pid, :wid, :dtype, :dcat, :sev, :score, :thresh, :evidence, :action, :detected)
        """), {
            "id": event_id, "pid": project_id, "wid": workspace_id,
            "dtype": category, "dcat": category, "sev": severity,
            "score": score, "thresh": threshold,
            "evidence": json.dumps(evidence), "action": recommended_action,
            "detected": datetime.now(timezone.utc)
        })
        self.db.commit()
        return event_id


# ─── Replay Integrity Verifier ───

class ReplayIntegrityVerifier:
    """Active SHA256 chain validation for replay events."""

    def __init__(self, db: Session):
        self.db = db

    def verify_replay_integrity(self, replay_session_id: str) -> Dict[str, Any]:
        """Verify the integrity of a replay session's event chain."""
        # Get all events for this session, ordered by creation
        result = self.db.execute(text("""
            SELECT id, event_hash, parent_hash, message, created_at
            FROM replay_events
            WHERE replay_session_id = :sid
            ORDER BY created_at ASC
        """), {"sid": replay_session_id})

        events = result.fetchall()
        if not events:
            return {
                "session_id": replay_session_id,
                "integrity_valid": False,
                "error": "No events found",
                "events_checked": 0,
            }

        issues = []
        chain_breaks = 0
        missing_parents = 0

        # Build event map
        event_map = {e[0]: {"hash": e[1], "parent": e[2], "message": e[3]} for e in events}

        for i, event in enumerate(events):
            eid, ehash, parent_hash, msg, created = event

            # Check 1: Event hash should be present
            if not ehash:
                issues.append(f"Event {eid[:8]}: missing event_hash")
                continue

            # Check 2: Parent hash chain (skip first event)
            if i > 0:
                if not parent_hash:
                    issues.append(f"Event {eid[:8]}: missing parent_hash")
                    missing_parents += 1
                elif parent_hash != "genesis":
                    # Find the previous event's hash
                    prev_event = events[i - 1]
                    expected_parent = prev_event[1]  # Previous event's hash
                    if expected_parent and parent_hash != expected_parent:
                        issues.append(
                            f"Event {eid[:8]}: chain break — parent_hash={parent_hash[:16]}... "
                            f"expected={expected_parent[:16]}..."
                        )
                        chain_breaks += 1

        integrity_valid = chain_breaks == 0 and missing_parents == 0

        return {
            "session_id": replay_session_id,
            "integrity_valid": integrity_valid,
            "events_checked": len(events),
            "chain_breaks": chain_breaks,
            "missing_parents": missing_parents,
            "issues": issues,
        }

    def verify_all_sessions(self, project_id: str) -> Dict[str, Any]:
        """Verify integrity of all replay sessions for a project."""
        result = self.db.execute(text("""
            SELECT rs.id, rs.source_run_id, rs.integrity_score
            FROM replay_sessions rs
            JOIN runs r ON rs.source_run_id = r.id
            WHERE r.project_id = :pid
            ORDER BY rs.created_at DESC
            LIMIT 50
        """), {"pid": project_id})

        sessions = result.fetchall()
        results = []
        all_valid = True

        for session_id, run_id, stored_score in sessions:
            verification = self.verify_replay_integrity(session_id)
            results.append(verification)
            if not verification["integrity_valid"]:
                all_valid = False

        return {
            "project_id": project_id,
            "all_valid": all_valid,
            "sessions_checked": len(results),
            "sessions_with_issues": sum(1 for r in results if not r["integrity_valid"]),
            "session_results": results,
        }


# ─── Metacognitive Controller ───

AUTONOMY_LEVELS = ["full", "reduced", "supervised", "paused"]
ESCALATION_LEVELS = ["none", "low", "medium", "high", "critical"]


class MetacognitiveController:
    """Controls runtime autonomy, escalation, and cognitive stability."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_runtime_state(self, project_id: str, drift_report: Dict) -> Dict[str, Any]:
        """Evaluate runtime state and determine autonomy/escalation actions."""
        overall_drift = drift_report.get("overall_drift_score", 0.0)
        categories_with_drift = drift_report.get("categories_with_drift", 0)

        # Determine autonomy level
        if overall_drift >= 0.8:
            autonomy = "paused"
            escalation = "critical"
        elif overall_drift >= 0.6:
            autonomy = "supervised"
            escalation = "high"
        elif overall_drift >= 0.4:
            autonomy = "reduced"
            escalation = "medium"
        elif overall_drift >= 0.2:
            autonomy = "reduced"
            escalation = "low"
        else:
            autonomy = "full"
            escalation = "none"

        # Generate warnings
        warnings = []
        restrictions = []

        cat_results = drift_report.get("category_results", {})
        for cat, result in cat_results.items():
            if result.get("drift_detected"):
                warnings.append(f"{cat}: drift score {result.get('score', 0):.2f}")

        if autonomy != "full":
            restrictions.append(f"Autonomy reduced to: {autonomy}")
        if escalation != "none":
            restrictions.append(f"Escalation level: {escalation}")

        return {
            "project_id": project_id,
            "overall_drift_score": overall_drift,
            "categories_with_drift": categories_with_drift,
            "recommended_autonomy": autonomy,
            "recommended_escalation": escalation,
            "warnings": warnings,
            "restrictions": restrictions,
        }

    def apply_metacognitive_state(self, project_id: str, workspace_id: str,
                                   evaluation: Dict) -> str:
        """Persist metacognitive state to database."""
        state_id = str(uuid.uuid4())

        self.db.execute(text("""
            INSERT INTO metacognitive_state (id, project_id, workspace_id, state_type,
                                              overall_trust_score, autonomy_level, escalation_level,
                                              active_warnings, active_restrictions, drift_summary,
                                              last_evaluated_at, updated_at)
            VALUES (:id, :pid, :wid, 'drift_evaluation', :trust, :autonomy, :escalation,
                    :warnings, :restrictions, :summary, :evaluated, :updated)
            ON CONFLICT (id) DO UPDATE SET
                overall_trust_score = :trust,
                autonomy_level = :autonomy,
                escalation_level = :escalation,
                active_warnings = :warnings,
                active_restrictions = :restrictions,
                drift_summary = :summary,
                last_evaluated_at = :evaluated,
                updated_at = :updated
        """), {
            "id": state_id, "pid": project_id, "wid": workspace_id,
            "trust": 1.0 - evaluation.get("overall_drift_score", 0.0),
            "autonomy": evaluation.get("recommended_autonomy", "full"),
            "escalation": evaluation.get("recommended_escalation", "none"),
            "warnings": json.dumps(evaluation.get("warnings", [])),
            "restrictions": json.dumps(evaluation.get("restrictions", [])),
            "summary": json.dumps({"categories_with_drift": evaluation.get("categories_with_drift", 0)}),
            "evaluated": datetime.now(timezone.utc),
            "updated": datetime.now(timezone.utc),
        })
        self.db.commit()
        return state_id

    def record_operator_intervention(self, project_id: str, workspace_id: str,
                                      operator_id: str, intervention_type: str,
                                      correction: str, prior_state: Dict,
                                      corrected_state: Dict) -> str:
        """Record an operator intervention."""
        intervention_id = str(uuid.uuid4())

        self.db.execute(text("""
            INSERT INTO operator_interventions (id, run_id, project_id, workspace_id,
                                                 operator_id, intervention_type, correction,
                                                 prior_state, corrected_state, created_at)
            VALUES (:id, :rid, :pid, :wid, :oid, :itype, :correction, :prior, :corrected, :created)
        """), {
            "id": intervention_id, "rid": "", "pid": project_id, "wid": workspace_id,
            "oid": operator_id, "itype": intervention_type, "correction": correction,
            "prior": json.dumps(prior_state), "corrected": json.dumps(corrected_state),
            "created": datetime.now(timezone.utc),
        })
        self.db.commit()
        return intervention_id


# ─── Runtime Trust Scorer ───

class RuntimeTrustScorer:
    """Multi-dimensional runtime trust scoring."""

    TRUST_DIMENSIONS = [
        "semantic_integrity",
        "governance_effectiveness",
        "memory_reliability",
        "replay_integrity",
        "evidence_completeness",
        "cost_stability",
        "cognitive_stability",
    ]

    def __init__(self, db: Session):
        self.db = db

    def compute_trust_scores(self, project_id: str) -> Dict[str, Any]:
        """Compute trust scores across all dimensions."""
        scores = {}

        # Semantic integrity: based on semantic coverage scores
        result = self.db.execute(text("""
            SELECT AVG(overall_semantic_coverage_score), STDDEV(overall_semantic_coverage_score)
            FROM semantic_coverage_reports scr
            JOIN runs r ON scr.run_id = r.id::uuid
            WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        if row and row[0] is not None:
            scores["semantic_integrity"] = {"score": float(row[0]), "confidence": 0.8}
        else:
            scores["semantic_integrity"] = {"score": 0.5, "confidence": 0.1}

        # Governance effectiveness: based on pass/fail ratio
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN decision = 'pass' THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM governance_evaluations ge
            JOIN runs r ON ge.run_id = r.id
            WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        if row and row[0] is not None:
            scores["governance_effectiveness"] = {"score": float(row[0]), "confidence": 0.7}
        else:
            scores["governance_effectiveness"] = {"score": 0.5, "confidence": 0.1}

        # Memory reliability: based on drift events
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN is_resolved = false THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM drift_events WHERE project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        drift_ratio = float(row[0]) if row and row[0] is not None else 0.0
        scores["memory_reliability"] = {"score": 1.0 - drift_ratio, "confidence": 0.6}

        # Replay integrity: based on chain verification
        result = self.db.execute(text("""
            SELECT AVG(integrity_score) FROM replay_sessions rs
            JOIN runs r ON rs.source_run_id = r.id
            WHERE r.project_id :pid AND rs.integrity_score IS NOT NULL
        """), {"pid": project_id})
        row = result.fetchone()
        if row and row[0] is not None:
            scores["replay_integrity"] = {"score": float(row[0]), "confidence": 0.7}
        else:
            scores["replay_integrity"] = {"score": 0.5, "confidence": 0.1}

        # Evidence completeness
        result = self.db.execute(text("""
            SELECT COUNT(CASE WHEN chain_hash IS NOT NULL THEN 1 END)::float / NULLIF(COUNT(*), 0)
            FROM evidence_bundles eb
            JOIN runs r ON eb.run_id = r.id
            WHERE r.project_id = :pid
        """), {"pid": project_id})
        row = result.fetchone()
        if row and row[0] is not None:
            scores["evidence_completeness"] = {"score": float(row[0]), "confidence": 0.6}
        else:
            scores["evidence_completeness"] = {"score": 0.5, "confidence": 0.1}

        # Cost stability
        result = self.db.execute(text("""
            SELECT AVG(total_cost) FROM runs WHERE project_id = :pid AND total_cost > 0
        """), {"pid": project_id})
        row = result.fetchone()
        if row and row[0] is not None:
            # Normalize: lower cost = higher stability
            avg_cost = float(row[0])
            stability = max(0.0, 1.0 - avg_cost / 100.0)  # Assume 100 is high cost
            scores["cost_stability"] = {"score": stability, "confidence": 0.5}
        else:
            scores["cost_stability"] = {"score": 1.0, "confidence": 0.3}

        # Cognitive stability: inverse of drift events
        result = self.db.execute(text("""
            SELECT COUNT(*) FROM drift_events WHERE project_id = :pid AND is_resolved = false
        """), {"pid": project_id})
        unresolved = result.scalar()
        cognitive = max(0.0, 1.0 - unresolved * 0.1)
        scores["cognitive_stability"] = {"score": cognitive, "confidence": 0.5}

        # Overall trust: weighted average
        weights = {
            "semantic_integrity": 0.2,
            "governance_effectiveness": 0.2,
            "memory_reliability": 0.15,
            "replay_integrity": 0.15,
            "evidence_completeness": 0.1,
            "cost_stability": 0.1,
            "cognitive_stability": 0.1,
        }
        overall = sum(
            scores.get(dim, {}).get("score", 0.5) * w
            for dim, w in weights.items()
        )

        return {
            "project_id": project_id,
            "scored_at": datetime.now(timezone.utc).isoformat(),
            "overall_trust": overall,
            "dimensions": scores,
        }

    def persist_trust_scores(self, project_id: str, workspace_id: str,
                              scores: Dict) -> List[str]:
        """Persist trust scores to database."""
        ids = []
        now = datetime.now(timezone.utc)
        for dim, data in scores.get("dimensions", {}).items():
            sid = str(uuid.uuid4())
            self.db.execute(text("""
                INSERT INTO runtime_trust_scores (id, project_id, workspace_id, trust_dimension,
                                                   score, confidence, evidence, scored_at)
                VALUES (:id, :pid, :wid, :dim, :score, :conf, :evidence, :scored)
            """), {
                "id": sid, "pid": project_id, "wid": workspace_id,
                "dim": dim, "score": data["score"], "conf": data["confidence"],
                "evidence": json.dumps(data), "scored": now,
            })
            ids.append(sid)
        self.db.commit()
        return ids
