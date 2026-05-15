"""Replay Runtime — Deterministic Forensic Replay Engine.

Uses a completely isolated approach:
1. ThreadPoolExecutor to run in a separate thread
2. Dedicated async event loop in that thread
3. Fresh async session with its own engine
4. No shared state with FastAPI's DI session
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.hashing import (
    compute_hash, compute_chain_hash, compute_replay_hash,
    compute_event_hash, compute_artifact_hash, compute_governance_hash,
    compute_traceability_hash,
)
from src.core.logging import get_logger
from src.core.config import settings
from src.models import (
    Run, LogEvent, RunSnapshot, Artifact, TraceabilityLink,
    GovernanceEvaluation, ReplaySession, ReplayEvent, ReplayManifest,
)

logger = get_logger("replay_runtime")


class ReplayContext:
    def __init__(self, replay_id: str, run_id: str, replay_mode: str = "full"):
        self.replay_id = replay_id
        self.run_id = run_id
        self.replay_mode = replay_mode
        self.phase = "initialized"
        self.events_replayed: int = 0
        self.artifacts_replayed: int = 0
        self.governance_replayed: int = 0
        self.snapshots_replayed: int = 0
        self.traceability_replayed: int = 0
        self.divergence_count: int = 0
        self.integrity_score: float = 0.0
        self.chain_continuity_valid: bool = True
        self.replay_hash: str = ""
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None


# Thread pool for isolated replay execution
_replay_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="replay")


class ReplayRuntime:
    """Deterministic replay runtime that runs in a completely isolated thread."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def execute(self, replay_mode: str = "full",
                       from_timestamp: Optional[str] = None,
                       phase_name: Optional[str] = None) -> ReplayContext:
        """Execute replay in an isolated thread."""
        loop = asyncio.get_running_loop()
        ctx = await loop.run_in_executor(
            _replay_executor,
            self._run_in_thread,
            replay_mode,
            from_timestamp,
            phase_name,
        )
        if ctx.error:
            raise RuntimeError(ctx.error)
        return ctx

    def _run_in_thread(self, replay_mode: str, from_timestamp: Optional[str],
                        phase_name: Optional[str]) -> ReplayContext:
        """Run the async replay in a new event loop in this thread."""
        try:
            return asyncio.run(self._async_replay(replay_mode, from_timestamp, phase_name))
        except Exception as e:
            ctx = ReplayContext(replay_id="error", run_id=self.run_id)
            ctx.error = str(e)
            return ctx

    async def _async_replay(self, replay_mode: str, from_timestamp: Optional[str],
                             phase_name: Optional[str]) -> ReplayContext:
        """Actual async replay with its own engine and session."""
        replay_id = str(uuid.uuid4())
        ctx = ReplayContext(replay_id=replay_id, run_id=self.run_id, replay_mode=replay_mode)
        ctx.started_at = datetime.now(timezone.utc)

        # Create a completely fresh engine and session — no shared state
        engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_size=2,
            max_overflow=5,
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        try:
            async with session_factory() as session:
                async with session.begin():
                    ctx.phase = "reconstructing"
                    data = await self._reconstruct(session, ctx, from_timestamp)

                    ctx.phase = "replaying"
                    await self._replay(session, ctx, data)

                    ctx.phase = "finalizing"
                    await self._finalize(session, ctx)

            ctx.phase = "completed"
        except Exception as e:
            ctx.phase = "failed"
            ctx.error = str(e)
            logger.error(f"Replay {replay_id} failed: {e}")
        finally:
            await engine.dispose()

        ctx.completed_at = datetime.now(timezone.utc)
        return ctx

    async def _reconstruct(self, session: AsyncSession, ctx: ReplayContext,
                            from_timestamp: Optional[str]):
        """Reconstruct original run state."""
        from sqlalchemy import select

        run = await session.get(Run, self.run_id)
        if not run:
            raise ValueError(f"Run {self.run_id} not found")

        events_q = select(LogEvent).where(LogEvent.run_id == self.run_id)
        if from_timestamp:
            events_q = events_q.where(LogEvent.created_at >= from_timestamp)
        events_q = events_q.order_by(LogEvent.created_at)
        events = (await session.execute(events_q)).scalars().all()

        artifacts = (await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id).order_by(Artifact.created_at)
        )).scalars().all()

        gov_evals = (await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )).scalars().all()

        snaps = (await session.execute(
            select(RunSnapshot).where(RunSnapshot.run_id == self.run_id).order_by(RunSnapshot.created_at)
        )).scalars().all()

        links = (await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )).scalars().all()

        return (events, artifacts, gov_evals, snaps, links)

    async def _replay(self, session: AsyncSession, ctx: ReplayContext, data):
        """Replay all entities."""
        events, artifacts, gov_evals, snaps, links = data
        chain_hash = "GENESIS"

        for event in events:
            expected_hash = compute_event_hash(
                run_id=self.run_id, event_type="log", message=event.message,
                timestamp=event.created_at.isoformat() if event.created_at else "",
                severity=event.severity, source_file=event.source_file,
                phase_id=event.phase_id, trace_id=event.trace_id,
            )
            expected_chain = compute_chain_hash(chain_hash, expected_hash)
            divergence = False
            if event.event_hash and event.event_hash != expected_hash:
                divergence = True
                ctx.divergence_count += 1
            if event.chain_hash and event.chain_hash != expected_chain:
                divergence = True
                ctx.chain_continuity_valid = False
            session.add(ReplayEvent(
                replay_session_id=ctx.replay_id, original_event_id=event.id,
                event_type="log", severity=event.severity, message=event.message,
                source_file=event.source_file, phase_id=event.phase_id,
                trace_id=event.trace_id, event_hash=expected_hash,
                parent_hash=chain_hash if chain_hash != "GENESIS" else None,
                replayed_at=datetime.now(timezone.utc), divergence_detected=divergence,
            ))
            chain_hash = expected_hash
            ctx.events_replayed += 1

        for art in artifacts:
            expected_hash = compute_artifact_hash(
                artifact_type=art.artifact_type, name=art.name,
                content=art.content, phase_name=art.phase_name, metadata=art.metadata_,
            )
            divergence = art.artifact_hash and art.artifact_hash != expected_hash
            if divergence:
                ctx.divergence_count += 1
            session.add(ReplayEvent(
                replay_session_id=ctx.replay_id, original_event_id=None,
                event_type="artifact.replayed", severity="info",
                message=f"Artifact replayed: {art.name} ({art.artifact_type})",
                event_hash=expected_hash, divergence_detected=divergence,
            ))
            ctx.artifacts_replayed += 1

        for ev in gov_evals:
            policy_name = ev.policy.name if ev.policy else "unknown"
            expected_hash = compute_governance_hash(
                policy_name=policy_name, decision=ev.decision,
                input_data=ev.findings if isinstance(ev.findings, dict) else {},
                output_data=ev.evidence if isinstance(ev.evidence, dict) else {},
                run_id=ev.run_id, artifact_id=ev.artifact_id,
            )
            divergence = ev.integrity_hash and ev.integrity_hash != expected_hash
            if divergence:
                ctx.divergence_count += 1
            session.add(ReplayEvent(
                replay_session_id=ctx.replay_id, original_event_id=None,
                event_type="governance.replayed", severity="info",
                message=f"Governance replayed: {policy_name} → {ev.decision}",
                event_hash=expected_hash, divergence_detected=divergence,
            ))
            ctx.governance_replayed += 1

        for snap in snaps:
            session.add(ReplayEvent(
                replay_session_id=ctx.replay_id, original_event_id=None,
                event_type="snapshot.loaded", severity="info",
                message=f"Snapshot loaded: {snap.snapshot_type}",
                event_hash=snap.snapshot_hash,
            ))
            ctx.snapshots_replayed += 1

        for link in links:
            expected_hash = compute_traceability_hash(
                source_type=link.source_type, source_id=link.source_id,
                target_type=link.target_type, target_id=link.target_id,
                link_type=link.link_type, run_id=link.run_id,
            )
            session.add(ReplayEvent(
                replay_session_id=ctx.replay_id, original_event_id=None,
                event_type="lineage.linked", severity="info",
                message=f"Traceability: {link.source_type}:{link.source_id} → {link.target_type}:{link.target_id}",
                event_hash=expected_hash,
            ))
            ctx.traceability_replayed += 1

    async def _finalize(self, session: AsyncSession, ctx: ReplayContext):
        """Finalize replay."""
        total = max(ctx.events_replayed, 1)
        ctx.integrity_score = max(0.0, 1.0 - (ctx.divergence_count / total))
        if not ctx.chain_continuity_valid:
            ctx.integrity_score = max(0.0, ctx.integrity_score - 0.2)

        ctx.replay_hash = compute_replay_hash(
            run_id=self.run_id, event_count=ctx.events_replayed,
            artifact_count=ctx.artifacts_replayed, snapshot_count=ctx.snapshots_replayed,
            traceability_count=ctx.traceability_replayed, governance_count=ctx.governance_replayed,
            replay_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        session.add(ReplaySession(
            id=ctx.replay_id, source_run_id=self.run_id, replay_mode=ctx.replay_mode,
            status="completed", started_at=ctx.started_at,
            completed_at=datetime.now(timezone.utc),
            total_events_replayed=ctx.events_replayed,
            total_artifacts_replayed=ctx.artifacts_replayed,
            total_governance_replayed=ctx.governance_replayed,
            divergence_count=ctx.divergence_count, integrity_score=ctx.integrity_score,
            replay_hash=ctx.replay_hash,
        ))

        session.add(ReplayManifest(
            run_id=self.run_id, replay_session_id=ctx.replay_id,
            manifest_type=ctx.replay_mode, manifest_data={"replay_id": ctx.replay_id, "run_id": ctx.run_id},
            manifest_hash=ctx.replay_hash, event_count=ctx.events_replayed,
            artifact_count=ctx.artifacts_replayed, traceability_count=ctx.traceability_replayed,
            governance_count=ctx.governance_replayed, snapshot_count=ctx.snapshots_replayed,
        ))
