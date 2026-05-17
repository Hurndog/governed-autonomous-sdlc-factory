"""Synchronous Integrity Verification Runtime.

Provides a completely independent sync integrity verification engine
that runs in a thread pool, avoiding async/greenlet conflicts.

Pattern mirrors replay_runtime_sync.py:
    FastAPI Route (async)
    → loop.run_in_executor(integrity_executor, verify_integrity_sync, run_id)
    → IntegrityVerifier (sync)
    → SyncSessionLocal (sync SQLAlchemy)
    → structured integrity report

No async. No greenlet. No event loop. Pure sync execution.
"""
import time
import uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.sync_database import SyncSessionLocal
from src.core.hashing import (
    compute_hash, compute_chain_hash, compute_timeline_chain_hash,
    compute_artifact_hash, compute_event_hash, compute_snapshot_hash,
    compute_traceability_hash, compute_governance_hash,
    _filter_metadata_for_hash,
)
from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, GovernanceReleaseGate, GovernancePolicy,
)
from src.core.logging import get_logger

logger = get_logger("integrity_runtime_sync")

# Dedicated thread pool for integrity verification
_integrity_executor = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="sync-integrity",
)


class IntegrityComponentResult:
    """Result of a single integrity check component."""

    def __init__(self, verification_type: str, status: str, integrity_score: float,
                 expected_hash: Optional[str] = None, actual_hash: Optional[str] = None,
                 details: Optional[dict] = None):
        self.verification_type = verification_type
        self.status = status
        self.integrity_score = integrity_score
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.details = details or {}


