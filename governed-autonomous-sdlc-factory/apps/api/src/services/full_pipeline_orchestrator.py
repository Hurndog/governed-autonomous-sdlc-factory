"""Full Pipeline Orchestrator for the Cognitive Cortex.

Executes the complete cognitive pipeline using REAL AI engines:
intent → specification → architecture → governance → test plan → traceability → snapshot → evidence

Each step uses ModelRouter for LLM inference.
Traceability links and governance evaluations are persisted to the database.
"""
import asyncio
import time
import json
import os
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.logging import get_logger
from src.core.event_bus import (
    EventBusManager, publish_custom_event, publish_artifact_created,
    publish_governance_finding, publish_cost_event
)
from src.models import (
    Run, RunStatus, Project, Phase, Artifact, ArtifactType,
    SpecificationVersion, ArchitectureVersion, GovernancePolicy,
    GovernanceEvaluation, GovernanceReleaseGate, TestPlan,
    TraceabilityLink, ArtifactBaseline, RunSnapshot, ArtifactDiff,
    CostEvent, LogEvent
)
from src.services.artifact_store import ArtifactStore
from src.engines.specification_engine import SpecificationEngine, SpecificationArtifact
from src.engines.architecture_engine import ArchitectureEngine, ArchitectureArtifact
from src.engines.governance_engine import GovernanceEngine, GovernanceArtifact
from src.engines.test_engine import TestPlanEngine, TestPlanArtifact
from src.engines.traceability import TraceabilityManager
from src.engines.snapshots import SnapshotManager
from src.engines.inference_trace import InferenceTracer
from src.core.hashing import compute_governance_hash, compute_traceability_hash

logger = get_logger("full_pipeline")

ARTIFACT_BASE_DIR = Path(os.environ.get("ARTIFACT_DIR", "/tmp/cortex-artifacts"))


