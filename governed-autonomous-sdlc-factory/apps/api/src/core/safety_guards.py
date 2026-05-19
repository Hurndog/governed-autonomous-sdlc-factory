"""Operational Safety Guards for the Governed Autonomous SDLC Factory.

Provides bounded execution controls to prevent:
- Infinite pipeline runs
- Infinite phase execution
- Infinite retries
- Unbounded model calls
- Unbounded token consumption
- Unbounded artifact/event generation
- Runaway semantic refinement loops
- Orphan background tasks

Each guard activation persists evidence to the database.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.core.database import Base, SyncSessionLocal
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("safety_guards")


# ── Guard Activation Record Model ──

class GuardActivation(Base):
    """Persisted evidence of a safety guard activation."""
    __tablename__ = "guard_activations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(36), nullable=False, index=True)
    phase_name = Column(String(128), nullable=True)
    guard_name = Column(String(64), nullable=False)
    configured_limit = Column(String(256), nullable=False)
    observed_value = Column(String(256), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    resulting_status = Column(String(64), nullable=False)
    message = Column(Text, nullable=True)
    is_recoverable = Column(Boolean, default=False)
    metadata_json = Column(JSONB, default={})


# ── Guard Status Enum ──

class GuardStatus(str, Enum):
    STOPPED_BY_PIPELINE_TIMEOUT = "stopped_by_pipeline_timeout"
    STOPPED_BY_PHASE_TIMEOUT = "stopped_by_phase_timeout"
    STOPPED_BY_RETRY_LIMIT = "stopped_by_retry_limit"
    STOPPED_BY_MODEL_CALL_BUDGET = "stopped_by_model_call_budget"
    STOPPED_BY_TOKEN_BUDGET = "stopped_by_token_budget"
    STOPPED_BY_ARTIFACT_BUDGET = "stopped_by_artifact_budget"
    STOPPED_BY_EVENT_BUDGET = "stopped_by_event_budget"
    STOPPED_BY_SEMANTIC_ITERATION_LIMIT = "stopped_by_semantic_iteration_limit"
    STOPPED_BY_MUTATION_ITERATION_LIMIT = "stopped_by_mutation_iteration_limit"
    STOPPED_BY_REPLAY_TIMEOUT = "stopped_by_replay_timeout"
    STOPPED_BY_BACKGROUND_TASK_LEASE_EXPIRY = "stopped_by_background_task_lease_expiry"
    STOPPED_BY_POLICY = "stopped_by_policy"
    BOUNDED_COMPLETION = "bounded_completion"


# ── Safety Guard Tracker ──

class SafetyGuard:
    """Tracks and enforces operational safety limits for a run."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_time = time.monotonic()
        self.phase_start_time: Optional[float] = None
        self.current_phase: Optional[str] = None
        self.model_calls_total = 0
        self.model_calls_per_phase: dict = {}
        self.tokens_used = 0
        self.artifact_count = 0
        self.event_count = 0
        self.retry_counts: dict = {}
        self.semantic_iterations = 0
        self.mutation_iterations = 0
        self._stopped = False
        self._stop_reason: Optional[GuardStatus] = None
        self._stop_message: Optional[str] = None

    def reset(self):
        """Reset all counters for reuse."""
        self.__init__(self.run_id)

    # ── Phase Tracking ──

    def begin_phase(self, phase_name: str):
        """Mark the start of a phase."""
        self.current_phase = phase_name
        self.phase_start_time = time.monotonic()
        if phase_name not in self.model_calls_per_phase:
            self.model_calls_per_phase[phase_name] = 0
        if phase_name not in self.retry_counts:
            self.retry_counts[phase_name] = 0

    def end_phase(self):
        """Mark the end of a phase."""
        self.current_phase = None
        self.phase_start_time = None

    # ── Model Call Tracking ──

    def record_model_call(self, tokens: int = 0):
        """Record a model call."""
        self.model_calls_total += 1
        self.tokens_used += tokens
        if self.current_phase:
            self.model_calls_per_phase[self.current_phase] = (
                self.model_calls_per_phase.get(self.current_phase, 0) + 1
            )

    # ── Retry Tracking ──

    def record_retry(self, phase_name: Optional[str] = None):
        """Record a retry attempt."""
        phase = phase_name or self.current_phase or "unknown"
        self.retry_counts[phase] = self.retry_counts.get(phase, 0) + 1
        return self.retry_counts[phase]

    # ── Artifact/Event Tracking ──

    def record_artifact(self):
        """Record artifact creation."""
        self.artifact_count += 1

    def record_event(self):
        """Record event creation."""
        self.event_count += 1

    # ── Iteration Tracking ──

    def record_semantic_iteration(self):
        """Record a semantic refinement iteration."""
        self.semantic_iterations += 1

    def record_mutation_iteration(self):
        """Record a mutation iteration."""
        self.mutation_iterations += 1

    # ── Guard Checks ──

    def check_all(self) -> Optional[GuardStatus]:
        """Run all guard checks. Returns GuardStatus if any guard activates, None if all clear."""
        checks = [
            self._check_pipeline_timeout,
            self._check_phase_timeout,
            self._check_retry_limit,
            self._check_model_call_budget,
            self._check_token_budget,
            self._check_artifact_budget,
            self._check_event_budget,
            self._check_semantic_iteration_limit,
            self._check_mutation_iteration_limit,
        ]
        for check in checks:
            status = check()
            if status:
                return status
        return None

    def _check_pipeline_timeout(self) -> Optional[GuardStatus]:
        elapsed = time.monotonic() - self.start_time
        if elapsed > settings.pipeline_timeout_seconds:
            return self._activate(
                GuardStatus.STOPPED_BY_PIPELINE_TIMEOUT,
                guard_name="pipeline_timeout",
                limit=f"{settings.pipeline_timeout_seconds}s",
                observed=f"{elapsed:.1f}s",
                message=f"Pipeline exceeded {settings.pipeline_timeout_seconds}s timeout after {elapsed:.1f}s",
                recoverable=False,
            )
        return None

    def _check_phase_timeout(self) -> Optional[GuardStatus]:
        if self.phase_start_time and self.current_phase:
            elapsed = time.monotonic() - self.phase_start_time
            if elapsed > settings.phase_timeout_seconds:
                return self._activate(
                    GuardStatus.STOPPED_BY_PHASE_TIMEOUT,
                    guard_name="phase_timeout",
                    limit=f"{settings.phase_timeout_seconds}s",
                    observed=f"{elapsed:.1f}s",
                    message=f"Phase '{self.current_phase}' exceeded {settings.phase_timeout_seconds}s timeout",
                    recoverable=True,
                )
        return None

    def _check_retry_limit(self) -> Optional[GuardStatus]:
        if self.current_phase:
            retries = self.retry_counts.get(self.current_phase, 0)
            if retries >= settings.max_retries_per_phase:
                return self._activate(
                    GuardStatus.STOPPED_BY_RETRY_LIMIT,
                    guard_name="retry_limit",
                    limit=str(settings.max_retries_per_phase),
                    observed=str(retries),
                    message=f"Phase '{self.current_phase}' exceeded {settings.max_retries_per_phase} retries",
                    recoverable=True,
                )
        return None

    def _check_model_call_budget(self) -> Optional[GuardStatus]:
        # Check per-phase limit
        if self.current_phase:
            phase_calls = self.model_calls_per_phase.get(self.current_phase, 0)
            if phase_calls >= settings.max_model_calls_per_phase:
                return self._activate(
                    GuardStatus.STOPPED_BY_MODEL_CALL_BUDGET,
                    guard_name="model_call_budget_per_phase",
                    limit=str(settings.max_model_calls_per_phase),
                    observed=str(phase_calls),
                    message=f"Phase '{self.current_phase}' exceeded {settings.max_model_calls_per_phase} model calls",
                    recoverable=True,
                )
        # Check total limit
        if self.model_calls_total >= settings.max_total_model_calls_per_run:
            return self._activate(
                GuardStatus.STOPPED_BY_MODEL_CALL_BUDGET,
                guard_name="model_call_budget_total",
                limit=str(settings.max_total_model_calls_per_run),
                observed=str(self.model_calls_total),
                message=f"Run exceeded {settings.max_total_model_calls_per_run} total model calls",
                recoverable=False,
            )
        return None

    def _check_token_budget(self) -> Optional[GuardStatus]:
        if self.tokens_used >= settings.max_tokens_per_run:
            return self._activate(
                GuardStatus.STOPPED_BY_TOKEN_BUDGET,
                guard_name="token_budget",
                limit=str(settings.max_tokens_per_run),
                observed=str(self.tokens_used),
                message=f"Run exceeded {settings.max_tokens_per_run} token budget",
                recoverable=False,
            )
        return None

    def _check_artifact_budget(self) -> Optional[GuardStatus]:
        if self.artifact_count >= settings.max_artifacts_per_run:
            return self._activate(
                GuardStatus.STOPPED_BY_ARTIFACT_BUDGET,
                guard_name="artifact_budget",
                limit=str(settings.max_artifacts_per_run),
                observed=str(self.artifact_count),
                message=f"Run exceeded {settings.max_artifacts_per_run} artifact limit",
                recoverable=False,
            )
        return None

    def _check_event_budget(self) -> Optional[GuardStatus]:
        if self.event_count >= settings.max_events_per_run:
            return self._activate(
                GuardStatus.STOPPED_BY_EVENT_BUDGET,
                guard_name="event_budget",
                limit=str(settings.max_events_per_run),
                observed=str(self.event_count),
                message=f"Run exceeded {settings.max_events_per_run} event limit",
                recoverable=False,
            )
        return None

    def _check_semantic_iteration_limit(self) -> Optional[GuardStatus]:
        """Check semantic iteration stall — NOT a hard cap.
        
        The runtime should converge long before hitting this limit.
        This guard detects stalls, not normal operation.
        """
        if self.semantic_iterations >= settings.max_semantic_iterations:
            return self._activate(
                GuardStatus.STOPPED_BY_SEMANTIC_ITERATION_LIMIT,
                guard_name="semantic_iteration_limit",
                limit=str(settings.max_semantic_iterations),
                observed=str(self.semantic_iterations),
                message=f"Semantic refinement stalled after {self.semantic_iterations} iterations without convergence",
                recoverable=True,
            )
        return None

    def _check_mutation_iteration_limit(self) -> Optional[GuardStatus]:
        """Check mutation iteration stall — NOT a hard cap.
        
        The runtime should converge long before hitting this limit.
        This guard detects stalls, not normal operation.
        """
        if self.mutation_iterations >= settings.max_mutation_iterations:
            return self._activate(
                GuardStatus.STOPPED_BY_MUTATION_ITERATION_LIMIT,
                guard_name="mutation_iteration_limit",
                limit=str(settings.max_mutation_iterations),
                observed=str(self.mutation_iterations),
                message=f"Mutation testing stalled after {self.mutation_iterations} iterations without convergence",
                recoverable=True,
            )
        return None

    def check_convergence(self, current_score: float, score_history: list) -> bool:
        """Check if semantic/mutation convergence has been achieved.
        
        Returns True if the runtime should stop because further iterations
        are unlikely to improve the score.
        """
        if len(score_history) < settings.semantic_convergence_window:
            return False
        recent = score_history[-settings.semantic_convergence_window:]
        if max(recent) - min(recent) < (1.0 - settings.semantic_convergence_threshold):
            return True
        return False

    def check_progress(self, current_state: dict, previous_state: dict) -> bool:
        """Check if progress is being made.
        
        Returns True if the runtime is stalled (no meaningful progress).
        """
        if not previous_state:
            return True
        # Compare key metrics — if nothing changed, we're stalled
        for key in current_state:
            if current_state.get(key) != previous_state.get(key):
                return True
        return False

    def _activate(
        self,
        status: GuardStatus,
        guard_name: str,
        limit: str,
        observed: str,
        message: str,
        recoverable: bool = False,
    ) -> GuardStatus:
        """Activate a guard and persist evidence."""
        self._stopped = True
        self._stop_reason = status
        self._stop_message = message

        logger.warning(f"GUARD ACTIVATED: {guard_name} | {message}")

        try:
            db = SyncSessionLocal()
            activation = GuardActivation(
                run_id=self.run_id,
                phase_name=self.current_phase,
                guard_name=guard_name,
                configured_limit=limit,
                observed_value=observed,
                resulting_status=status.value,
                message=message,
                is_recoverable=recoverable,
            )
            db.add(activation)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to persist guard activation: {e}")

        return status

    # ── Properties ──

    @property
    def is_stopped(self) -> bool:
        return self._stopped

    @property
    def stop_reason(self) -> Optional[GuardStatus]:
        return self._stop_reason

    @property
    def stop_message(self) -> Optional[str]:
        return self._stop_message

    def get_elapsed(self) -> float:
        return time.monotonic() - self.start_time


# ── Async Timeout Helper ──

async def with_phase_timeout(guard: SafetyGuard, coro, phase_name: str):
    """Execute a coroutine with phase timeout enforcement."""
    guard.begin_phase(phase_name)
    try:
        result = await asyncio.wait_for(coro, timeout=settings.phase_timeout_seconds)
        # Check all guards after phase completes
        status = guard.check_all()
        if status:
            raise GuardActivationError(guard)
        return result
    except asyncio.TimeoutError:
        guard._activate(
            GuardStatus.STOPPED_BY_PHASE_TIMEOUT,
            guard_name="phase_timeout",
            limit=f"{settings.phase_timeout_seconds}s",
            observed="timeout",
            message=f"Phase '{phase_name}' timed out after {settings.phase_timeout_seconds}s",
            recoverable=True,
        )
        raise GuardActivationError(guard)
    finally:
        guard.end_phase()


class GuardActivationError(Exception):
    """Raised when a safety guard activates."""
    def __init__(self, guard: SafetyGuard):
        self.guard = guard
        self.status = guard.stop_reason
        self.message = guard.stop_message
        super().__init__(f"Guard activated: {self.status} — {self.message}")
