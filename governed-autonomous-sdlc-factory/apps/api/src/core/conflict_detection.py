"""Minimal Conflict Detection for Requirements.

Detects obvious contradictions between requirements and persists findings.
This is not a formal logic engine — it catches common-sense conflicts.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.core.database import Base, SyncSessionLocal
from src.core.logging import get_logger

logger = get_logger("conflict_detection")


# ── Conflict Finding Model ──

class RequirementConflict(Base):
    """Persisted evidence of a detected requirement conflict."""
    __tablename__ = "requirement_conflicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(36), nullable=False, index=True)
    requirement_id_1 = Column(String(64), nullable=False)
    requirement_id_2 = Column(String(64), nullable=False)
    conflict_type = Column(String(64), nullable=False)
    severity = Column(String(16), nullable=False)  # low, medium, high, critical
    explanation = Column(Text, nullable=False)
    recommended_resolution = Column(Text)
    release_gate_impact = Column(String(16), nullable=False)  # pass, warn, fail
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    metadata_json = Column(JSONB, default={})


# ── Conflict Detector ──

class ConflictDetector:
    """Detects conflicts between normalized requirements."""

    # Conflict pattern definitions
    CONFLICT_PATTERNS = [
        {
            "name": "immutability_vs_editability",
            "type": "immutability_vs_editability",
            "severity": "critical",
            "keywords_1": ["immutable", "unchangeable", "read-only", "cannot be modified", "must not be changed"],
            "keywords_2": ["edit", "modify", "update", "change", "alter", "overwrite"],
            "explanation": "One requirement states data must be immutable while another allows editing.",
            "recommended_resolution": "Clarify which operations are allowed. Consider append-only with soft-delete, or versioned edits.",
            "release_gate_impact": "fail",
        },
        {
            "name": "retention_vs_deletion",
            "type": "retention_vs_deletion",
            "severity": "critical",
            "keywords_1": ["retain", "retention", "must be kept", "must be stored", "preserve", "seven years", "5 years", "10 years"],
            "keywords_2": ["delete", "permanently delete", "erase", "remove", "right to be forgotten"],
            "explanation": "One requirement mandates data retention while another allows permanent deletion.",
            "recommended_resolution": "Clarify retention policy vs deletion rights. Consider legal hold, soft-delete, or anonymization.",
            "release_gate_impact": "fail",
        },
        {
            "name": "auditability_vs_no_logging",
            "type": "auditability_vs_no_logging",
            "severity": "high",
            "keywords_1": ["auditable", "audit trail", "audit log", "must be logged", "traceable"],
            "keywords_2": ["no log", "must not store", "no record", "do not log", "without logging"],
            "explanation": "One requirement demands auditability while another prohibits logging.",
            "recommended_resolution": "Clarify what must be logged vs what must not be stored. Consider separate audit storage.",
            "release_gate_impact": "fail",
        },
        {
            "name": "tenant_isolation_vs_cross_tenant_access",
            "type": "tenant_isolation_vs_cross_tenant_access",
            "severity": "critical",
            "keywords_1": ["tenant isolation", "cross-tenant", "own tenant", "only their own", "tenant boundary"],
            "keywords_2": ["all tenants", "cross-tenant", "any tenant", "without approval", "all incidents"],
            "explanation": "One requirement enforces tenant isolation while another allows cross-tenant access without restriction.",
            "recommended_resolution": "Define explicit cross-tenant access policies with approval workflows.",
            "release_gate_impact": "fail",
        },
    ]

    def __init__(self, run_id: str):
        self.run_id = run_id

    def detect_conflicts(self, requirements: List) -> List[RequirementConflict]:
        """Detect conflicts among a list of RequirementNormalization records."""
        conflicts = []
        for i, req1 in enumerate(requirements):
            for req2 in requirements[i + 1:]:
                conflict = self._check_pair(req1, req2)
                if conflict:
                    conflicts.append(conflict)
        return conflicts

    def _check_pair(self, req1, req2) -> Optional[RequirementConflict]:
        """Check a pair of requirements for conflicts."""
        text1 = (req1.original_text or "").lower()
        text2 = (req2.original_text or "").lower()

        for pattern in self.CONFLICT_PATTERNS:
            if self._matches_pattern(text1, text2, pattern):
                return RequirementConflict(
                    run_id=self.run_id,
                    requirement_id_1=req1.requirement_id,
                    requirement_id_2=req2.requirement_id,
                    conflict_type=pattern["type"],
                    severity=pattern["severity"],
                    explanation=pattern["explanation"],
                    recommended_resolution=pattern["recommended_resolution"],
                    release_gate_impact=pattern["release_gate_impact"],
                )
        return None

    def _matches_pattern(self, text1: str, text2: str, pattern: dict) -> bool:
        """Check if two texts match a conflict pattern."""
        kw1 = pattern["keywords_1"]
        kw2 = pattern["keywords_2"]

        # Check if text1 has keywords from group 1 and text2 has keywords from group 2
        text1_has_kw1 = any(kw in text1 for kw in kw1)
        text2_has_kw2 = any(kw in text2 for kw in kw2)

        if text1_has_kw1 and text2_has_kw2:
            return True

        # Also check the reverse
        text1_has_kw2 = any(kw in text1 for kw in kw2)
        text2_has_kw1 = any(kw in text2 for kw in kw1)

        if text1_has_kw2 and text2_has_kw1:
            return True

        return False

    def persist_conflicts(self, conflicts: List[RequirementConflict]):
        """Persist conflict findings to the database."""
        db = SyncSessionLocal()
        try:
            for conflict in conflicts:
                db.add(conflict)
            db.commit()
            logger.info(f"Persisted {len(conflicts)} conflict findings for run {self.run_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist conflicts: {e}")
        finally:
            db.close()

    def get_conflicts_for_run(self, run_id: str) -> List[RequirementConflict]:
        """Retrieve persisted conflicts for a run."""
        db = SyncSessionLocal()
        try:
            return db.query(RequirementConflict).filter(
                RequirementConflict.run_id == run_id
            ).all()
        finally:
            db.close()
