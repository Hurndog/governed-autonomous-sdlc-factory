"""Divergence Analyzer for the Cognitive Cortex.

Compares original runs against replays to detect:
- Event sequence divergence
- Artifact divergence
- Governance decision divergence
- Timing divergence
- Topology divergence
- Traceability divergence
- Integrity hash divergence
"""

import json
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, ReplaySession, DivergenceRecord,
)
from src.core.logging import get_logger

logger = get_logger("divergence")


@dataclass
class DivergenceFinding:
    """A single divergence finding."""
    divergence_type: str
    severity: str
    location: str
    expected: dict
    actual: dict
    causal_impact: str


@dataclass
class DivergenceReport:
    """Complete divergence analysis report."""
    run_id: str
    replay_session_id: str
    total_divergences: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    findings: list = field(default_factory=list)
    event_divergences: int = 0
    artifact_divergences: int = 0
    governance_divergences: int = 0
    timing_divergences: int = 0
    topology_divergences: int = 0
    traceability_divergences: int = 0
    integrity_divergences: int = 0
    generated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "replay_session_id": self.replay_session_id,
            "total_divergences": self.total_divergences,
            "severity_breakdown": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
            },
            "type_breakdown": {
                "event": self.event_divergences,
                "artifact": self.artifact_divergences,
                "governance": self.governance_divergences,
                "timing": self.timing_divergences,
                "topology": self.topology_divergences,
                "traceability": self.traceability_divergences,
                "integrity": self.integrity_divergences,
            },
            "findings": [
                {
                    "type": f.divergence_type,
                    "severity": f.severity,
                    "location": f.location,
                    "expected": f.expected,
                    "actual": f.actual,
                    "causal_impact": f.causal_impact,
                }
                for f in self.findings
            ],
            "generated_at": self.generated_at,
        }


