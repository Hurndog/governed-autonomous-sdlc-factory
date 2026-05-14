"""Test Plan Generator for the Governed Autonomous SDLC Factory.

Generates comprehensive test plans linked to requirements:
- Unit test strategy
- Integration test strategy
- API contract tests
- Edge cases
- Smoke tests
- Governance tests
- Regression strategy
- Full traceability map (requirement_id -> test_ids)

All test artifacts are traceable back to specific requirements.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import EventBusManager, Event, publish_artifact_created, publish_custom_event
from src.models import (
    TestPlan, Artifact, ArtifactType, TraceabilityLink, Run, Project
)
from src.core.logging import get_logger

logger = get_logger("test_engine")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class TestCase:
    """Single test case."""
    def __init__(self, test_id: str, name: str, description: str,
                 test_type: str, priority: str = "must",
                 requirement_ids: list = None, steps: list = None,
                 expected_result: str = "", edge_case: bool = False):
        self.id = test_id
        self.name = name
        self.description = description
        self.type = test_type  # unit, integration, contract, smoke, governance, regression
        self.priority = priority
        self.requirement_ids = requirement_ids or []
        self.steps = steps or []
        self.expected_result = expected_result
        self.edge_case = edge_case

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "requirement_ids": self.requirement_ids,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "edge_case": self.edge_case,
        }


class TestPlanGenerator:
    """Generates comprehensive test plans from specifications."""

    def __init__(self, run_id: str, project_id: str):
        self.run_id = run_id
        self.project_id = project_id
        self.bus = EventBusManager.get_bus(run_id)
        self.test_cases: list[TestCase] = []
        self.traceability_map: dict = {}  # requirement_id -> [test_id, ...]
        self._version: Optional[TestPlan] = None

    # -----------------------------------------------------------------
    # TEST GENERATION FROM REQUIREMENTS
    # -----------------------------------------------------------------

    def generate_from_requirements(self, requirements: list[dict], nfr: list[dict] = None):
        """Generate test cases from structured requirements."""
        nfr = nfr or []
        all_reqs = requirements + nfr

        for req in all_reqs:
            req_id = req.get("id", str(uuid.uuid4())[:8])
            req_title = req.get("title", "Unknown")
            req_type = req.get("type", "functional")
            ac_list = req.get("acceptance_criteria", [])

            # Generate unit tests for each acceptance criterion
            for i, ac in enumerate(ac_list):
                test_id = f"TEST-{req_id}-U{i+1}"
                tc = TestCase(
                    test_id=test_id,
                    name=f"Unit: {req_title} - AC{i+1}",
                    description=f"Verify: {ac}",
                    test_type="unit",
                    priority=req.get("priority", "must"),
                    requirement_ids=[req_id],
                    steps=[
                        f"Setup test context for {req_id}",
                        f"Execute: {ac}",
                        f"Assert expected behavior",
                    ],
                    expected_result=ac,
                )
                self.test_cases.append(tc)
                self._add_traceability(req_id, test_id)

            # Generate integration test
            if req_type == "functional":
                int_test_id = f"TEST-{req_id}-INT"
                tc = TestCase(
                    test_id=int_test_id,
                    name=f"Integration: {req_title}",
                    description=f"End-to-end integration test for: {req_title}",
                    test_type="integration",
                    priority=req.get("priority", "must"),
                    requirement_ids=[req_id],
                    steps=[
                        f"Initialize system components",
                        f"Execute {req_id} through full stack",
                        f"Verify system state and outputs",
                    ],
                    expected_result=f"{req_id} completes successfully with correct output",
                )
                self.test_cases.append(tc)
                self._add_traceability(req_id, int_test_id)

            # Generate edge case tests for must-have requirements
            if req.get("priority") == "must":
                edge_tests = self._generate_edge_cases(req)
                for tc in edge_tests:
                    self.test_cases.append(tc)
                    self._add_traceability(req_id, tc.id)

        # Generate API contract tests
        self._generate_contract_tests(requirements)

        # Generate smoke tests
        self._generate_smoke_tests(requirements)

        # Generate governance tests
        self._generate_governance_tests()

        # Generate regression strategy
        self._generate_regression_strategy(requirements)

    def _generate_edge_cases(self, req: dict) -> list[TestCase]:
        """Generate edge case tests for a requirement."""
        req_id = req.get("id", "UNKNOWN")
        req_title = req.get("title", "Unknown")
        edge_cases = []

        # Common edge cases
        edge_cases.append(TestCase(
            test_id=f"TEST-{req_id}-EDGE-1",
            name=f"Edge: {req_title} - Empty Input",
            description=f"Test {req_id} with empty/null input",
            test_type="unit",
            priority="should",
            requirement_ids=[req_id],
            steps=[f"Call {req_id} with empty input", "Verify graceful handling"],
            expected_result="Returns appropriate error, no crash",
            edge_case=True,
        ))

        edge_cases.append(TestCase(
            test_id=f"TEST-{req_id}-EDGE-2",
            name=f"Edge: {req_title} - Boundary Values",
            description=f"Test {req_id} with boundary/extreme values",
            test_type="unit",
            priority="should",
            requirement_ids=[req_id],
            steps=[f"Call {req_id} with min/max values", "Verify correct handling"],
            expected_result="Handles boundary values correctly",
            edge_case=True,
        ))

        edge_cases.append(TestCase(
            test_id=f"TEST-{req_id}-EDGE-3",
            name=f"Edge: {req_title} - Concurrent Access",
            description=f"Test {req_id} under concurrent access",
            test_type="integration",
            priority="could",
            requirement_ids=[req_id],
            steps=[f"Simulate concurrent calls to {req_id}", "Verify data consistency"],
            expected_result="No race conditions or data corruption",
            edge_case=True,
        ))

        return edge_cases

    def _generate_contract_tests(self, requirements: list[dict]):
        """Generate API contract tests."""
        contract_tests = [
            TestCase(
                test_id="TEST-CONTRACT-001",
                name="API Schema Validation",
                description="Verify all API endpoints conform to OpenAPI schema",
                test_type="contract",
                priority="must",
                requirement_ids=[],
                steps=["Load OpenAPI spec", "Validate all endpoints", "Check request/response schemas"],
                expected_result="All endpoints match OpenAPI specification",
            ),
            TestCase(
                test_id="TEST-CONTRACT-002",
                name="Error Response Format",
                description="Verify all error responses follow the standard error format",
                test_type="contract",
                priority="must",
                requirement_ids=[],
                steps=["Trigger various error conditions", "Verify error response structure"],
                expected_result="All errors return {code, message, details} format",
            ),
            TestCase(
                test_id="TEST-CONTRACT-003",
                name="Authentication Contract",
                description="Verify authentication endpoints return correct token format",
                test_type="contract",
                priority="must",
                requirement_ids=["AUTH-001"],
                steps=["Login with valid credentials", "Verify JWT structure", "Verify token expiry"],
                expected_result="Valid JWT with correct claims and expiry",
            ),
        ]
        self.test_cases.extend(contract_tests)

    def _generate_smoke_tests(self, requirements: list[dict]):
        """Generate smoke tests for critical paths."""
        smoke_tests = [
            TestCase(
                test_id="TEST-SMOKE-001",
                name="Health Check",
                description="Verify system health endpoint responds",
                test_type="smoke",
                priority="must",
                requirement_ids=[],
                steps=["GET /health", "Verify 200 response"],
                expected_result="System reports healthy",
            ),
            TestCase(
                test_id="TEST-SMOKE-002",
                name="Database Connectivity",
                description="Verify database connection is working",
                test_type="smoke",
                priority="must",
                requirement_ids=[],
                steps=["Query database", "Verify response"],
                expected_result="Database responds within 100ms",
            ),
            TestCase(
                test_id="TEST-SMOKE-003",
                name="Authentication Flow",
                description="Verify basic auth flow works end-to-end",
                test_type="smoke",
                priority="must",
                requirement_ids=["AUTH-001"],
                steps=["Register user", "Login", "Access protected endpoint"],
                expected_result="Full auth flow completes successfully",
            ),
        ]
        self.test_cases.extend(smoke_tests)

    def _generate_governance_tests(self):
        """Generate governance compliance tests."""
        gov_tests = [
            TestCase(
                test_id="TEST-GOV-001",
                name="Policy Evaluation",
                description="Verify governance policies can be evaluated",
                test_type="governance",
                priority="must",
                requirement_ids=[],
                steps=["Load all policies", "Evaluate against test input", "Verify results"],
                expected_result="All policies evaluate correctly",
            ),
            TestCase(
                test_id="TEST-GOV-002",
                name="Release Gate Blocking",
                description="Verify release gates block deployment when policies fail",
                test_type="governance",
                priority="must",
                requirement_ids=[],
                steps=["Create failing policy evaluation", "Attempt deployment", "Verify block"],
                expected_result="Deployment is blocked with clear error message",
            ),
            TestCase(
                test_id="TEST-GOV-003",
                name="Audit Trail",
                description="Verify all governance decisions are logged",
                test_type="governance",
                priority="must",
                requirement_ids=[],
                steps=["Perform governance actions", "Check audit log"],
                expected_result="All actions logged with timestamps and actors",
            ),
        ]
        self.test_cases.extend(gov_tests)

    def _generate_regression_strategy(self, requirements: list[dict]) -> dict:
        """Generate regression testing strategy."""
        return {
            "trigger": "On every merge to main and before deployment",
            "scope": "All must-priority tests + smoke tests",
            "automation": "CI/CD pipeline with pytest",
            "parallelization": "Tests run in parallel using pytest-xdist",
            "coverage_target": "80% minimum line coverage",
            "flaky_test_policy": "Flaky tests are quarantined after 3 failures and tracked in backlog",
            "regression_suite": {
                "smoke": [tc.id for tc in self.test_cases if tc.type == "smoke"],
                "unit": [tc.id for tc in self.test_cases if tc.type == "unit" and tc.priority == "must"],
                "integration": [tc.id for tc in self.test_cases if tc.type == "integration" and tc.priority == "must"],
                "contract": [tc.id for tc in self.test_cases if tc.type == "contract"],
                "governance": [tc.id for tc in self.test_cases if tc.type == "governance"],
            },
            "estimated_runtime": f"{len(self.test_cases) * 0.5:.0f} seconds (parallel)",
        }

    def _add_traceability(self, requirement_id: str, test_id: str):
        """Add a traceability link between requirement and test."""
        if requirement_id not in self.traceability_map:
            self.traceability_map[requirement_id] = []
        self.traceability_map[requirement_id].append(test_id)

    # -----------------------------------------------------------------
    # ARTIFACT GENERATION
    # -----------------------------------------------------------------

    def generate_unit_test_strategy(self) -> dict:
        unit_tests = [tc.to_dict() for tc in self.test_cases if tc.type == "unit"]
        return {
            "framework": "pytest",
            "coverage_target": "80%",
            "test_count": len(unit_tests),
            "tests": unit_tests,
            "organization": "Mirror source code structure in tests/ directory",
            "naming": "test_{module}_{scenario}",
            "fixtures": "Shared fixtures in conftest.py",
        }

    def generate_integration_test_strategy(self) -> dict:
        int_tests = [tc.to_dict() for tc in self.test_cases if tc.type == "integration"]
        return {
            "framework": "pytest + httpx",
            "test_count": len(int_tests),
            "tests": int_tests,
            "setup": "Test database with migrations, test Redis instance",
            "teardown": "Rollback transactions, flush cache",
            "isolation": "Each test runs in a transaction that is rolled back",
        }

    def generate_test_plan_dict(self) -> dict:
        """Generate the complete test plan as a dict."""
        return {
            "metadata": {
                "version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
                "project_id": self.project_id,
                "total_tests": len(self.test_cases),
            },
            "unit_test_strategy": self.generate_unit_test_strategy(),
            "integration_test_strategy": self.generate_integration_test_strategy(),
            "api_contract_tests": [tc.to_dict() for tc in self.test_cases if tc.type == "contract"],
            "edge_cases": [tc.to_dict() for tc in self.test_cases if tc.edge_case],
            "smoke_tests": [tc.to_dict() for tc in self.test_cases if tc.type == "smoke"],
            "governance_tests": [tc.to_dict() for tc in self.test_cases if tc.type == "governance"],
            "regression_strategy": self._generate_regression_strategy([]),
            "traceability_map": self.traceability_map,
            "summary": {
                "total": len(self.test_cases),
                "unit": len([tc for tc in self.test_cases if tc.type == "unit"]),
                "integration": len([tc for tc in self.test_cases if tc.type == "integration"]),
                "contract": len([tc for tc in self.test_cases if tc.type == "contract"]),
                "smoke": len([tc for tc in self.test_cases if tc.type == "smoke"]),
                "governance": len([tc for tc in self.test_cases if tc.type == "governance"]),
                "edge_cases": len([tc for tc in self.test_cases if tc.edge_case]),
                "must": len([tc for tc in self.test_cases if tc.priority == "must"]),
                "should": len([tc for tc in self.test_cases if tc.priority == "should"]),
                "could": len([tc for tc in self.test_cases if tc.priority == "could"]),
            },
        }

    # -----------------------------------------------------------------
    # PERSISTENCE
    # -----------------------------------------------------------------

    async def persist(self, session: AsyncSession, generated_by: str = "test-engine") -> TestPlan:
        """Persist test plan to database."""
        plan_data = self.generate_test_plan_dict()

        result = await session.execute(
            select(TestPlan)
            .where(TestPlan.run_id == self.run_id)
            .order_by(TestPlan.version.desc())
        )
        latest = result.scalars().first()
        version_num = (latest.version + 1) if latest else 1

        test_plan = TestPlan(
            run_id=self.run_id,
            project_id=self.project_id,
            version=version_num,
            status="draft",
            unit_test_strategy=plan_data["unit_test_strategy"],
            integration_test_strategy=plan_data["integration_test_strategy"],
            api_contract_tests=plan_data["api_contract_tests"],
            edge_cases=plan_data["edge_cases"],
            smoke_tests=plan_data["smoke_tests"],
            governance_tests=plan_data["governance_tests"],
            regression_strategy=plan_data["regression_strategy"],
            traceability_map=self.traceability_map,
            generated_by=generated_by,
        )
        session.add(test_plan)
        await session.flush()

        # Create artifact
        artifact = Artifact(
            run_id=self.run_id,
            name="test-plan.json",
            type=ArtifactType.TEST_PLAN,
            phase_name="quality",
            content=json.dumps(plan_data, indent=2)[:10000],
            metadata_={"test_plan_id": test_plan.id, "version": version_num},
        )
        session.add(artifact)

        # Create traceability links
        for req_id, test_ids in self.traceability_map.items():
            for test_id in test_ids:
                link = TraceabilityLink(
                    run_id=self.run_id,
                    source_type="requirement",
                    source_id=req_id,
                    target_type="test",
                    target_id=test_id,
                    link_type="validates",
                )
                session.add(link)

        await session.commit()
        self._version = test_plan

        await publish_custom_event(
            self.run_id, "testplan.generated",
            f"Test plan v{version_num} generated: {len(self.test_cases)} tests, {len(self.traceability_map)} traceability links",
            data={
                "test_plan_id": test_plan.id,
                "version": version_num,
                "test_count": len(self.test_cases),
                "traceability_count": sum(len(v) for v in self.traceability_map.values()),
            },
        )

        logger.info(f"Test plan v{version_num} persisted: {len(self.test_cases)} tests")
        return test_plan


# =============================================================================
# CONVENIENCE: Generate test plan from spec
# =============================================================================

async def generate_test_plan_from_spec(run_id: str, project_id: str,
                                        requirements: list[dict],
                                        nfr: list[dict] = None) -> TestPlan:
    """Generate a test plan from specification requirements."""
    generator = TestPlanGenerator(run_id, project_id)
    generator.generate_from_requirements(requirements, nfr)

    async with async_session_factory() as session:
        plan = await generator.persist(session, generated_by="test-engine")
        return plan
