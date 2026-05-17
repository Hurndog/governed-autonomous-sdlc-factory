"""Semantic Coverage Engine — Stable v3 implementation.

This engine implements the semantic coverage and test alignment contract
with a focus on stability, idempotency, and honest scoring.

It extracts requirements, acceptance criteria, and test cases from
JSON blob artifacts and evaluates semantic alignment between them.

Persistence strategy:
- All methods use deterministic upsert (query by natural key, update if exists, add if new).
- No merge() calls — merge is fragile with new UUIDs and stale session state.
- No blind add_all() — always check for existing records first.
- _clear_existing uses raw SQL DELETE + expire_all for clean re-runs.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
    NegativeTestRequirement, RuntimeEvidenceBinding, SemanticCoverageReport,
    SemanticCoverageWaiver,
)
from src.models import Artifact, TraceabilityLink, LogEvent


class SemanticCoverageEngine:
    """Engine for computing semantic coverage and test alignment."""

    def __init__(self, db: Session):
        self.db = db

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _to_uuid(self, run_id: str):
        """Convert string run_id to UUID for semantic coverage tables."""
        return uuid.UUID(run_id) if isinstance(run_id, str) else run_id

    def _to_str(self, run_id: str) -> str:
        """Convert run_id to string for pipeline tables."""
        return str(run_id)

    def _load_json_artifact(self, run_id: str, artifact_type: str, name: str) -> Optional[tuple]:
        """Load and parse a JSON artifact. Returns (data, artifact_id, source_hash) or None."""
        artifact = self.db.query(Artifact).filter(
            Artifact.run_id == self._to_str(run_id),
            Artifact.artifact_type == artifact_type,
            Artifact.name == name,
        ).first()

        if not artifact or not artifact.content:
            return None

        try:
            data = json.loads(artifact.content)
        except (json.JSONDecodeError, TypeError):
            return None

        source_hash = hashlib.sha256(artifact.content.encode('utf-8')).hexdigest()
        return data, artifact.id, source_hash

    def _clear_existing(self, run_id: str):
        """Clear existing semantic coverage records for idempotent re-runs."""
        rid = self._to_uuid(run_id)
        # Delete in reverse dependency order
        for model in [SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
                      NegativeTestRequirement, RuntimeEvidenceBinding, TestObligation,
                      AcceptanceCriteriaContract, RequirementNormalization,
                      SemanticCoverageReport]:
            # Use raw SQL for reliable deletion regardless of session state
            table_name = model.__tablename__
            self.db.execute(text(f'DELETE FROM {table_name} WHERE run_id = :rid'), {'rid': rid})
        self.db.commit()
        self.db.expire_all()  # Invalidate identity map after raw SQL cleanup

    def _upsert_by_natural_key(
        self,
        model_class,
        natural_key_filters: dict,
        new_record,
        update_fields: List[str],
    ):
        """Deterministic upsert: query by natural key, update if exists, add if new.

        Args:
            model_class: SQLAlchemy model class
            natural_key_filters: dict of column_name -> value for the WHERE clause
            new_record: the new record with updated values
            update_fields: list of field names to update if record exists

        Returns:
            The persisted record (existing or new)
        """
        query = self.db.query(model_class)
        for col_name, col_val in natural_key_filters.items():
            query = query.filter(getattr(model_class, col_name) == col_val)
        existing = query.first()

        if existing:
            # Update existing record
            for field in update_fields:
                setattr(existing, field, getattr(new_record, field))
            return existing
        else:
            # Insert new record
            self.db.add(new_record)
            return new_record

    # ─── 1. Requirement Normalization ─────────────────────────────────────

    def normalize_requirements(self, run_id: str) -> List[RequirementNormalization]:
        """Extract and normalize requirements from specification artifacts (idempotent)."""
        loaded = self._load_json_artifact(run_id, "specification", "requirements.json")
        if not loaded:
            return []

        data, artifact_id, source_hash = loaded
        if not isinstance(data, list):
            return []

        normalized = []
        for idx, req in enumerate(data):
            if not isinstance(req, dict):
                continue

            req_id = req.get("id", f"REQ-{idx:03d}")
            description = req.get("description", "")
            priority = req.get("priority", "should_have")
            complexity = req.get("complexity", "medium")

            # Map priority to criticality
            criticality_map = {
                "must_have": "critical",
                "should_have": "high",
                "could_have": "medium",
                "wont_have": "low",
            }
            criticality = criticality_map.get(priority, "medium")

            # Determine security/governance relevance
            desc_lower = description.lower()
            security_relevance = any(kw in desc_lower for kw in [
                "auth", "jwt", "token", "password", "encrypt", "security",
                "rate limit", "access", "permission", "revocation", "login",
            ])
            governance_relevance = any(kw in desc_lower for kw in [
                "audit", "log", "compliance", "gdpr", "privacy", "data",
                "retention", "deletion", "export", "tenant",
            ])

            # Extract actor/action/object
            actor = self._extract_actor(description)
            action = self._extract_action(description)
            obj = self._extract_object(description)
            normalized_stmt = f"{actor} SHALL {action} {obj}"

            ambiguity = self._compute_ambiguity(description)
            testability = self._compute_testability(req, description)

            record = RequirementNormalization(
                id=uuid.uuid4(),
                run_id=self._to_uuid(run_id),
                requirement_id=req_id,
                original_text=description,
                normalized_statement=normalized_stmt,
                actor=actor,
                action=action,
                object=obj,
                constraints_json={"complexity": complexity, "priority": priority},
                criticality=criticality,
                security_relevance=security_relevance,
                governance_relevance=governance_relevance,
                ambiguity_score=ambiguity,
                testability_score=testability,
            )
            normalized.append(record)

        # Deterministic upsert by natural key: (run_id, requirement_id)
        for norm in normalized:
            self._upsert_by_natural_key(
                RequirementNormalization,
                natural_key_filters={
                    "run_id": norm.run_id,
                    "requirement_id": norm.requirement_id,
                },
                new_record=norm,
                update_fields=[
                    "original_text", "normalized_statement", "actor", "action", "object",
                    "constraints_json", "criticality", "security_relevance",
                    "governance_relevance", "ambiguity_score", "testability_score",
                ],
            )
        self.db.commit()
        return normalized

    # ─── 2. Acceptance Criteria Validation ────────────────────────────────

    def validate_acceptance_criteria(self, run_id: str) -> List[AcceptanceCriteriaContract]:
        """Extract and validate acceptance criteria from artifacts (idempotent)."""
        loaded = self._load_json_artifact(run_id, "specification", "acceptance_criteria.json")
        if not loaded:
            return []

        data, artifact_id, source_hash = loaded
        if not isinstance(data, list):
            return []

        records = []
        for idx, ac in enumerate(data):
            if not isinstance(ac, dict):
                continue

            ac_id = ac.get("id", f"AC-{idx:03d}")
            req_id = ac.get("requirement_id", "")
            criteria = ac.get("criteria", "")

            given, when, then = self._parse_gwt(criteria)
            criteria_lower = criteria.lower()

            negative_required = any(kw in criteria_lower for kw in [
                "invalid", "error", "fail", "reject", "deny", "unauthorized",
                "expired", "missing", "incorrect", "cannot",
            ])
            security_required = any(kw in criteria_lower for kw in [
                "auth", "jwt", "token", "password", "encrypt", "security",
                "rate limit", "access", "permission",
            ])
            governance_required = any(kw in criteria_lower for kw in [
                "audit", "log", "compliance", "gdpr", "privacy",
            ])

            record = AcceptanceCriteriaContract(
                id=uuid.uuid4(),
                run_id=self._to_uuid(run_id),
                requirement_id=req_id,
                acceptance_criterion_id=ac_id,
                given_text=given,
                when_text=when,
                then_text=then or criteria,
                negative_case_required=negative_required,
                security_case_required=security_required,
                governance_case_required=governance_required,
            )
            records.append(record)

        # Deterministic upsert by natural key: (run_id, acceptance_criterion_id)
        for rec in records:
            self._upsert_by_natural_key(
                AcceptanceCriteriaContract,
                natural_key_filters={
                    "run_id": rec.run_id,
                    "acceptance_criterion_id": rec.acceptance_criterion_id,
                },
                new_record=rec,
                update_fields=[
                    "requirement_id", "given_text", "when_text", "then_text",
                    "negative_case_required", "security_case_required",
                    "governance_case_required",
                ],
            )
        self.db.commit()
        return records

    # ─── 3. Test Obligation Generation ────────────────────────────────────

    def generate_test_obligations(self, run_id: str) -> List[TestObligation]:
        """Generate test obligations from acceptance criteria (idempotent)."""
        acs = self.db.query(AcceptanceCriteriaContract).filter(
            AcceptanceCriteriaContract.run_id == self._to_uuid(run_id)
        ).all()

        obligations = []
        for ac in acs:
            # Each acceptance criterion generates at least one test obligation
            obl_id = f"OBL-{ac.requirement_id}-{ac.acceptance_criterion_id}-FUNC"
            obl = TestObligation(
                id=uuid.uuid4(),
                run_id=self._to_uuid(run_id),
                requirement_id=ac.requirement_id,
                acceptance_criterion_id=ac.acceptance_criterion_id,
                obligation_id=obl_id,
                obligation_type="functional",
                proof_statement=f"Test must verify: {ac.then_text[:200]}",
                required_test_type="unit" if "unit" in ac.then_text.lower() else "integration",
                criticality="high" if ac.security_case_required else "medium",
                status="pending",
            )
            obligations.append(obl)

            # Security case obligation
            if ac.security_case_required:
                obl_sec_id = f"OBL-{ac.requirement_id}-{ac.acceptance_criterion_id}-SEC"
                obl_sec = TestObligation(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    requirement_id=ac.requirement_id,
                    acceptance_criterion_id=ac.acceptance_criterion_id,
                    obligation_id=obl_sec_id,
                    obligation_type="security",
                    proof_statement=f"Security test must verify: {ac.then_text[:200]}",
                    required_test_type="security",
                    criticality="critical",
                    status="pending",
                )
                obligations.append(obl_sec)

            # Negative case obligation
            if ac.negative_case_required:
                obl_neg_id = f"OBL-{ac.requirement_id}-{ac.acceptance_criterion_id}-NEG"
                obl_neg = TestObligation(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    requirement_id=ac.requirement_id,
                    acceptance_criterion_id=ac.acceptance_criterion_id,
                    obligation_id=obl_neg_id,
                    obligation_type="negative",
                    proof_statement=f"Negative test must verify rejection: {ac.then_text[:200]}",
                    required_test_type="negative",
                    criticality="high",
                    status="pending",
                )
                obligations.append(obl_neg)

            # Governance case obligation
            if ac.governance_case_required:
                obl_gov_id = f"OBL-{ac.requirement_id}-{ac.acceptance_criterion_id}-GOV"
                obl_gov = TestObligation(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    requirement_id=ac.requirement_id,
                    acceptance_criterion_id=ac.acceptance_criterion_id,
                    obligation_id=obl_gov_id,
                    obligation_type="governance",
                    proof_statement=f"Governance test must verify evidence: {ac.then_text[:200]}",
                    required_test_type="governance",
                    criticality="high",
                    status="pending",
                )
                obligations.append(obl_gov)

        # Deterministic upsert by natural key: (run_id, obligation_id)
        for obl in obligations:
            self._upsert_by_natural_key(
                TestObligation,
                natural_key_filters={
                    "run_id": obl.run_id,
                    "obligation_id": obl.obligation_id,
                },
                new_record=obl,
                update_fields=[
                    "requirement_id", "acceptance_criterion_id", "obligation_type",
                    "proof_statement", "required_test_type", "criticality", "status",
                ],
            )
        self.db.commit()
        return obligations

    # ─── 4. Test Alignment Evaluation ─────────────────────────────────────

    def evaluate_test_alignment(self, run_id: str) -> List[SemanticAlignmentEvaluation]:
        """Evaluate semantic alignment between test cases and obligations (idempotent)."""
        # Load test cases from test_plan artifact
        loaded = self._load_json_artifact(run_id, "test_plan", "test_plan.json")
        test_cases = []
        if loaded:
            data, _, _ = loaded
            if isinstance(data, dict):
                test_cases = data.get("test_cases", [])

        obligations = self.db.query(TestObligation).filter(
            TestObligation.run_id == self._to_uuid(run_id)
        ).all()

        evaluations = []
        for tc in test_cases:
            if not isinstance(tc, dict):
                continue

            tc_id = tc.get("id", "")
            req_id = tc.get("requirement_id", "")
            tc_name = tc.get("name", "")
            tc_type = tc.get("type", "unit")
            expected = tc.get("expected_result", "")

            # Find matching obligations
            matching_obls = [o for o in obligations if o.requirement_id == req_id]

            for obl in matching_obls:
                # Compute semantic alignment score
                alignment = self._compute_alignment(tc_name, expected, obl.proof_statement)

                # Check if test is tautological (expected result = test description)
                is_tautological = self._is_tautological(tc_name, expected)

                # Check if broken code could pass
                can_broken_pass = self._can_broken_code_pass(tc_name, expected, tc_type)

                eval_record = SemanticAlignmentEvaluation(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    test_case_id=tc_id,
                    requirement_id=req_id,
                    obligation_id=obl.obligation_id,
                    semantic_alignment_score=alignment,
                    coverage_score=alignment * 0.8,
                    evidence_score=0.5 if obl.obligation_type == "governance" else 0.0,
                    verifier_verdict="pass" if alignment >= 0.6 else "fail",
                    critique=self._generate_critique(tc_name, expected, alignment, is_tautological),
                    missing_assertions_json=self._find_missing_assertions(tc_name, expected),
                    missing_edge_cases_json=[],
                    can_broken_code_pass=can_broken_pass,
                    status="evaluated",
                )
                evaluations.append(eval_record)

        # For obligations without matching test cases, create "not covered" evaluations
        covered_obl_ids = {e.obligation_id for e in evaluations}
        for obl in obligations:
            if obl.obligation_id not in covered_obl_ids:
                eval_record = SemanticAlignmentEvaluation(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    test_case_id="MISSING",
                    requirement_id=obl.requirement_id,
                    obligation_id=obl.obligation_id,
                    semantic_alignment_score=0.0,
                    coverage_score=0.0,
                    evidence_score=0.0,
                    verifier_verdict="fail",
                    critique=f"No test case found for obligation: {obl.proof_statement[:100]}",
                    missing_assertions_json=["No test case"],
                    missing_edge_cases_json=[],
                    can_broken_code_pass=True,
                    status="not_covered",
                )
                evaluations.append(eval_record)

        # Deterministic upsert by natural key: (run_id, test_case_id, obligation_id)
        for ev in evaluations:
            self._upsert_by_natural_key(
                SemanticAlignmentEvaluation,
                natural_key_filters={
                    "run_id": ev.run_id,
                    "test_case_id": ev.test_case_id,
                    "obligation_id": ev.obligation_id,
                },
                new_record=ev,
                update_fields=[
                    "requirement_id", "semantic_alignment_score", "coverage_score",
                    "evidence_score", "verifier_verdict", "critique",
                    "missing_assertions_json", "missing_edge_cases_json",
                    "can_broken_code_pass", "status",
                ],
            )
        self.db.commit()
        return evaluations

    # ─── 5. Independent Verifier ──────────────────────────────────────────

    def run_independent_verifier(self, run_id: str) -> List[VerifierCritique]:
        """Run deterministic verifier critique on test alignment (idempotent)."""
        evaluations = self.db.query(SemanticAlignmentEvaluation).filter(
            SemanticAlignmentEvaluation.run_id == self._to_uuid(run_id)
        ).all()

        critiques = []
        for ev in evaluations:
            # Deterministic verifier: check structural quality
            verdict = "pass"
            confidence = 0.7
            critique_text = ""
            recommendations = []

            if ev.semantic_alignment_score < 0.4:
                verdict = "fail"
                confidence = 0.9
                critique_text = "Low semantic alignment. Test does not clearly prove the obligation."
                recommendations.append("Add specific assertions matching the obligation proof statement")
            elif ev.semantic_alignment_score < 0.7:
                verdict = "partial"
                confidence = 0.8
                critique_text = "Moderate alignment. Test covers the obligation but may miss edge cases."
                recommendations.append("Add boundary condition tests")
            else:
                verdict = "pass"
                confidence = 0.85
                critique_text = "Good semantic alignment between test and obligation."

            if ev.can_broken_code_pass:
                verdict = "fail" if verdict == "pass" else verdict
                confidence = max(confidence, 0.9)
                critique_text += " WARNING: Broken code could pass this test."
                recommendations.append("Add negative assertions to detect broken behavior")

            vc = VerifierCritique(
                id=uuid.uuid4(),
                run_id=self._to_uuid(run_id),
                test_case_id=ev.test_case_id,
                obligation_id=ev.obligation_id,
                verifier_model="deterministic_v2",
                verdict=verdict,
                confidence=confidence,
                critique=critique_text,
                recommendations_json=recommendations,
            )
            critiques.append(vc)

        # Deterministic upsert by natural key: (run_id, test_case_id, obligation_id)
        for vc in critiques:
            self._upsert_by_natural_key(
                VerifierCritique,
                natural_key_filters={
                    "run_id": vc.run_id,
                    "test_case_id": vc.test_case_id,
                    "obligation_id": vc.obligation_id,
                },
                new_record=vc,
                update_fields=[
                    "verifier_model", "verdict", "confidence", "critique",
                    "recommendations_json",
                ],
            )
        self.db.commit()
        return critiques

    # ─── 6. Mutation Test Planning ────────────────────────────────────────

    def plan_mutation_tests(self, run_id: str) -> List[MutationTest]:
        """Plan mutation tests for critical requirements (idempotent)."""
        critical_reqs = self.db.query(RequirementNormalization).filter(
            RequirementNormalization.run_id == self._to_uuid(run_id),
            RequirementNormalization.criticality.in_(["critical", "high"]),
        ).all()

        mutations = []
        mutation_types = [
            ("boundary_shift", "Shift boundary values by ±1"),
            ("null_injection", "Inject null/empty values"),
            ("type_confusion", "Swap parameter types"),
            ("logic_inversion", "Invert boolean conditions"),
            ("off_by_one", "Off-by-one in loop boundaries"),
        ]

        for req in critical_reqs:
            for mut_type, mut_desc in mutation_types:
                mt = MutationTest(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    requirement_id=req.requirement_id,
                    mutation_id=f"MUT-{req.requirement_id}-{mut_type}",
                    mutation_type=mut_type,
                    mutated_component=req.object or "system",
                    mutation_description=mut_desc,
                    expected_test_failure=True,
                    actual_test_result=None,
                    killed=False,
                    survived=False,
                    mutation_score_impact=0.0,
                )
                mutations.append(mt)

        # Deterministic upsert by natural key: (run_id, mutation_id)
        for mt in mutations:
            self._upsert_by_natural_key(
                MutationTest,
                natural_key_filters={
                    "run_id": mt.run_id,
                    "mutation_id": mt.mutation_id,
                },
                new_record=mt,
                update_fields=[
                    "requirement_id", "mutation_type", "mutated_component",
                    "mutation_description", "expected_test_failure",
                    "actual_test_result", "killed", "survived", "mutation_score_impact",
                ],
            )
        self.db.commit()
        return mutations

    # ─── 7. Negative Test Coverage ────────────────────────────────────────

    def evaluate_negative_test_coverage(self, run_id: str) -> List[NegativeTestRequirement]:
        """Evaluate negative test coverage from security findings and compliance gaps (idempotent)."""
        records = []

        # From security findings
        sec_loaded = self._load_json_artifact(run_id, "governance", "security_findings.json")
        if sec_loaded:
            data, _, _ = sec_loaded
            if isinstance(data, list):
                for idx, finding in enumerate(data):
                    if not isinstance(finding, dict):
                        continue
                    req_id = self._match_requirement(finding.get("finding", ""))
                    testing_req = finding.get("testing_requirement", finding.get("finding", ""))
                    records.append(NegativeTestRequirement(
                        id=uuid.uuid4(),
                        run_id=self._to_uuid(run_id),
                        requirement_id=req_id or f"SEC-{idx:03d}",
                        required_negative_case=testing_req[:500] if testing_req else "Security test required",
                        status="pending",
                    ))

        # From compliance gaps
        comp_loaded = self._load_json_artifact(run_id, "governance", "compliance_gaps.json")
        if comp_loaded:
            data, _, _ = comp_loaded
            if isinstance(data, list):
                for idx, gap in enumerate(data):
                    if not isinstance(gap, dict):
                        continue
                    req_id = self._match_requirement(gap.get("gap", ""))
                    records.append(NegativeTestRequirement(
                        id=uuid.uuid4(),
                        run_id=self._to_uuid(run_id),
                        requirement_id=req_id or f"COMP-{idx:03d}",
                        required_negative_case=f"Compliance: {gap.get('gap', '')[:400]}",
                        status="pending",
                    ))

        # From acceptance criteria that require negative cases
        neg_acs = self.db.query(AcceptanceCriteriaContract).filter(
            AcceptanceCriteriaContract.run_id == self._to_uuid(run_id),
            AcceptanceCriteriaContract.negative_case_required == True,
        ).all()
        for ac in neg_acs:
            # Check if we already have a record for this requirement
            existing = [r for r in records if r.requirement_id == ac.requirement_id]
            if not existing:
                records.append(NegativeTestRequirement(
                    id=uuid.uuid4(),
                    run_id=self._to_uuid(run_id),
                    requirement_id=ac.requirement_id,
                    required_negative_case=f"Negative case for: {ac.then_text[:300]}",
                    status="pending",
                ))

        # Deterministic upsert by natural key: (run_id, requirement_id)
        # Note: requirement_id is the natural key since each requirement has at most one negative test requirement
        for rec in records:
            self._upsert_by_natural_key(
                NegativeTestRequirement,
                natural_key_filters={
                    "run_id": rec.run_id,
                    "requirement_id": rec.requirement_id,
                },
                new_record=rec,
                update_fields=[
                    "required_negative_case", "generated_test_id", "status",
                ],
            )
        self.db.commit()
        return records

    # ─── 8. Runtime Evidence Binding ──────────────────────────────────────

    def bind_runtime_evidence(self, run_id: str) -> List[RuntimeEvidenceBinding]:
        """Bind runtime evidence to test obligations (idempotent)."""
        obligations = self.db.query(TestObligation).filter(
            TestObligation.run_id == self._to_uuid(run_id),
            TestObligation.obligation_type == "governance",
        ).all()

        bindings = []
        for obl in obligations:
            # Check for log events as evidence
            log_count = self.db.query(LogEvent).filter(
                LogEvent.run_id == self._to_str(run_id),
            ).count()

            binding = RuntimeEvidenceBinding(
                id=uuid.uuid4(),
                run_id=self._to_uuid(run_id),
                test_case_id="GOVERNANCE",
                obligation_id=obl.obligation_id,
                evidence_type="audit_log",
                evidence_ref=f"log_events:{log_count}",
                evidence_hash="",
                binding_status="bound" if log_count > 0 else "failed",
            )
            bindings.append(binding)

        # Deterministic upsert by natural key: (run_id, test_case_id, obligation_id)
        for binding in bindings:
            self._upsert_by_natural_key(
                RuntimeEvidenceBinding,
                natural_key_filters={
                    "run_id": binding.run_id,
                    "test_case_id": binding.test_case_id,
                    "obligation_id": binding.obligation_id,
                },
                new_record=binding,
                update_fields=[
                    "evidence_type", "evidence_ref", "evidence_hash", "binding_status",
                ],
            )
        self.db.commit()
        return bindings

    # ─── 9. Score Computation ─────────────────────────────────────────────

    def compute_semantic_coverage_score(self, run_id: str) -> SemanticCoverageReport:
        """Compute the overall semantic coverage score."""
        rid = self._to_uuid(run_id)

        # Gather data
        reqs = self.db.query(RequirementNormalization).filter(
            RequirementNormalization.run_id == rid
        ).all()
        obligations = self.db.query(TestObligation).filter(
            TestObligation.run_id == rid
        ).all()
        evaluations = self.db.query(SemanticAlignmentEvaluation).filter(
            SemanticAlignmentEvaluation.run_id == rid
        ).all()
        critiques = self.db.query(VerifierCritique).filter(
            VerifierCritique.run_id == rid
        ).all()
        mutations = self.db.query(MutationTest).filter(
            MutationTest.run_id == rid
        ).all()
        neg_reqs = self.db.query(NegativeTestRequirement).filter(
            NegativeTestRequirement.run_id == rid
        ).all()
        bindings = self.db.query(RuntimeEvidenceBinding).filter(
            RuntimeEvidenceBinding.run_id == rid
        ).all()

        # Compute sub-scores
        # 1. Obligation coverage: % of requirements with at least one obligation
        req_ids_with_obligations = {o.requirement_id for o in obligations}
        obligation_coverage = len(req_ids_with_obligations) / max(len(reqs), 1)

        # 2. Semantic alignment: average alignment score
        alignment_scores = [e.semantic_alignment_score for e in evaluations if e.status == "evaluated"]
        semantic_alignment = sum(alignment_scores) / max(len(alignment_scores), 1) if alignment_scores else 0.0

        # 3. Mutation score: planned mutations (not executed — honest scoring)
        # Since mutations are only planned, not executed, score is 0.0
        # This is honest — we don't claim execution that didn't happen
        mutation_score = 0.0

        # 4. Negative coverage: % of security/governance requirements with negative tests
        sec_gov_reqs = [r for r in reqs if r.security_relevance or r.governance_relevance]
        neg_covered = set()
        for nr in neg_reqs:
            neg_covered.add(nr.requirement_id)
        negative_coverage = len(neg_covered) / max(len(sec_gov_reqs), 1) if sec_gov_reqs else 1.0

        # 5. Runtime evidence: % of governance obligations with bound evidence
        gov_obligations = [o for o in obligations if o.obligation_type == "governance"]
        bound_evidence = [b for b in bindings if b.binding_status == "bound"]
        runtime_evidence = len(bound_evidence) / max(len(gov_obligations), 1) if gov_obligations else 1.0

        # 6. Verifier confidence: average confidence from critiques
        verifier_scores = [c.confidence for c in critiques]
        verifier_confidence = sum(verifier_scores) / max(len(verifier_scores), 1) if verifier_scores else 0.0

        # Overall score (weighted)
        overall = (
            0.30 * obligation_coverage +
            0.25 * semantic_alignment +
            0.20 * mutation_score +
            0.10 * negative_coverage +
            0.10 * runtime_evidence +
            0.05 * verifier_confidence
        )

        # Critical requirements check
        critical_reqs = [r for r in reqs if r.criticality == "critical"]
        critical_passed = True
        for cr in critical_reqs:
            cr_evals = [e for e in evaluations if e.requirement_id == cr.requirement_id and e.status == "evaluated"]
            if not cr_evals or all(e.semantic_alignment_score < 0.5 for e in cr_evals):
                critical_passed = False
                break

        # Release gate
        gate_status = "pass" if (overall >= 0.5 and critical_passed) else "fail"
        if overall < 0.3:
            gate_status = "fail"
        elif not critical_passed:
            gate_status = "fail"

        report_data = {
            "requirements_count": len(reqs),
            "obligations_count": len(obligations),
            "evaluations_count": len(evaluations),
            "critiques_count": len(critiques),
            "mutations_planned": len(mutations),
            "mutations_executed": 0,
            "negative_requirements": len(neg_reqs),
            "evidence_bindings": len(bindings),
            "critical_requirements": len(critical_reqs),
            "critical_passed": critical_passed,
            "formula": "0.30*obligation + 0.25*alignment + 0.20*mutation + 0.10*negative + 0.10*evidence + 0.05*verifier",
            "note": "mutations are planned but not executed — score is 0.0 for mutation component",
        }

        # Deterministic upsert for report by natural key: run_id
        new_report = SemanticCoverageReport(
            id=uuid.uuid4(),
            run_id=rid,
            obligation_coverage_score=round(obligation_coverage, 4),
            semantic_alignment_score=round(semantic_alignment, 4),
            mutation_score=round(mutation_score, 4),
            negative_coverage_score=round(negative_coverage, 4),
            runtime_evidence_score=round(runtime_evidence, 4),
            verifier_confidence_score=round(verifier_confidence, 4),
            overall_semantic_coverage_score=round(overall, 4),
            critical_requirements_passed=critical_passed,
            release_gate_status=gate_status,
            report_json=report_data,
        )

        # Use upsert instead of merge
        existing_report = self.db.query(SemanticCoverageReport).filter(
            SemanticCoverageReport.run_id == rid
        ).first()

        if existing_report:
            # Update existing report — preserve original created_at
            existing_report.obligation_coverage_score = new_report.obligation_coverage_score
            existing_report.semantic_alignment_score = new_report.semantic_alignment_score
            existing_report.mutation_score = new_report.mutation_score
            existing_report.negative_coverage_score = new_report.negative_coverage_score
            existing_report.runtime_evidence_score = new_report.runtime_evidence_score
            existing_report.verifier_confidence_score = new_report.verifier_confidence_score
            existing_report.overall_semantic_coverage_score = new_report.overall_semantic_coverage_score
            existing_report.critical_requirements_passed = new_report.critical_requirements_passed
            existing_report.release_gate_status = new_report.release_gate_status
            existing_report.report_json = new_report.report_json
            existing_report.updated_at = datetime.utcnow()
            report = existing_report
        else:
            self.db.add(new_report)
            report = new_report

        self.db.commit()
        return report

    # ─── 10. Full Pipeline ────────────────────────────────────────────────

    def run_full_semantic_coverage(self, run_id: str) -> SemanticCoverageReport:
        """Run the full semantic coverage pipeline for a run (idempotent)."""
        # Clear existing records for idempotent re-run
        self._clear_existing(run_id)

        # 1. Normalize requirements
        self.normalize_requirements(run_id)

        # 2. Validate acceptance criteria
        self.validate_acceptance_criteria(run_id)

        # 3. Generate test obligations
        self.generate_test_obligations(run_id)

        # 4. Evaluate test alignment
        self.evaluate_test_alignment(run_id)

        # 5. Run independent verifier
        self.run_independent_verifier(run_id)

        # 6. Plan mutation tests (not execute — honest)
        self.plan_mutation_tests(run_id)

        # 7. Evaluate negative test coverage
        self.evaluate_negative_test_coverage(run_id)

        # 8. Bind runtime evidence
        self.bind_runtime_evidence(run_id)

        # 9. Compute score
        return self.compute_semantic_coverage_score(run_id)

    # ─── Internal Helpers ─────────────────────────────────────────────────

    def _extract_actor(self, text: str) -> str:
        actors = ["user", "system", "admin", "api gateway", "auth service",
                  "task service", "audit service", "notification service",
                  "client", "server", "database"]
        text_lower = text.lower()
        for actor in actors:
            if actor in text_lower:
                return actor.title()
        return "The system"

    def _extract_action(self, text: str) -> str:
        action_keywords = [
            "register", "authenticate", "create", "read", "update", "delete",
            "validate", "enforce", "log", "notify", "route", "limit",
            "encrypt", "decrypt", "sign", "verify", "revoke", "export",
        ]
        text_lower = text.lower()
        for action in action_keywords:
            if action in text_lower:
                return action
        return "process"

    def _extract_object(self, text: str) -> str:
        object_keywords = [
            "jwt", "token", "user", "task", "request", "response",
            "audit log", "notification", "rate limit", "password",
            "email", "data", "api", "endpoint",
        ]
        text_lower = text.lower()
        for obj in object_keywords:
            if obj in text_lower:
                return obj
        return "the request"

    def _compute_ambiguity(self, text: str) -> float:
        vague_terms = ["should", "might", "could", "may", "possibly", "perhaps",
                       "appropriate", "reasonable", "sufficient", "adequate", "etc"]
        text_lower = text.lower()
        count = sum(1 for term in vague_terms if term in text_lower)
        return min(count * 0.2, 1.0)

    def _compute_testability(self, req: dict, text: str) -> float:
        score = 0.5
        if req.get("id"):
            score += 0.1
        if req.get("priority") == "must_have":
            score += 0.2
        elif req.get("priority") == "should_have":
            score += 0.1
        specific_terms = ["jwt", "http", "api", "endpoint", "response", "status",
                          "rate limit", "timeout", "expiration", "signature"]
        text_lower = text.lower()
        specificity = sum(1 for t in specific_terms if t in text_lower)
        score += min(specificity * 0.05, 0.2)
        return min(score, 1.0)

    def _parse_gwt(self, text: str) -> tuple:
        given, when, then = "", "", ""
        text_lower = text.lower()
        if "given" in text_lower and "when" in text_lower and "then" in text_lower:
            parts = text.split("Given")
            if len(parts) > 1:
                rest = parts[1]
                when_parts = rest.split("When")
                if len(when_parts) > 1:
                    given = when_parts[0].strip()
                    rest = when_parts[1]
                    then_parts = rest.split("Then")
                    if len(then_parts) > 1:
                        when = then_parts[0].strip()
                        then = then_parts[1].strip()
        elif "shall" in text_lower:
            then = text.strip()
        else:
            then = text.strip()
        return given, when, then

    def _compute_alignment(self, tc_name: str, expected: str, proof_statement: str) -> float:
        """Compute semantic alignment between test case and obligation."""
        score = 0.3  # baseline — they're related by requirement_id

        # Check keyword overlap
        tc_words = set((tc_name + " " + expected).lower().split())
        proof_words = set(proof_statement.lower().split())
        overlap = tc_words & proof_words
        if overlap:
            score += min(len(overlap) * 0.1, 0.4)

        # Check for specific assertion keywords
        assertion_keywords = ["assert", "verify", "check", "validate", "expect", "return", "status", "error", "reject"]
        has_assertions = any(kw in expected.lower() for kw in assertion_keywords)
        if has_assertions:
            score += 0.2

        # Check for specific values/behaviors
        specific_patterns = ["http", "jwt", "token", "429", "401", "403", "200", "201", "null", "empty", "invalid"]
        has_specifics = any(p in (tc_name + " " + expected).lower() for p in specific_patterns)
        if has_specifics:
            score += 0.1

        return min(score, 1.0)

    def _is_tautological(self, tc_name: str, expected: str) -> bool:
        """Check if test is tautological (expected result = test description)."""
        name_lower = tc_name.lower()
        expected_lower = expected.lower()
        # If the expected result is essentially the same as the test name
        name_words = set(name_lower.split())
        expected_words = set(expected_lower.split())
        if name_words and expected_words:
            overlap = name_words & expected_words
            if len(overlap) / max(len(name_words), 1) > 0.7:
                return True
        return False

    def _can_broken_code_pass(self, tc_name: str, expected: str, tc_type: str) -> bool:
        """Check if broken code could pass this test."""
        # Tests without specific assertions are weak
        assertion_keywords = ["assert", "verify", "check", "validate", "expect", "return", "status", "error", "reject", "throw", "raise"]
        has_assertions = any(kw in expected.lower() for kw in assertion_keywords)
        if not has_assertions:
            return True
        # Edge/governance tests with specific checks are stronger
        if tc_type in ["edge", "governance", "security"]:
            return False
        return False

    def _generate_critique(self, tc_name: str, expected: str, alignment: float, is_tautological: bool) -> str:
        parts = []
        if alignment < 0.4:
            parts.append("Low semantic alignment. The test does not clearly prove the obligation.")
        elif alignment < 0.7:
            parts.append("Moderate alignment. Consider adding more specific assertions.")
        else:
            parts.append("Good alignment between test and obligation.")
        if is_tautological:
            parts.append("WARNING: Test appears tautological — expected result mirrors test description.")
        return " ".join(parts)

    def _find_missing_assertions(self, tc_name: str, expected: str) -> List[str]:
        missing = []
        if "assert" not in expected.lower() and "verify" not in expected.lower():
            missing.append("No explicit assertion keywords found")
        if "error" not in expected.lower() and "reject" not in expected.lower():
            missing.append("No error/rejection handling")
        return missing

    def _match_requirement(self, text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["jwt", "auth", "login", "register", "token"]):
            return "FR-001"
        if any(kw in text_lower for kw in ["rate limit", "throttle", "request limit"]):
            return "FR-002"
        if any(kw in text_lower for kw in ["audit", "log", "immutable"]):
            return "FR-003"
        if any(kw in text_lower for kw in ["notification", "real-time", "websocket"]):
            return "FR-004"
        if any(kw in text_lower for kw in ["task", "crud", "create", "update", "delete"]):
            return "FR-005"
        if any(kw in text_lower for kw in ["tenant", "isolation", "multi-tenant"]):
            return "FR-006"
        return ""
