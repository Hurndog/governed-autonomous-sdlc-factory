"""SQLAlchemy models for Semantic Coverage and Test Alignment."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Index, String, Text,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class RequirementNormalization(Base):
    __tablename__ = "requirement_normalizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False)
    original_text = Column(Text)
    normalized_statement = Column(Text, nullable=False)
    actor = Column(String(128))
    action = Column(String(256))
    object = Column(String(256))
    constraints_json = Column(JSONB, default={})
    expected_behavior = Column(Text)
    failure_behavior = Column(Text)
    governance_relevance = Column(Boolean, default=False)
    security_relevance = Column(Boolean, default=False)
    evidence_required_json = Column(JSONB, default=[])
    criticality = Column(String(16), default="medium")
    ambiguity_score = Column(Float, default=0.0)
    testability_score = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("run_id", "requirement_id", name="uq_req_norm"),
        Index("idx_req_norm_security", "security_relevance"),
        Index("idx_req_norm_governance", "governance_relevance"),
    )


class AcceptanceCriteriaContract(Base):
    __tablename__ = "acceptance_criteria_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    acceptance_criterion_id = Column(String(64), nullable=False)
    given_text = Column(Text)
    when_text = Column(Text)
    then_text = Column(Text, nullable=False)
    and_conditions_json = Column(JSONB, default=[])
    evidence_required_json = Column(JSONB, default=[])
    negative_case_required = Column(Boolean, default=False)
    governance_case_required = Column(Boolean, default=False)
    security_case_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("run_id", "acceptance_criterion_id", name="uq_ac_contract"),
        Index("idx_ac_negative", "negative_case_required"),
        Index("idx_ac_security", "security_case_required"),
    )


class TestObligation(Base):
    __tablename__ = "test_obligations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    acceptance_criterion_id = Column(String(64))
    obligation_id = Column(String(64), nullable=False)
    obligation_type = Column(String(32), nullable=False)
    proof_statement = Column(Text, nullable=False)
    required_test_type = Column(String(16))
    required_evidence_type = Column(String(32))
    criticality = Column(String(16), default="medium")
    status = Column(String(16), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("run_id", "obligation_id", name="uq_test_obligation"),
        Index("idx_to_status", "status"),
        Index("idx_to_type", "obligation_type"),
        Index("idx_to_critical", "criticality"),
    )


class SemanticAlignmentEvaluation(Base):
    __tablename__ = "semantic_alignment_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    test_case_id = Column(String(64), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    acceptance_criterion_id = Column(String(64))
    obligation_id = Column(String(64), nullable=False)
    semantic_alignment_score = Column(Float, default=0.0)
    coverage_score = Column(Float, default=0.0)
    evidence_score = Column(Float, default=0.0)
    verifier_verdict = Column(String(16))
    critique = Column(Text)
    missing_assertions_json = Column(JSONB, default=[])
    missing_edge_cases_json = Column(JSONB, default=[])
    can_broken_code_pass = Column(Boolean, default=True)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_sae_verdict", "verifier_verdict"),
        Index("idx_sae_broken", "can_broken_code_pass"),
    )


class VerifierCritique(Base):
    __tablename__ = "verifier_critiques"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    test_case_id = Column(String(64), nullable=False, index=True)
    obligation_id = Column(String(64), nullable=False)
    verifier_model = Column(String(64), default="deterministic")
    prompt_hash = Column(String(64))
    response_hash = Column(String(64))
    verdict = Column(String(16))
    confidence = Column(Float, default=0.0)
    critique = Column(Text)
    recommendations_json = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_vc_verdict", "verdict"),
    )


class MutationTest(Base):
    __tablename__ = "mutation_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    obligation_id = Column(String(64))
    mutation_id = Column(String(64), nullable=False)
    mutation_type = Column(String(32), nullable=False)
    mutated_component = Column(String(128))
    mutation_description = Column(Text)
    expected_test_failure = Column(Boolean, default=True)
    actual_test_result = Column(String(16))
    killed = Column(Boolean, default=False)
    survived = Column(Boolean, default=False)
    mutation_score_impact = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("run_id", "mutation_id", name="uq_mutation_test"),
        Index("idx_mt_killed", "killed"),
        Index("idx_mt_survived", "survived"),
        Index("idx_mt_type", "mutation_type"),
    )


class NegativeTestRequirement(Base):
    __tablename__ = "negative_test_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    acceptance_criterion_id = Column(String(64))
    required_negative_case = Column(Text, nullable=False)
    generated_test_id = Column(String(64))
    status = Column(String(16), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ntr_status", "status"),
    )


class RuntimeEvidenceBinding(Base):
    __tablename__ = "runtime_evidence_bindings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    test_case_id = Column(String(64), nullable=False, index=True)
    obligation_id = Column(String(64))
    evidence_type = Column(String(32), nullable=False)
    evidence_ref = Column(String(256))
    evidence_hash = Column(String(64))
    binding_status = Column(String(16), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_reb_type", "evidence_type"),
        Index("idx_reb_status", "binding_status"),
    )


class SemanticCoverageReport(Base):
    __tablename__ = "semantic_coverage_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    obligation_coverage_score = Column(Float, default=0.0)
    semantic_alignment_score = Column(Float, default=0.0)
    mutation_score = Column(Float, default=0.0)
    negative_coverage_score = Column(Float, default=0.0)
    runtime_evidence_score = Column(Float, default=0.0)
    verifier_confidence_score = Column(Float, default=0.0)
    overall_semantic_coverage_score = Column(Float, default=0.0)
    critical_requirements_passed = Column(Boolean, default=False)
    release_gate_status = Column(String(16), default="pending")
    report_json = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_scr_gate", "release_gate_status"),
        Index("idx_scr_critical", "critical_requirements_passed"),
    )


class SemanticCoverageWaiver(Base):
    __tablename__ = "semantic_coverage_waivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False, index=True)
    obligation_id = Column(String(64))
    waiver_reason = Column(Text, nullable=False)
    waiver_scope = Column(String(16), default="obligation")
    approved_by = Column(String(128))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_scw_expires", "expires_at"),
    )
