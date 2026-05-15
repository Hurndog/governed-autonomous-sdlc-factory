"""Real Governance Generation Engine — AI-driven governance analysis.

Generates governance artifacts dynamically from specifications and architecture.
Not just static policies — real AI-driven governance findings.
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

logger = get_logger("governance_engine")


@dataclass
class GovernanceArtifact:
    """Generated governance artifact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    project_id: str = ""
    spec_id: str = ""
    arch_id: str = ""
    runtime_governance_concerns: list = field(default_factory=list)
    architecture_governance_findings: list = field(default_factory=list)
    deployment_governance_findings: list = field(default_factory=list)
    security_sensitive_findings: list = field(default_factory=list)
    evidence_requirements: list = field(default_factory=list)
    audit_requirements: list = field(default_factory=list)
    compliance_gaps: list = field(default_factory=list)
    risk_assessment: dict = field(default_factory=dict)
    model_used: str = ""
    provider_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GovernanceEngine:
    """AI-driven governance generation."""

    GOVERNANCE_PROMPT = """You are a governance, risk, and compliance (GRC) specialist. Analyze the following software specification and architecture for governance concerns.

SPECIFICATION:
{specification}

ARCHITECTURE:
{architecture}

INSTRUCTIONS:
Produce a comprehensive governance analysis in the following JSON format:

{{
  "runtime_governance_concerns": [
    {{
      "id": "RGC-001",
      "concern": "Runtime governance concern description",
      "category": "data_handling|access_control|audit_logging|error_handling|rate_limiting|data_retention",
      "severity": "critical|high|medium|low",
      "recommendation": "Specific recommendation",
      "evidence_required": "What evidence must be collected"
    }}
  ],
  "architecture_governance_findings": [
    {{
      "id": "AGF-001",
      "finding": "Architecture governance finding",
      "component": "Affected component",
      "concern": "security|privacy|compliance|reliability|observability",
      "severity": "critical|high|medium|low",
      "recommendation": "Architecture recommendation"
    }}
  ],
  "deployment_governance_findings": [
    {{
      "id": "DGF-001",
      "finding": "Deployment governance finding",
      "environment": "production|staging|all",
      "concern": "secrets_management|network_security|access_control|monitoring|backup",
      "severity": "critical|high|medium|low",
      "recommendation": "Deployment recommendation"
    }}
  ],
  "security_sensitive_findings": [
    {{
      "id": "SSF-001",
      "finding": "Security-sensitive finding",
      "attack_vector": "Potential attack vector",
      "impact": "high|medium|low",
      "mitigation": "Specific mitigation",
      "testing_requirement": "How to verify the mitigation"
    }}
  ],
  "evidence_requirements": [
    {{
      "id": "EVR-001",
      "requirement": "Evidence that must be collected",
      "source": "runtime|build|test|deployment|audit",
      "frequency": "continuous|on_change|on_release|periodic",
      "retention": "How long to retain"
    }}
  ],
  "audit_requirements": [
    {{
      "id": "AUD-001",
      "requirement": "Audit requirement description",
      "scope": "What must be auditable",
      "method": "log_review|automated_check|manual_review|penetration_test",
      "frequency": "continuous|daily|weekly|monthly|quarterly"
    }}
  ],
  "compliance_gaps": [
    {{
      "id": "CG-001",
      "framework": "GDPR|HIPAA|SOC2|PCI-DSS|ISO27001|custom",
      "gap": "Specific compliance gap",
      "severity": "critical|high|medium|low",
      "remediation": "How to close the gap"
    }}
  ],
  "risk_assessment": {{
    "overall_risk": "high|medium|low",
    "technical_risk": "high|medium|low",
    "security_risk": "high|medium|low",
    "compliance_risk": "high|medium|low",
    "operational_risk": "high|medium|low",
    "top_risks": [
      {{
        "risk": "Top risk description",
        "likelihood": "high|medium|low",
        "impact": "high|medium|low",
        "mitigation": "Primary mitigation strategy"
      }}
    ]
  }}
}}

RULES:
1. Be specific and actionable, not generic
2. Generate at least 3 runtime governance concerns
3. Generate at least 2 architecture governance findings
4. Generate at least 2 security-sensitive findings
5. Generate at least 2 evidence requirements
6. Generate at least 2 audit requirements
7. Assess compliance gaps for relevant frameworks
8. Output ONLY valid JSON, no markdown, no explanations

OUTPUT:"""

    def __init__(self, router: Optional[ModelRouter] = None):
        self._router = router
        self._tracer: Optional[InferenceTracer] = None

    async def _get_router(self) -> ModelRouter:
        if self._router is None:
            self._router = await get_router()
        return self._router

    async def generate_governance(
        self,
        spec: SpecificationArtifact,
        arch: ArchitectureArtifact,
        run_id: str = "",
        tracer: Optional[InferenceTracer] = None,
    ) -> GovernanceArtifact:
        """Generate governance analysis from specification and architecture."""
        self._tracer = tracer
        router = await self._get_router()

        prompt = self.GOVERNANCE_PROMPT.format(
            specification=spec.intent[:500],
            architecture=arch.architecture_proposal[:500],
        )

        result = await router.complete(
            messages=[
                {"role": "system", "content": "You are a GRC specialist. Output ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=8192,
            run_id=run_id,
            phase="governance_generation",
        )

        if not result.success:
            logger.error(f"Governance generation failed: {result.error}")
            return GovernanceArtifact(
                run_id=run_id,
                project_id=spec.project_id,
                spec_id=spec.id,
                arch_id=arch.id,
            )

        try:
            gov_data = json.loads(result.response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', result.response, re.DOTALL)
            gov_data = json.loads(json_match.group()) if json_match else {}

        artifact = GovernanceArtifact(
            run_id=run_id,
            project_id=spec.project_id,
            spec_id=spec.id,
            arch_id=arch.id,
            runtime_governance_concerns=gov_data.get("runtime_governance_concerns", []),
            architecture_governance_findings=gov_data.get("architecture_governance_findings", []),
            deployment_governance_findings=gov_data.get("deployment_governance_findings", []),
            security_sensitive_findings=gov_data.get("security_sensitive_findings", []),
            evidence_requirements=gov_data.get("evidence_requirements", []),
            audit_requirements=gov_data.get("audit_requirements", []),
            compliance_gaps=gov_data.get("compliance_gaps", []),
            risk_assessment=gov_data.get("risk_assessment", {}),
            model_used=result.model,
            provider_used=result.provider,
            tokens_used=result.total_tokens,
            cost_usd=result.cost_usd,
        )

        if self._tracer:
            self._tracer.record(InferenceTraceRecord(
                run_id=run_id,
                phase="governance_generation",
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
            f"Governance generated: {len(artifact.runtime_governance_concerns)} runtime concerns, "
            f"{len(artifact.security_sensitive_findings)} security findings, "
            f"{len(artifact.compliance_gaps)} compliance gaps, "
            f"model={result.model}, tokens={result.total_tokens}"
        )

        return artifact
