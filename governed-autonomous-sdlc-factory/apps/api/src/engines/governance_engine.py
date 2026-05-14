"""Governance Engine for the Governed Autonomous SDLC Factory.

Implements executable governance:
- OPA/Rego policy definitions
- Policy evaluation against artifacts and code
- Governance findings with severity
- Release gates (blocking/non-blocking)
- Evidence collection per evaluation

NOT: "the system should be secure."
ACTUAL: Executable Rego policies that evaluate to pass/fail with evidence.
"""
import hashlib
import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import EventBusManager, Event, publish_governance_finding, publish_custom_event
from src.models import (
    GovernancePolicy, GovernanceEvaluation, GovernanceReleaseGate,
    Artifact, ArtifactType, Run
)
from src.core.logging import get_logger

logger = get_logger("gov_engine")


# =============================================================================
# DEFAULT REGO POLICIES
# =============================================================================

DEFAULT_POLICIES = [
    {
        "name": "no-deployment-without-tests",
        "description": "Deployment is blocked if no test artifacts exist for the current run.",
        "category": "quality",
        "severity": "critical",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    count(test_artifacts) > 0
}

test_artifacts[artifact] {
    some artifact in input.artifacts
    artifact.type == "test_plan"
    artifact.phase_name == "quality"
}

violations[msg] {
    count(test_artifacts) == 0
    msg := "No test artifacts found. Deployment requires at least one test plan."
}
''',
    },
    {
        "name": "no-deployment-without-evidence",
        "description": "Deployment is blocked if no evidence artifacts exist.",
        "category": "compliance",
        "severity": "critical",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    count(evidence_artifacts) > 0
}

evidence_artifacts[artifact] {
    some artifact in input.artifacts
    artifact.type == "evidence"
}

violations[msg] {
    count(evidence_artifacts) == 0
    msg := "No evidence artifacts found. Deployment requires evidence of quality checks."
}
''',
    },
    {
        "name": "no-direct-push-to-main",
        "description": "Direct commits to main branch are not allowed. All changes must go through a pull request.",
        "category": "compliance",
        "severity": "error",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    not direct_push
}

direct_push {
    some commit in input.commits
    commit.branch == "main"
    not commit.via_pull_request
}

violations[msg] {
    direct_push
    msg := "Direct push to main branch detected. All changes must go through a pull request."
}
''',
    },
    {
        "name": "no-missing-readme",
        "description": "The project must have a README.md file.",
        "category": "quality",
        "severity": "warning",
        "is_blocking": False,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    has_readme
}

has_readme {
    some file in input.files
    file.name == "README.md"
    file.size_bytes > 0
}

violations[msg] {
    not has_readme
    msg := "README.md is missing or empty. All projects must have documentation."
}
''',
    },
    {
        "name": "no-missing-architecture-doc",
        "description": "The project must have an architecture document.",
        "category": "quality",
        "severity": "warning",
        "is_blocking": False,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    has_arch_doc
}

has_arch_doc {
    some artifact in input.artifacts
    artifact.type == "architecture"
    artifact.name == "architecture.md"
}

violations[msg] {
    not has_arch_doc
    msg := "Architecture document is missing. All projects must have an architecture.md."
}
''',
    },
    {
        "name": "no-missing-specification",
        "description": "The project must have a specification document.",
        "category": "quality",
        "severity": "error",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    has_spec
}

has_spec {
    some artifact in input.artifacts
    artifact.type == "specification"
}

violations[msg] {
    not has_spec
    msg := "Specification document is missing. All projects must have requirements."
}
''',
    },
    {
        "name": "test-coverage-minimum",
        "description": "Test coverage must meet the minimum threshold (80%).",
        "category": "quality",
        "severity": "error",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    input.coverage_percent >= 80
}

violations[msg] {
    input.coverage_percent < 80
    msg := sprintf("Test coverage %.1f%% is below minimum threshold of 80%%", [input.coverage_percent])
}
''',
    },
    {
        "name": "no-critical-vulnerabilities",
        "description": "No critical security vulnerabilities are allowed in dependencies.",
        "category": "security",
        "severity": "critical",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    count(critical_vulns) == 0
}

critical_vulns[vuln] {
    some vuln in input.vulnerabilities
    vuln.severity == "critical"
}

violations[msg] {
    count(critical_vulns) > 0
    msg := sprintf("Found %d critical security vulnerabilities", [count(critical_vulns)])
}
''',
    },
    {
        "name": "spec-has-acceptance-criteria",
        "description": "All must/should requirements must have acceptance criteria.",
        "category": "quality",
        "severity": "warning",
        "is_blocking": False,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    count(missing_ac) == 0
}

