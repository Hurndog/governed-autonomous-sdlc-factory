"""Cognitive Execution API endpoints.

These endpoints power the REAL AI-driven SDLC pipeline:
- Specification generation from user intent
- Architecture generation from specifications
- Test plan generation from spec + architecture
- Governance analysis from spec + architecture
- Full autonomous pipeline execution
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_no_autoflush
from src.core.auth import get_current_auth as get_current_user
from src.core.logging import get_logger
from src.engines.model_router import get_router
from src.engines.specification_engine import SpecificationEngine
from src.engines.architecture_engine import ArchitectureEngine
from src.engines.test_engine import TestPlanEngine
from src.engines.governance_engine import GovernanceEngine
from src.engines.inference_trace import InferenceTracer

logger = get_logger("api.cognitive")

router = APIRouter(prefix="/cognitive", tags=["cognitive"])


@router.post("/generate-specification/{run_id}")
async def generate_specification(
    run_id: str,
    intent: str = Query(..., description="User intent / project description"),
    project_id: str = Query(default=""),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Generate a REAL specification from user intent using LLM inference."""
    try:
        router = await get_router()
        engine = SpecificationEngine(router=router)
        tracer = InferenceTracer(run_id=run_id)

        spec = await engine.generate_specification(
            intent=intent,
            run_id=run_id,
            project_id=project_id,
            tracer=tracer,
        )

        return {
            "status": "generated",
            "spec_id": spec.id,
            "functional_requirements_count": len(spec.functional_requirements),
            "non_functional_requirements_count": len(spec.non_functional_requirements),
            "acceptance_criteria_count": len(spec.acceptance_criteria),
            "governance_sensitive_areas_count": len(spec.governance_sensitive_areas),
            "model_used": spec.model_used,
            "provider_used": spec.provider_used,
            "tokens_used": spec.tokens_used,
            "cost_usd": spec.cost_usd,
            "inference_summary": tracer.get_summary(),
        }
    except Exception as e:
        logger.error(f"Specification generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Specification generation failed: {str(e)}")


@router.post("/generate-architecture/{run_id}")
async def generate_architecture(
    run_id: str,
    spec_id: str = Query(..., description="Specification ID to generate architecture from"),
    project_id: str = Query(default=""),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Generate a REAL architecture from specification using LLM inference."""
    try:
        # Fetch specification from DB
        from src.models import SpecificationVersion
        spec_record = await db.get(SpecificationVersion, spec_id)
        if not spec_record:
            raise HTTPException(status_code=404, detail="Specification not found")

        # Reconstruct spec artifact
        from src.engines.specification_engine import SpecificationArtifact
        spec = SpecificationArtifact(
            id=spec_record.id,
            run_id=run_id,
            project_id=project_id,
            intent=spec_record.functional_spec or "",
        )

        model_router = await get_router()
        engine = ArchitectureEngine(router=model_router)
        tracer = InferenceTracer(run_id=run_id)

        arch = await engine.generate_architecture(
            spec=spec,
            run_id=run_id,
            tracer=tracer,
        )

        return {
            "status": "generated",
            "arch_id": arch.id,
            "components_count": len(arch.component_breakdown),
            "adrs_count": len(arch.adrs),
            "diagrams_count": len(arch.mermaid_diagrams),
            "governance_findings_count": len(arch.governance_findings),
            "model_used": arch.model_used,
            "provider_used": arch.provider_used,
            "tokens_used": arch.tokens_used,
            "cost_usd": arch.cost_usd,
            "inference_summary": tracer.get_summary(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Architecture generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Architecture generation failed: {str(e)}")


@router.post("/generate-test-plan/{run_id}")
async def generate_test_plan(
    run_id: str,
    spec_id: str = Query(...),
    arch_id: str = Query(...),
    project_id: str = Query(default=""),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Generate a REAL test plan from spec + architecture using LLM inference."""
    try:
        from src.models import SpecificationVersion, ArchitectureVersion
        from src.engines.specification_engine import SpecificationArtifact
        from src.engines.architecture_engine import ArchitectureArtifact

        spec_record = await db.get(SpecificationVersion, spec_id)
        arch_record = await db.get(ArchitectureVersion, arch_id)
        if not spec_record or not arch_record:
            raise HTTPException(status_code=404, detail="Specification or architecture not found")

        spec = SpecificationArtifact(id=spec_record.id, intent=spec_record.functional_spec or "")
        arch = ArchitectureArtifact(id=arch_record.id, architecture_proposal=arch_record.architecture_md or "")

        model_router = await get_router()
        engine = TestPlanEngine(router=model_router)
        tracer = InferenceTracer(run_id=run_id)

        test_plan = await engine.generate_test_plan(spec=spec, arch=arch, run_id=run_id, tracer=tracer)

        return {
            "status": "generated",
            "test_plan_id": test_plan.id,
            "test_cases_count": len(test_plan.test_cases),
            "edge_cases_count": len(test_plan.edge_cases),
            "governance_tests_count": len(test_plan.governance_tests),
            "model_used": test_plan.model_used,
            "provider_used": test_plan.provider_used,
            "tokens_used": test_plan.tokens_used,
            "cost_usd": test_plan.cost_usd,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test plan generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Test plan generation failed: {str(e)}")


@router.post("/generate-governance/{run_id}")
async def generate_governance(
    run_id: str,
    spec_id: str = Query(...),
    arch_id: str = Query(...),
    project_id: str = Query(default=""),
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    """Generate REAL governance analysis from spec + architecture using LLM inference."""
    try:
        from src.models import SpecificationVersion, ArchitectureVersion
        from src.engines.specification_engine import SpecificationArtifact
        from src.engines.architecture_engine import ArchitectureArtifact

        spec_record = await db.get(SpecificationVersion, spec_id)
        arch_record = await db.get(ArchitectureVersion, arch_id)
        if not spec_record or not arch_record:
            raise HTTPException(status_code=404, detail="Specification or architecture not found")

        spec = SpecificationArtifact(id=spec_record.id, intent=spec_record.functional_spec or "")
        arch = ArchitectureArtifact(id=arch_record.id, architecture_proposal=arch_record.architecture_md or "")

        model_router = await get_router()
        engine = GovernanceEngine(router=model_router)
        tracer = InferenceTracer(run_id=run_id)

        governance = await engine.generate_governance(spec=spec, arch=arch, run_id=run_id, tracer=tracer)

        return {
            "status": "generated",
            "governance_id": governance.id,
            "runtime_concerns_count": len(governance.runtime_governance_concerns),
            "security_findings_count": len(governance.security_sensitive_findings),
            "compliance_gaps_count": len(governance.compliance_gaps),
            "evidence_requirements_count": len(governance.evidence_requirements),
            "audit_requirements_count": len(governance.audit_requirements),
            "model_used": governance.model_used,
            "provider_used": governance.provider_used,
            "tokens_used": governance.tokens_used,
            "cost_usd": governance.cost_usd,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Governance generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Governance generation failed: {str(e)}")


@router.get("/model-status")
async def get_model_status(
    user=Depends(get_current_user),
):
    """Get model router status and available models."""
    try:
        r = await get_router()
        return r.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
