"""Real Test Plan Generation Engine — AI-driven test planning.

Generates comprehensive test plans from specifications and architecture.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from src.core.logging import get_logger
from src.engines.model_router import ModelRouter, get_router
from src.engines.inference_trace import InferenceTracer, InferenceTraceRecord
from src.engines.specification_engine import SpecificationArtifact
from src.engines.architecture_engine import ArchitectureArtifact

logger = get_logger("test_engine")


@dataclass
class TestPlanArtifact:
    """Generated test plan artifact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    project_id: str = ""
    spec_id: str = ""
    arch_id: str = ""
    unit_test_strategy: str = ""
    integration_strategy: str = ""
    edge_cases: list = field(default_factory=list)
    governance_tests: list = field(default_factory=list)
    api_contract_tests: list = field(default_factory=list)
    regression_plan: str = ""
    test_cases: list = field(default_factory=list)
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TestPlanEngine:
    """AI-driven test plan generation."""

    TEST_PLAN_PROMPT = """You are a senior QA engineer and test architect. Based on the following specification and architecture, create a comprehensive test plan.

SPECIFICATION:
{specification}

ARCHITECTURE:
{architecture}

INSTRUCTIONS:
Create a comprehensive test plan in the following JSON format:

{{
  "unit_test_strategy": "Overall unit test strategy (1 paragraph)",
  "integration_strategy": "Integration test strategy (1 paragraph)",
  "edge_cases": [
    {{
      "id": "EC-001",
      "requirement_id": "FR-001",
      "description": "Edge case description",
      "expected_behavior": "What should happen",
      "test_approach": "How to test this"
    }}
  ],
  "governance_tests": [
    {{
      "id": "GT-001",
      "area": "security|privacy|compliance|access_control|audit",
      "description": "Governance test description",
      "acceptance_criteria": "Pass/fail criteria",
      "severity": "critical|high|medium|low"
    }}
  ],
  "api_contract_tests": [
    {{
      "id": "ACT-001",
      "endpoint": "API endpoint or integration point",
      "description": "Contract test description",
      "expected_behavior": "Expected contract"
    }}
  ],
  "regression_plan": "Regression testing strategy (1 paragraph)",
  "test_cases": [
    {{
      "id": "TC-001",
      "name": "Test case name",
      "type": "unit|integration|contract|governance|edge",
      "requirement_id": "FR-001",
      "preconditions": "Test preconditions",
      "steps": ["Step 1", "Step 2"],
      "expected_result": "Expected outcome",
      "priority": "critical|high|medium|low"
    }}
  ]
}}

RULES:
1. Generate at least 5 test cases
2. Generate at least 3 edge cases
3. Generate at least 2 governance tests
4. Generate at least 2 API contract tests
5. Link test cases to specific requirements
6. Output ONLY valid JSON, no markdown, no explanations

OUTPUT:"""

    def __init__(self, router: Optional[ModelRouter] = None):
        self._router = router
        self._tracer: Optional[InferenceTracer] = None

    async def _get_router(self) -> ModelRouter:
        if self._router is None:
            self._router = await get_router()
        return self._router

    async def generate_test_plan(
        self,
        spec: SpecificationArtifact,
        arch: ArchitectureArtifact,
        run_id: str = "",
        tracer: Optional[InferenceTracer] = None,
    ) -> TestPlanArtifact:
        """Generate a test plan from specification and architecture."""
        self._tracer = tracer
        router = await self._get_router()

        prompt = self.TEST_PLAN_PROMPT.format(
            specification=spec.intent[:500],
            architecture=arch.architecture_proposal[:500],
        )

        result = await router.complete(
            messages=[
                {"role": "system", "content": "You are a senior QA engineer. Output ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=8192,
            run_id=run_id,
            phase="test_plan_generation",
        )

        if not result.success:
            logger.error(f"Test plan generation failed: {result.error}")
            return TestPlanArtifact(
                run_id=run_id,
                project_id=spec.project_id,
                spec_id=spec.id,
                arch_id=arch.id,
            )

        try:
            test_data = json.loads(result.response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', result.response, re.DOTALL)
            test_data = json.loads(json_match.group()) if json_match else {}

        artifact = TestPlanArtifact(
            run_id=run_id,
            project_id=spec.project_id,
            spec_id=spec.id,
            arch_id=arch.id,
            unit_test_strategy=test_data.get("unit_test_strategy", ""),
            integration_strategy=test_data.get("integration_strategy", ""),
            edge_cases=test_data.get("edge_cases", []),
            governance_tests=test_data.get("governance_tests", []),
            api_contract_tests=test_data.get("api_contract_tests", []),
            regression_plan=test_data.get("regression_plan", ""),
            test_cases=test_data.get("test_cases", []),
            model_used=result.model,
            provider_used=result.provider,
            tokens_used=result.total_tokens,
            cost_usd=result.cost_usd,
        )

        if self._tracer:
            self._tracer.record(InferenceTraceRecord(
                run_id=run_id,
                phase="test_plan_generation",
                provider=result.provider,
                model=result.model,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.total_tokens,
                cost_usd=result.cost_usd,
                latency_ms=result.latency_ms,
                success=result.success,
                derived_artifacts=[artifact.id],
            ))

        logger.info(
            f"Test plan generated: {len(artifact.test_cases)} test cases, "
            f"{len(artifact.edge_cases)} edge cases, "
            f"{len(artifact.governance_tests)} governance tests, "
            f"model={result.model}, tokens={result.total_tokens}"
        )

        return artifact
