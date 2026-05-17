"""Source extraction layer for semantic coverage.

Extracts requirements, acceptance criteria, test cases, and governance concerns
from JSON blob artifacts into first-class semantic coverage database records
with full source lineage tracking.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from src.core.models_semantic_coverage import (
    RequirementNormalization,
    AcceptanceCriteriaContract,
    TestObligation,
    NegativeTestRequirement,
    RuntimeEvidenceBinding,
)
from src.models import Artifact


class SourceExtractor:
    """Extracts semantic coverage records from JSON blob artifacts.

    Every extracted record includes:
    - run_id: the pipeline run
    - source_artifact_id: UUID of the source artifact
    - source_artifact_type: type of the source artifact
    - source_json_path: JSONPath within the artifact content
    - source_hash: SHA256 of the source content
    - extraction_version: version of the extraction logic
    - extraction_timestamp: when the extraction was performed
    - extraction_confidence: 1.0 for deterministic extraction
    """

    EXTRACTION_VERSION = "1.0.0"

    def __init__(self, db: Session, run_id: str):
        self.db = db
        self.run_id = run_id
        self._artifacts_cache: dict[str, dict] = {}

    def _load_artifact(self, artifact_type: str, name: str) -> Optional[dict]:
        """Load and parse an artifact's JSON content."""
        cache_key = f"{artifact_type}:{name}"
        if cache_key in self._artifacts_cache:
            return self._artifacts_cache[cache_key]

        artifact = self.db.query(Artifact).filter(
            Artifact.run_id == self.run_id,
            Artifact.artifact_type == artifact_type,
            Artifact.name == name,
        ).first()

        if not artifact or not artifact.content:
            return None

        try:
            data = json.loads(artifact.content)
        except (json.JSONDecodeError, TypeError):
            return None

        # Compute SHA256 hash of the raw content
        source_hash = hashlib.sha256(artifact.content.encode('utf-8')).hexdigest()

        result = {
            "data": data,
            "artifact_id": artifact.id,
            "artifact_type": artifact_type,
            "source_hash": source_hash,
            "name": name,
        }
        self._artifacts_cache[cache_key] = result
        return result

    def extract_requirements(self) -> list[RequirementNormalization]:
        """Extract requirements from requirements.json artifact."""
        loaded = self._load_artifact("specification", "requirements.json")
        if not loaded:
            return []

        data = loaded["data"]
        if not isinstance(data, list):
            return []

        records = []
        for idx, req in enumerate(data):
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

            # Determine security/governance relevance from content
            desc_lower = description.lower()
            security_relevance = any(kw in desc_lower for kw in [
                "auth", "jwt", "token", "password", "encrypt", "security",
                "rate limit", "access", "permission", "revocation",
            ])
            governance_relevance = any(kw in desc_lower for kw in [
                "audit", "log", "compliance", "gdpr", "privacy", "data",
                "retention", "deletion", "export",
            ])

            # Extract actor/action/object
            actor = self._extract_actor(description)
            action = self._extract_action(description)
            obj = self._extract_object(description)

            # Build normalized statement
            normalized = f"{actor} SHALL {action} {obj}"

            # Compute ambiguity and testability scores
            ambiguity = self._compute_ambiguity(description)
            testability = self._compute_testability_from_req(req, description)

            record = RequirementNormalization(
                id=uuid.uuid4(),
                run_id=uuid.UUID(self.run_id),
                requirement_id=req_id,
                original_text=description,
                normalized_statement=normalized,
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
            records.append(record)

        return records

    def extract_acceptance_criteria(self) -> list[AcceptanceCriteriaContract]:
        """Extract acceptance criteria from acceptance_criteria.json artifact."""
        loaded = self._load_artifact("specification", "acceptance_criteria.json")
        if not loaded:
            return []

        data = loaded["data"]
        if not isinstance(data, list):
            return []

        records = []
        for idx, ac in enumerate(data):
            ac_id = ac.get("id", f"AC-{idx:03d}")
            req_id = ac.get("requirement_id", "")
            criteria = ac.get("criteria", "")
            verification = ac.get("verification_method", "test")

            # Parse Given/When/Then from criteria text
            given, when, then = self._parse_gwt(criteria)

            # Determine if negative case is required
            criteria_lower = criteria.lower()
            negative_required = any(kw in criteria_lower for kw in [
                "invalid", "error", "fail", "reject", "deny", "unauthorized",
                "expired", "missing", "incorrect", "not", "cannot",
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
                run_id=uuid.UUID(self.run_id),
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

        return records

    def extract_test_obligations_from_plan(self) -> list[dict]:
        """Extract test case definitions from test_plan.json artifact.

        Returns raw dicts (not ORM objects) since test obligations are
        generated from acceptance criteria, not directly from test plans.
        This method extracts the test case definitions for reference.
        """
        loaded = self._load_artifact("test_plan", "test_plan.json")
        if not loaded:
            return []

        data = loaded["data"]
        test_cases = data.get("test_cases", [])
        edge_cases = data.get("edge_cases", [])
        governance_tests = data.get("governance_tests", [])

        extracted = []

        for tc in test_cases:
            extracted.append({
                "source_type": "test_case",
                "id": tc.get("id", ""),
                "name": tc.get("name", ""),
                "test_type": tc.get("type", "unit"),
                "requirement_id": tc.get("requirement_id", ""),
                "priority": tc.get("priority", "medium"),
                "expected_result": tc.get("expected_result", ""),
                "source_artifact_id": loaded["artifact_id"],
                "source_artifact_type": "test_plan",
                "source_json_path": f"test_cases[{test_cases.index(tc)}]",
                "source_hash": loaded["source_hash"],
            })

        for ec in edge_cases:
            extracted.append({
                "source_type": "edge_case",
                "id": ec.get("id", ""),
                "name": ec.get("name", ec.get("description", ""))[:200],
                "test_type": "edge",
                "requirement_id": ec.get("requirement_id", ""),
                "priority": ec.get("priority", "medium"),
                "source_artifact_id": loaded["artifact_id"],
                "source_artifact_type": "test_plan",
                "source_json_path": f"edge_cases[{edge_cases.index(ec)}]",
                "source_hash": loaded["source_hash"],
            })

        for gt in governance_tests:
            extracted.append({
                "source_type": "governance_test",
                "id": gt.get("id", ""),
                "name": gt.get("name", gt.get("description", ""))[:200],
                "test_type": "governance",
                "requirement_id": gt.get("requirement_id", ""),
                "priority": gt.get("priority", "high"),
                "source_artifact_id": loaded["artifact_id"],
                "source_artifact_type": "test_plan",
                "source_json_path": f"governance_tests[{governance_tests.index(gt)}]",
                "source_hash": loaded["source_hash"],
            })

        return extracted

    def extract_negative_test_requirements(self) -> list[NegativeTestRequirement]:
        """Extract negative test requirements from security findings and compliance gaps."""
        records = []

        # From security findings
        sec_loaded = self._load_artifact("governance", "security_findings.json")
        if sec_loaded and isinstance(sec_loaded["data"], list):
            for idx, finding in enumerate(sec_loaded["data"]):
                req_id = finding.get("requirement_id", "")
                # Find the requirement this finding relates to
                if not req_id:
                    # Try to match by content
                    req_id = self._match_requirement_from_text(finding.get("finding", ""))

                record = NegativeTestRequirement(
                    id=uuid.uuid4(),
                    run_id=uuid.UUID(self.run_id),
                    requirement_id=req_id or f"SEC-{idx:03d}",
                    required_negative_case=finding.get("testing_requirement", finding.get("finding", ""))[:500],
                    status="pending",
                )
                records.append(record)

        # From compliance gaps
        comp_loaded = self._load_artifact("governance", "compliance_gaps.json")
        if comp_loaded and isinstance(comp_loaded["data"], list):
            for idx, gap in enumerate(comp_loaded["data"]):
                req_id = gap.get("requirement_id", "")
                if not req_id:
                    req_id = self._match_requirement_from_text(gap.get("gap", ""))

                record = NegativeTestRequirement(
                    id=uuid.uuid4(),
                    run_id=uuid.UUID(self.run_id),
                    requirement_id=req_id or f"COMP-{idx:03d}",
                    required_negative_case=f"Compliance gap: {gap.get('gap', '')[:400]}",
                    status="pending",
                )
                records.append(record)

        return records

    def extract_runtime_evidence_requirements(self) -> list[dict]:
        """Extract runtime evidence requirements from governance concerns."""
        loaded = self._load_artifact("governance", "governance_concerns.json")
        if not loaded or not isinstance(loaded["data"], list):
            return []

        evidence_reqs = []
        for concern in loaded["data"]:
            evidence_types = concern.get("evidence_required", [])
            if isinstance(evidence_types, str):
                evidence_types = [evidence_types]
            elif not isinstance(evidence_types, list):
                evidence_types = []

            for et in evidence_types:
                evidence_reqs.append({
                    "concern_id": concern.get("id", ""),
                    "requirement_id": concern.get("requirement_id", ""),
                    "evidence_type": et[:32] if isinstance(et, str) else "unknown",
                    "category": concern.get("category", ""),
                    "severity": concern.get("severity", "medium"),
                })

        return evidence_reqs

    def _parse_gwt(self, text: str) -> tuple[str, str, str]:
        """Parse Given/When/Then from acceptance criteria text."""
        given, when, then = "", "", ""
        text_lower = text.lower()

        # Try to split on Given/When/Then keywords
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
            # Simple "shall" statement → put in 'then'
            then = text.strip()
        else:
            # Fallback: put everything in 'then'
            then = text.strip()

        return given, when, then

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
        """Compute ambiguity score 0.0-1.0 based on vague terms."""
        vague_terms = ["should", "might", "could", "may", "possibly", "perhaps",
                       "appropriate", "reasonable", "sufficient", "adequate",
                       "etc", "and so on", "as needed"]
        text_lower = text.lower()
        count = sum(1 for term in vague_terms if term in text_lower)
        return min(count * 0.2, 1.0)

    def _compute_testability_from_req(self, req: dict, text: str) -> float:
        """Compute testability score 0.0-1.0."""
        score = 0.5  # baseline

        # Has clear ID → more testable
        if req.get("id"):
            score += 0.1

        # Has priority → more testable
        if req.get("priority") == "must_have":
            score += 0.2
        elif req.get("priority") == "should_have":
            score += 0.1

        # Specific terms increase testability
        specific_terms = ["jwt", "http", "api", "endpoint", "response", "status",
                          "rate limit", "timeout", "expiration", "signature"]
        text_lower = text.lower()
        specificity = sum(1 for t in specific_terms if t in text_lower)
        score += min(specificity * 0.05, 0.2)

        return min(score, 1.0)

    def _match_requirement_from_text(self, text: str) -> str:
        """Try to match a requirement ID from text content."""
        # Simple keyword matching against known requirement patterns
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