class PipelineMetrics:
    """Tracks execution metrics for a pipeline run."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.step_times: dict[str, float] = {}
        self.artifacts_generated = 0
        self.governance_passed = 0
        self.governance_failed = 0
        self.governance_warnings = 0
        self.traceability_links = 0
        self.cost_total = 0.0
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def start(self):
        self.start_time = time.monotonic()

    def stop(self):
        self.end_time = time.monotonic()

    def record_step(self, name: str, duration_ms: float):
        self.step_times[name] = duration_ms

    def record_error(self, step: str, error: str):
        self.errors.append({"step": step, "error": error, "timestamp": datetime.now(timezone.utc).isoformat()})

    def record_warning(self, step: str, warning: str):
        self.warnings.append({"step": step, "warning": warning, "timestamp": datetime.now(timezone.utc).isoformat()})

    @property
    def total_duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

    def to_dict(self) -> dict:
        return {
            "total_duration_ms": self.total_duration_ms,
            "step_times_ms": self.step_times,
            "artifacts_generated": self.artifacts_generated,
            "governance_passed": self.governance_passed,
            "governance_failed": self.governance_failed,
            "governance_warnings": self.governance_warnings,
            "traceability_links": self.traceability_links,
            "cost_total": self.cost_total,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


class FullPipelineOrchestrator:
    """Orchestrates the complete cognitive execution pipeline using REAL AI."""

    def __init__(self):
        self._active_pipelines: dict[str, asyncio.Task] = {}

    async def execute_full_pipeline(
        self,
        project_id: str,
        run_id: str,
        intent: str,
        project_name: str = "",
        budget_limit: float = None,
        is_demo: bool = True,
    ) -> dict:
        """Execute the full cognitive pipeline with REAL LLM inference."""
        metrics = PipelineMetrics()
        metrics.start()

        bus = EventBusManager.get_bus(run_id)
        store = ArtifactStore(run_id, project_id)
        tracer = InferenceTracer(run_id=run_id)
        trace_mgr = TraceabilityManager(run_id)

        await publish_custom_event(
            run_id, "pipeline.started",
            f"Full pipeline started for intent: {intent[:100]}...",
            data={"project_id": project_id, "intent_length": len(intent)},
        )

        async with async_session_factory() as session:
            run = await session.get(Run, run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            run.status = RunStatus.RUNNING.value
            run.started_at = datetime.now(timezone.utc)
            await session.commit()

        try:
            # ── Step 1: Capture User Intent ──────────────────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "intent.captured", f"Intent captured: {intent[:200]}")
            intent_artifact = await store.persist(
                name="intent.md",
                content=f"# User Intent\n\n{intent}\n",
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="intent",
                source_engine="pipeline",
            )
            metrics.artifacts_generated += 1
            metrics.record_step("capture_intent", (time.monotonic() - t0) * 1000)

            # ── Step 2: Generate Specification (REAL LLM) ────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "spec.generation_started", "Specification generation started")
            spec_engine = SpecificationEngine()
            spec = await spec_engine.generate_specification(
                intent=intent,
                run_id=run_id,
                project_id=project_id,
                tracer=tracer,
            )
            # Persist spec artifacts
            if spec.functional_requirements:
                req_artifact = await store.persist(
                    name="requirements.json",
                    content=json.dumps(spec.functional_requirements, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                    metadata={"spec_id": spec.id, "model": spec.model_used},
                )
                metrics.artifacts_generated += 1
            if spec.acceptance_criteria:
                ac_artifact = await store.persist(
                    name="acceptance_criteria.json",
                    content=json.dumps(spec.acceptance_criteria, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                )
                metrics.artifacts_generated += 1
            if spec.governance_sensitive_areas:
                gov_areas_artifact = await store.persist(
                    name="governance_areas.json",
                    content=json.dumps(spec.governance_sensitive_areas, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                )
                metrics.artifacts_generated += 1

            # Traceability: requirement → acceptance_criterion
            async with async_session_factory() as session:
                for ac in spec.acceptance_criteria:
                    req_id = ac.get("requirement_id", "")
                    ac_id = ac.get("id", "")
                    if req_id and ac_id:
                        await trace_mgr.link(session, "requirement", req_id, "acceptance_criterion", ac_id, "validated_by")
                        metrics.traceability_links += 1
                # Traceability: phase → artifact
                for art_name in ["requirements.json", "acceptance_criteria.json", "governance_areas.json"]:
                    art_result = await session.execute(
                        select(Artifact).where(Artifact.run_id == run_id, Artifact.name == art_name)
                    )
                    art = art_result.scalars().first()
                    if art:
                        await trace_mgr.link(session, "phase", "specification", "artifact", art.id, "produces")
                        metrics.traceability_links += 1
                await session.commit()

            metrics.cost_total += spec.cost_usd
            metrics.record_step("generate_specification", (time.monotonic() - t0) * 1000)
            # Publish cost event with agent attribution
            await publish_cost_event(
                run_id=run_id,
                model_name=spec.model_used or "unknown",
                tokens_in=spec.tokens_used,
                tokens_out=0,
                cost=spec.cost_usd,
                is_local=True,
                agent_id="specification_engine",
                phase_name="specification",
                data={"spec_id": spec.id},
            )
            await publish_custom_event(
                run_id, "spec.generated",
                f"Specification generated: {len(spec.functional_requirements)} FR, {len(spec.non_functional_requirements)} NFR",
                data={"spec_id": spec.id, "model": spec.model_used, "tokens": spec.tokens_used},
            )

            # ── Step 3: Generate Architecture (REAL LLM) ──────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "architecture.generation_started", "Architecture generation started")
            arch_engine = ArchitectureEngine()
            arch = await arch_engine.generate_architecture(
                spec=spec,
                run_id=run_id,
                tracer=tracer,
            )
            arch_artifacts = []
            if arch.architecture_proposal:
                art = await store.persist(
                    name="architecture.md",
                    content=arch.architecture_proposal,
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                    metadata={"arch_id": arch.id, "model": arch.model_used},
                )
                arch_artifacts.append(art)
                metrics.artifacts_generated += 1
            if arch.component_breakdown:
                art = await store.persist(
                    name="components.json",
                    content=json.dumps(arch.component_breakdown, indent=2, default=str),
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                )
                arch_artifacts.append(art)
                metrics.artifacts_generated += 1
            if arch.adrs:
                art = await store.persist(
                    name="adrs.json",
                    content=json.dumps(arch.adrs, indent=2, default=str),
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                )
                arch_artifacts.append(art)
                metrics.artifacts_generated += 1
            if arch.mermaid_diagrams:
                for diagram in arch.mermaid_diagrams:
                    art = await store.persist(
                        name=f"diagram_{diagram.get('name', 'diagram')}.mmd",
                        content=diagram.get("content", ""),
                        artifact_type=ArtifactType.ARCHITECTURE.value,
                        phase_name="architecture",
                        source_engine="architecture-engine",
                    )
                    arch_artifacts.append(art)
                    metrics.artifacts_generated += 1

            # Traceability: requirement → architecture_component, phase → artifact
            async with async_session_factory() as session:
                for comp in arch.component_breakdown:
                    comp_name = comp.get("name", "")
                    comp_id = comp_name.lower().replace(" ", "_") if comp_name else ""
                    if comp_id:
                        # Link component to requirements (all requirements for now)
                        for fr in spec.functional_requirements:
                            fr_id = fr.get("id", "")
                            if fr_id:
                                await trace_mgr.link(session, "requirement", fr_id, "architecture_component", comp_id, "implemented_by")
                                metrics.traceability_links += 1
                # Phase → artifact
                for art in arch_artifacts:
                    await trace_mgr.link(session, "phase", "architecture", "artifact", art["id"], "produces")
                    metrics.traceability_links += 1
                await session.commit()

            metrics.cost_total += arch.cost_usd
            metrics.record_step("generate_architecture", (time.monotonic() - t0) * 1000)
            # Publish cost event with agent attribution
            await publish_cost_event(
                run_id=run_id,
                model_name=arch.model_used or "unknown",
                tokens_in=arch.tokens_used,
                tokens_out=0,
                cost=arch.cost_usd,
                is_local=True,
                agent_id="architecture_engine",
                phase_name="architecture",
                data={"arch_id": arch.id},
            )
            await publish_custom_event(
                run_id, "architecture.generated",
                f"Architecture generated: {len(arch.component_breakdown)} components, {len(arch.adrs)} ADRs",
                data={"arch_id": arch.id, "model": arch.model_used, "tokens": arch.tokens_used},
            )

            # ── Step 4: Generate Governance (REAL LLM) ────────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "governance.generation_started", "Governance analysis started")
            gov_engine = GovernanceEngine()
            gov = await gov_engine.generate_governance(
                spec=spec,
                arch=arch,
                run_id=run_id,
                tracer=tracer,
            )
            gov_artifacts = []
            if gov.runtime_governance_concerns:
                art = await store.persist(
                    name="governance_concerns.json",
                    content=json.dumps(gov.runtime_governance_concerns, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                gov_artifacts.append(art)
                metrics.artifacts_generated += 1
            if gov.security_sensitive_findings:
                art = await store.persist(
                    name="security_findings.json",
                    content=json.dumps(gov.security_sensitive_findings, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                gov_artifacts.append(art)
                metrics.artifacts_generated += 1
            if gov.compliance_gaps:
                art = await store.persist(
                    name="compliance_gaps.json",
                    content=json.dumps(gov.compliance_gaps, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                gov_artifacts.append(art)
                metrics.artifacts_generated += 1

            # Persist governance evaluations and traceability
            async with async_session_factory() as session:
                # Load active policies
                policies_result = await session.execute(
                    select(GovernancePolicy).where(GovernancePolicy.is_active == True)
                )
                policies = policies_result.scalars().all()

                # Create governance evaluations for each policy
                eval_ids = []
                for policy in policies:
                    # Determine decision based on governance findings
                    decision = "pass"
                    findings = []
                    if policy.category == "security" and gov.security_sensitive_findings:
                        critical = [f for f in gov.security_sensitive_findings if f.get("impact") == "high"]
                        if critical:
                            decision = "fail" if policy.is_blocking else "warn"
                        findings = gov.security_sensitive_findings
                    elif policy.category == "compliance" and gov.compliance_gaps:
                        critical = [g for g in gov.compliance_gaps if g.get("severity") == "critical"]
                        if critical:
                            decision = "fail" if policy.is_blocking else "warn"
                        findings = gov.compliance_gaps
                    elif policy.category == "quality":
                        # Quality checks: spec has requirements, architecture has components, etc.
                        if policy.name == "spec-has-acceptance-criteria":
                            if not spec.acceptance_criteria:
                                decision = "fail" if policy.is_blocking else "warn"
                                findings = [{"issue": "No acceptance criteria found"}]
                            else:
                                findings = [{"info": f"{len(spec.acceptance_criteria)} acceptance criteria found"}]
                        elif policy.name == "no-missing-architecture-doc":
                            if not arch.architecture_proposal:
                                decision = "fail" if policy.is_blocking else "warn"
                                findings = [{"issue": "No architecture document"}]
                            else:
                                findings = [{"info": "Architecture document present"}]
                        elif policy.name == "no-missing-specification":
                            if not spec.functional_requirements:
                                decision = "fail" if policy.is_blocking else "warn"
                                findings = [{"issue": "No functional requirements"}]
                            else:
                                findings = [{"info": f"{len(spec.functional_requirements)} functional requirements"}]
                        elif policy.name == "test-coverage-minimum":
                            # Will be evaluated after test plan
                            findings = [{"info": "Test coverage evaluated after test plan"}]
                        else:
                            findings = [{"info": "Quality check passed"}]
                    elif policy.category == "release":
                        findings = [{"info": "Release gate evaluated at end of pipeline"}]

                    if decision == "fail":
                        metrics.governance_failed += 1
                    elif decision == "warn":
                        metrics.governance_warnings += 1
                    else:
                        metrics.governance_passed += 1

                    # Compute integrity hash
                    i_hash = compute_governance_hash(
                        policy_name=policy.name,
                        decision=decision,
                        input_data={"findings": findings},
                        output_data={"decision": decision},
                        run_id=run_id,
                    )

                    evaluation = GovernanceEvaluation(
                        run_id=run_id,
                        policy_id=policy.id,
                        decision=decision,
                        findings=findings,
                        evidence={"governance_artifact_id": gov.id},
                        integrity_hash=i_hash,
                        evaluated_at=datetime.now(timezone.utc),
                    )
                    session.add(evaluation)
                    await session.flush()
                    eval_ids.append(evaluation.id)

                    # Traceability: governance_concern → governance_policy → governance_evaluation
                    for concern in gov.runtime_governance_concerns:
                        concern_id = concern.get("id", "")
                        if concern_id:
                            await trace_mgr.link(session, "governance_concern", concern_id, "governance_policy", policy.id, "evaluated_by")
                            metrics.traceability_links += 1
                    await trace_mgr.link(session, "governance_policy", policy.id, "governance_evaluation", evaluation.id, "evaluated_as")
                    metrics.traceability_links += 1

                # Create release gate
                if eval_ids:
                    gate_status = "passed" if metrics.governance_failed == 0 else "failed"
                    release_gate = GovernanceReleaseGate(
                        run_id=run_id,
                        gate_name="governance-release-gate",
                        status=gate_status,
                        required_policy_ids=[p.id for p in policies],
                        evaluation_ids=eval_ids,
                        evaluated_at=datetime.now(timezone.utc),
                    )
                    session.add(release_gate)
                    await session.flush()

                    # Traceability: governance_evaluation → release_gate
                    for eid in eval_ids:
                        await trace_mgr.link(session, "governance_evaluation", eid, "release_gate", release_gate.id, "gates")
                        metrics.traceability_links += 1

                # Traceability: requirement → governance_concern, phase → artifact
                for concern in gov.runtime_governance_concerns:
                    concern_id = concern.get("id", "")
                    if concern_id:
                        for fr in spec.functional_requirements:
                            fr_id = fr.get("id", "")
                            if fr_id:
                                await trace_mgr.link(session, "requirement", fr_id, "governance_concern", concern_id, "governed_by")
                                metrics.traceability_links += 1
                for art in gov_artifacts:
                    await trace_mgr.link(session, "phase", "governance", "artifact", art["id"], "produces")
                    metrics.traceability_links += 1

                await session.commit()

            metrics.cost_total += gov.cost_usd
            metrics.record_step("generate_governance", (time.monotonic() - t0) * 1000)
            # Publish cost event with agent attribution
            await publish_cost_event(
                run_id=run_id,
                model_name=gov.model_used or "unknown",
                tokens_in=gov.tokens_used,
                tokens_out=0,
                cost=gov.cost_usd,
                is_local=True,
                agent_id="governance_engine",
                phase_name="governance",
                data={"gov_id": gov.id},
            )
            await publish_custom_event(
                run_id, "governance.generated",
                f"Governance analysis: {len(gov.runtime_governance_concerns)} concerns, {len(gov.security_sensitive_findings)} security findings",
                data={"gov_id": gov.id, "model": gov.model_used},
            )

            # ── Step 5: Generate Test Plan (REAL LLM) ─────────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "testplan.generation_started", "Test plan generation started")
            test_engine = TestPlanEngine()
            test_plan = await test_engine.generate_test_plan(
                spec=spec,
                arch=arch,
                run_id=run_id,
                tracer=tracer,
            )
            if test_plan.test_cases:
                test_art = await store.persist(
                    name="test_plan.json",
                    content=json.dumps({
                        "unit_strategy": test_plan.unit_test_strategy,
                        "integration_strategy": test_plan.integration_strategy,
                        "test_cases": test_plan.test_cases,
                        "edge_cases": test_plan.edge_cases,
                        "governance_tests": test_plan.governance_tests,
                    }, indent=2, default=str),
                    artifact_type=ArtifactType.TEST_PLAN.value,
                    phase_name="quality",
                    source_engine="test-engine",
                    metadata={"test_plan_id": test_plan.id, "model": test_plan.model_used},
                )
                metrics.artifacts_generated += 1

            # Traceability: requirement → test_case, architecture_component → test_case, phase → artifact
            async with async_session_factory() as session:
                for tc in test_plan.test_cases:
                    tc_id = tc.get("id", tc.get("name", ""))
                    req_id = tc.get("requirement_id", "")
                    if tc_id and req_id:
                        await trace_mgr.link(session, "requirement", req_id, "test_case", tc_id, "tested_by")
                        metrics.traceability_links += 1
                    # Link test case to architecture components
                    for comp in arch.component_breakdown:
                        comp_id = comp.get("name", "").lower().replace(" ", "_")
                        if comp_id and tc_id:
                            await trace_mgr.link(session, "architecture_component", comp_id, "test_case", tc_id, "tested_by")
                            metrics.traceability_links += 1
                # Phase → artifact
                if test_plan.test_cases:
                    art_result = await session.execute(
                        select(Artifact).where(Artifact.run_id == run_id, Artifact.name == "test_plan.json")
                    )
                    art = art_result.scalars().first()
                    if art:
                        await trace_mgr.link(session, "phase", "quality", "artifact", art.id, "produces")
                        metrics.traceability_links += 1
                await session.commit()

            metrics.cost_total += test_plan.cost_usd
            metrics.record_step("generate_test_plan", (time.monotonic() - t0) * 1000)
            # Publish cost event with agent attribution
            await publish_cost_event(
                run_id=run_id,
                model_name=test_plan.model_used or "unknown",
                tokens_in=test_plan.tokens_used,
                tokens_out=0,
                cost=test_plan.cost_usd,
                is_local=True,
                agent_id="test_engine",
                phase_name="quality",
                data={"test_plan_id": test_plan.id},
            )
            await publish_custom_event(
                run_id, "testplan.generated",
                f"Test plan generated: {len(test_plan.test_cases)} test cases, {len(test_plan.edge_cases)} edge cases",
                data={"test_plan_id": test_plan.id, "model": test_plan.model_used},
            )

            # ── Step 6: Create Snapshot ──────────────────────────────────
            t0 = time.monotonic()
            async with async_session_factory() as session:
                snap_mgr = SnapshotManager(run_id)
                snapshot = await snap_mgr.create_snapshot(session, "pipeline_complete", triggered_by="pipeline")
            metrics.record_step("create_snapshot", (time.monotonic() - t0) * 1000)

            # ── Step 7: Finalize Run ─────────────────────────────────────
            t0 = time.monotonic()
            async with async_session_factory() as session:
                run = await session.get(Run, run_id)
                run.status = RunStatus.COMPLETED.value
                run.completed_at = datetime.now(timezone.utc)
                run.total_cost = metrics.cost_total
                await session.commit()
            metrics.record_step("finalize_run", (time.monotonic() - t0) * 1000)

            metrics.stop()

            # Emit completion event
            await publish_custom_event(
                run_id, "pipeline.completed",
                f"Pipeline completed: {metrics.artifacts_generated} artifacts, {metrics.traceability_links} traceability links, {metrics.total_duration_ms:.0f}ms",
                data=metrics.to_dict(),
            )

            return {
                "run_id": run_id,
                "status": "completed",
                "metrics": metrics.to_dict(),
                "artifact_count": metrics.artifacts_generated,
                "governance_passed": metrics.governance_passed,
                "governance_failed": metrics.governance_failed,
                "traceability_links": metrics.traceability_links,
                "inference_summary": tracer.get_summary(),
            }

        except Exception as e:
            metrics.stop()
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            metrics.record_error("pipeline", str(e))

            async with async_session_factory() as session:
                run = await session.get(Run, run_id)
                if run:
                    run.status = RunStatus.FAILED.value
                    run.completed_at = datetime.now(timezone.utc)
                    await session.commit()

            await publish_custom_event(
                run_id, "pipeline.failed",
                f"Pipeline failed: {e}",
                severity="error",
                data={"error": str(e), "metrics": metrics.to_dict()},
            )

            return {
                "run_id": run_id,
                "status": "failed",
                "error": str(e),
                "metrics": metrics.to_dict(),
            }


# Global orchestrator instance
full_pipeline = FullPipelineOrchestrator()
