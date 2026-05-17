"""API endpoints for Semantic Coverage and Test Alignment."""

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
    NegativeTestRequirement, RuntimeEvidenceBinding, SemanticCoverageReport,
    SemanticCoverageWaiver,
)
from src.engines.semantic_coverage_engine import SemanticCoverageEngine

router = APIRouter(prefix="/semantic-coverage", tags=["semantic-coverage"])

# Thread pool for sync DB operations
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="semantic-coverage")


def _get_sync_engine():
    """Create a new SemanticCoverageEngine with a sync session."""
    from src.core.database import SyncSessionLocal
    db = SyncSessionLocal()
    return SemanticCoverageEngine(db), db


def _get_run_sync(run_id: str) -> dict:
    """Synchronously check if a run exists. Returns dict with run or error."""
    from src.models import Run as PipelineRun
    engine, db = _get_sync_engine()
    try:
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if not run:
            return {"error": "not_found"}
        return {"run": run}
    finally:
        db.close()


def _get_summary_sync(run_id: str) -> dict:
    """Synchronously get semantic coverage summary."""
    from src.models import Run as PipelineRun
    engine, db = _get_sync_engine()
    try:
        report = db.query(SemanticCoverageReport).filter(
            SemanticCoverageReport.run_id == UUID(run_id)
        ).first()

        if not report:
            run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if not run:
                return {"error": "not_found"}
            return {
                "run_id": run_id,
                "status": "pre_semantic_coverage",
                "message": "Semantic coverage has not been evaluated for this run",
            }

        return {
            "run_id": run_id,
            "overall_semantic_coverage_score": report.overall_semantic_coverage_score,
            "obligation_coverage_score": report.obligation_coverage_score,
            "semantic_alignment_score": report.semantic_alignment_score,
            "mutation_score": report.mutation_score,
            "negative_coverage_score": report.negative_coverage_score,
            "runtime_evidence_score": report.runtime_evidence_score,
            "verifier_confidence_score": report.verifier_confidence_score,
            "critical_requirements_passed": report.critical_requirements_passed,
            "release_gate_status": report.release_gate_status,
            "report": report.report_json,
        }
    finally:
        db.close()


def _get_requirements_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        reqs = db.query(RequirementNormalization).filter(
            RequirementNormalization.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(reqs),
            "requirements": [
                {
                    "requirement_id": r.requirement_id,
                    "normalized_statement": r.normalized_statement,
                    "actor": r.actor,
                    "action": r.action,
                    "object": r.object,
                    "criticality": r.criticality,
                    "security_relevance": r.security_relevance,
                    "governance_relevance": r.governance_relevance,
                    "ambiguity_score": r.ambiguity_score,
                    "testability_score": r.testability_score,
                }
                for r in reqs
            ],
        }
    finally:
        db.close()


def _get_acceptance_criteria_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        acs = db.query(AcceptanceCriteriaContract).filter(
            AcceptanceCriteriaContract.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(acs),
            "acceptance_criteria": [
                {
                    "acceptance_criterion_id": ac.acceptance_criterion_id,
                    "requirement_id": ac.requirement_id,
                    "given": ac.given_text,
                    "when": ac.when_text,
                    "then": ac.then_text,
                    "negative_case_required": ac.negative_case_required,
                    "security_case_required": ac.security_case_required,
                    "governance_case_required": ac.governance_case_required,
                }
                for ac in acs
            ],
        }
    finally:
        db.close()


def _get_test_obligations_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        obligations = db.query(TestObligation).filter(
            TestObligation.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(obligations),
            "obligations": [
                {
                    "obligation_id": o.obligation_id,
                    "requirement_id": o.requirement_id,
                    "obligation_type": o.obligation_type,
                    "proof_statement": o.proof_statement,
                    "required_test_type": o.required_test_type,
                    "criticality": o.criticality,
                    "status": o.status,
                }
                for o in obligations
            ],
        }
    finally:
        db.close()


def _get_alignment_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        evals = db.query(SemanticAlignmentEvaluation).filter(
            SemanticAlignmentEvaluation.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(evals),
            "evaluations": [
                {
                    "evaluation_id": str(e.id),
                    "test_case_id": e.test_case_id,
                    "requirement_id": e.requirement_id,
                    "obligation_id": e.obligation_id,
                    "semantic_alignment_score": e.semantic_alignment_score,
                    "verifier_verdict": e.verifier_verdict,
                    "can_broken_code_pass": e.can_broken_code_pass,
                    "critique": e.critique,
                }
                for e in evals
            ],
        }
    finally:
        db.close()


def _get_verifier_critiques_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        critiques = db.query(VerifierCritique).filter(
            VerifierCritique.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(critiques),
            "critiques": [
                {
                    "test_case_id": c.test_case_id,
                    "obligation_id": c.obligation_id,
                    "verifier_model": c.verifier_model,
                    "verdict": c.verdict,
                    "confidence": c.confidence,
                    "critique": c.critique,
                    "recommendations": c.recommendations_json,
                }
                for c in critiques
            ],
        }
    finally:
        db.close()


def _get_mutations_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        mutations = db.query(MutationTest).filter(
            MutationTest.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(mutations),
            "killed": sum(1 for m in mutations if m.killed),
            "survived": sum(1 for m in mutations if m.survived),
            "mutations": [
                {
                    "mutation_id": m.mutation_id,
                    "requirement_id": m.requirement_id,
                    "mutation_type": m.mutation_type,
                    "mutated_component": m.mutated_component,
                    "expected_test_failure": m.expected_test_failure,
                    "actual_test_result": m.actual_test_result,
                    "killed": m.killed,
                    "survived": m.survived,
                }
                for m in mutations
            ],
        }
    finally:
        db.close()


