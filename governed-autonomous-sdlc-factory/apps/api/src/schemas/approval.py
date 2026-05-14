"""Approval schemas for the Governed Autonomous SDLC Factory API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ApprovalDecision(str, Enum):
    """Approval decision values."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalStatus(str, Enum):
    """Approval lifecycle states."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalCreate(BaseModel):
    """Schema for creating a new approval request."""

    run_id: str = Field(..., description="Run ID.")
    phase_id: str = Field(..., description="Phase ID requiring approval.")
    phase_name: str = Field(..., description="Phase name.")
    title: str = Field(
        ..., min_length=1, max_length=500, description="Approval title."
    )
    description: str | None = Field(
        None, max_length=5000, description="Detailed description."
    )
    approver_id: str | None = Field(
        None, description="Specific approver ID (optional)."
    )
    timeout_hours: int | None = Field(
        None, ge=1, le=168, description="Timeout in hours."
    )
    evidence_ids: list[str] = Field(
        default_factory=list, description="Related evidence artifact IDs."
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Arbitrary metadata."
    )


class ApprovalDecisionRequest(BaseModel):
    """Schema for submitting an approval decision."""

    decision: ApprovalDecision = Field(
        ..., description="Approve or reject."
    )
    comment: str | None = Field(
        None, max_length=2000, description="Decision comment."
    )
    approver_id: str | None = Field(
        None, description="Approver ID (for audit)."
    )


class ApprovalResponse(BaseModel):
    """Approval response schema."""

    id: str = Field(..., description="Approval ID (UUID).")
    run_id: str = Field(..., description="Run ID.")
    phase_id: str = Field(..., description="Phase ID.")
    phase_name: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    status: ApprovalStatus = Field(...)
    decision: ApprovalDecision | None = Field(None)
    comment: str | None = Field(None)
    approver_id: str | None = Field(None)
    requested_at: datetime = Field(...)
    decided_at: datetime | None = Field(None)
    expires_at: datetime | None = Field(None)
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    is_auto_approved: bool = Field(default=False)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
