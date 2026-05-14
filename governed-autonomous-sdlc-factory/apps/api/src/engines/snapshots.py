"""Run Snapshot management for the Governed Autonomous SDLC Factory.

Captures full system-state snapshots for:
- Manual snapshots
- Phase transition snapshots
- Pre-deployment snapshots
- Post-mortem analysis
- Export/import
"""
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import publish_custom_event
from src.models import (
    RunSnapshot, Run, Phase, Artifact, CostEvent,
    GovernanceEvaluation, SpecificationVersion, ArchitectureVersion,
    TestPlan, TraceabilityLink
)
from src.core.logging import get_logger

logger = get_logger("snapshots")


class SnapshotManager:
    """Manages run snapshots."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def create_snapshot(self, session: AsyncSession, snapshot_type: str = "manual",
                               triggered_by: str = "user") -> RunSnapshot:
        """Create a full system-state snapshot."""
        # Gather all state
        run = await session.get(Run, self.run_id)
        if not run:
            raise ValueError(f"Run {self.run_id} not found")

        # Phases
        phases_result = await session.execute(
            select(Phase).where(Phase.run_id == self.run_id)
        )
        phases = phases_result.scalars().all()
        phase_states = {
            p.name: {
                "status": p.status,
                "started_at": p.started_at.isoformat() if p.started_at else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                "agent_id": p.agent_id,
            }
            for p in phases
        }

        # Artifacts
        artifacts_result = await session.execute(
            select(Artifact).where(Artifact.run_id == self.run_id)
        )
        artifacts = artifacts_result.scalars().all()
        artifact_states = {
            a.name: {
                "type": a.type.value if hasattr(a.type, 'value') else str(a.type),
                "phase": a.phase_name,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in artifacts
        }

        # Costs
        costs_result = await session.execute(
            select(CostEvent).where(CostEvent.run_id == self.run_id)
        )
        costs = costs_result.scalars().all()
        cost_summary = {
            "total_cost": sum(c.estimated_cost for c in costs),
            "total_tokens_in": sum(c.tokens_in for c in costs),
            "total_tokens_out": sum(c.tokens_out for c in costs),
            "entry_count": len(costs),
        }

        # Governance
        gov_result = await session.execute(
            select(GovernanceEvaluation).where(GovernanceEvaluation.run_id == self.run_id)
        )
        gov_evals = gov_result.scalars().all()
        governance_summary = {
            "total_evaluations": len(gov_evals),
            "passed": len([e for e in gov_evals if e.decision == "pass"]),
            "failed": len([e for e in gov_evals if e.decision == "fail"]),
            "warnings": len([e for e in gov_evals if e.decision == "warning"]),
        }

        # Full state
        state_data = {
            "run": {
                "id": run.id,
                "name": run.name,
                "status": run.status.value if hasattr(run.status, 'value') else str(run.status),
                "created_at": run.created_at.isoformat() if run.created_at else None,
            },
            "snapshot_type": snapshot_type,
            "triggered_by": triggered_by,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

        snapshot = RunSnapshot(
            run_id=self.run_id,
            snapshot_type=snapshot_type,
            state_data=state_data,
            phase_states=phase_states,
            artifact_states=artifact_states,
            cost_summary=cost_summary,
            governance_summary=governance_summary,
        )
        session.add(snapshot)
        await session.commit()

        await publish_custom_event(
            self.run_id, "snapshot.created",
            f"Snapshot created ({snapshot_type}): {len(artifacts)} artifacts, {len(phases)} phases",
            data={"snapshot_id": snapshot.id, "type": snapshot_type},
        )

        logger.info(f"Snapshot {snapshot.id} created for run {self.run_id}")
        return snapshot

    async def get_snapshots(self, session: AsyncSession) -> list[RunSnapshot]:
        """Get all snapshots for a run."""
        result = await session.execute(
            select(RunSnapshot)
            .where(RunSnapshot.run_id == self.run_id)
            .order_by(RunSnapshot.created_at.desc())
        )
        return list(result.scalars().all())

    async def export_snapshot(self, session: AsyncSession, snapshot_id: str) -> dict:
        """Export a snapshot as a portable dict."""
        snapshot = await session.get(RunSnapshot, snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        return {
            "export_version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "snapshot": {
                "id": snapshot.id,
                "run_id": snapshot.run_id,
                "type": snapshot.snapshot_type,
                "state": snapshot.state_data,
                "phases": snapshot.phase_states,
                "artifacts": snapshot.artifact_states,
                "costs": snapshot.cost_summary,
                "governance": snapshot.governance_summary,
                "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            },
        }