missing_ac[req_id] {
    some req_id, req in input.requirements
    req.priority == "must"
    count(req.acceptance_criteria) == 0
}

violations[msg] {
    count(missing_ac) > 0
    msg := sprintf("Requirements without acceptance criteria: %v", [concat(", ", [k | k := missing_ac[_]])])
}
''',
    },
    {
        "name": "governance-evaluation-required",
        "description": "All governance policies must be evaluated before deployment.",
        "category": "compliance",
        "severity": "critical",
        "is_blocking": True,
        "rego_code": '''package sdlc.governance

import future.keywords.in

default allow := false

allow {
    count(required_policies) == count(passed_policies)
}

required_policy_ids[pid] {
    some pid in input.required_policy_ids
}

passed_policies[pid] {
    some eval in input.evaluations
    eval.policy_id == pid
    eval.decision == "pass"
}

required_policies[pid] {
    pid := required_policy_ids[_]
}

violations[msg] {
    count(required_policies) > count(passed_policies)
    msg := sprintf("Not all required governance policies passed. Required: %d, Passed: %d", [count(required_policies), count(passed_policies)])
}
''',
    },
]


# =============================================================================
# GOVERNANCE ENGINE
# =============================================================================

class GovernanceEngine:
    """Core governance engine for policy evaluation and release gates."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.bus = EventBusManager.get_bus(run_id)
        self.opa_available = self._check_opa()

    def _check_opa(self) -> bool:
        """Check if OPA binary is available."""
        try:
            result = subprocess.run(["opa", "version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("OPA binary not found. Using built-in Rego evaluation.")
            return False

    # -----------------------------------------------------------------
    # POLICY MANAGEMENT
    # -----------------------------------------------------------------

    async def seed_default_policies(self, session: AsyncSession):
        """Seed default governance policies if they don't exist."""
        for policy_data in DEFAULT_POLICIES:
            result = await session.execute(
                select(GovernancePolicy).where(GovernancePolicy.name == policy_data["name"])
            )
            existing = result.scalars().first()
            if not existing:
                policy = GovernancePolicy(
                    name=policy_data["name"],
                    description=policy_data["description"],
                    category=policy_data["category"],
                    severity=policy_data["severity"],
                    is_blocking=policy_data["is_blocking"],
                    rego_code=policy_data["rego_code"],
                    is_active=True,
                )
                session.add(policy)
                logger.info(f"Seeded policy: {policy_data['name']}")
        await session.commit()

    async def get_policies(self, session: AsyncSession, active_only: bool = True) -> list[GovernancePolicy]:
        """Get all governance policies."""
        query = select(GovernancePolicy)
        if active_only:
            query = query.where(GovernancePolicy.is_active == True)
        result = await session.execute(query)
        return list(result.scalars().all())

    # -----------------------------------------------------------------
    # POLICY EVALUATION
    # -----------------------------------------------------------------

    async def evaluate_policy(self, session: AsyncSession, policy: GovernancePolicy,
                               input_data: dict, artifact_id: str = None) -> GovernanceEvaluation:
        """Evaluate a single policy against input data."""
        if self.opa_available:
            decision, findings = await self._evaluate_with_opa(policy, input_data)
        else:
            decision, findings = self._evaluate_builtin(policy, input_data)

        evaluation = GovernanceEvaluation(
            run_id=self.run_id,
            policy_id=policy.id,
            artifact_id=artifact_id,
            decision=decision,
            findings=findings,
            evidence={
                "input_hash": hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest(),
                "policy_version": policy.version,
                "evaluated_by": "opa" if self.opa_available else "builtin",
            },
        )
        session.add(evaluation)
        await session.flush()

        severity = "info" if decision == "pass" else policy.severity
        await publish_governance_finding(
            self.run_id, policy.name, decision,
            severity=severity,
            data={
                "evaluation_id": evaluation.id,
                "policy_id": policy.id,
                "findings_count": len(findings),
            },
        )

        return evaluation

    async def _evaluate_with_opa(self, policy: GovernancePolicy, input_data: dict) -> tuple[str, list]:
        """Evaluate policy using OPA binary."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rego', delete=False) as f:
                f.write(policy.rego_code)
                policy_path = f.name

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"input": input_data}, f)
                input_path = f.name

            result = subprocess.run(
                ["opa", "eval", "--format", "json", "-d", policy_path, "-i", input_path,
                 "data.sdlc.governance"],
                capture_output=True, text=True, timeout=30
            )

            os.unlink(policy_path)
            os.unlink(input_path)

            if result.returncode == 0:
                opa_result = json.loads(result.stdout)
                if "result" in opa_result and opa_result["result"]:
                    for r in opa_result["result"]:
                        if "expressions" in r:
                            for expr in r["expressions"]:
                                if isinstance(expr["value"], dict):
                                    allow = expr["value"].get("allow", False)
                                    violations = expr["value"].get("violations", [])
                                    if allow:
                                        return "pass", []
                                    else:
                                        findings = [v for v in violations if isinstance(v, str)]
                                        return "fail", findings

            return "error", [f"OPA evaluation error: {result.stderr}"]
        except Exception as e:
            logger.error(f"OPA evaluation failed: {e}")
            return "error", [str(e)]

    def _evaluate_builtin(self, policy: GovernancePolicy, input_data: dict) -> tuple[str, list]:
        """Built-in Rego-like evaluation when OPA is not available."""
        name = policy.name
        findings = []

        if name == "no-deployment-without-tests":
            test_artifacts = [a for a in input_data.get("artifacts", [])
                              if a.get("type") == "test_plan" and a.get("phase_name") == "quality"]
            if test_artifacts:
                return "pass", []
            return "fail", ["No test artifacts found. Deployment requires at least one test plan."]

        elif name == "no-deployment-without-evidence":
            evidence = [a for a in input_data.get("artifacts", []) if a.get("type") == "evidence"]
            if evidence:
                return "pass", []
            return "fail", ["No evidence artifacts found. Deployment requires evidence of quality checks."]

        elif name == "no-direct-push-to-main":
            commits = input_data.get("commits", [])
            direct = [c for c in commits if c.get("branch") == "main" and not c.get("via_pull_request")]
            if not direct:
                return "pass", []
            return "fail", [f"Direct push to main detected: {len(commits)} commits"]

        elif name == "no-missing-readme":
            files = input_data.get("files", [])
            readme = [f for f in files if f.get("name") == "README.md" and f.get("size_bytes", 0) > 0]
            if readme:
                return "pass", []
            return "fail", ["README.md is missing or empty."]

        elif name == "no-missing-architecture-doc":
            artifacts = input_data.get("artifacts", [])
            arch = [a for a in artifacts if a.get("type") == "architecture" and a.get("name") == "architecture.md"]
            if arch:
                return "pass", []
            return "fail", ["Architecture document is missing."]

        elif name == "no-missing-specification":
            artifacts = input_data.get("artifacts", [])
            specs = [a for a in artifacts if a.get("type") == "specification"]
            if specs:
                return "pass", []
            return "fail", ["Specification document is missing."]

        elif name == "test-coverage-minimum":
            coverage = input_data.get("coverage_percent", 0)
            if coverage >= 80:
                return "pass", []
            return "fail", [f"Test coverage {coverage}% is below minimum threshold of 80%"]

        elif name == "no-critical-vulnerabilities":
            vulns = input_data.get("vulnerabilities", [])
            critical = [v for v in vulns if v.get("severity") == "critical"]
            if not critical:
                return "pass", []
            return "fail", [f"Found {len(critical)} critical security vulnerabilities"]

        elif name == "spec-has-acceptance-criteria":
            requirements = input_data.get("requirements", {})
            missing = [rid for rid, req in requirements.items()
                       if req.get("priority") == "must" and not req.get("acceptance_criteria")]
            if not missing:
                return "pass", []
            return "fail", [f"Requirements without acceptance criteria: {', '.join(missing)}"]

        elif name == "governance-evaluation-required":
            required = set(input_data.get("required_policy_ids", []))
            evaluations = input_data.get("evaluations", [])
            passed = {e["policy_id"] for e in evaluations if e.get("decision") == "pass"}
            if required and required == passed:
                return "pass", []
            return "fail", [f"Not all required policies passed. Required: {len(required)}, Passed: {len(passed)}"]

        return "warning", [f"Unknown policy: {name}"]

    # -----------------------------------------------------------------
    # BATCH EVALUATION
    # -----------------------------------------------------------------

    async def evaluate_all_policies(self, session: AsyncSession, input_data: dict,
                                     artifact_id: str = None) -> list[GovernanceEvaluation]:
        """Evaluate all active policies."""
        policies = await self.get_policies(session)
        evaluations = []
        for policy in policies:
            eval_result = await self.evaluate_policy(session, policy, input_data, artifact_id)
            evaluations.append(eval_result)
        await session.commit()
        return evaluations

    # -----------------------------------------------------------------
    # RELEASE GATES
    # -----------------------------------------------------------------

    async def create_release_gate(self, session: AsyncSession, gate_name: str,
                                   required_policy_ids: list[str]) -> GovernanceReleaseGate:
        """Create a release gate for a run."""
        gate = GovernanceReleaseGate(
            run_id=self.run_id,
            gate_name=gate_name,
            status="pending",
            required_policy_ids=required_policy_ids,
        )
        session.add(gate)
        await session.commit()
        return gate

    async def evaluate_release_gate(self, session: AsyncSession, gate_id: str) -> GovernanceReleaseGate:
        """Evaluate a release gate against current evaluations."""
        gate = await session.get(GovernanceReleaseGate, gate_id)
        if not gate:
            raise ValueError(f"Release gate {gate_id} not found")

        # Get evaluations for required policies
        result = await session.execute(
            select(GovernanceEvaluation)
            .where(GovernanceEvaluation.run_id == self.run_id)
            .where(GovernanceEvaluation.policy_id.in_(gate.required_policy_ids))
            .order_by(GovernanceEvaluation.evaluated_at.desc())
        )
        evaluations = list(result.scalars().all())

        # Deduplicate by policy_id (take latest)
        latest_evals = {}
        for ev in evaluations:
            if ev.policy_id not in latest_evals:
                latest_evals[ev.policy_id] = ev

        # Check if all required policies passed
        all_passed = all(
            latest_evals.get(pid) and latest_evals[pid].decision == "pass"
            for pid in gate.required_policy_ids
        )

        blocking_failed = any(
            latest_evals.get(pid) and latest_evals[pid].decision == "fail"
            for pid in gate.required_policy_ids
            if latest_evals.get(pid)
        )

        gate.evaluation_ids = [ev.id for ev in latest_evals.values()]
        gate.evaluated_at = datetime.now(timezone.utc)

        if all_passed:
            gate.status = "passed"
        elif blocking_failed:
            gate.status = "failed"
        else:
            gate.status = "pending"

        await session.commit()

        await publish_custom_event(
            self.run_id, "governance.gate_evaluated",
            f"Release gate '{gate.gate_name}': {gate.status}",
            severity="info" if gate.status == "passed" else "warning" if gate.status == "pending" else "error",
            data={"gate_id": gate.id, "gate_name": gate.gate_name, "status": gate.status},
        )

        return gate

    async def waive_release_gate(self, session: AsyncSession, gate_id: str,
                                  waived_by: str, reason: str) -> GovernanceReleaseGate:
        """Waive a release gate (with audit trail)."""
        gate = await session.get(GovernanceReleaseGate, gate_id)
        if not gate:
            raise ValueError(f"Release gate {gate_id} not found")

        gate.status = "waived"
        gate.waived_by = waived_by
        gate.waived_reason = reason
        await session.commit()

        await publish_custom_event(
            self.run_id, "governance.gate_waived",
            f"Release gate '{gate.gate_name}' waived by {waived_by}: {reason}",
            severity="warning",
            data={"gate_id": gate.id, "waived_by": waived_by},
        )

        return gate


# =============================================================================
# CONVENIENCE: Seed policies + evaluate
# =============================================================================

async def seed_governance_policies():
    """Seed all default governance policies."""
    async with async_session_factory() as session:
        engine = GovernanceEngine("system")
        await engine.seed_default_policies(session)
        logger.info("Default governance policies seeded")
