"""Real Specification Engine — AI-driven specification generation.

Uses the ModelRouter to generate real specifications from user intent.
No templates. No static defaults. Real LLM inference.

Pipeline:
    User Intent → Intent Parsing → Requirement Extraction →
    Requirement Structuring → Governance Tagging → Specification Baseline
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from src.core.logging import get_logger
from src.engines.model_router import ModelRouter, InferenceResult, RoutingPolicy, get_router
from src.engines.inference_trace import InferenceTracer, InferenceTraceRecord

logger = get_logger("spec_engine")


@dataclass
class SpecificationArtifact:
    """Generated specification artifact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    project_id: str = ""
    intent: str = ""
    functional_requirements: list = field(default_factory=list)
    non_functional_requirements: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    acceptance_criteria: list = field(default_factory=list)
    governance_sensitive_areas: list = field(default_factory=list)
    technical_constraints: list = field(default_factory=list)
    implementation_risks: list = field(default_factory=list)
    dependency_assumptions: list = field(default_factory=list)
    raw_specification: str = ""
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SpecificationEngine:
    """AI-driven specification generation engine."""

    SPEC_GENERATION_PROMPT = """You are a senior software architect and requirements engineer. Your task is to analyze a user's software idea and produce a comprehensive, structured specification.

USER INTENT:
{intent}

INSTRUCTIONS:
Analyze the above intent and produce a structured specification in the following JSON format. Be thorough, specific, and technically precise.

{{
  "functional_requirements": [
    {{
      "id": "FR-001",
      "description": "Clear, testable functional requirement",
      "priority": "must_have|should_have|could_have",
      "complexity": "low|medium|high"
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR-001",
      "category": "performance|security|scalability|reliability|usability|maintainability",
      "description": "Measurable non-functional requirement",
      "metric": "How to measure compliance"
    }}
  ],
  "assumptions": [
    "Explicit assumption about the system or domain"
  ],
  "acceptance_criteria": [
    {{
      "id": "AC-001",
      "requirement_id": "FR-001",
      "criteria": "Specific, testable acceptance criteria",
      "verification_method": "test|review|demo|analysis"
    }}
  ],
  "governance_sensitive_areas": [
    {{
      "area": "Description of governance-sensitive area",
      "concern": "privacy|security|compliance|data_retention|access_control|audit",
      "severity": "critical|high|medium|low",
      "mitigation": "Suggested mitigation approach"
    }}
  ],
  "technical_constraints": [
    "Technical constraint that shapes the architecture"
  ],
  "implementation_risks": [
    {{
      "risk": "Description of implementation risk",
      "likelihood": "high|medium|low",
      "impact": "high|medium|low",
      "mitigation": "Suggested mitigation"
    }}
  ],
  "dependency_assumptions": [
    "External dependency or integration assumption"
  ]
}}

RULES:
1. Generate at least 5 functional requirements
2. Generate at least 3 non-functional requirements
3. Generate acceptance criteria for each functional requirement
4. Identify at least 2 governance-sensitive areas
5. Identify at least 2 implementation risks
6. Be specific and technical, not generic
7. Consider security, privacy, and compliance implications
8. Output ONLY valid JSON, no markdown, no explanations

OUTPUT:"""

    def __init__(self, router: Optional[ModelRouter] = None):
        self._router = router
        self._tracer: Optional[InferenceTracer] = None

    async def _get_router(self) -> ModelRouter:
        if self._router is None:
            self._router = await get_router()
        return self._router

    async def generate_specification(
        self,
        intent: str,
        run_id: str = "",
        project_id: str = "",
        tracer: Optional[InferenceTracer] = None,
    ) -> SpecificationArtifact:
        """Generate a complete specification from user intent.

        Uses real LLM inference via ModelRouter.
        """
        self._tracer = tracer
        router = await self._get_router()

        # Build prompt
        prompt = self.SPEC_GENERATION_PROMPT.format(intent=intent)

        # Execute inference with structured output
        result = await router.complete(
            messages=[
                {"role": "system", "content": "You are a senior software architect. Output ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more structured output
            max_tokens=8192,
            run_id=run_id,
            phase="specification_generation",
        )

        if not result.success:
            logger.error(f"Specification generation failed: {result.error}")
            return SpecificationArtifact(
                run_id=run_id,
                project_id=project_id,
                intent=intent,
                raw_specification=f"ERROR: {result.error}",
            )

        # Parse the JSON response
        try:
            spec_data = json.loads(result.response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse specification JSON: {e}")
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', result.response, re.DOTALL)
            if json_match:
                try:
                    spec_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    spec_data = {}
            else:
                spec_data = {}

        # Build artifact
        artifact = SpecificationArtifact(
            run_id=run_id,
            project_id=project_id,
            intent=intent,
            functional_requirements=spec_data.get("functional_requirements", []),
            non_functional_requirements=spec_data.get("non_functional_requirements", []),
            assumptions=spec_data.get("assumptions", []),
            acceptance_criteria=spec_data.get("acceptance_criteria", []),
            governance_sensitive_areas=spec_data.get("governance_sensitive_areas", []),
            technical_constraints=spec_data.get("technical_constraints", []),
            implementation_risks=spec_data.get("implementation_risks", []),
            dependency_assumptions=spec_data.get("dependency_assumptions", []),
            raw_specification=result.response,
            model_used=result.model,
            provider_used=result.provider,
            tokens_used=result.total_tokens,
            cost_usd=result.cost_usd,
        )

        # Record inference trace
        if self._tracer:
            self._tracer.record(InferenceTraceRecord(
                run_id=run_id,
                phase="specification_generation",
                provider=result.provider,
                model=result.model,
                prompt_hash=str(hash(prompt)),
                response_hash=str(hash(result.response)),
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.total_tokens,
                cost_usd=result.cost_usd,
                latency_ms=result.latency_ms,
                success=result.success,
                error=result.error,
                fallback_used=result.provider != router.registry.get_default().provider if router.registry.get_default() else False,
                derived_artifacts=[artifact.id],
            ))

        logger.info(
            f"Specification generated: {len(artifact.functional_requirements)} FR, "
            f"{len(artifact.non_functional_requirements)} NFR, "
            f"{len(artifact.acceptance_criteria)} AC, "
            f"model={result.model}, tokens={result.total_tokens}, cost=${result.cost_usd:.4f}"
        )

        return artifact