def _get_negative_coverage_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        neg_reqs = db.query(NegativeTestRequirement).filter(
            NegativeTestRequirement.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(neg_reqs),
            "pending": sum(1 for n in neg_reqs if n.status == 'pending'),
            "generated": sum(1 for n in neg_reqs if n.status == 'generated'),
            "requirements": [
                {
                    "requirement_id": n.requirement_id,
                    "required_negative_case": n.required_negative_case,
                    "status": n.status,
                }
                for n in neg_reqs
            ],
        }
    finally:
        db.close()


def _get_runtime_evidence_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        bindings = db.query(RuntimeEvidenceBinding).filter(
            RuntimeEvidenceBinding.run_id == UUID(run_id)
        ).all()
        return {
            "run_id": run_id,
            "total": len(bindings),
            "bound": sum(1 for b in bindings if b.binding_status == 'bound'),
            "failed": sum(1 for b in bindings if b.binding_status == 'failed'),
            "bindings": [
                {
                    "test_case_id": b.test_case_id,
                    "obligation_id": b.obligation_id,
                    "evidence_type": b.evidence_type,
                    "binding_status": b.binding_status,
                }
                for b in bindings
            ],
        }
    finally:
        db.close()


def _get_full_report_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        report = db.query(SemanticCoverageReport).filter(
            SemanticCoverageReport.run_id == UUID(run_id)
        ).first()
        if not report:
            return {"error": "no_report"}
        return {
            "run_id": run_id,
            "scores": {
                "obligation_coverage": report.obligation_coverage_score,
                "semantic_alignment": report.semantic_alignment_score,
                "mutation": report.mutation_score,
                "negative_coverage": report.negative_coverage_score,
                "runtime_evidence": report.runtime_evidence_score,
                "verifier_confidence": report.verifier_confidence_score,
                "overall": report.overall_semantic_coverage_score,
            },
            "critical_requirements_passed": report.critical_requirements_passed,
            "release_gate_status": report.release_gate_status,
            "report": report.report_json,
        }
    finally:
        db.close()


def _evaluate_semantic_coverage_sync(run_id: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        report = engine.run_full_semantic_coverage(run_id)
        return {
            "run_id": run_id,
            "status": "evaluated",
            "overall_semantic_coverage_score": report.overall_semantic_coverage_score,
            "critical_requirements_passed": report.critical_requirements_passed,
            "release_gate_status": report.release_gate_status,
        }
    finally:
        db.close()


def _create_waiver_sync(run_id: str, requirement_id: str, waiver_reason: str,
                        waiver_scope: str, approved_by: str) -> dict:
    engine, db = _get_sync_engine()
    try:
        waiver = SemanticCoverageWaiver(
            id=uuid.uuid4(),
            run_id=UUID(run_id),
            requirement_id=requirement_id,
            obligation_id=None,
            waiver_reason=waiver_reason,
            waiver_scope=waiver_scope,
            approved_by=approved_by,
        )
        db.add(waiver)
        db.commit()
        return {"waiver_id": str(waiver.id), "status": "created"}
    finally:
        db.close()


# ── Async endpoint wrappers ──────────────────────────────────────────────

@router.get("/runs/{run_id}/summary")
async def get_semantic_coverage_summary(run_id: str):
    """Get semantic coverage summary for a run."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _get_summary_sync, run_id)
    if "error" in result:
        if result["error"] == "not_found":
            raise HTTPException(status_code=404, detail="Run not found")
    return result


@router.get("/runs/{run_id}/requirements")
async def get_requirements(run_id: str):
    """Get normalized requirements for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_requirements_sync, run_id)


@router.get("/runs/{run_id}/acceptance-criteria")
async def get_acceptance_criteria(run_id: str):
    """Get acceptance criteria contracts for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_acceptance_criteria_sync, run_id)


@router.get("/runs/{run_id}/test-obligations")
async def get_test_obligations(run_id: str):
    """Get test obligations for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_test_obligations_sync, run_id)


@router.get("/runs/{run_id}/alignment")
async def get_alignment(run_id: str):
    """Get semantic alignment evaluations for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_alignment_sync, run_id)


@router.get("/runs/{run_id}/verifier-critiques")
async def get_verifier_critiques(run_id: str):
    """Get verifier critiques for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_verifier_critiques_sync, run_id)


@router.get("/runs/{run_id}/mutations")
async def get_mutations(run_id: str):
    """Get mutation tests for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_mutations_sync, run_id)


@router.get("/runs/{run_id}/negative-coverage")
async def get_negative_coverage(run_id: str):
    """Get negative test coverage for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_negative_coverage_sync, run_id)


@router.get("/runs/{run_id}/runtime-evidence")
async def get_runtime_evidence(run_id: str):
    """Get runtime evidence bindings for a run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_runtime_evidence_sync, run_id)


@router.get("/runs/{run_id}/report")
async def get_full_report(run_id: str):
    """Get full semantic coverage report for a run."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _get_full_report_sync, run_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail="No semantic coverage report for this run")
    return result


@router.post("/runs/{run_id}/evaluate")
async def evaluate_semantic_coverage(run_id: str):
    """Run full semantic coverage evaluation for a run."""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _evaluate_semantic_coverage_sync, run_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/runs/{run_id}/waivers")
async def create_waiver(
    run_id: str,
    requirement_id: str = Query(...),
    waiver_reason: str = Query(...),
    waiver_scope: str = Query("obligation"),
    approved_by: str = Query("system"),
):
    """Create a semantic coverage waiver."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, _create_waiver_sync,
        run_id, requirement_id, waiver_reason, waiver_scope, approved_by
    )
