"""Deterministic Replay Engine for the Cognitive Cortex.

Reconstructs and replays execution runs with full determinism.

Uses the caller's session with no_autoflush to prevent premature FK violations.
The caller's get_db() dependency handles commit/rollback.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.hashing import (
    compute_hash, compute_chain_hash, compute_replay_hash,
    compute_event_hash, compute_artifact_hash, compute_governance_hash,
    compute_traceability_hash,
)
from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, ReplaySession, ReplayEvent, ReplayManifest,
    SemanticGraphNode, SemanticGraphEdge, Phase, CostEvent,
    GovernancePolicy,
)
from src.core.logging import get_logger

logger = get_logger("replay_engine")


@dataclass
class ReplayResult:
    """Result of a replay operation."""
    replay_session_id: str
    run_id: str
    replay_mode: str
    status: str
    events_replayed: int = 0
    artifacts_replayed: int = 0
    governance_replayed: int = 0
    snapshots_replayed: int = 0
    traceability_replayed: int = 0
    divergence_count: int = 0
    integrity_score: float = 0.0
    replay_hash: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    manifest: dict = field(default_factory=dict)


class ReplayEngine:
    """Deterministic replay engine for cognitive execution runs."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def replay(self, session: AsyncSession, replay_mode: str = "full",
                      from_timestamp: Optional[str] = None,
                      phase_name: Optional[str] = None) -> ReplayResult:
        """Execute a deterministic replay of the run."""
        started_at = datetime.now(timezone.utc)
        replay_session_id = str(uuid.uuid4())

        # Create replay session object (not yet added to session)
        replay_session = ReplaySession(
            id=replay_session_id,
            source_run_id=self.run_id,
            replay_mode=replay_mode,
            status="running",
            started_at=started_at,
        )

        # Use no_autoflush to prevent premature FK violations
        # when replay events reference the replay_session before it's inserted
        with session.no_autoflush:
            session.add(replay_session)

            # Execute replay based on mode
            if replay_mode == "full":
                result = await self._replay_full(session, replay_session_id, from_timestamp)
            elif replay_mode == "phase":
                result = await self._replay_phase(session, replay_session_id, phase_name)
            elif replay_mode == "event":
                result = await self._replay_events(session, replay_session_id, from_timestamp)
            elif replay_mode == "snapshot":
                result = await self._replay_snapshots(session, replay_session_id)
            elif replay_mode == "semantic":
                result = await self._replay_semantic(session, replay_session_id)
            else:
                raise ValueError(f"Unknown replay mode: {replay_mode}")

        # Now compute hash and update (outside no_autoflush)
        replay_hash = compute_replay_hash(
            run_id=self.run_id,
            event_count=result["events_replayed"],
            artifact_count=result["artifacts_replayed"],
            snapshot_count=result["snapshots_replayed"],
            traceability_count=result["traceability_replayed"],
            governance_count=result["governance_replayed"],
            replay_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        completed_at = datetime.now(timezone.utc)

        # Update replay session with final state
        replay_session.status = "completed"
        replay_session.completed_at = completed_at
        replay_session.total_events_replayed = result["events_replayed"]
        replay_session.total_artifacts_replayed = result["artifacts_replayed"]
        replay_session.total_governance_replayed = result["governance_replayed"]
        replay_session.divergence_count = result.get("divergence_count", 0)
        replay_session.integrity_score = result.get("integrity_score", 1.0)
        replay_session.replay_hash = replay_hash

        # Create manifest
        manifest = ReplayManifest(
            run_id=self.run_id,
            replay_session_id=replay_session_id,
            manifest_type=replay_mode,
            manifest_data=result,
            manifest_hash=replay_hash,
            event_count=result["events_replayed"],
            artifact_count=result["artifacts_replayed"],
            traceability_count=result["traceability_replayed"],
            governance_count=result["governance_replayed"],
            snapshot_count=result["snapshots_replayed"],
        )
        session.add(manifest)

        logger.info(f"Replay {replay_session_id} prepared: {result['events_replayed']} events")

        return ReplayResult(
            replay_session_id=replay_session_id,
            run_id=self.run_id,
            replay_mode=replay_mode,
            status="completed",
            events_replayed=result["events_replayed"],
            artifacts_replayed=result["artifacts_replayed"],
            governance_replayed=result["governance_replayed"],
            snapshots_replayed=result["snapshots_replayed"],
            traceability_replayed=result["traceability_replayed"],
            divergence_count=result.get("divergence_count", 0),
            integrity_score=result.get("integrity_score", 1.0),
            replay_hash=replay_hash,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            manifest=result,
        )

    async def _replay_full(self, session: AsyncSession, replay_session_id: str,
                            from_timestamp: Optional[str] = None) -> dict:
        """Full replay: reconstruct entire run state."""
        events_result = await self._replay_events(session, replay_session_id, from_timestamp)
        artifacts_result = await self._replay_artifacts(session, replay_session_id)
        governance_result = await self._replay_governance(session, replay_session_id)
        snapshots_result = await self._replay_snapshots(session, replay_session_id)
        traceability_result = await self._replay_traceability(session, replay_session_id)

        return {
            "events_replayed": events_result["count"],
            "artifacts_replayed": artifacts_result["count"],
            "governance_replayed": governance_result["count"],
            "snapshots_replayed": snapshots_result["count"],
            "traceability_replayed": traceability_result["count"],
            "divergence_count": max(
                events_result.get("divergence_count", 0),
                artifacts_result.get("divergence_count", 0),
                governance_result.get("divergence_count", 0),
            ),
            "integrity_score": min(
                events_result.get("integrity_score", 1.0),
                artifacts_result.get("integrity_score", 1.0),
                governance_result.get("integrity_score", 1.0),
            ),
        }

    async def _replay_phase(self, session: AsyncSession, replay_session_id: str,
                             phase_name: Optional[str] = None) -> dict:
        """Phase replay: reconstruct a single phase."""
        if not phase_name:
            return {"events_replayed": 0, "artifacts_replayed": 0, "governance_replayed": 0,
                    "snapshots_replayed": 0, "traceability_replayed": 0, "error": "No phase specified"}

        phase_result = await session.execute(
            select(Phase).where(and_(Phase.run_id == self.run_id, Phase.name == phase_name))
        )
        phase = phase_result.scalars().first()
        if not phase:
            return {"events_replayed": 0, "artifacts_replayed": 0, "governance_replayed": 0,
                    "snapshots_replayed": 0, "traceability_replayed": 0, "error": f"Phase {phase_name} not found"}

        events_query = select(LogEvent).where(
            and_(LogEvent.run_id == self.run_id, LogEvent.phase_id == phase.id)
        ).order_by(LogEvent.created_at)
        events_result = await session.execute(events_query)
        events = events_result.scalars().all()

        for event in events:
            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=event.id,
                event_type="log",
                severity=event.severity,
                message=event.message,
                source_file=event.source_file,
                phase_id=event.phase_id,
                trace_id=event.trace_id,
            )
            session.add(replay_event)

        return {
            "events_replayed": len(events),
            "artifacts_replayed": 0,
            "governance_replayed": 0,
            "snapshots_replayed": 0,
            "traceability_replayed": 0,
            "phase": phase_name,
        }

    async def _replay_events(self, session: AsyncSession, replay_session_id: str,
                              from_timestamp: Optional[str] = None) -> dict:
        """Event replay: reconstruct event sequence."""
        events_query = select(LogEvent).where(LogEvent.run_id == self.run_id)
        if from_timestamp:
            events_query = events_query.where(LogEvent.created_at >= from_timestamp)
        events_query = events_query.order_by(LogEvent.created_at)
        events_result = await session.execute(events_query)
        events = events_result.scalars().all()

        replayed = 0
        divergence_count = 0
        chain_hash = "GENESIS"

        for event in events:
            expected_hash = compute_event_hash(
                run_id=self.run_id,
                event_type="log",
                message=event.message,
                timestamp=event.created_at.isoformat() if event.created_at else "",
                severity=event.severity,
                source_file=event.source_file,
                phase_id=event.phase_id,
                trace_id=event.trace_id,
            )
            expected_chain = compute_chain_hash(chain_hash, expected_hash)

            divergence = False
            if event.event_hash and event.event_hash != expected_hash:
                divergence = True
                divergence_count += 1
            if event.chain_hash and event.chain_hash != expected_chain:
                divergence = True
                divergence_count += 1

            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=event.id,
                event_type="log",
                severity=event.severity,
                message=event.message,
                source_file=event.source_file,
                phase_id=event.phase_id,
                trace_id=event.trace_id,
                event_hash=expected_hash,
                parent_hash=chain_hash if chain_hash != "GENESIS" else None,
                replayed_at=datetime.now(timezone.utc),
                divergence_detected=divergence,
            )
            session.add(replay_event)
            chain_hash = expected_chain
            replayed += 1

        integrity_score = 1.0 - (divergence_count / replayed) if replayed > 0 else 1.0
        return {"count": replayed, "divergence_count": divergence_count, "integrity_score": max(0.0, integrity_score)}

    async def _replay_artifacts(self, session: AsyncSession, replay_session_id: str) -> dict:
        """Artifact replay: reconstruct artifact state."""
        artifacts_result = await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        )
        artifacts = artifacts_result.scalars().all()

        replayed = 0
        divergence_count = 0

        for art in artifacts:
            expected_hash = compute_artifact_hash(
                artifact_type=art.artifact_type,
                name=art.name,
                content=art.content,
                phase_name=art.phase_name,
                metadata=art.metadata_,
            )

            divergence = False
            if art.artifact_hash and art.artifact_hash != expected_hash:
                divergence = True
                divergence_count += 1

            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=None,
                event_type="artifact.replayed",
                severity="info",
                message=f"Artifact replayed: {art.name} ({art.artifact_type})",
                event_hash=expected_hash,
                divergence_detected=divergence,
            )
            session.add(replay_event)
            replayed += 1

        integrity_score = 1.0 - (divergence_count / replayed) if replayed > 0 else 1.0
        return {"count": replayed, "divergence_count": divergence_count, "integrity_score": max(0.0, integrity_score)}

    async def _replay_governance(self, session: AsyncSession, replay_session_id: str) -> dict:
        """Governance replay: reconstruct governance decisions."""
        gov_result = await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )
        evals = gov_result.scalars().all()

        replayed = 0
        divergence_count = 0

        for ev in evals:
            policy_name = ev.policy.name if ev.policy else "unknown"
            expected_hash = compute_governance_hash(
                policy_name=policy_name,
                decision=ev.decision,
                input_data=ev.findings if isinstance(ev.findings, dict) else {},
                output_data=ev.evidence if isinstance(ev.evidence, dict) else {},
                run_id=ev.run_id,
                artifact_id=ev.artifact_id,
            )

            divergence = False
            if ev.integrity_hash and ev.integrity_hash != expected_hash:
                divergence = True
                divergence_count += 1

            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=None,
                event_type="governance.replayed",
                severity="info",
                message=f"Governance replayed: {policy_name} → {ev.decision}",
                event_hash=expected_hash,
                divergence_detected=divergence,
            )
            session.add(replay_event)
            replayed += 1

        integrity_score = 1.0 - (divergence_count / replayed) if replayed > 0 else 1.0
        return {"count": replayed, "divergence_count": divergence_count, "integrity_score": max(0.0, integrity_score)}

    async def _replay_snapshots(self, session: AsyncSession, replay_session_id: str) -> dict:
        """Snapshot replay: reconstruct state from snapshots."""
        snaps_result = await session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        )
        snaps = snaps_result.scalars().all()

        replayed = 0
        for snap in snaps:
            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=None,
                event_type="snapshot.loaded",
                severity="info",
                message=f"Snapshot loaded: {snap.snapshot_type}",
                event_hash=snap.snapshot_hash,
            )
            session.add(replay_event)
            replayed += 1

        return {"count": replayed}

    async def _replay_traceability(self, session: AsyncSession, replay_session_id: str) -> dict:
        """Traceability replay: reconstruct traceability graph."""
        links_result = await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )
        links = links_result.scalars().all()

        replayed = 0
        for link in links:
            expected_hash = compute_traceability_hash(
                source_type=link.source_type,
                source_id=link.source_id,
                target_type=link.target_type,
                target_id=link.target_id,
                link_type=link.link_type,
                run_id=link.run_id,
            )

            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=None,
                event_type="lineage.linked",
                severity="info",
                message=f"Traceability: {link.source_type}:{link.source_id} → {link.target_type}:{link.target_id}",
                event_hash=expected_hash,
            )
            session.add(replay_event)
            replayed += 1

        return {"count": replayed}

    async def _replay_semantic(self, session: AsyncSession, replay_session_id: str) -> dict:
        """Semantic replay: reconstruct semantic transitions."""
        nodes_result = await session.execute(
            select(SemanticGraphNode).where(SemanticGraphNode.run_id == self.run_id).order_by(SemanticGraphNode.created_at)
        )
        nodes = nodes_result.scalars().all()

        replayed = 0
        for node in nodes:
            replay_event = ReplayEvent(
                replay_session_id=replay_session_id,
                original_event_id=None,
                event_type="semantic.transition_detected",
                severity="info",
                message=f"Semantic transition: {node.node_type} {node.entity_name or node.entity_id}",
                event_hash=node.node_hash,
            )
            session.add(replay_event)
            replayed += 1

        return {"events_replayed": replayed, "artifacts_replayed": 0, "governance_replayed": 0,
                "snapshots_replayed": 0, "traceability_replayed": 0}

    async def get_replay_sessions(self, session: AsyncSession) -> list[ReplaySession]:
        """Get all replay sessions for this run."""
        result = await session.execute(
            select(ReplaySession).where(
                ReplaySession.source_run_id == self.run_id
            ).order_by(ReplaySession.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_replay_events(self, session: AsyncSession,
                                 replay_session_id: str) -> list[ReplayEvent]:
        """Get all events for a replay session."""
        result = await session.execute(
            select(ReplayEvent).where(
                ReplayEvent.replay_session_id == replay_session_id
            ).order_by(ReplayEvent.created_at)
        )
        return list(result.scalars().all())