class DivergenceAnalyzer:
    """Analyzes divergence between original runs and replays."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def analyze(self, session: AsyncSession, replay_session_id: str) -> DivergenceReport:
        """Run full divergence analysis between original run and replay."""
        report = DivergenceReport(
            run_id=self.run_id,
            replay_session_id=replay_session_id,
        )

        # Run all divergence checks
        await self._check_event_sequence_divergence(session, report)
        await self._check_artifact_divergence(session, report)
        await self._check_governance_divergence(session, report)
        await self._check_timing_divergence(session, report)
        await self._check_topology_divergence(session, report)
        await self._check_traceability_divergence(session, report)
        await self._check_integrity_divergence(session, report)

        # Update counts
        report.total_divergences = len(report.findings)
        report.critical_count = sum(1 for f in report.findings if f.severity == "critical")
        report.high_count = sum(1 for f in report.findings if f.severity == "high")
        report.medium_count = sum(1 for f in report.findings if f.severity == "medium")
        report.low_count = sum(1 for f in report.findings if f.severity == "low")
        report.info_count = sum(1 for f in report.findings if f.severity == "info")
        report.generated_at = datetime.now(timezone.utc).isoformat()

        # Persist divergence records
        for finding in report.findings:
            record = DivergenceRecord(
                replay_session_id=replay_session_id,
                run_id=self.run_id,
                divergence_type=finding.divergence_type,
                severity=finding.severity,
                divergence_location=finding.location,
                expected_value=finding.expected,
                actual_value=finding.actual,
                causal_impact=finding.causal_impact,
                detected_at=datetime.now(timezone.utc),
            )
            session.add(record)

        # Update replay session divergence count
        replay_result = await session.execute(
            select(ReplaySession).where(ReplaySession.id == replay_session_id)
        )
        replay = replay_result.scalars().first()
        if replay:
            replay.divergence_count = report.total_divergences

        await session.commit()
        logger.info(f"Divergence analysis complete: {report.total_divergences} divergences found")
        return report

    async def _check_event_sequence_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for event sequence divergence."""
        # Get original events
        original_result = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        )
        original_events = original_result.scalars().all()

        if not original_events:
            return

        # Check for missing hashes (indicates pre-hashing era data)
        events_without_hashes = [e for e in original_events if not e.event_hash]
        if events_without_hashes:
            report.findings.append(DivergenceFinding(
                divergence_type="event_sequence",
                severity="medium",
                location="event_chain",
                expected={"hashed_events": len(original_events)},
                actual={"hashed_events": len(original_events) - len(events_without_hashes)},
                causal_impact="Events without hashes cannot be verified for integrity. This indicates the run was executed before hashing was implemented.",
            ))
            report.event_divergences += 1

        # Check for chain continuity
        chain_hash = "GENESIS"
        broken_chains = 0
        for event in original_events:
            if event.event_hash:
                from src.core.hashing import compute_chain_hash
                expected_chain = compute_chain_hash(chain_hash, event.event_hash)
                if event.chain_hash and event.chain_hash != expected_chain:
                    broken_chains += 1
                chain_hash = expected_chain

        if broken_chains > 0:
            report.findings.append(DivergenceFinding(
                divergence_type="event_sequence",
                severity="high",
                location="event_chain",
                expected={"broken_links": 0},
                actual={"broken_links": broken_chains},
                causal_impact="Broken chain links indicate event tampering or data corruption. Timeline integrity is compromised.",
            ))
            report.event_divergences += 1

    async def _check_artifact_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for artifact divergence."""
        artifacts_result = await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        )
        artifacts = artifacts_result.scalars().all()

        if not artifacts:
            return

        # Check for missing artifact hashes
        artifacts_without_hashes = [a for a in artifacts if not a.artifact_hash]
        if artifacts_without_hashes:
            report.findings.append(DivergenceFinding(
                divergence_type="artifact",
                severity="medium",
                location="artifact_chain",
                expected={"hashed_artifacts": len(artifacts)},
                actual={"hashed_artifacts": len(artifacts) - len(artifacts_without_hashes)},
                causal_impact="Artifacts without hashes cannot be content-verified. Artifact integrity cannot be proven.",
            ))
            report.artifact_divergences += 1

    async def _check_governance_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for governance decision divergence."""
        gov_result = await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )
        evals = gov_result.scalars().all()

        if not evals:
            return

        # Check for missing integrity hashes
        evals_without_hashes = [e for e in evals if not e.integrity_hash]
        if evals_without_hashes:
            report.findings.append(DivergenceFinding(
                divergence_type="governance",
                severity="medium",
                location="governance_chain",
                expected={"hashed_evaluations": len(evals)},
                actual={"hashed_evaluations": len(evals) - len(evals_without_hashes)},
                causal_impact="Governance evaluations without hashes cannot be verified. Governance integrity is unproven.",
            ))
            report.governance_divergences += 1

    async def _check_timing_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for timing anomalies."""
        events_result = await session.execute(
            select(LogEvent).where(LogEvent.run_id == self.run_id).order_by(LogEvent.created_at)
        )
        events = events_result.scalars().all()

        if len(events) < 2:
            return

        # Check for out-of-order timestamps
        ordering_issues = 0
        for i in range(1, len(events)):
            if events[i].created_at and events[i-1].created_at:
                if events[i].created_at < events[i-1].created_at:
                    ordering_issues += 1

        if ordering_issues > 0:
            severity = "high" if ordering_issues > len(events) * 0.1 else "medium"
            report.findings.append(DivergenceFinding(
                divergence_type="timing",
                severity=severity,
                location="event_timestamps",
                expected={"ordering_violations": 0},
                actual={"ordering_violations": ordering_issues},
                causal_impact="Out-of-order timestamps indicate clock skew or data corruption. Causal reconstruction may be inaccurate.",
            ))
            report.timing_divergences += 1

    async def _check_topology_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for topology divergence in the execution graph."""
        # Check phase count consistency
        phases_result = await session.execute(
            select(LogEvent.phase_id).where(
                and_(LogEvent.run_id == self.run_id, LogEvent.phase_id.isnot(None))
            ).distinct()
        )
        phases = phases_result.scalars().all()

        if not phases:
            report.findings.append(DivergenceFinding(
                divergence_type="topology",
                severity="low",
                location="phase_graph",
                expected={"phases": ">=1"},
                actual={"phases": 0},
                causal_impact="No phase assignments found. Execution topology is flat.",
            ))
            report.topology_divergences += 1

    async def _check_traceability_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for traceability graph divergence."""
        links_result = await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )
        links = links_result.scalars().all()

        if not links:
            return

        # Check for missing edge hashes
        links_without_hashes = [l for l in links if not l.edge_hash]
        if links_without_hashes:
            report.findings.append(DivergenceFinding(
                divergence_type="traceability",
                severity="medium",
                location="traceability_graph",
                expected={"hashed_links": len(links)},
                actual={"hashed_links": len(links) - len(links_without_hashes)},
                causal_impact="Traceability links without hashes cannot be verified. Lineage integrity is unproven.",
            ))
            report.traceability_divergences += 1

    async def _check_integrity_divergence(self, session: AsyncSession, report: DivergenceReport):
        """Check for overall integrity divergence."""
        run = await session.get(Run, self.run_id)
        if not run:
            return

        if not run.integrity_hash:
            report.findings.append(DivergenceFinding(
                divergence_type="integrity",
                severity="low",
                location="run_integrity",
                expected={"integrity_hash": "present"},
                actual={"integrity_hash": "missing"},
                causal_impact="Run-level integrity hash is missing. Overall run integrity cannot be verified.",
            ))
            report.integrity_divergences += 1
