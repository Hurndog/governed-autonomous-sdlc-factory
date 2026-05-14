"""Database models for the Governed Autonomous SDLC Factory."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, ForeignKey,
    JSON, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ArtifactType(str, Enum):
    SPECIFICATION = "specification"
    ARCHITECTURE = "architecture"
    TEST_PLAN = "test_plan"
    EVIDENCE = "evidence"
    CODE = "code"
    DEPLOYMENT = "deployment"
    GOVERNANCE = "governance"
    TRACEABILITY = "traceability"
    SNAPSHOT = "snapshot"


# 5.2.1 projects
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    idea_text: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active")
    github_repo_url: Mapped[Optional[str]] = mapped_column(String(500))
    local_path: Mapped[Optional[str]] = mapped_column(String(500))
    config: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    runs: Mapped[List["Run"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    spec_versions: Mapped[list["SpecificationVersion"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    arch_versions: Mapped[list["ArchitectureVersion"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    test_plans: Mapped[list["TestPlan"]] = relationship(back_populates="project", cascade="all, delete-orphan")


# 5.3.2 runs
class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=RunStatus.PENDING.value)
    branch_name: Mapped[Optional[str]] = mapped_column(String(255))
    current_phase: Mapped[Optional[str]] = mapped_column(String(100))
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    budget_limit: Mapped[Optional[float]] = mapped_column(Float)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    project: Mapped["Project"] = relationship(back_populates="runs")
    phases: Mapped[List["Phase"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    cost_events: Mapped[List["CostEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    log_events: Mapped[List["LogEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    evidence_bundles: Mapped[List["EvidenceBundle"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    model_calls: Mapped[List["ModelCall"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    tool_calls_list: Mapped[List["ToolCall"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    checkpoints: Mapped[List["RunCheckpoint"]] = relationship(back_populates="run", cascade="all, delete-orphan")

    # ── Phase 4: Engine relationships ──────────────────────────────────
    spec_versions: Mapped[list["SpecificationVersion"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    arch_versions: Mapped[list["ArchitectureVersion"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    governance_evals: Mapped[list["GovernanceEvaluation"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    release_gates: Mapped[list["GovernanceReleaseGate"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    test_plans: Mapped[list["TestPlan"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    traceability_links: Mapped[list["TraceabilityLink"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    artifact_baselines: Mapped[list["ArtifactBaseline"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    snapshots: Mapped[list["RunSnapshot"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    artifact_diffs: Mapped[list["ArtifactDiff"]] = relationship(back_populates="run", cascade="all, delete-orphan")


# 5.3.3 phases
class Phase(Base):
    __tablename__ = "phases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=PhaseStatus.PENDING.value)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"))
    model_used: Mapped[Optional[str]] = mapped_column(String(255))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="phases")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="phases")
    tasks: Mapped[List["Task"]] = relationship(back_populates="phase", cascade="all, delete-orphan")


# 5.3.4 agents
class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    allowed_tools: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    disallowed_tools: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    model_preference: Mapped[Optional[str]] = mapped_column(String(255))
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    phases: Mapped[List["Phase"]] = relationship(back_populates="agent")


# 5.3.5 tasks
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phase_id: Mapped[str] = mapped_column(String(36), ForeignKey("phases.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    requirement_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    acceptance_criteria_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    expected_artifacts: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    test_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    governance_check_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    phase: Mapped["Phase"] = relationship(back_populates="tasks")
    artifacts: Mapped[List["Artifact"]] = relationship(back_populates="task", cascade="all, delete-orphan")


# 5.3.6 artifacts
class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    task: Mapped["Task"] = relationship(back_populates="artifacts")


# 5.3.7 approvals
class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    artifact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("artifacts.id"))
    approval_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=ApprovalStatus.PENDING.value)
    approver: Mapped[Optional[str]] = mapped_column(String(255))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    artifact_version: Mapped[Optional[int]] = mapped_column(Integer)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.8 requirements
class Requirement(Base):
    __tablename__ = "requirements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    req_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    req_type: Mapped[str] = mapped_column(String(50), default="functional")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    value_source: Mapped[str] = mapped_column(String(20), default="inferred")
    domain: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("project_id", "req_id"),)


# 5.3.9 functional_designs
class FunctionalDesign(Base):
    __tablename__ = "functional_designs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    structured_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.10 architecture_documents
class ArchitectureDocument(Base):
    __tablename__ = "architecture_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    structured_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.11 architecture_decisions
class ArchitectureDecision(Base):
    __tablename__ = "architecture_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    adr_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text)
    decision: Mapped[Optional[str]] = mapped_column(Text)
    consequences: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("project_id", "adr_id"),)


# 5.3.12 design_proposals
class DesignProposal(Base):
    __tablename__ = "design_proposals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    structured_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.13 data_models
class DataModel(Base):
    __tablename__ = "data_models"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_yaml: Mapped[Optional[str]] = mapped_column(Text)
    erd_mermaid: Mapped[Optional[str]] = mapped_column(Text)
    sql_schema: Mapped[Optional[str]] = mapped_column(Text)
    migration_sql: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.14 api_contracts
class ApiContract(Base):
    __tablename__ = "api_contracts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    request_schema: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    response_schema: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.15 mcp_contracts
class McpContract(Base):
    __tablename__ = "mcp_contracts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    server_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    allowed_operations: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.16 governance_requirements
class GovernanceRequirement(Base):
    __tablename__ = "governance_requirements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    policy_ref: Mapped[Optional[str]] = mapped_column(String(255))
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.17 test_plans
class TestPlan(Base):
    __tablename__ = "test_plans"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("runs.id"))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    coverage_threshold: Mapped[float] = mapped_column(Float, default=80.0)
    # Phase 4 engine extensions
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    unit_test_strategy: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    integration_test_strategy: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    api_contract_tests: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    edge_cases: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    smoke_tests: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    governance_tests: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    regression_strategy: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    traceability_map: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    generated_by: Mapped[Optional[str]] = mapped_column(String(100))
    # Relationships
    test_cases: Mapped[List["TestCase"]] = relationship(back_populates="test_plan", cascade="all, delete-orphan")
    run: Mapped["Run"] = relationship(back_populates="test_plans")
    project: Mapped["Project"] = relationship(back_populates="test_plans")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# 5.3.18 test_cases
class TestCase(Base):
    __tablename__ = "test_cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_plans.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_type: Mapped[str] = mapped_column(String(50), default="unit")
    description: Mapped[Optional[str]] = mapped_column(Text)
    linked_requirement_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    test_plan: Mapped["TestPlan"] = relationship(back_populates="test_cases")


# 5.3.19 commits
class Commit(Base):
    __tablename__ = "commits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    commit_hash: Mapped[Optional[str]] = mapped_column(String(100))
    branch_name: Mapped[Optional[str]] = mapped_column(String(255))
    message: Mapped[Optional[str]] = mapped_column(Text)
    files_changed: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    artifact_ids: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    is_refactor: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.20 pull_requests
class PullRequest(Base):
    __tablename__ = "pull_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="open")
    source_branch: Mapped[Optional[str]] = mapped_column(String(255))
    target_branch: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.21 test_results
class TestResult(Base):
    __tablename__ = "test_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    test_case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("test_cases.id"))
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float)
    output: Mapped[Optional[str]] = mapped_column(Text)
    error: Mapped[Optional[str]] = mapped_column(Text)
    coverage_pct: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.22 security_findings
class SecurityFinding(Base):
    __tablename__ = "security_findings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    scanner: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    line_number: Mapped[Optional[int]] = mapped_column(Integer)
    remediation: Mapped[Optional[str]] = mapped_column(Text)
    is_exception: Mapped[bool] = mapped_column(Boolean, default=False)
    exception_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.23 governance_findings
class GovernanceFinding(Base):
    __tablename__ = "governance_findings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    output_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.24 cost_events
class CostEvent(Base):
    __tablename__ = "cost_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    phase_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("phases.id"))
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(255))
    provider: Mapped[Optional[str]] = mapped_column(String(100))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost: Mapped[Optional[float]] = mapped_column(Float)
    is_local: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="cost_events")


# 5.3.25 log_events
class LogEvent(Base):
    __tablename__ = "log_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    phase_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("phases.id"))
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"))
    task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"))
    trace_id: Mapped[Optional[str]] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(20), default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500))
    commit_hash: Mapped[Optional[str]] = mapped_column(String(100))
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="log_events")
    __table_args__ = (
        Index("ix_log_events_run_severity", "run_id", "severity"),
        Index("ix_log_events_run_created", "run_id", "created_at"),
    )


# 5.3.26 evidence_bundles
class EvidenceBundle(Base):
    __tablename__ = "evidence_bundles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    bundle_path: Mapped[Optional[str]] = mapped_column(String(500))
    bundle_hash: Mapped[Optional[str]] = mapped_column(String(100))
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    artifact_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="evidence_bundles")


# 5.3.27 deployments
class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    localhost_url: Mapped[Optional[str]] = mapped_column(String(500))
    port: Mapped[Optional[int]] = mapped_column(Integer)
    container_id: Mapped[Optional[str]] = mapped_column(String(255))
    health_status: Mapped[str] = mapped_column(String(50), default="unknown")
    deployment_log: Mapped[Optional[str]] = mapped_column(Text)
    evidence_bundle_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("evidence_bundles.id"))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.28 patterns
class Pattern(Base):
    __tablename__ = "patterns"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False)
    problem_solved: Mapped[Optional[str]] = mapped_column(Text)
    applicability: Mapped[Optional[str]] = mapped_column(Text)
    implementation_notes: Mapped[Optional[str]] = mapped_column(Text)
    source_project: Mapped[Optional[str]] = mapped_column(String(255))
    related_files: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(500))
    cost_profile: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    success_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.29 pattern_usages
class PatternUsage(Base):
    __tablename__ = "pattern_usages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_id: Mapped[str] = mapped_column(String(36), ForeignKey("patterns.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("runs.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.30 memory_items
class MemoryItem(Base):
    __tablename__ = "memory_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"))
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    vector_id: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.31 mcp_tools
class McpTool(Base):
    __tablename__ = "mcp_tools"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    server_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("server_name", "tool_name"),)


# 5.3.32 mcp_permissions
class McpPermission(Base):
    __tablename__ = "mcp_permissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False)
    tool_id: Mapped[str] = mapped_column(String(36), ForeignKey("mcp_tools.id"), nullable=False)
    is_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.33 policy_results
class PolicyResult(Base):
    __tablename__ = "policy_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    output_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.34 model_calls
class ModelCall(Base):
    __tablename__ = "model_calls"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    phase_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("phases.id"))
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"))
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost: Mapped[Optional[float]] = mapped_column(Float)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    is_success: Mapped[bool] = mapped_column(Boolean, default=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="model_calls")


# 5.3.35 tool_calls
class ToolCall(Base):
    __tablename__ = "tool_calls"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    phase_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("phases.id"))
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"))
    task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"))
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    server_name: Mapped[Optional[str]] = mapped_column(String(255))
    arguments: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    result: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    is_success: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="tool_calls_list")


# 5.3.36 file_artifacts
class FileArtifact(Base):
    __tablename__ = "file_artifacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id: Mapped[str] = mapped_column(String(36), ForeignKey("artifacts.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(100))
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.37 run_checkpoints
class RunCheckpoint(Base):
    __tablename__ = "run_checkpoints"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    phase_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_data: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="checkpoints")


# 5.3.38 user_commands
class UserCommand(Base):
    __tablename__ = "user_commands"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("runs.id"))
    command: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_action: Mapped[Optional[str]] = mapped_column(String(100))
    is_slash_command: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 5.3.39 system_settings
class SystemSetting(Base):
    __tablename__ = "system_settings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(50), default="string")
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# =============================================================================
# PHASE 4: ENGINE MODELS
# =============================================================================

# 5.4.1 specification_versions
class SpecificationVersion(Base):
    __tablename__ = "specification_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("specification_versions.id"))
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, reviewing, approved, locked, superseded
    requirements_yaml: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    functional_spec: Mapped[Optional[str]] = mapped_column(Text)
    acceptance_criteria: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    non_functional_requirements: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    assumptions: Mapped[Optional[str]] = mapped_column(Text)
    validation_errors: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    generated_by: Mapped[Optional[str]] = mapped_column(String(100))
    approved_by: Mapped[Optional[str]] = mapped_column(String(100))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    run: Mapped["Run"] = relationship(back_populates="spec_versions")
    project: Mapped["Project"] = relationship(back_populates="spec_versions")


# 5.4.2 architecture_versions
class ArchitectureVersion(Base):
    __tablename__ = "architecture_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("architecture_versions.id"))
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, reviewing, approved, locked, superseded
    architecture_yaml: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    architecture_md: Mapped[Optional[str]] = mapped_column(Text)
    mermaid_diagrams: Mapped[Optional[dict]] = mapped_column(JSONB, default={})  # component, sequence, deployment
    adrs: Mapped[Optional[list]] = mapped_column(JSONB, default=[])  # Architecture Decision Records
    constraints: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    fitness_functions: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    drift_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    generated_by: Mapped[Optional[str]] = mapped_column(String(100))
    approved_by: Mapped[Optional[str]] = mapped_column(String(100))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    run: Mapped["Run"] = relationship(back_populates="arch_versions")
    project: Mapped["Project"] = relationship(back_populates="arch_versions")


# 5.4.3 governance_policies
class GovernancePolicy(Base):
    __tablename__ = "governance_policies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # security, quality, compliance, release
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # info, warning, error, critical
    rego_code: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocking: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# 5.4.4 governance_evaluations
class GovernanceEvaluation(Base):
    __tablename__ = "governance_evaluations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("governance_policies.id"), nullable=False)
    artifact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("artifacts.id"))
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # pass, fail, warning, error
    findings: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="governance_evals")
    policy: Mapped["GovernancePolicy"] = relationship()


# 5.4.5 governance_release_gates
class GovernanceReleaseGate(Base):
    __tablename__ = "governance_release_gates"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    gate_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, passed, failed, waived
    required_policy_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    evaluation_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=[])
    waived_by: Mapped[Optional[str]] = mapped_column(String(100))
    waived_reason: Mapped[Optional[str]] = mapped_column(Text)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="release_gates")


# 5.4.6 test_plans — EXTENDED from original (regel 305)
# The original TestPlan has been extended with engine fields below.
# See the extended version at the end of this section.


# 5.4.7 traceability_links
class TraceabilityLink(Base):
    __tablename__ = "traceability_links"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # requirement, design, architecture, test, governance, code, deployment
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    link_type: Mapped[str] = mapped_column(String(50), default="implements")  # implements, validates, depends_on, derives_from
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="traceability_links")
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", "target_type", "target_id", "link_type", name="uq_traceability_link"),
    )


# 5.4.8 artifact_baselines
class ArtifactBaseline(Base):
    __tablename__ = "artifact_baselines"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # specification, architecture, test_plan
    artifact_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    locked_by: Mapped[Optional[str]] = mapped_column(String(100))
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    run: Mapped["Run"] = relationship(back_populates="artifact_baselines")


# 5.4.9 run_snapshots
class RunSnapshot(Base):
    __tablename__ = "run_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String(30), default="manual")  # manual, phase_transition, pre_deployment, post_mortem
    state_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    phase_states: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    artifact_states: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    cost_summary: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    governance_summary: Mapped[Optional[dict]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="snapshots")


# 5.4.10 artifact_diffs
class ArtifactDiff(Base):
    __tablename__ = "artifact_diffs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    to_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    diff_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    run: Mapped["Run"] = relationship(back_populates="artifact_diffs")

