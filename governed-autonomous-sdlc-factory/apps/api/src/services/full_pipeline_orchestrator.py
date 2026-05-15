"""Full Pipeline Orchestrator for the Cognitive Cortex.

Executes the complete cognitive pipeline using REAL AI engines:
intent → specification → architecture → governance → test plan → traceability → snapshot → evidence

Each step uses ModelRouter for LLM inference.
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
                await store.persist(
                    name="requirements.json",
                    content=json.dumps(spec.functional_requirements, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                    metadata={"spec_id": spec.id, "model": spec.model_used},
                )
                metrics.artifacts_generated += 1
            if spec.acceptance_criteria:
                await store.persist(
                    name="acceptance_criteria.json",
                    content=json.dumps(spec.acceptance_criteria, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                )
                metrics.artifacts_generated += 1
            if spec.governance_sensitive_areas:
                await store.persist(
                    name="governance_areas.json",
                    content=json.dumps(spec.governance_sensitive_areas, indent=2, default=str),
                    artifact_type=ArtifactType.SPECIFICATION.value,
                    phase_name="specification",
                    source_engine="specification-engine",
                )
                metrics.artifacts_generated += 1
            metrics.cost_total += spec.cost_usd
            metrics.record_step("generate_specification", (time.monotonic() - t0) * 1000)
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
            if arch.architecture_proposal:
                await store.persist(
                    name="architecture.md",
                    content=arch.architecture_proposal,
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                    metadata={"arch_id": arch.id, "model": arch.model_used},
                )
                metrics.artifacts_generated += 1
            if arch.component_breakdown:
                await store.persist(
                    name="components.json",
                    content=json.dumps(arch.component_breakdown, indent=2, default=str),
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                )
                metrics.artifacts_generated += 1
            if arch.adrs:
                await store.persist(
                    name="adrs.json",
                    content=json.dumps(arch.adrs, indent=2, default=str),
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    source_engine="architecture-engine",
                )
                metrics.artifacts_generated += 1
            if arch.mermaid_diagrams:
                for diagram in arch.mermaid_diagrams:
                    await store.persist(
                        name=f"diagram_{diagram.get('name', 'diagram')}.mmd",
                        content=diagram.get("content", ""),
                        artifact_type=ArtifactType.ARCHITECTURE.value,
                        phase_name="architecture",
                        source_engine="architecture-engine",
                    )
                    metrics.artifacts_generated += 1
            metrics.cost_total += arch.cost_usd
            metrics.record_step("generate_architecture", (time.monotonic() - t0) * 1000)
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
            if gov.runtime_governance_concerns:
                await store.persist(
                    name="governance_concerns.json",
                    content=json.dumps(gov.runtime_governance_concerns, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                metrics.artifacts_generated += 1
            if gov.security_sensitive_findings:
                await store.persist(
                    name="security_findings.json",
                    content=json.dumps(gov.security_sensitive_findings, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                metrics.artifacts_generated += 1
            if gov.compliance_gaps:
                await store.persist(
                    name="compliance_gaps.json",
                    content=json.dumps(gov.compliance_gaps, indent=2, default=str),
                    artifact_type=ArtifactType.GOVERNANCE.value,
                    phase_name="governance",
                    source_engine="governance-engine",
                )
                metrics.artifacts_generated += 1
            metrics.governance_passed = len([f for f in gov.runtime_governance_concerns if f.get("severity") != "critical"])
            metrics.governance_failed = len([f for f in gov.security_sensitive_findings if f.get("impact") == "high"])
            metrics.governance_warnings = len(gov.compliance_gaps)
            metrics.cost_total += gov.cost_usd
            metrics.record_step("generate_governance", (time.monotonic() - t0) * 1000)
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
                await store.persist(
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
            metrics.cost_total += test_plan.cost_usd
            metrics.record_step("generate_test_plan", (time.monotonic() - t0) * 1000)
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
                f"Pipeline completed: {metrics.artifacts_generated} artifacts, {metrics.total_duration_ms:.0f}ms",
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
