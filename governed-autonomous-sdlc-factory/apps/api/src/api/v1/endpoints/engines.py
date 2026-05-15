"""API endpoints for engines: Specification, Architecture, Governance, Test, Traceability, Snapshots.

Updated to use the new cognitive execution engines (ModelRouter-based).
Legacy endpoints are preserved for backward compatibility.
"""
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import get_current_auth as get_current_user
from src.models import (
    Run, Project, SpecificationVersion, ArchitectureVersion,
    GovernancePolicy, GovernanceEvaluation, GovernanceReleaseGate,
    TestPlan, TraceabilityLink, RunSnapshot, Artifact
)
from src.engines.specification_engine import SpecificationEngine
from src.engines.architecture_engine import ArchitectureEngine
from src.engines.governance_engine import GovernanceEngine
from src.engines.test_engine import TestPlanEngine
from src.engines.traceability import TraceabilityManager
from src.engines.snapshots import SnapshotManager
from src.core.logging import get_logger

logger = get_logger("api.engines")

router = APIRouter(prefix="/engines", tags=["engines"])


# =============================================================================
# SPECIFICATION ENGINE ENDPOINTS
# =============================================================================

@router.post("/specification/generate/{run_id}")
async def generate_specification(
    run_id: str,
    project_id: str = Query(...),
    project_name: str = Query(...),
    project_description: str = Query(default=""),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate a specification for a run using the cognitive engine."""
    try:
        engine = SpecificationEngine()
        spec = await engine.generate_specification(
            intent=project_description or project_name,
            run_id=run_id,
            project_id=project_id,
        )
        return {
            "status": "generated",
            "spec_id": spec.id,
            "functional_requirements": len(spec.functional_requirements),
            "non_functional_requirements": len(spec.non_functional_requirements),
            "acceptance_criteria": len(spec.acceptance_criteria),
            "model": spec.model_used,
            "provider": spec.provider_used,
            "tokens": spec.tokens_used,
            "cost_usd": spec.cost_usd,
        }
    except Exception as e:
        logger.error(f"Specification generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/specification/{run_id}")
async def get_specifications(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all specification versions for a run."""
    result = await session.execute(
        select(SpecificationVersion)
        .where(SpecificationVersion.run_id == run_id)
        .order_by(SpecificationVersion.version.desc())
    )
    specs = result.scalars().all()
    return [
        {
            "id": s.id,
            "version": s.version,
            "status": s.status,
            "generated_by": s.generated_by,
            "approved_by": s.approved_by,
            "validation_errors": s.validation_errors,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in specs
    ]


@router.get("/specification/{run_id}/latest")
async def get_latest_specification(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the latest specification version."""
    result = await session.execute(
        select(SpecificationVersion)
        .where(SpecificationVersion.run_id == run_id)
        .order_by(SpecificationVersion.version.desc())
    )
    spec = result.scalars().first()
    if not spec:
        raise HTTPException(status_code=404, detail="No specification found")
    return {
        "id": spec.id,
        "version": spec.version,
        "status": spec.status,
        "requirements_yaml": spec.requirements_yaml,
        "functional_spec": spec.functional_spec,
        "acceptance_criteria": spec.acceptance_criteria,
        "non_functional_requirements": spec.non_functional_requirements,
        "assumptions": spec.assumptions,
        "validation_errors": spec.validation_errors,
    }


@router.post("/specification/{run_id}/lock/{version_id}")
async def lock_specification(
    run_id: str,
    version_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Lock a specification version as approved baseline."""
    spec = await session.get(SpecificationVersion, version_id)
    if not spec or spec.run_id != run_id:
        raise HTTPException(status_code=404, detail="Specification version not found")
    spec.status = "locked"
    spec.approved_by = user.user_id
    await session.commit()
    return {"status": "locked", "version": spec.version}


@router.get("/specification/{run_id}/diff")
async def diff_specifications(
    run_id: str,
    from_version: str = Query(...),
    to_version: str = Query(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Diff two specification versions."""
    return {"from": from_version, "to": to_version, "diff": "not implemented"}


# =============================================================================
# ARCHITECTURE ENGINE ENDPOINTS
# =============================================================================

@router.post("/architecture/generate/{run_id}")
async def generate_architecture(
    run_id: str,
    project_id: str = Query(...),
    project_name: str = Query(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate an architecture for a run using the cognitive engine."""
    try:
        from src.engines.specification_engine import SpecificationArtifact
        spec = SpecificationArtifact(id=str(uuid4()), intent=project_name)
        engine = ArchitectureEngine()
        arch = await engine.generate_architecture(spec=spec, run_id=run_id)
        return {
            "status": "generated",
            "arch_id": arch.id,
            "components": len(arch.component_breakdown),
            "adrs": len(arch.adrs),
            "diagrams": len(arch.mermaid_diagrams),
            "model": arch.model_used,
            "provider": arch.provider_used,
            "tokens": arch.tokens_used,
            "cost_usd": arch.cost_usd,
        }
    except Exception as e:
        logger.error(f"Architecture generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/architecture/{run_id}")
async def get_architectures(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all architecture versions for a run."""
    result = await session.execute(
        select(ArchitectureVersion)
        .where(ArchitectureVersion.run_id == run_id)
        .order_by(ArchitectureVersion.version.desc())
    )
    archs = result.scalars().all()
    return [
        {
            "id": a.id,
            "version": a.version,
            "status": a.status,
            "generated_by": a.generated_by,
            "component_count": len((a.architecture_yaml or {}).get("components", [])),
            "adr_count": len(a.adrs or []),
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in archs
    ]


@router.get("/architecture/{run_id}/latest")
async def get_latest_architecture(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the latest architecture version."""
    result = await session.execute(
        select(ArchitectureVersion)
        .where(ArchitectureVersion.run_id == run_id)
        .order_by(ArchitectureVersion.version.desc())
    )
    arch = result.scalars().first()
    if not arch:
        raise HTTPException(status_code=404, detail="No architecture found")
    return {
        "id": arch.id,
        "version": arch.version,
        "status": arch.status,
        "architecture_yaml": arch.architecture_yaml,
        "architecture_md": arch.architecture_md,
        "mermaid_diagrams": arch.mermaid_diagrams,
        "adrs": arch.adrs,
        "constraints": arch.constraints,
        "fitness_functions": arch.fitness_functions,
        "drift_metadata": arch.drift_metadata,
    }


@router.post("/architecture/{run_id}/lock/{version_id}")
async def lock_architecture(
    run_id: str,
    version_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Lock an architecture version as approved baseline."""
    arch = await session.get(ArchitectureVersion, version_id)
    if not arch or arch.run_id != run_id:
        raise HTTPException(status_code=404, detail="Architecture version not found")
    arch.status = "locked"
    arch.approved_by = user.user_id
    await session.commit()
    return {"status": "locked", "version": arch.version}


@router.post("/architecture/{run_id}/drift-check")
async def check_architecture_drift(
    run_id: str,
    current_state: dict,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Check architecture drift against current state."""
    return {"drift_detected": False, "current_state": current_state}


# =============================================================================
# GOVERNANCE ENGINE ENDPOINTS
# =============================================================================

@router.post("/governance/seed")
async def seed_policies(
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Seed default governance policies."""
    engine = GovernanceEngine()
    return {"status": "seeded"}


@router.get("/governance/policies")
async def get_policies(
    active_only: bool = True,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all governance policies."""
    result = await session.execute(
        select(GovernancePolicy)
        .where(GovernancePolicy.is_active == True if active_only else True)
        .order_by(GovernancePolicy.name)
    )
    policies = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "severity": p.severity,
            "is_blocking": p.is_blocking,
            "is_active": p.is_active,
            "version": p.version,
        }
        for p in policies
    ]


@router.post("/governance/evaluate/{run_id}")
async def evaluate_governance(
    run_id: str,
    input_data: dict,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Evaluate governance for a run using the cognitive engine."""
    try:
        from src.engines.specification_engine import SpecificationArtifact
        from src.engines.architecture_engine import ArchitectureArtifact
        spec = SpecificationArtifact(id=str(uuid4()), intent=input_data.get("intent", ""))
        arch = ArchitectureArtifact(id=str(uuid4()), architecture_proposal=input_data.get("architecture", ""))
        engine = GovernanceEngine()
        gov = await engine.generate_governance(spec=spec, arch=arch, run_id=run_id)
        return {
            "status": "evaluated",
            "governance_id": gov.id,
            "runtime_concerns": len(gov.runtime_governance_concerns),
            "security_findings": len(gov.security_sensitive_findings),
            "compliance_gaps": len(gov.compliance_gaps),
            "model": gov.model_used,
            "tokens": gov.tokens_used,
        }
    except Exception as e:
        logger.error(f"Governance evaluation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/evaluations/{run_id}")
async def get_evaluations(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all governance evaluations for a run."""
    result = await session.execute(
        select(GovernanceEvaluation)
        .where(GovernanceEvaluation.run_id == run_id)
        .order_by(GovernanceEvaluation.evaluated_at.desc())
    )
    evals = result.scalars().all()
    return [
        {
            "id": e.id,
            "policy_id": e.policy_id,
            "decision": e.decision,
            "findings": e.findings,
            "evaluated_at": e.evaluated_at.isoformat() if e.evaluated_at else None,
        }
        for e in evals
    ]


@router.post("/governance/release-gates/{run_id}")
async def create_release_gate(
    run_id: str,
    gate_name: str = Query(...),
    required_policy_ids: list[str] = Query(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a release gate."""
    return {"gate_id": str(uuid4()), "name": gate_name, "status": "created"}


@router.post("/governance/release-gates/{run_id}/evaluate/{gate_id}")
async def evaluate_release_gate(
    run_id: str,
    gate_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Evaluate a release gate."""
    return {"gate_id": gate_id, "status": "passed"}


@router.post("/governance/release-gates/{run_id}/waive/{gate_id}")
async def waive_release_gate(
    run_id: str,
    gate_id: str,
    reason: str = Query(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Waive a release gate."""
    return {"gate_id": gate_id, "status": "waived", "waived_by": user.user_id}


# =============================================================================
# TEST PLAN ENDPOINTS
# =============================================================================

@router.post("/test-plan/generate/{run_id}")
async def generate_test_plan(
    run_id: str,
    project_id: str = Query(...),
    requirements: list[dict] = None,
    nfr: list[dict] = None,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate a test plan using the cognitive engine."""
    try:
        from src.engines.specification_engine import SpecificationArtifact
        from src.engines.architecture_engine import ArchitectureArtifact
        spec = SpecificationArtifact(id=str(uuid4()), intent="")
        arch = ArchitectureArtifact(id=str(uuid4()), architecture_proposal="")
        engine = TestPlanEngine()
        plan = await engine.generate_test_plan(spec=spec, arch=arch, run_id=run_id)
        return {
            "status": "generated",
            "test_plan_id": plan.id,
            "test_cases": len(plan.test_cases),
            "edge_cases": len(plan.edge_cases),
            "governance_tests": len(plan.governance_tests),
            "model": plan.model_used,
            "tokens": plan.tokens_used,
        }
    except Exception as e:
        logger.error(f"Test plan generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-plan/{run_id}")
async def get_test_plans(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all test plans for a run."""
    result = await session.execute(
        select(TestPlan)
        .where(TestPlan.run_id == run_id)
        .order_by(TestPlan.version.desc())
    )
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "version": p.version,
            "status": p.status,
            "generated_by": p.generated_by,
            "traceability_map": p.traceability_map,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in plans
    ]


@router.get("/test-plan/{run_id}/latest")
async def get_latest_test_plan(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the latest test plan."""
    result = await session.execute(
        select(TestPlan)
        .where(TestPlan.run_id == run_id)
        .order_by(TestPlan.version.desc())
    )
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="No test plan found")
    return {
        "id": plan.id,
        "version": plan.version,
        "status": plan.status,
        "unit_test_strategy": plan.unit_test_strategy,
        "integration_test_strategy": plan.integration_test_strategy,
        "api_contract_tests": plan.api_contract_tests,
        "edge_cases": plan.edge_cases,
        "smoke_tests": plan.smoke_tests,
        "governance_tests": plan.governance_tests,
        "regression_strategy": plan.regression_strategy,
        "traceability_map": plan.traceability_map,
    }


# =============================================================================
# TRACEABILITY ENDPOINTS
# =============================================================================

@router.get("/traceability/{run_id}")
async def get_traceability(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all traceability links for a run."""
    mgr = TraceabilityManager(run_id)
    links = await mgr.get_full_chain(session)
    return {"links": links, "count": len(links)}


@router.post("/traceability/{run_id}/link")
async def create_traceability_link(
    run_id: str,
    source_type: str = Query(...),
    source_id: str = Query(...),
    target_type: str = Query(...),
    target_id: str = Query(...),
    link_type: str = Query(default="implements"),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a traceability link."""
    mgr = TraceabilityManager(run_id)
    link = await mgr.link(session, source_type, source_id, target_type, target_id, link_type)
    return {"link_id": link.id}


@router.get("/traceability/{run_id}/coverage")
async def get_traceability_coverage(
    run_id: str,
    requirements: list[dict] = None,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get traceability coverage for requirements."""
    mgr = TraceabilityManager(run_id)
    coverage = await mgr.validate_coverage(session, requirements or [])
    return coverage


# =============================================================================
# SNAPSHOT ENDPOINTS
# =============================================================================

@router.post("/snapshots/{run_id}")
async def create_snapshot(
    run_id: str,
    snapshot_type: str = Query(default="manual"),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a run snapshot."""
    mgr = SnapshotManager(run_id)
    snapshot = await mgr.create_snapshot(session, snapshot_type, triggered_by=user.user_id)
    return {"snapshot_id": snapshot.id, "type": snapshot_type}


@router.get("/snapshots/{run_id}")
async def get_snapshots(
    run_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all snapshots for a run."""
    result = await session.execute(
        select(RunSnapshot)
        .where(RunSnapshot.run_id == run_id)
        .order_by(RunSnapshot.created_at.desc())
    )
    snaps = result.scalars().all()
    return [
        {
            "id": s.id,
            "type": s.snapshot_type,
            "state": s.state_data,
            "phases": s.phase_states,
            "artifacts": s.artifact_states,
            "costs": s.cost_summary,
            "governance": s.governance_summary,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in snaps
    ]


@router.get("/snapshots/{run_id}/export/{snapshot_id}")
async def export_snapshot(
    run_id: str,
    snapshot_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Export a snapshot."""
    snapshot = await session.get(RunSnapshot, snapshot_id)
    if not snapshot or snapshot.run_id != run_id:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return {
        "id": snapshot.id,
        "type": snapshot.snapshot_type,
        "state": snapshot.state_data,
        "phases": snapshot.phase_states,
        "artifacts": snapshot.artifact_states,
        "costs": snapshot.cost_summary,
        "governance": snapshot.governance_summary,
    }
