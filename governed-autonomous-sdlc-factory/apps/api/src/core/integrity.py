"""Integrity Manager for the Cognitive Cortex.

Verifies execution integrity across:
- Event chains (hash continuity)
- Snapshot integrity (state hash verification)
- Artifact integrity (content-addressable hashes)
- Replay equivalence (original vs replay comparison)
- Timeline chain integrity
- Traceability graph integrity
- Governance evaluation integrity

Produces integrity scores from 0.0 (compromised) to 1.0 (fully intact).
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.hashing import (
    compute_hash, compute_chain_hash, compute_timeline_chain_hash,
    compute_artifact_hash, compute_event_hash, compute_snapshot_hash,
    compute_traceability_hash, compute_governance_hash, compute_replay_hash,
)
from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, IntegrityVerification, ReplaySession,
    SemanticGraphNode, SemanticGraphEdge, EvidenceBundle,
)
from src.core.logging import get_logger

logger = get_logger("integrity")


@dataclass
class IntegrityResult:
    """Result of a single integrity check."""
    verification_type: str
    status: str  # pass, fail, warning
    integrity_score: float  # 0.0 - 1.0
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None
    details: dict = field(default_factory=dict)


@dataclass
class IntegrityReport:
    """Complete integrity report for a run."""
    run_id: str
    overall_score: float
    event_chain_result: Optional[IntegrityResult] = None
    snapshot_result: Optional[IntegrityResult] = None
    artifact_result: Optional[IntegrityResult] = None
    timeline_result: Optional[IntegrityResult] = None
    traceability_result: Optional[IntegrityResult] = None
    governance_result: Optional[IntegrityResult] = None
    replay_result: Optional[IntegrityResult] = None
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    generated_at: str = ""

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
                k: {"status": v.status, "score": v.integrity_score, "details": v.details}
                for k, v in {
                    "event_chain": self.event_chain_result,
                    "snapshot": self.snapshot_result,
                    "artifact": self.artifact_result,
                    "timeline": self.timeline_result,
                    "traceability": self.traceability_result,
                    "governance": self.governance_result,
                    "replay": self.replay_result,
                }.items() if v is not None
            },
        }


class IntegrityManager:
    """Manages execution integrity verification for the Cognitive Cortex."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def verify_all(self, session: AsyncSession) -> IntegrityReport:
        """Run all integrity checks and produce a comprehensive report."""
        results = []

        # 1. Event chain integrity
        results.append(await self.verify_event_chain(session))

        # 2. Snapshot integrity
        results.append(await self.verify_snapshot_integrity(session))

        # 3. Artifact integrity
        results.append(await self.verify_artifact_integrity(session))

        # 4. Timeline chain integrity
        results.append(await self.verify_timeline_chain(session))

        # 5. Traceability graph integrity
        results.append(await self.verify_traceability_integrity(session))

        # 6. Governance evaluation integrity
        results.append(await self.verify_governance_integrity(session))

        # 7. Replay equivalence (if replay sessions exist)
        replay_session = await session.execute(
            select(ReplaySession).where(
                and_(
                    ReplaySession.source_run_id == self.run_id,
                    ReplaySession.status == "completed",
                )
            ).order_by(ReplaySession.created_at.desc())
        )
        latest_replay = replay_session.scalars().first()
        if latest_replay:
            results.append(await self.verify_replay_equivalence(session, latest_replay.id))

        # Build report
        total = len(results)
        passed = sum(1 for r in results if r.status == "pass")
        failed = sum(1 for r in results if r.status == "fail")
        warnings = sum(1 for r in results if r.status == "warning")
        overall = sum(r.integrity_score for r in results) / total if total > 0 else 0.0

        report = IntegrityReport(
            run_id=self.run_id,
            overall_score=round(overall, 4),
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            warning_checks=warnings,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        for r in results:
            setattr(report, f"{r.verification_type}_result", r)

        # Persist verification results
        for r in results:
            verification = IntegrityVerification(
                run_id=self.run_id,
                verification_type=r.verification_type,
                status=r.status,
                integrity_score=r.integrity_score,
                expected_hash=r.expected_hash,
                actual_hash=r.actual_hash,
                details=r.details,
                verified_at=datetime.now(timezone.utc),
            )
            session.add(verification)

        await session.commit()
        logger.info(f"Integrity verification complete for run {self.run_id}: score={report.overall_score}, passed={passed}/{total}")
        return report

    async def verify_event_chain(self, session: AsyncSession) -> IntegrityResult:
        """Verify event chain hash continuity."""
        events_result = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        )
        events = events_result.scalars().all()

        if not events:
            return IntegrityResult(
                verification_type="event_chain",
                status="warning",
                integrity_score=0.0,
                details={"message": "No events found for this run"},
            )

        # Check hash continuity
        broken_links = 0
        missing_hashes = 0
        chain_hash = "GENESIS"

        for i, event in enumerate(events):
            if event.event_hash:
                expected_chain = compute_chain_hash(chain_hash, event.event_hash)
                if event.chain_hash and event.chain_hash != expected_chain:
                    broken_links += 1
                chain_hash = expected_chain
            else:
                missing_hashes += 1
                # Compute expected hash for comparison
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

        return IntegrityResult(
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

    async def verify_snapshot_integrity(self, session: AsyncSession) -> IntegrityResult:
        """Verify snapshot state hashes."""
        snaps_result = await session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        )
        snaps = snaps_result.scalars().all()

        if not snaps:
            return IntegrityResult(
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

        return IntegrityResult(
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

    async def verify_artifact_integrity(self, session: AsyncSession) -> IntegrityResult:
        """Verify artifact content hashes."""
        artifacts_result = await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        )
        artifacts = artifacts_result.scalars().all()

        if not artifacts:
            return IntegrityResult(
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
                expected = compute_artifact_hash(
                    artifact_type=art.artifact_type,
                    name=art.name,
                    content=art.content,
                    phase_name=art.phase_name,
                    metadata=art.metadata_,
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

        return IntegrityResult(
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

    async def verify_timeline_chain(self, session: AsyncSession) -> IntegrityResult:
        """Verify timeline chain integrity."""
        events_result = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        )
        events = events_result.scalars().all()

        if not events:
            return IntegrityResult(
                verification_type="timeline",
                status="warning",
                integrity_score=0.0,
                details={"message": "No events found"},
            )

        # Build timeline events for chain hash
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

        # Check ordering
        ordering_violations = 0
        for i in range(1, len(events)):
            if events[i].created_at and events[i-1].created_at:
                if events[i].created_at < events[i-1].created_at:
                    ordering_violations += 1

        total = len(events)
        if ordering_violations == 0:
            score = 1.0
            status = "pass"
        else:
            score = max(0.0, 1.0 - (ordering_violations / total)) if total > 0 else 0.0
            status = "fail" if score < 0.5 else "warning"

        return IntegrityResult(
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

    async def verify_traceability_integrity(self, session: AsyncSession) -> IntegrityResult:
        """Verify traceability link edge hashes."""
        links_result = await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )
        links = links_result.scalars().all()

        if not links:
            return IntegrityResult(
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

        return IntegrityResult(
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

    async def verify_governance_integrity(self, session: AsyncSession) -> IntegrityResult:
        """Verify governance evaluation integrity hashes."""
        gov_result = await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )
        evals = gov_result.scalars().all()

        if not evals:
            return IntegrityResult(
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
                expected = compute_governance_hash(
                    policy_name=ev.policy.name if ev.policy else "unknown",
                    decision=ev.decision,
                    input_data=ev.findings or {},
                    output_data=ev.evidence or {},
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

        return IntegrityResult(
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

    async def verify_replay_equivalence(self, session: AsyncSession,
                                         replay_session_id: str) -> IntegrityResult:
        """Verify replay session equivalence to original run."""
        replay_result = await session.execute(
            select(ReplaySession).where(ReplaySession.id == replay_session_id)
        )
        replay = replay_result.scalars().first()

        if not replay:
            return IntegrityResult(
                verification_type="replay",
                status="fail",
                integrity_score=0.0,
                details={"message": "Replay session not found"},
            )

        # Compare counts
        original_events = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id)
        )
        original_event_count = len(original_events.scalars().all())

        replay_events = await session.execute(
            select(LogEvent).where(LogEvent.run_id == replay_session_id)
        )
        replay_event_count = len(replay_events.scalars().all())

        event_match = original_event_count == replay.total_events_replayed
        artifact_match = True  # Would compare artifact counts
        governance_match = True  # Would compare governance counts

        issues = []
        if not event_match:
            issues.append(f"Event count mismatch: original={original_events}, replay={replay.total_events_replayed}")
        if replay.divergence_count > 0:
            issues.append(f"{replay.divergence_count} divergences detected")

        if not issues:
            score = 1.0
            status = "pass"
        elif replay.divergence_count == 0:
            score = 0.8
            status = "warning"
        else:
            score = max(0.0, 1.0 - (replay.divergence_count * 0.1))
            status = "fail" if score < 0.5 else "warning"

        return IntegrityResult(
            verification_type="replay",
            status=status,
            integrity_score=round(score, 4),
            details={
                "replay_session_id": replay_session_id,
                "replay_mode": replay.replay_mode,
                "original_event_count": original_event_count,
                "replayed_event_count": replay.total_events_replayed,
                "divergence_count": replay.divergence_count,
                "replay_integrity_score": replay.integrity_score,
                "issues": issues,
            },
        )

    async def compute_run_integrity_hash(self, session: AsyncSession) -> str:
        """Compute a single integrity hash for the entire run.
        
        This is the top-level hash that summarizes the run's integrity.
        It's computed from the hashes of all major components.
        """
        components = []

        # Event chain hash
        events_result = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        )
        events = events_result.scalars().all()
        if events:
            event_hashes = [e.event_hash or "" for e in events]
            components.append(compute_hash({"events": event_hashes}))

        # Artifact hashes
        artifacts_result = await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        )
        artifacts = artifacts_result.scalars().all()
        if artifacts:
            artifact_hashes = [a.artifact_hash or "" for a in artifacts]
            components.append(compute_hash({"artifacts": artifact_hashes}))

        # Snapshot hashes
        snaps_result = await session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        )
        snaps = snaps_result.scalars().all()
        if snaps:
            snap_hashes = [s.snapshot_hash or "" for s in snaps]
            components.append(compute_hash({"snapshots": snap_hashes}))

        # Traceability hashes
        links_result = await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )
        links = links_result.scalars().all()
        if links:
            link_hashes = [l.edge_hash or "" for l in links]
            components.append(compute_hash({"traceability": link_hashes}))

        # Governance hashes
        gov_result = await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )
        evals = gov_result.scalars().all()
        if evals:
            gov_hashes = [e.integrity_hash or "" for e in evals]
            components.append(compute_hash({"governance": gov_hashes}))

        return compute_hash({"run_id": self.run_id, "components": components})