class IntegrityReport:
    """Complete integrity report for a run."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.overall_score: float = 0.0
        self.total_checks: int = 0
        self.passed_checks: int = 0
        self.failed_checks: int = 0
        self.warning_checks: int = 0
        self.generated_at: str = ""
        self.results: dict[str, IntegrityComponentResult] = {}

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "overall_score": self.overall_score,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warning_checks": self.warning_checks,
            "generated_at": self.generated_at,
            "results": {
                k: {
                    "status": v.status,
                    "score": v.integrity_score,
                    "details": v.details,
                }
                for k, v in self.results.items()
            },
        }


class IntegrityVerifier:
    """Synchronous integrity verifier using sync SQLAlchemy sessions."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    def verify(self) -> IntegrityReport:
        """Run all integrity checks and produce a comprehensive report."""
        report = IntegrityReport(self.run_id)
        session = SyncSessionLocal()

        try:
            # Verify run exists
            run = session.get(Run, self.run_id)
            if not run:
                report.results["run"] = IntegrityComponentResult(
                    verification_type="run",
                    status="fail",
                    integrity_score=0.0,
                    details={"message": f"Run {self.run_id} not found"},
                )
                report.total_checks = 1
                report.failed_checks = 1
                report.generated_at = datetime.now(timezone.utc).isoformat()
                return report

            # Run all checks
            results = []
            results.append(self._verify_event_chain(session))
            results.append(self._verify_snapshot_integrity(session))
            results.append(self._verify_artifact_integrity(session))
            results.append(self._verify_timeline_chain(session))
            results.append(self._verify_traceability_integrity(session))
            results.append(self._verify_governance_integrity(session))
            results.append(self._verify_semantic_coverage(session))  # NEW: 7th component

            # Build report
            report.total_checks = len(results)
            for r in results:
                report.results[r.verification_type] = r
                if r.status == "pass":
                    report.passed_checks += 1
                elif r.status == "fail":
                    report.failed_checks += 1
                elif r.status == "warning":
                    report.warning_checks += 1

            report.overall_score = (
                sum(r.integrity_score for r in results) / len(results)
                if results else 0.0
            )
            report.overall_score = round(report.overall_score, 4)
            report.generated_at = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            logger.error(f"Integrity verification failed for run {self.run_id}: {e}", exc_info=True)
            report.results["error"] = IntegrityComponentResult(
                verification_type="error",
                status="fail",
                integrity_score=0.0,
                details={"message": str(e)},
            )
            report.total_checks = 1
            report.failed_checks = 1
        finally:
            session.close()

        return report

    def _verify_event_chain(self, session: Session) -> IntegrityComponentResult:
        """Verify event chain hash continuity."""
        events = list(session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        ).scalars().all())

        if not events:
            return IntegrityComponentResult(
                verification_type="event_chain",
                status="warning",
                integrity_score=0.0,
                details={"message": "No events found for this run"},
            )

        broken_links = 0
        missing_hashes = 0
        chain_hash = "GENESIS"

        for event in events:
            if event.event_hash:
                expected_chain = compute_chain_hash(chain_hash, event.event_hash)
                if event.chain_hash and event.chain_hash != expected_chain:
                    broken_links += 1
                chain_hash = expected_chain
            else:
                missing_hashes += 1
                expected_event_hash = compute_event_hash(
                    run_id=self.run_id,
                    event_type="log",
                    message=event.message,
                    timestamp=event.created_at.isoformat() if event.created_at else "",
                    severity=event.severity,
                    source_file=event.source_file,
                    phase_id=event.phase_id,
                    trace_id=event.trace_id,
                )
                chain_hash = compute_chain_hash(chain_hash, expected_event_hash)

        total_events = len(events)
        if missing_hashes == 0 and broken_links == 0:
            score = 1.0
            status = "pass"
        elif broken_links == 0 and missing_hashes < total_events * 0.5:
            score = 0.7
            status = "warning"
        else:
            score = max(0.0, 1.0 - (broken_links / total_events)) if total_events > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="event_chain",
            status=status,
            integrity_score=round(score, 4),
            details={
                "total_events": total_events,
                "events_with_hashes": total_events - missing_hashes,
                "broken_chain_links": broken_links,
                "missing_hashes": missing_hashes,
                "final_chain_hash": chain_hash,
            },
        )

    def _verify_snapshot_integrity(self, session: Session) -> IntegrityComponentResult:
        """Verify snapshot state hashes."""
        snaps = list(session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        ).scalars().all())

        if not snaps:
            return IntegrityComponentResult(
                verification_type="snapshot",
                status="warning",
                integrity_score=0.0,
                details={"message": "No snapshots found for this run"},
            )

        verified = 0
        mismatched = 0
        missing_hashes = 0

        for snap in snaps:
            if snap.snapshot_hash:
                expected = compute_snapshot_hash(
                    run_id=self.run_id,
                    snapshot_type=snap.snapshot_type,
                    state_data=snap.state_data or {},
                    phase_states=snap.phase_states or {},
                    artifact_states=snap.artifact_states or {},
                    cost_summary=snap.cost_summary or {},
                    governance_summary=snap.governance_summary or {},
                )
                if snap.snapshot_hash == expected:
                    verified += 1
                else:
                    mismatched += 1
            else:
                missing_hashes += 1

        total = len(snaps)
        if missing_hashes == 0 and mismatched == 0:
            score = 1.0
            status = "pass"
        elif mismatched == 0:
            score = verified / total if total > 0 else 0.0
            status = "warning"
        else:
            score = max(0.0, (verified - mismatched) / total) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="snapshot",
            status=status,
            integrity_score=round(score, 4),
            details={
                "total_snapshots": total,
                "verified": verified,
                "mismatched": mismatched,
                "missing_hashes": missing_hashes,
            },
        )

    def _verify_artifact_integrity(self, session: Session) -> IntegrityComponentResult:
        """Verify artifact content hashes."""
        artifacts = list(session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        ).scalars().all())

        if not artifacts:
            return IntegrityComponentResult(
                verification_type="artifact",
                status="warning",
                integrity_score=0.0,
                details={"message": "No artifacts found for this run"},
            )

        verified = 0
        mismatched = 0
        missing_hashes = 0

        for art in artifacts:
            if art.artifact_hash:
                safe_metadata = _filter_metadata_for_hash(art.metadata_)
                expected = compute_artifact_hash(
                    artifact_type=art.artifact_type,
                    name=art.name,
                    content=art.content,
                    phase_name=art.phase_name,
                    metadata=safe_metadata,
                )
                if art.artifact_hash == expected:
                    verified += 1
                else:
                    mismatched += 1
            else:
                missing_hashes += 1

        total = len(artifacts)
        if missing_hashes == 0 and mismatched == 0:
            score = 1.0
            status = "pass"
        elif mismatched == 0:
            score = verified / total if total > 0 else 0.0
            status = "warning"
        else:
            score = max(0.0, (verified - mismatched) / total) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="artifact",
            status=status,
            integrity_score=round(score, 4),
            details={
                "total_artifacts": total,
                "verified": verified,
                "mismatched": mismatched,
                "missing_hashes": missing_hashes,
            },
        )

    def _verify_timeline_chain(self, session: Session) -> IntegrityComponentResult:
        """Verify timeline chain integrity."""
        events = list(session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        ).scalars().all())

        if not events:
            return IntegrityComponentResult(
                verification_type="timeline",
                status="warning",
                integrity_score=0.0,
                details={"message": "No events found"},
            )

        timeline_events = []
        for e in events:
            timeline_events.append({
                "id": e.id,
                "severity": e.severity,
                "message": e.message,
                "timestamp": e.created_at.isoformat() if e.created_at else "",
                "source_file": e.source_file or "",
                "phase_id": e.phase_id or "",
                "trace_id": e.trace_id or "",
            })

        computed_chain_hash = compute_timeline_chain_hash(timeline_events)

        ordering_violations = 0
        for i in range(1, len(events)):
            if events[i].created_at and events[i - 1].created_at:
                if events[i].created_at < events[i - 1].created_at:
                    ordering_violations += 1

        total = len(events)
        if ordering_violations == 0:
            score = 1.0
            status = "pass"
        else:
            score = max(0.0, 1.0 - (ordering_violations / total)) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="timeline",
            status=status,
            integrity_score=round(score, 4),
            expected_hash=computed_chain_hash,
            details={
                "total_events": total,
                "ordering_violations": ordering_violations,
                "timeline_chain_hash": computed_chain_hash,
            },
        )

    def _verify_traceability_integrity(self, session: Session) -> IntegrityComponentResult:
        """Verify traceability link edge hashes."""
        links = list(session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        ).scalars().all())

        if not links:
            return IntegrityComponentResult(
                verification_type="traceability",
                status="warning",
                integrity_score=0.0,
                details={"message": "No traceability links found"},
            )

        verified = 0
        mismatched = 0
        missing_hashes = 0

        for link in links:
            if link.edge_hash:
                expected = compute_traceability_hash(
                    source_type=link.source_type,
                    source_id=link.source_id,
                    target_type=link.target_type,
                    target_id=link.target_id,
                    link_type=link.link_type,
                    run_id=link.run_id,
                )
                if link.edge_hash == expected:
                    verified += 1
                else:
                    mismatched += 1
            else:
                missing_hashes += 1

        total = len(links)
        if missing_hashes == 0 and mismatched == 0:
            score = 1.0
            status = "pass"
        elif mismatched == 0:
            score = verified / total if total > 0 else 0.0
            status = "warning"
        else:
            score = max(0.0, (verified - mismatched) / total) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="traceability",
            status=status,
            integrity_score=round(score, 4),
            details={
                "total_links": total,
                "verified": verified,
                "mismatched": mismatched,
                "missing_hashes": missing_hashes,
            },
        )

    def _verify_governance_integrity(self, session: Session) -> IntegrityComponentResult:
        """Verify governance evaluation integrity hashes."""
        evals = list(session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        ).scalars().all())

        if not evals:
            return IntegrityComponentResult(
                verification_type="governance",
                status="warning",
                integrity_score=0.0,
                details={"message": "No governance evaluations found"},
            )

        verified = 0
        mismatched = 0
        missing_hashes = 0

        for ev in evals:
            if ev.integrity_hash:
                # Load policy name
                policy_name = "unknown"
                if ev.policy_id:
                    policy = session.get(GovernancePolicy, ev.policy_id)
                    if policy:
                        policy_name = policy.name

                # Recompute hash using the same structure as the pipeline:
                # input_data={"findings": findings}, output_data={"decision": decision}
                expected = compute_governance_hash(
                    policy_name=policy_name,
                    decision=ev.decision,
                    input_data={"findings": ev.findings} if ev.findings else {},
                    output_data={"decision": ev.decision},
                    run_id=ev.run_id,
                    artifact_id=ev.artifact_id,
                )
                if ev.integrity_hash == expected:
                    verified += 1
                else:
                    mismatched += 1
            else:
                missing_hashes += 1

        total = len(evals)
        if missing_hashes == 0 and mismatched == 0:
            score = 1.0
            status = "pass"
        elif mismatched == 0:
            score = verified / total if total > 0 else 0.0
            status = "warning"
        else:
            score = max(0.0, (verified - mismatched) / total) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityComponentResult(
            verification_type="governance",
            status=status,
            integrity_score=round(score, 4),
            details={
                "total_evaluations": total,
                "verified": verified,
                "mismatched": mismatched,
                "missing_hashes": missing_hashes,
            },
        )

    def _verify_semantic_coverage(self, session: Session) -> IntegrityComponentResult:
        """Verify semantic coverage — the 7th integrity component."""
        try:
            from src.core.models_semantic_coverage import SemanticCoverageReport

            report = session.execute(
                select(SemanticCoverageReport).where(
                    SemanticCoverageReport.run_id == self.run_id
                )
            ).scalar_one_or_none()

            if not report:
                return IntegrityComponentResult(
                    verification_type="semantic_coverage",
                    status="warning",
                    integrity_score=0.0,
                    details={
                        "message": "No semantic coverage report for this run",
                        "status": "pre_semantic_coverage",
                    },
                )

            score = report.overall_semantic_coverage_score
            status = "pass" if score >= 0.90 else "warning" if score >= 0.50 else "fail"

            return IntegrityComponentResult(
                verification_type="semantic_coverage",
                status=status,
                integrity_score=round(score, 4),
                details={
                    "overall_score": score,
                    "obligation_coverage": report.obligation_coverage_score,
                    "semantic_alignment": report.semantic_alignment_score,
                    "mutation_score": report.mutation_score,
                    "negative_coverage": report.negative_coverage_score,
                    "runtime_evidence": report.runtime_evidence_score,
                    "verifier_confidence": report.verifier_confidence_score,
                    "critical_requirements_passed": report.critical_requirements_passed,
                    "release_gate_status": report.release_gate_status,
                },
            )
        except Exception as e:
            logger.warning(f"Semantic coverage verification failed: {e}")
            return IntegrityComponentResult(
                verification_type="semantic_coverage",
                status="warning",
                integrity_score=0.0,
                details={"message": f"Semantic coverage check error: {str(e)}"},
            )


def verify_integrity_sync(run_id: str) -> dict:
    """Entry point for running synchronous integrity verification in a thread pool.

    This function is called via loop.run_in_executor() from the FastAPI route.
    It creates an IntegrityVerifier and runs all checks synchronously.

    Args:
        run_id: The run to verify

    Returns:
        Structured integrity report as dict
    """
    start = time.monotonic()
    verifier = IntegrityVerifier(run_id=run_id)
    report = verifier.verify()
    duration_ms = (time.monotonic() - start) * 1000
    logger.info(f"Integrity verification for run {run_id}: score={report.overall_score}, duration={duration_ms:.0f}ms")
    result = report.to_dict()
    result["duration_ms"] = round(duration_ms, 2)
    return result
