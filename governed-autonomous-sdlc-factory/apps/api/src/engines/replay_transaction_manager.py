"""Replay Transaction Manager — deterministic transaction orchestration.

Manages transaction boundaries for the synchronous replay runtime.
Ensures deterministic flush ordering, rollback safety, and replay consistency.

Transaction rules:
1. Only specific phases may flush
2. Only specific phases may commit
3. No nested transactions
4. No sub-method commits
5. Deterministic ordering guaranteed
"""
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from src.core.logging import get_logger

logger = get_logger("replay_txn")


class ReplayPhase(str, Enum):
    INITIALIZED = "initialized"
    RECONSTRUCTING = "reconstructing"
    VALIDATING = "validating"
    REPLAYING = "replaying"
    PERSISTING = "persisting"
    VERIFYING = "verifying"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# Phases that are allowed to flush
FLUSH_PHASES = {ReplayPhase.RECONSTRUCTING, ReplayPhase.REPLAYING, ReplayPhase.PERSISTING}

# Phases that are allowed to commit
COMMIT_PHASES = {ReplayPhase.FINALIZING}

# Phases that may create integrity checkpoints
CHECKPOINT_PHASES = {ReplayPhase.REPLAYING, ReplayPhase.PERSISTING, ReplayPhase.VERIFYING}


class ReplayTransactionManager:
    """Manages deterministic transaction boundaries for replay execution.

    The transaction manager ensures:
    - Flush only happens in allowed phases
    - Commit only happens in allowed phases
    - Rollback is always safe
    - Checkpoints are created at deterministic points
    """

    def __init__(self, session: Session):
        self._session = session
        self._phase = ReplayPhase.INITIALIZED
        self._flush_count = 0
        self._checkpoint_count = 0
        self._is_committed = False
        self._is_rolled_back = False

    @property
    def phase(self) -> ReplayPhase:
        return self._phase

    @property
    def session(self) -> Session:
        return self._session

    def transition_to(self, new_phase: ReplayPhase) -> None:
        """Transition to a new replay phase."""
        old_phase = self._phase
        self._phase = new_phase
        logger.debug(f"Replay phase transition: {old_phase} → {new_phase}")

    def flush(self) -> None:
        """Flush the session — only allowed in specific phases."""
        if self._phase not in FLUSH_PHASES:
            raise RuntimeError(
                f"Flush not allowed in phase '{self._phase}'. "
                f"Allowed phases: {FLUSH_PHASES}"
            )
        self._session.flush()
        self._flush_count += 1
        logger.debug(f"Flush #{self._flush_count} in phase '{self._phase}'")

    def commit(self) -> None:
        """Commit the transaction — only allowed in finalizing phase."""
        if self._phase not in COMMIT_PHASES:
            raise RuntimeError(
                f"Commit not allowed in phase '{self._phase}'. "
                f"Allowed phases: {COMMIT_PHASES}"
            )
        if self._is_committed:
            raise RuntimeError("Transaction already committed")
        if self._is_rolled_back:
            raise RuntimeError("Cannot commit after rollback")
        self._session.commit()
        self._is_committed = True
        logger.info(f"Transaction committed (flushes: {self._flush_count}, checkpoints: {self._checkpoint_count})")

    def rollback(self) -> None:
        """Rollback the transaction — always safe."""
        if self._is_committed:
            raise RuntimeError("Cannot rollback after commit")
        self._session.rollback()
        self._is_rolled_back = True
        self._phase = ReplayPhase.ROLLED_BACK
        logger.warning(f"Transaction rolled back (was in phase '{self._phase}')")

    def checkpoint(self, label: str = "") -> dict:
        """Create an integrity checkpoint."""
        if self._phase not in CHECKPOINT_PHASES:
            raise RuntimeError(
                f"Checkpoint not allowed in phase '{self._phase}'. "
                f"Allowed phases: {CHECKPOINT_PHASES}"
            )
        self._checkpoint_count += 1
        cp = {
            "checkpoint_id": self._checkpoint_count,
            "phase": self._phase.value,
            "label": label,
            "flush_count": self._flush_count,
        }
        logger.debug(f"Checkpoint #{self._checkpoint_count}: {label} in phase '{self._phase}'")
        return cp

    def get_stats(self) -> dict:
        """Get transaction statistics."""
        return {
            "phase": self._phase.value,
            "flush_count": self._flush_count,
            "checkpoint_count": self._checkpoint_count,
            "is_committed": self._is_committed,
            "is_rolled_back": self._is_rolled_back,
        }
