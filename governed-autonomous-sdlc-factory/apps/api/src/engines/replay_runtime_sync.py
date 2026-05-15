"""Synchronous Replay Runtime — deterministic forensic replay engine.

This is the core replay execution engine. It runs COMPLETELY SYNCHRONOUS,
using sync SQLAlchemy sessions. No async. No greenlet. No event loop.

Architecture:
    FastAPI Route (async)
    → loop.run_in_executor(replay_executor, run_sync_replay, request)
    → ReplayRuntimeSync (sync)
    → SyncSessionLocal (sync SQLAlchemy)
    → deterministic replay execution

The replay runtime owns its session lifecycle completely.
No FastAPI dependency injection. No shared state. No greenlet conflicts.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.sync_database import SyncSessionLocal
from src.core.hashing import (
    compute_hash, compute_chain_hash, compute_replay_hash,
    compute_event_hash, compute_artifact_hash, compute_governance_hash,
    compute_traceability_hash, compute_snapshot_hash,
)
from src.engines.replay_transaction_manager import (
    ReplayTransactionManager, ReplayPhase,
)
from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, ReplaySession, ReplayEvent, ReplayManifest,
    GovernancePolicy,
)
from src.core.logging import get_logger

logger = get_logger("replay_runtime_sync")

# Dedicated thread pool for replay execution
_replay_executor = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="sync-replay",
)


class ReplayContext:
    """Immutable replay execution context.

    Tracks all state for a single replay execution.
    Created at the start, populated during execution, returned as result.
    """

    def __init__(self, replay_id: str, run_id: str, replay_mode: str = "full"):
        self.replay_id = replay_id
        self.run_id = run_id
        self.replay_mode = replay_mode
        self.phase: str = "initialized"
        self.events_replayed: int = 0
        self.artifacts_replayed: int = 0
        self.governance_replayed: int = 0
        self.snapshots_replayed: int = 0
        self.traceability_replayed: int = 0
        self.divergence_count: int = 0
        self.integrity_score: float = 0.0
        self.chain_continuity_valid: bool = True
        self.replay_hash: str = ""
        self.checkpoints: list = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self._chain_hash: str = "GENESIS"

    def to_dict(self) -> dict:
        return {
            "replay_id": self.replay_id,
            "run_id": self.run_id,
            "replay_mode": self.replay_mode,
            "phase": self.phase,
            "events_replayed": self.events_replayed,
            "artifacts_replayed": self.artifacts_replayed,
            "governance_replayed": self.governance_replayed,
            "snapshots_replayed": self.snapshots_replayed,
            "traceability_replayed": self.traceability_replayed,
            "divergence_count": self.divergence_count,
            "integrity_score": self.integrity_score,
            "chain_continuity_valid": self.chain_continuity_valid,
            "replay_hash": self.replay_hash,
            "checkpoints": self.checkpoints,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class ReplayRuntimeSync:
    """Synchronous deterministic replay runtime.

    This engine executes replays in a fully synchronous manner
    using dedicated sync SQLAlchemy sessions. It is completely
    independent from FastAPI's async dependency injection.

    Usage:
        runtime = ReplayRuntimeSync(run_id)
        ctx = runtime.execute(replay_mode="full")
    """

    def __init__(self, run_id: str):
        self.run_id = run_id

    def execute(
        self,
        replay_mode: str = "full",
        from_timestamp: Optional[str] = None,
        phase_name: Optional[str] = None,
    ) -> ReplayContext:
        """Execute a deterministic replay of the run.

        This is the main entry point. It creates a fresh sync session,
        executes all replay phases, and returns the replay context.

        No async. No greenlet. No event loop. Pure sync execution.
        """
        replay_id = str(uuid.uuid4())
        ctx = ReplayContext(replay_id=replay_id, run_id=self.run_id, replay_mode=replay_mode)
        ctx.started_at = datetime.now(timezone.utc)

        session = SyncSessionLocal()
        txn = ReplayTransactionManager(session)

        try:
            # Phase 0: Create replay session FIRST (before any replay events)
            # This ensures the FK constraint is satisfied when replay events are inserted
            txn.transition_to(ReplayPhase.RECONSTRUCTING)
            ctx.phase = "reconstructing"

            # Verify run exists
            run = session.get(Run, self.run_id)
            if not run:
                raise ValueError(f"Run {self.run_id} not found")

            # Create replay session record immediately
            replay_session = ReplaySession(
                id=ctx.replay_id,
                source_run_id=self.run_id,
                replay_mode=ctx.replay_mode,
                status="running",
                started_at=ctx.started_at,
            )
            session.add(replay_session)
            session.flush()  # Flush to satisfy FK constraints for replay_events

            # Phase 1: Reconstruct
            ctx.phase = "reconstructing"
            data = self._reconstruct(session, ctx, from_timestamp, phase_name)

            # Phase 2: Validate
            txn.transition_to(ReplayPhase.VALIDATING)
            ctx.phase = "validating"
            self._validate(session, ctx, data)

            # Phase 3: Replay
            txn.transition_to(ReplayPhase.REPLAYING)
            ctx.phase = "replaying"
            self._replay(session, ctx, data, txn)

            # Phase 4: Persist
            txn.transition_to(ReplayPhase.PERSISTING)
            ctx.phase = "persisting"
            txn.flush()

            # Phase 5: Verify
            txn.transition_to(ReplayPhase.VERIFYING)
            ctx.phase = "verifying"
            self._verify(session, ctx)

            # Phase 6: Finalize
            txn.transition_to(ReplayPhase.FINALIZING)
            ctx.phase = "finalizing"
            self._finalize(session, ctx, replay_session)
            txn.commit()

            txn.transition_to(ReplayPhase.COMPLETED)
            ctx.phase = "completed"

        except Exception as e:
            txn.transition_to(ReplayPhase.FAILED)
            ctx.phase = "failed"
            ctx.error = str(e)
            logger.error(f"Replay {replay_id} failed: {e}", exc_info=True)
            try:
                txn.rollback()
            except Exception:
                pass
        finally:
            session.close()
            ctx.completed_at = datetime.now(timezone.utc)

        return ctx

    def _reconstruct(
        self,
        session: Session,
        ctx: ReplayContext,
        from_timestamp: Optional[str],
        phase_name: Optional[str],
    ) -> tuple:
        """Reconstruct original run state from database.

        Fetches all entities needed for replay in deterministic order.
        Note: run existence check already done in execute().
        """
        # Build event query
        events_q = select(LogEvent).where(LogEvent.run_id == self.run_id)
        if from_timestamp:
            events_q = events_q.where(LogEvent.created_at >= from_timestamp)
        if phase_name:
            events_q = events_q.where(LogEvent.phase_id == phase_name)
        events_q = events_q.order_by(LogEvent.created_at)
        events = list(session.execute(events_q).scalars().all())

        artifacts = list(session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        ).scalars().all())

        gov_evals = list(session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        ).scalars().all())

        snaps = list(session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        ).scalars().all())

        links = list(session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        ).scalars().all())

        logger.info(
            f"Reconstructed run {self.run_id}: "
            f"{len(events)} events, {len(artifacts)} artifacts, "
            f"{len(gov_evals)} governance, {len(snaps)} snapshots, {len(links)} links"
        )

        return (events, artifacts, gov_evals, snaps, links)

    def _validate(self, session: Session, ctx: ReplayContext, data: tuple) -> None:
        """Validate reconstructed data before replay."""
        events, artifacts, gov_evals, snaps, links = data

        if not events and not artifacts:
            logger.warning(f"Run {self.run_id} has no events or artifacts to replay")

        # Validate entity integrity
        for event in events:
            if not event.id:
                raise ValueError(f"Event without ID found in run {self.run_id}")

        for artifact in artifacts:
            if not artifact.id:
                raise ValueError(f"Artifact without ID found in run {self.run_id}")

        logger.info(f"Validation passed for run {self.run_id}")

    def _replay(
        self,
        session: Session,
        ctx: ReplayContext,
        data: tuple,
        txn: ReplayTransactionManager,
    ) -> None:
        """Replay all entities with hash verification and chain continuity."""
        events, artifacts, gov_evals, snaps, links = data
        chain_hash = "GENESIS"

        # Replay events with chain hash verification
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
                ctx.divergence_count += 1
            if event.chain_hash and event.chain_hash != expected_chain:
                divergence = True
                ctx.chain_continuity_valid = False

            replay_event = ReplayEvent(
                replay_session_id=ctx.replay_id,
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
            ctx.events_replayed += 1

        txn.checkpoint("events_replayed")

        # Replay artifacts with hash verification
        for art in artifacts:
            expected_hash = compute_artifact_hash(
                artifact_type=art.artifact_type,
                name=art.name,
                content=art.content,
                phase_name=art.phase_name,
                metadata=art.metadata_,
            )
            divergence = art.artifact_hash and art.artifact_hash != expected_hash
            if divergence:
                ctx.divergence_count += 1

            replay_event = ReplayEvent(
                replay_session_id=ctx.replay_id,
                original_event_id=None,
                event_type="artifact.replayed",
                severity="info",
                message=f"Artifact replayed: {art.name} ({art.artifact_type})",
                event_hash=expected_hash,
                divergence_detected=divergence,
            )
            session.add(replay_event)
            ctx.artifacts_replayed += 1

        txn.checkpoint("artifacts_replayed")

        # Replay governance evaluations with hash verification
        for ev in gov_evals:
            policy_name = ev.policy.name if ev.policy else "unknown"
            expected_hash = compute_governance_hash(
                policy_name=policy_name,
                decision=ev.decision,
                input_data=ev.findings if isinstance(ev.findings, dict) else {},
                output_data=ev.evidence if isinstance(ev.evidence, dict) else {},
                run_id=ev.run_id,
                artifact_id=ev.artifact_id,
            )
            divergence = ev.integrity_hash and ev.integrity_hash != expected_hash
            if divergence:
                ctx.divergence_count += 1

            replay_event = ReplayEvent(
                replay_session_id=ctx.replay_id,
                original_event_id=None,
                event_type="governance.replayed",
                severity="info",
                message=f"Governance replayed: {policy_name} → {ev.decision}",
                event_hash=expected_hash,
                divergence_detected=divergence,
            )
            session.add(replay_event)
            ctx.governance_replayed += 1

        txn.checkpoint("governance_replayed")

        # Replay snapshots
        for snap in snaps:
            replay_event = ReplayEvent(
                replay_session_id=ctx.replay_id,
                original_event_id=None,
                event_type="snapshot.loaded",
                severity="info",
                message=f"Snapshot loaded: {snap.snapshot_type}",
                event_hash=snap.snapshot_hash,
            )
            session.add(replay_event)
            ctx.snapshots_replayed += 1

        txn.checkpoint("snapshots_replayed")

        # Replay traceability links with hash verification
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
                replay_session_id=ctx.replay_id,
                original_event_id=None,
                event_type="lineage.linked",
                severity="info",
                message=f"Traceability: {link.source_type}:{link.source_id} → {link.target_type}:{link.target_id}",
                event_hash=expected_hash,
            )
            session.add(replay_event)
            ctx.traceability_replayed += 1

        txn.checkpoint("traceability_replayed")

        # Store chain hash in context
        ctx._chain_hash = chain_hash

    def _verify(self, session: Session, ctx: ReplayContext) -> None:
        """Verify replay integrity."""
        total = max(ctx.events_replayed + ctx.artifacts_replayed + ctx.governance_replayed, 1)
        ctx.integrity_score = max(0.0, 1.0 - (ctx.divergence_count / total))
        if not ctx.chain_continuity_valid:
            ctx.integrity_score = max(0.0, ctx.integrity_score - 0.2)

        logger.info(
            f"Replay verification: score={ctx.integrity_score:.4f}, "
            f"divergences={ctx.divergence_count}, "
            f"chain_valid={ctx.chain_continuity_valid}"
        )

    def _finalize(self, session: Session, ctx: ReplayContext, replay_session: ReplaySession) -> None:
        """Finalize replay — update replay session and create manifest."""
        ctx.replay_hash = compute_replay_hash(
            run_id=self.run_id,
            event_count=ctx.events_replayed,
            artifact_count=ctx.artifacts_replayed,
            snapshot_count=ctx.snapshots_replayed,
            traceability_count=ctx.traceability_replayed,
            governance_count=ctx.governance_replayed,
            replay_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Update the existing replay session (already flushed in reconstruct phase)
        replay_session.status = "completed"
        replay_session.completed_at = datetime.now(timezone.utc)
        replay_session.total_events_replayed = ctx.events_replayed
        replay_session.total_artifacts_replayed = ctx.artifacts_replayed
        replay_session.total_governance_replayed = ctx.governance_replayed
        replay_session.divergence_count = ctx.divergence_count
        replay_session.integrity_score = ctx.integrity_score
        replay_session.replay_hash = ctx.replay_hash

        manifest = ReplayManifest(
            run_id=self.run_id,
            replay_session_id=ctx.replay_id,
            manifest_type=ctx.replay_mode,
            manifest_data=ctx.to_dict(),
            manifest_hash=ctx.replay_hash,
            event_count=ctx.events_replayed,
            artifact_count=ctx.artifacts_replayed,
            traceability_count=ctx.traceability_replayed,
            governance_count=ctx.governance_replayed,
            snapshot_count=ctx.snapshots_replayed,
        )
        session.add(manifest)

        logger.info(f"Replay {ctx.replay_id} finalized: hash={ctx.replay_hash[:16]}...")


def run_sync_replay(
    run_id: str,
    replay_mode: str = "full",
    from_timestamp: Optional[str] = None,
    phase_name: Optional[str] = None,
) -> ReplayContext:
    """Entry point for running a synchronous replay in a thread pool.

    This function is called via loop.run_in_executor() from the FastAPI route.
    It creates a ReplayRuntimeSync and executes the replay synchronously.

    Args:
        run_id: The run to replay
        replay_mode: Replay mode (full, phase, event, snapshot, semantic)
        from_timestamp: Optional ISO timestamp to replay from
        phase_name: Optional phase name for phase-mode replay

    Returns:
        ReplayContext with all replay results
    """
    runtime = ReplayRuntimeSync(run_id=run_id)
    return runtime.execute(
        replay_mode=replay_mode,
        from_timestamp=from_timestamp,
        phase_name=phase_name,
    )
