"""Phase, Artifact, Approval, Cost, and Log schemas."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


# Phase schemas
class PhaseResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}
    id: str
    run_id: str
    name: str
    status: str
    order_index: int
    agent_id: Optional[str]
    model_used: Optional[str]
    tokens_in: int
    tokens_out: int
    cost: float
    retry_count: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class PhaseDetailResponse(PhaseResponse):
    tasks: List["TaskResponse"] = []


# Task schemas
class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    phase_id: str
    name: str
    description: Optional[str]
    status: str
    requirement_ids: Optional[List[str]]
    created_at: datetime


# Artifact schemas
class ArtifactCreate(BaseModel):
    task_id: str
    run_id: str
    name: str
    artifact_type: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ArtifactResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    task_id: str
    run_id: str
    name: str
    artifact_type: str
    content: Optional[str]
    file_path: Optional[str]
    version: int
    is_baseline: bool
    is_locked: bool
    metadata_: Optional[Dict[str, Any]]
    created_at: datetime


# Approval schemas
class ApprovalCreate(BaseModel):
    run_id: str
    artifact_id: Optional[str] = None
    approval_type: str
    is_demo: bool = False
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    run_id: str
    artifact_id: Optional[str]
    approval_type: str
    status: str
    approver: Optional[str]
    approved_at: Optional[datetime]
    artifact_version: Optional[int]
    is_demo: bool
    notes: Optional[str]
    created_at: datetime


# Cost schemas
class CostEventCreate(BaseModel):
    model_config = {"protected_namespaces": ()}
    run_id: str
    phase_id: Optional[str] = None
    agent_id: Optional[str] = None
    event_type: str
    model_name: Optional[str] = None
    provider: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    estimated_cost: float = 0.0
    actual_cost: Optional[float] = None
    is_local: bool = True
    latency_ms: Optional[float] = None


class CostReportResponse(BaseModel):
    run_id: str
    total_cost: float
    budget_limit: Optional[float]
    remaining_budget: Optional[float]
    warning_threshold: float
    is_near_limit: bool
    is_hard_limit_reached: bool
    local_cost: float
    paid_cost: float
    estimated_savings: float
    by_phase: Dict[str, float]
    by_agent: Dict[str, float]
    by_model: Dict[str, float]


# Log schemas
class LogEventResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}
    id: str
    run_id: str
    phase_id: Optional[str]
    agent_id: Optional[str]
    task_id: Optional[str]
    trace_id: Optional[str]
    severity: str
    message: str
    source_file: Optional[str]
    commit_hash: Optional[str]
    metadata_: Optional[Dict[str, Any]]
    created_at: datetime


class LogFilterParams(BaseModel):
    run_id: Optional[str] = None
    phase_id: Optional[str] = None
    agent_id: Optional[str] = None
    severity: Optional[str] = None
    error_only: bool = False
    source_file: Optional[str] = None
    commit_hash: Optional[str] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = 0
