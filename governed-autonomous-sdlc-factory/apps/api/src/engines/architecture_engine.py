"""Real Architecture Generation Engine — AI-driven architecture design.

Uses ModelRouter to generate architecture proposals from specifications.
Produces structured architecture documents with ADRs, component breakdowns,
integration points, and Mermaid diagrams.
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

logger = get_logger("architecture_engine")


@dataclass
class ArchitectureArtifact:
    """Generated architecture artifact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    project_id: str = ""
    spec_id: str = ""
    architecture_proposal: str = ""
    component_breakdown: list = field(default_factory=list)
    integration_points: list = field(default_factory=list)
    deployment_topology: dict = field(default_factory=dict)
    adrs: list = field(default_factory=list)
    constraints: list = field(default_factory=list)
    tradeoffs: list = field(default_factory=list)
    architecture_rationale: str = ""
    mermaid_diagrams: list = field(default_factory=list)
    governance_findings: list = field(default_factory=list)
    raw_response: str = ""
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ArchitectureEngine:
    """AI-driven architecture generation engine."""

    ARCHITECTURE_PROMPT = """You are a senior software architect. Based on the following specification, design a comprehensive software architecture.

SPECIFICATION:
{specification}

INSTRUCTIONS:
Design a complete architecture and output in the following JSON format:

{{
  "architecture_proposal": "High-level architecture description (2-3 paragraphs)",
  "component_breakdown": [
    {{
      "name": "Component name",
      "type": "service|library|database|queue|cache|gateway|ui",
      "responsibility": "What this component does",
      "technology": "Suggested technology/framework",
      "interfaces": ["Interface descriptions"]
    }}
  ],
  "integration_points": [
    {{
      "source": "Source component",
      "target": "Target component",
      "protocol": "REST|gRPC|GraphQL|MessageQueue|EventStream|Database",
      "description": "What data flows and why",
      "criticality": "critical|important|optional"
    }}
  ],
  "deployment_topology": {{
    "pattern": "monolith|microservices|serverless|hybrid",
    "environments": ["development", "staging", "production"],
    "scaling_strategy": "How the system scales",
    "high_availability": "HA approach"
  }},
  "adrs": [
    {{
      "id": "ADR-001",
      "title": "Architecture Decision Record title",
      "context": "Context for the decision",
      "decision": "The decision made",
      "consequences": "Positive and negative consequences",
      "alternatives_considered": ["Alternative 1", "Alternative 2"]
    }}
  ],
  "constraints": [
    "Technical constraint shaping the architecture"
  ],
  "tradeoffs": [
    {{
      "tradeoff": "What is being traded off",
      "chosen": "What was chosen",
      "sacrificed": "What was sacrificed",
      "rationale": "Why this tradeoff was made"
    }}
  ],
  "architecture_rationale": "Overall rationale for the architecture (1-2 paragraphs)",
  "mermaid_diagrams": [
    {{
      "name": "diagram_name",
      "type": "flowchart|sequence|class|er|state",
      "content": "Valid Mermaid diagram syntax"
    }}
  ],
  "governance_findings": [
    {{
      "area": "Governance area affected",
      "finding": "Specific finding",
      "recommendation": "Architecture recommendation",
      "severity": "critical|high|medium|low"
    }}
  ]
}}

RULES:
1. Design for the specific requirements, not generic
2. Include at least 4 components
3. Include at least 3 integration points
4. Include at least 2 ADRs
5. Include at least 1 Mermaid diagram
6. Address governance concerns from the specification
7. Output ONLY valid JSON, no markdown, no explanations

OUTPUT:"""

    def __init__(self, router: Optional[ModelRouter] = None):
        self._router = router
        self._tracer: Optional[InferenceTracer] = None

    async def _get_router(self) -> ModelRouter:
        if self._router is None:
            self._router = await get_router()
        return self._router

    async def generate_architecture(
        self,
        spec: SpecificationArtifact,
        run_id: str = "",
        tracer: Optional[InferenceTracer] = None,
    ) -> ArchitectureArtifact:
        """Generate architecture from a specification artifact."""
        self._tracer = tracer
        router = await self._get_router()

        # Build specification summary for the prompt
        spec_summary = self._format_spec_summary(spec)
        prompt = self.ARCHITECTURE_PROMPT.format(specification=spec_summary)

        result = await router.complete(
            messages=[
                {"role": "system", "content": "You are a senior software architect. Output ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=8192,
            run_id=run_id,
            phase="architecture_generation",
        )

        if not result.success:
            logger.error(f"Architecture generation failed: {result.error}")
            return ArchitectureArtifact(
                run_id=run_id,
                project_id=spec.project_id,
                spec_id=spec.id,
                architecture_proposal=f"ERROR: {result.error}",
            )

        try:
            arch_data = json.loads(result.response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', result.response, re.DOTALL)
            arch_data = json.loads(json_match.group()) if json_match else {}

        artifact = ArchitectureArtifact(
            run_id=run_id,
            project_id=spec.project_id,
            spec_id=spec.id,
            architecture_proposal=arch_data.get("architecture_proposal", ""),
            component_breakdown=arch_data.get("component_breakdown", []),
            integration_points=arch_data.get("integration_points", []),
            deployment_topology=arch_data.get("deployment_topology", {}),
            adrs=arch_data.get("adrs", []),
            constraints=arch_data.get("constraints", []),
            tradeoffs=arch_data.get("tradeoffs", []),
            architecture_rationale=arch_data.get("architecture_rationale", ""),
            mermaid_diagrams=arch_data.get("mermaid_diagrams", []),
            governance_findings=arch_data.get("governance_findings", []),
            raw_response=result.response,
            model_used=result.model,
            provider_used=result.provider,
            tokens_used=result.total_tokens,
            cost_usd=result.cost_usd,
        )

        if self._tracer:
            self._tracer.record(InferenceTraceRecord(
                run_id=run_id,
                phase="architecture_generation",
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
            f"Architecture generated: {len(artifact.component_breakdown)} components, "
            f"{len(artifact.adrs)} ADRs, "
            f"{len(artifact.mermaid_diagrams)} diagrams, "
            f"model={result.model}, tokens={result.total_tokens}"
        )

        return artifact

    def _format_spec_summary(self, spec: SpecificationArtifact) -> str:
        """Format specification as a readable summary for the prompt."""
        lines = [f"Intent: {spec.intent}", ""]

        if spec.functional_requirements:
            lines.append("Functional Requirements:")
            for fr in spec.functional_requirements:
                lines.append(f"  - [{fr.get('id', '?')}] {fr.get('description', '')} (priority: {fr.get('priority', '?')})")
            lines.append("")

        if spec.non_functional_requirements:
            lines.append("Non-Functional Requirements:")
            for nfr in spec.non_functional_requirements:
                lines.append(f"  - [{nfr.get('id', '?')}] {nfr.get('description', '')} (category: {nfr.get('category', '?')})")
            lines.append("")

        if spec.governance_sensitive_areas:
            lines.append("Governance-Sensitive Areas:")
            for ga in spec.governance_sensitive_areas:
                lines.append(f"  - {ga.get('area', '')}: {ga.get('concern', '')} (severity: {ga.get('severity', '?')})")
            lines.append("")

        if spec.technical_constraints:
            lines.append("Technical Constraints:")
            for tc in spec.technical_constraints:
                lines.append(f"  - {tc}")
            lines.append("")

        return "\n".join(lines)
