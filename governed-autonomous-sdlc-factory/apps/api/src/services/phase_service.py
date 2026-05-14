"""Phase, Artifact, Approval, Log, and Cost services."""
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import (
    Phase, Artifact, Approval, LogEvent, CostEvent,
    ApprovalStatus, EvidenceBundle
)


class PhaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run_id: str, name: str, order_index: int = 0, agent_id: str = None) -> Phase:
        phase = Phase(run_id=run_id, name=name, order_index=order_index, agent_id=agent_id)
        self.db.add(phase)
        await self.db.flush()
        await self.db.refresh(phase)
        return phase

    async def get(self, phase_id: str) -> Optional[Phase]:
        result = await self.db.execute(select(Phase).where(Phase.id == phase_id))
        return result.scalar_one_or_none()

    async def list_by_run(self, run_id: str) -> List[Phase]:
        result = await self.db.execute(
            select(Phase).where(Phase.run_id == run_id).order_by(Phase.order_index)
        )
        return list(result.scalars().all())

    async def complete(self, phase_id: str, tokens_in: int = 0, tokens_out: int = 0, cost: float = 0.0) -> Optional[Phase]:
        phase = await self.get(phase_id)
        if not phase:
            return None
        phase.status = "completed"
        phase.tokens_in = tokens_in
        phase.tokens_out = tokens_out
        phase.cost = cost
        phase.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return phase

    async def fail(self, phase_id: str, error_message: str) -> Optional[Phase]:
        phase = await self.get(phase_id)
        if not phase:
            return None
        phase.status = "failed"
        phase.error_message = error_message
        phase.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return phase


class ArtifactService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task_id: str, run_id: str, name: str, artifact_type: str,
                     content: str = None, file_path: str = None, metadata: dict = None) -> Artifact:
        artifact = Artifact(
            task_id=task_id, run_id=run_id, name=name, artifact_type=artifact_type,
            content=content, file_path=file_path, metadata_=metadata or {},
        )
        self.db.add(artifact)
        await self.db.flush()
        await self.db.refresh(artifact)
        return artifact

    async def get(self, artifact_id: str) -> Optional[Artifact]:
        result = await self.db.execute(select(Artifact).where(Artifact.id == artifact_id))
        return result.scalar_one_or_none()

    async def list_by_run(self, run_id: str, artifact_type: str = None) -> List[Artifact]:
        query = select(Artifact).where(Artifact.run_id == run_id)
        if artifact_type:
            query = query.where(Artifact.artifact_type == artifact_type)
        result = await self.db.execute(query.order_by(Artifact.created_at.desc()))
        return list(result.scalars().all())

    async def lock_baseline(self, artifact_id: str) -> Optional[Artifact]:
        artifact = await self.get(artifact_id)
        if not artifact:
            return None
        artifact.is_baseline = True
        artifact.is_locked = True
        await self.db.flush()
        return artifact


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run_id: str, approval_type: str, artifact_id: str = None,
                     is_demo: bool = False, notes: str = None) -> Approval:
        status = ApprovalStatus.AUTO_APPROVED.value if is_demo else ApprovalStatus.PENDING.value
        approval = Approval(
            run_id=run_id, artifact_id=artifact_id, approval_type=approval_type,
            status=status, is_demo=is_demo, notes=notes,
        )
        if is_demo:
            approval.approver = "demo-auto-approver"
            approval.approved_at = datetime.now(timezone.utc)
        self.db.add(approval)
        await self.db.flush()
        await self.db.refresh(approval)
        return approval

    async def approve(self, approval_id: str, approver: str = "manual") -> Optional[Approval]:
        result = await self.db.execute(select(Approval).where(Approval.id == approval_id))
        approval = result.scalar_one_or_none()
        if not approval:
            return None
        approval.status = ApprovalStatus.APPROVED.value
        approval.approver = approver
        approval.approved_at = datetime.now(timezone.utc)
        await self.db.flush()
        return approval

    async def reject(self, approval_id: str, approver: str = "manual") -> Optional[Approval]:
        result = await self.db.execute(select(Approval).where(Approval.id == approval_id))
        approval = result.scalar_one_or_none()
        if not approval:
            return None
        approval.status = ApprovalStatus.REJECTED.value
        approval.approver = approver
        approval.approved_at = datetime.now(timezone.utc)
        await self.db.flush()
        return approval


class LogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, run_id: str, severity: str, message: str,
                  phase_id: str = None, agent_id: str = None, task_id: str = None,
                  trace_id: str = None, source_file: str = None, commit_hash: str = None,
                  metadata: dict = None) -> LogEvent:
        event = LogEvent(
            run_id=run_id, severity=severity, message=message,
            phase_id=phase_id, agent_id=agent_id, task_id=task_id,
            trace_id=trace_id, source_file=source_file, commit_hash=commit_hash,
            metadata_=metadata or {},
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def list_filtered(self, run_id: str = None, phase_id: str = None,
                            agent_id: str = None, severity: str = None,
                            error_only: bool = False, from_time: datetime = None,
                            to_time: datetime = None, limit: int = 100, offset: int = 0):
        query = select(LogEvent)
        if run_id:
            query = query.where(LogEvent.run_id == run_id)
        if phase_id:
            query = query.where(LogEvent.phase_id == phase_id)
        if agent_id:
            query = query.where(LogEvent.agent_id == agent_id)
        if severity:
            query = query.where(LogEvent.severity == severity)
        if error_only:
            query = query.where(LogEvent.severity.in_(["error", "critical"]))
        if from_time:
            query = query.where(LogEvent.created_at >= from_time)
        if to_time:
            query = query.where(LogEvent.created_at <= to_time)

        total = await self.db.execute(select(func.count()).select_from(query.subquery()))
        result = await self.db.execute(query.order_by(LogEvent.created_at.desc()).offset(offset).limit(limit))
        return result.scalars().all(), total.scalar()

    async def export_jsonl(self, run_id: str) -> str:
        result = await self.db.execute(
            select(LogEvent).where(LogEvent.run_id == run_id).order_by(LogEvent.created_at)
        )
        events = result.scalars().all()
        lines = []
        for e in events:
            lines.append(
                f'{{"timestamp":"{e.created_at.isoformat()}","severity":"{e.severity}",'
                f'"message":"{e.message}","run_id":"{e.run_id}","trace_id":"{e.trace_id or ""}"}}'
            )
        return "\n".join(lines)


class CostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_event(self, run_id: str, event_type: str, model_name: str = None,
                           provider: str = None, tokens_in: int = 0, tokens_out: int = 0,
                           estimated_cost: float = 0.0, actual_cost: float = None,
                           is_local: bool = True, latency_ms: float = None,
                           phase_id: str = None, agent_id: str = None) -> CostEvent:
        event = CostEvent(
            run_id=run_id, phase_id=phase_id, agent_id=agent_id,
            event_type=event_type, model_name=model_name, provider=provider,
            tokens_in=tokens_in, tokens_out=tokens_out,
            estimated_cost=estimated_cost, actual_cost=actual_cost,
            is_local=is_local, latency_ms=latency_ms,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def get_report(self, run_id: str) -> Dict:
        result = await self.db.execute(select(CostEvent).where(CostEvent.run_id == run_id))
        events = result.scalars().all()
        total = sum(e.estimated_cost for e in events)
        local = sum(e.estimated_cost for e in events if e.is_local)
        paid = sum(e.estimated_cost for e in events if not e.is_local)
        return {
            "total_cost": round(total, 4),
            "local_cost": round(local, 4),
            "paid_cost": round(paid, 4),
            "event_count": len(events),
        }
