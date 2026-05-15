"""Event bus for real-time WebSocket broadcasting and persistence.

This module provides:
1. In-memory event bus for subscribing/broadcasting events per run
2. Automatic persistence of all events to the database
3. WebSocket broadcast integration
4. Event replay from database for missed events
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Callable, Any, Set
from dataclasses import dataclass, field, asdict

from src.core.logging import get_logger
from src.core.database import async_session_factory
from src.models import LogEvent, Run, Phase, Agent

logger = get_logger("event_bus")


@dataclass
class Event:
    """Universal event type for the event bus."""
    type: str
    run_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    phase_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    trace_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class RunEventBus:
    """Per-run event bus with subscriber management."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self._subscribers: Set[Callable[[Event], None]] = set()
        self._event_buffer: List[Event] = []
        self._max_buffer = 1000

    def subscribe(self, callback: Callable[[Event], None]):
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[Event], None]):
        self._subscribers.discard(callback)

    async def publish(self, event: Event):
        """Publish event to all subscribers and persist to DB."""
        # Buffer for replay
        self._event_buffer.append(event)
        if len(self._event_buffer) > self._max_buffer:
            self._event_buffer = self._event_buffer[-self._max_buffer:]

        # Broadcast to WebSocket subscribers
        for cb in self._subscribers:
            try:
                cb(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")

        # Persist to database (fire-and-forget)
        asyncio.create_task(self._persist_event(event))

    async def _persist_event(self, event: Event):
        """Persist event to database."""
        try:
            async with async_session_factory() as session:
                log = LogEvent(
                    run_id=event.run_id,
                    phase_id=event.phase_id,
                    agent_id=event.agent_id,
                    task_id=event.task_id,
                    trace_id=event.trace_id or event.data.get("trace_id"),
                    severity=event.severity,
                    message=event.data.get("message", f"{event.type}: {json.dumps(event.data)}"),
                    source_file=event.data.get("source_file"),
                    commit_hash=event.data.get("commit_hash"),
                    metadata_=event.data,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist event: {e}")

    def get_buffered_events(self, since: Optional[str] = None) -> List[Event]:
        """Get buffered events, optionally since a timestamp."""
        if not since:
            return list(self._event_buffer)
        return [e for e in self._event_buffer if e.timestamp > since]


class EventBusManager:
    """Manages event buses for all active runs."""

    _buses: Dict[str, RunEventBus] = {}

    @classmethod
    def get_bus(cls, run_id: str) -> RunEventBus:
        if run_id not in cls._buses:
            cls._buses[run_id] = RunEventBus(run_id)
        return cls._buses[run_id]

    @classmethod
    def remove_bus(cls, run_id: str):
        cls._buses.pop(run_id, None)


# Convenience functions for publishing common event types
async def publish_phase_transition(run_id: str, phase_name: str, old_status: str, new_status: str,
                                    agent_id: str = None, data: dict = None):
    """Publish a phase transition event."""
    severity = "info" if new_status != "failed" else "error"
    event = Event(
        type="phase.transition",
        run_id=run_id,
        severity=severity,
        agent_id=agent_id,
        data={
            "phase_name": phase_name,
            "old_status": old_status,
            "new_status": new_status,
            "message": f"Phase '{phase_name}': {old_status} → {new_status}",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_agent_activity(run_id: str, agent_name: str, action: str, data: dict = None):
    """Publish an agent activity event."""
    event = Event(
        type="agent.activity",
        run_id=run_id,
        severity="info",
        data={
            "agent_name": agent_name,
            "action": action,
            "message": f"Agent '{agent_name}': {action}",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_artifact_created(run_id: str, artifact_name: str, artifact_type: str,
                                    phase_name: str = None, data: dict = None):
    """Publish an artifact creation event."""
    event = Event(
        type="artifact.created",
        run_id=run_id,
        severity="info",
        data={
            "artifact_name": artifact_name,
            "artifact_type": artifact_type,
            "phase_name": phase_name,
            "message": f"Artifact created: {artifact_name} ({artifact_type})",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_cost_event(run_id: str, model_name: str, tokens_in: int, tokens_out: int,
                              cost: float, is_local: bool, data: dict = None):
    """Publish a cost tracking event."""
    event = Event(
        type="cost.recorded",
        run_id=run_id,
        severity="info",
        data={
            "model_name": model_name,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "is_local": is_local,
            "message": f"Cost: ${cost:.4f} ({tokens_in + tokens_out} tokens, {model_name})",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_deployment_state(run_id: str, status: str, url: str = None, data: dict = None):
    """Publish a deployment state change event."""
    severity = "error" if status in ("failed", "error") else "info"
    event = Event(
        type="deployment.state_changed",
        run_id=run_id,
        severity=severity,
        data={
            "status": status,
            "url": url,
            "message": f"Deployment: {status}" + (f" at {url}" if url else ""),
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_governance_finding(run_id: str, policy_name: str, decision: str,
                                      severity: str = "info", data: dict = None):
    """Publish a governance finding event."""
    event = Event(
        type="governance.finding",
        run_id=run_id,
        severity=severity,
        data={
            "policy_name": policy_name,
            "decision": decision,
            "message": f"Governance: {policy_name} → {decision}",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_security_finding(run_id: str, scanner: str, finding_severity: str,
                                    title: str, data: dict = None):
    """Publish a security finding event."""
    event = Event(
        type="security.finding",
        run_id=run_id,
        severity=finding_severity if finding_severity in ("critical", "error") else "warning",
        data={
            "scanner": scanner,
            "finding_severity": finding_severity,
            "title": title,
            "message": f"Security [{scanner}]: {title} ({finding_severity})",
            **(data or {}),
        },
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def publish_custom_event(run_id: str, event_type: str, message: str,
                                severity: str = "info", data: dict = None):
    """Publish a custom event."""
    event = Event(
        type=event_type,
        run_id=run_id,
        severity=severity,
        data={"message": message, **(data or {})},
    )
    bus = EventBusManager.get_bus(run_id)
    await bus.publish(event)


async def replay_events(run_id: str, since: Optional[str] = None) -> List[Dict]:
    """Replay events from database for a run."""
    try:
        async with async_session_factory() as session:
            from sqlalchemy import select
            query = select(LogEvent).where(LogEvent.run_id == run_id)
            if since:
                query = query.where(LogEvent.created_at > since)
            query = query.order_by(LogEvent.created_at)
            result = await session.execute(query)
            events = result.scalars().all()
            return [
                {
                    "id": e.id,
                    "type": "log.entry",
                    "run_id": e.run_id,
                    "phase_id": e.phase_id,
                    "agent_id": e.agent_id,
                    "severity": e.severity,
                    "message": e.message,
                    "data": e.metadata_,
                    "timestamp": e.created_at.isoformat(),
                }
                for e in events
            ]
    except Exception as e:
        logger.error(f"Failed to replay events: {e}")
        return []
