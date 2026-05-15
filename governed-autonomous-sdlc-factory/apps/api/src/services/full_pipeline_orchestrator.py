"""Full Pipeline Orchestrator for the Cognitive Cortex.

Executes the complete cognitive pipeline:
intent → specification → architecture → governance → test plan → traceability → snapshot → evidence

Each step emits events, persists artifacts, records metrics, and supports replay.
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
from src.engines.specification_engine import SpecificationEngine, generate_default_specification
from src.engines.architecture_engine import ArchitectureEngine, generate_default_architecture
from src.engines.governance_engine import GovernanceEngine
from src.engines.test_engine import TestPlanGenerator, generate_test_plan_from_spec
from src.engines.traceability import TraceabilityManager
from src.engines.snapshots import SnapshotManager

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
    """Orchestrates the complete cognitive execution pipeline."""

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
        """Execute the full cognitive pipeline."""
        metrics = PipelineMetrics()
        metrics.start()

        bus = EventBusManager.get_bus(run_id)
        store = ArtifactStore(run_id, project_id)

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

            # ── Step 2: Generate Specification ───────────────────────────
            t0 = time.monotonic()
            await publish_custom_event(run_id, "spec.generation_started", "Specification generation started")
            spec = await self._step_generate_specification(session, run_id, project_id, project_name, intent, store, metrics)
            metrics.record_step("generate_specification", (time.monotonic() - t0) * 1000)

            # ── Step 3: Validate Specification ────────────────────────────
            t0 = time.monotonic()
            validation_result = await self._step_validate_specification(run_id, spec, store, metrics)
            metrics.record_step("validate_specification", (time.monotonic() - t0) * 1000)

            # ── Step 4: Create Specification Baseline ────────────────────
            t0 = time.monotonic()
            baseline = await self._step_create_spec_baseline(run_id, spec, store, metrics)
            metrics.record_step("create_spec_baseline", (time.monotonic() - t0) * 1000)

            # ── Step 5: Generate Architecture ─────────────────────────────
            t0 = time.monotonic()
            arch = await self._step_generate_architecture(run_id, project_id, project_name, spec, store, metrics)
            metrics.record_step("generate_architecture", (time.monotonic() - t0) * 1000)

            # ── Step 6: Generate Architecture Constraints ─────────────────
            t0 = time.monotonic()
            await self._step_generate_arch_constraints(run_id, arch, store, metrics)
            metrics.record_step("generate_arch_constraints", (time.monotonic() - t0) * 1000)

            # ── Step 7: Generate ADRs ─────────────────────────────────────
            t0 = time.monotonic()
            await self._step_generate_adrs(run_id, arch, store, metrics)
            metrics.record_step("generate_adrs", (time.monotonic() - t0) * 1000)

            # ── Step 8: Generate Governance Policies ──────────────────────
            t0 = time.monotonic()
            await self._step_generate_governance(run_id, store, metrics)
            metrics.record_step("generate_governance", (time.monotonic() - t0) * 1000)

            # ── Step 9: Evaluate Governance Policies ──────────────────────
            t0 = time.monotonic()
            gov_results = await self._step_evaluate_governance(run_id, project_id, spec, store, metrics)
            metrics.record_step("evaluate_governance", (time.monotonic() - t0) * 1000)

            # ── Step 10: Generate Test Plan ───────────────────────────────
            t0 = time.monotonic()
            test_plan = await self._step_generate_test_plan(run_id, project_id, spec, store, metrics)
            metrics.record_step("generate_test_plan", (time.monotonic() - t0) * 1000)

            # ── Step 11: Generate Traceability Links ──────────────────────
            t0 = time.monotonic()
            await self._step_generate_traceability(run_id, spec, arch, test_plan, store, metrics)
            metrics.record_step("generate_traceability", (time.monotonic() - t0) * 1000)

            # ── Step 12: Persist All Artifacts ────────────────────────────
            t0 = time.monotonic()
            manifest = await store.write_manifest()
            metrics.record_step("persist_artifacts", (time.monotonic() - t0) * 1000)

            # ── Step 13: Create Snapshot ──────────────────────────────────
            t0 = time.monotonic()
            snapshot = await self._step_create_snapshot(run_id, metrics)
            metrics.record_step("create_snapshot", (time.monotonic() - t0) * 1000)

            # ── Step 14: Generate Evidence Bundle ─────────────────────────
            t0 = time.monotonic()
            evidence = await self._step_generate_evidence(run_id, project_id, store, metrics, gov_results)
            metrics.record_step("generate_evidence", (time.monotonic() - t0) * 1000)

            # ── Step 15: Calculate Costs ──────────────────────────────────
            t0 = time.monotonic()
            await self._step_calculate_costs(run_id, metrics)
            metrics.record_step("calculate_costs", (time.monotonic() - t0) * 1000)

            # ── Step 16: Finalize Run ─────────────────────────────────────
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

    # ── Individual Step Implementations ─────────────────────────────────

    async def _step_generate_specification(self, session, run_id, project_id, project_name, intent, store, metrics):
        """Step 2: Generate specification from intent."""
        project_desc = intent or f"Autonomous SDLC project: {project_name}"
        spec = await generate_default_specification(run_id, project_id, project_name, project_desc)

        # Persist spec artifacts to filesystem
        if spec.requirements_yaml:
            await store.persist(
                name="requirements.yaml",
                content=json.dumps(spec.requirements_yaml, indent=2, default=str),
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="specification",
                source_engine="specification-engine",
                metadata={"spec_version_id": spec.id, "version": spec.version},
            )
            metrics.artifacts_generated += 1

        if spec.functional_spec:
            await store.persist(
                name="functional_spec.md",
                content=spec.functional_spec,
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="specification",
                source_engine="specification-engine",
                metadata={"spec_version_id": spec.id},
            )
            metrics.artifacts_generated += 1

        if spec.acceptance_criteria:
            await store.persist(
                name="acceptance_criteria.yaml",
                content=json.dumps(spec.acceptance_criteria, indent=2, default=str),
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="specification",
                source_engine="specification-engine",
            )
            metrics.artifacts_generated += 1

        if spec.non_functional_requirements:
            await store.persist(
                name="non_functional_requirements.yaml",
                content=json.dumps(spec.non_functional_requirements, indent=2, default=str),
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="specification",
                source_engine="specification-engine",
            )
            metrics.artifacts_generated += 1

        if spec.assumptions:
            await store.persist(
                name="assumptions.md",
                content=spec.assumptions,
                artifact_type=ArtifactType.SPECIFICATION.value,
                phase_name="specification",
                source_engine="specification-engine",
            )
            metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "spec.generated",
            f"Specification v{spec.version} generated: {len(spec.requirements_yaml or {})} requirements",
            data={"spec_version_id": spec.id, "version": spec.version},
        )

        return spec

    async def _step_validate_specification(self, run_id, spec, store, metrics):
        """Step 3: Validate specification and persist results."""
        validation_errors = spec.validation_errors or []
        error_count = len([e for e in validation_errors if e.get("severity") == "error"])
        warning_count = len([e for e in validation_errors if e.get("severity") == "warning"])

        validation_report = {
            "valid": error_count == 0,
            "error_count": error_count,
            "warning_count": warning_count,
            "errors": validation_errors,
        }

        await store.persist(
            name="validation-report.json",
            content=json.dumps(validation_report, indent=2, default=str),
            artifact_type=ArtifactType.SPECIFICATION.value,
            phase_name="specification",
            source_engine="specification-engine",
        )
        metrics.artifacts_generated += 1

        for err in validation_errors:
            if err.get("severity") == "error":
                metrics.record_warning("spec_validation", err.get("message", ""))

        await publish_custom_event(
            run_id, "spec.validated",
            f"Specification validation: {error_count} errors, {warning_count} warnings",
            severity="info" if error_count == 0 else "warning",
            data=validation_report,
        )

        return validation_report

    async def _step_create_spec_baseline(self, run_id, spec, store, metrics):
        """Step 4: Lock specification as approved baseline."""
        async with async_session_factory() as session:
            engine = SpecificationEngine(run_id, spec.project_id)
            engine._version = spec
            baseline = await engine.lock_baseline(session, locked_by="pipeline")

        await publish_custom_event(
            run_id, "spec.baseline_created",
            f"Specification v{spec.version} locked as baseline",
            data={"baseline_id": baseline.id},
        )

        return baseline

    async def _step_generate_architecture(self, run_id, project_id, project_name, spec, store, metrics):
        """Step 5: Generate architecture from specification."""
        arch = await generate_default_architecture(run_id, project_id, project_name)

        # Persist architecture artifacts
        if arch.architecture_yaml:
            await store.persist(
                name="architecture.yaml",
                content=json.dumps(arch.architecture_yaml, indent=2, default=str),
                artifact_type=ArtifactType.ARCHITECTURE.value,
                phase_name="architecture",
                source_engine="architecture-engine",
                metadata={"arch_version_id": arch.id, "version": arch.version},
            )
            metrics.artifacts_generated += 1

        if arch.architecture_md:
            await store.persist(
                name="architecture.md",
                content=arch.architecture_md,
                artifact_type=ArtifactType.ARCHITECTURE.value,
                phase_name="architecture",
                source_engine="architecture-engine",
            )
            metrics.artifacts_generated += 1

        # Persist Mermaid diagrams
        if arch.mermaid_diagrams:
            for diagram_name, diagram_content in arch.mermaid_diagrams.items():
                await store.persist(
                    name=f"{diagram_name}.mmd",
                    content=diagram_content,
                    artifact_type=ArtifactType.ARCHITECTURE.value,
                    phase_name="architecture",
                    subdir="diagrams",
                    source_engine="architecture-engine",
                )
                metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "architecture.generated",
            f"Architecture v{arch.version} generated: {len(arch.architecture_yaml.get('components', []))} components",
            data={"arch_version_id": arch.id, "version": arch.version},
        )

        return arch

    async def _step_generate_arch_constraints(self, run_id, arch, store, metrics):
        """Step 6: Generate architecture constraints."""
        constraints = arch.constraints or []
        fitness_functions = arch.fitness_functions or []

        constraints_report = {
            "constraints": constraints,
            "fitness_functions": fitness_functions,
            "total_constraints": len(constraints),
            "total_fitness_functions": len(fitness_functions),
        }

        await store.persist(
            name="architecture-constraints.json",
            content=json.dumps(constraints_report, indent=2, default=str),
            artifact_type=ArtifactType.ARCHITECTURE.value,
            phase_name="architecture",
            source_engine="architecture-engine",
        )
        metrics.artifacts_generated += 1

        for constraint in constraints:
            await publish_custom_event(
                run_id, "architecture.constraint_created",
                f"Constraint: {constraint.get('name', 'unknown')}",
                data={"constraint_id": constraint.get("id")},
            )

    async def _step_generate_adrs(self, run_id, arch, store, metrics):
        """Step 7: Generate Architecture Decision Records."""
        adrs = arch.adrs or []

        if adrs:
            adr_content = "# Architecture Decision Records\n\n"
            for adr in adrs:
                adr_content += f"## ADR-{adr.get('id', '???')}: {adr.get('title', 'Untitled')}\n\n"
                adr_content += f"**Status:** {adr.get('status', 'unknown')}\n\n"
                adr_content += f"**Context:** {adr.get('context', '')}\n\n"
                adr_content += f"**Decision:** {adr.get('decision', '')}\n\n"
                if adr.get('consequences'):
                    adr_content += "**Consequences:**\n"
                    for c in adr['consequences']:
                        adr_content += f"- {c}\n"
                    adr_content += "\n"
                adr_content += "---\n\n"

            await store.persist(
                name="ADRs.md",
                content=adr_content,
                artifact_type=ArtifactType.ARCHITECTURE.value,
                phase_name="architecture",
                source_engine="architecture-engine",
            )
            metrics.artifacts_generated += 1

        for adr in adrs:
            await publish_custom_event(
                run_id, "adr.created",
                f"ADR-{adr.get('id')}: {adr.get('title')} ({adr.get('status')})",
                data={"adr_id": adr.get("id"), "title": adr.get("title")},
            )

    async def _step_generate_governance(self, run_id, store, metrics):
        """Step 8: Generate governance policies."""
        gov_engine = GovernanceEngine(run_id)

        async with async_session_factory() as session:
            await gov_engine.seed_default_policies(session)
            policies = await gov_engine.get_policies(session)

        policies_report = {
            "total_policies": len(policies),
            "blocking": len([p for p in policies if p.is_blocking]),
            "by_category": {},
        }
        for p in policies:
            cat = p.category
            if cat not in policies_report["by_category"]:
                policies_report["by_category"][cat] = 0
            policies_report["by_category"][cat] += 1

        await store.persist(
            name="governance-policies.json",
            content=json.dumps(policies_report, indent=2, default=str),
            artifact_type=ArtifactType.GOVERNANCE.value,
            phase_name="governance",
            source_engine="governance-engine",
        )
        metrics.artifacts_generated += 1

        # Also persist individual Rego files
        for policy in policies:
            await store.persist(
                name=f"{policy.name}.rego",
                content=policy.rego_code,
                artifact_type=ArtifactType.GOVERNANCE.value,
                phase_name="governance",
                subdir="policies",
                source_engine="governance-engine",
                metadata={"policy_id": policy.id, "name": policy.name},
            )
            metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "governance.policy_generated",
            f"{len(policies)} governance policies generated",
            data={"total": len(policies), "blocking": policies_report["blocking"]},
        )

        return policies

    async def _step_evaluate_governance(self, run_id, project_id, spec, store, metrics):
        """Step 9: Evaluate governance policies."""
        gov_engine = GovernanceEngine(run_id)

        # Build evaluation input from spec artifacts
        requirements = {}
        if spec.requirements_yaml:
            for req in spec.requirements_yaml.get("requirements", []):
                requirements[req.get("id", "unknown")] = req

        input_data = {
            "artifacts": [
                {"type": "specification", "name": "requirements.yaml", "phase_name": "specification"},
                {"type": "architecture", "name": "architecture.md", "phase_name": "architecture"},
            ],
            "requirements": requirements,
            "commits": [],
            "files": [
                {"name": "README.md", "size_bytes": 100},
                {"name": "architecture.md", "size_bytes": 5000},
            ],
            "vulnerabilities": [],
            "coverage_percent": 0,
            "required_policy_ids": [],
            "evaluations": [],
        }

        async with async_session_factory() as session:
            evaluations = await gov_engine.evaluate_all_policies(session, input_data)

        passed = len([e for e in evaluations if e.decision == "pass"])
        failed = len([e for e in evaluations if e.decision == "fail"])
        warnings = len([e for e in evaluations if e.decision == "warning"])

        metrics.governance_passed = passed
        metrics.governance_failed = failed
        metrics.governance_warnings = warnings

        eval_report = {
            "total": len(evaluations),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "evaluations": [
                {
                    "policy_id": e.policy_id,
                    "decision": e.decision,
                    "findings": e.findings,
                }
                for e in evaluations
            ],
        }

        await store.persist(
            name="governance-report.json",
            content=json.dumps(eval_report, indent=2, default=str),
            artifact_type=ArtifactType.GOVERNANCE.value,
            phase_name="governance",
            source_engine="governance-engine",
        )
        metrics.artifacts_generated += 1

        # Also persist markdown report
        md_report = f"# Governance Evaluation Report\n\n"
        md_report += f"**Total:** {len(evaluations)} | **Passed:** {passed} | **Failed:** {failed} | **Warnings:** {warnings}\n\n"
        for e in evaluations:
            status = "✅" if e.decision == "pass" else "❌" if e.decision == "fail" else "⚠️"
            md_report += f"## {status} {e.policy_id}\n\n"
            md_report += f"**Decision:** {e.decision}\n\n"
            if e.findings:
                for f in e.findings:
                    md_report += f"- {f}\n"
            md_report += "\n"

        await store.persist(
            name="governance-report.md",
            content=md_report,
            artifact_type=ArtifactType.GOVERNANCE.value,
            phase_name="governance",
            source_engine="governance-engine",
        )
        metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "governance.policy_evaluated",
            f"Governance evaluation: {passed} passed, {failed} failed, {warnings} warnings",
            severity="info" if failed == 0 else "warning",
            data={"passed": passed, "failed": failed, "warnings": warnings},
        )

        return eval_report

    async def _step_generate_test_plan(self, run_id, project_id, spec, store, metrics):
        """Step 10: Generate test plan from specification."""
        requirements = []
        nfr = []
        if spec.requirements_yaml:
            requirements = spec.requirements_yaml.get("requirements", [])
            nfr = spec.requirements_yaml.get("non_functional_requirements", [])

        test_plan = await generate_test_plan_from_spec(run_id, project_id, requirements, nfr)

        # Persist test plan
        plan_data = test_plan.__dict__.copy()
        plan_data.pop("_sa_instance_state", None)
        plan_data.pop("traceability_map", None)

        await store.persist(
            name="test-plan.json",
            content=json.dumps(plan_data, indent=2, default=str),
            artifact_type=ArtifactType.TEST_PLAN.value,
            phase_name="quality",
            source_engine="test-engine",
            metadata={"test_plan_id": test_plan.id, "version": test_plan.version},
        )
        metrics.artifacts_generated += 1

        # Persist traceability map
        if test_plan.traceability_map:
            await store.persist(
                name="traceability-matrix.json",
                content=json.dumps(test_plan.traceability_map, indent=2, default=str),
                artifact_type=ArtifactType.TRACEABILITY.value,
                phase_name="quality",
                source_engine="test-engine",
            )
            metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "testplan.generated",
            f"Test plan v{test_plan.version} generated",
            data={"test_plan_id": test_plan.id},
        )

        return test_plan

    async def _step_generate_traceability(self, run_id, spec, arch, test_plan, store, metrics):
        """Step 11: Generate traceability links."""
        trace_mgr = TraceabilityManager(run_id)
        links_created = 0

        async with async_session_factory() as session:
            # Link spec → architecture
            if spec.id and arch.id:
                await trace_mgr.link(
                    session, "specification", spec.id,
                    "architecture", arch.id, "derives_from"
                )
                links_created += 1

            # Link architecture → test plan
            if arch.id and test_plan.id:
                await trace_mgr.link(
                    session, "architecture", arch.id,
                    "test_plan", test_plan.id, "validates"
                )
                links_created += 1

            # Link requirements → tests
            if test_plan.traceability_map:
                for req_id, test_ids in test_plan.traceability_map.items():
                    for test_id in test_ids:
                        await trace_mgr.link(
                            session, "requirement", req_id,
                            "test", test_id, "validates"
                        )
                        links_created += 1

        metrics.traceability_links = links_created

        # Persist traceability report
        trace_report = {
            "total_links": links_created,
            "by_type": {
                "spec_to_arch": 1,
                "arch_to_test": 1,
                "req_to_test": links_created - 2 if links_created > 2 else 0,
            },
        }

        await store.persist(
            name="traceability-report.json",
            content=json.dumps(trace_report, indent=2, default=str),
            artifact_type=ArtifactType.TRACEABILITY.value,
            phase_name="traceability",
            source_engine="traceability-engine",
        )
        metrics.artifacts_generated += 1

        await publish_custom_event(
            run_id, "traceability.linked",
            f"{links_created} traceability links created",
            data={"total_links": links_created},
        )

    async def _step_create_snapshot(self, run_id, metrics):
        """Step 13: Create system snapshot."""
        snap_mgr = SnapshotManager(run_id)

        async with async_session_factory() as session:
            snapshot = await snap_mgr.create_snapshot(session, "pre_deployment", "pipeline")

        await publish_custom_event(
            run_id, "snapshot.created",
            f"Snapshot created: {snapshot.id}",
            data={"snapshot_id": snapshot.id},
        )

        return snapshot

    async def _step_generate_evidence(self, run_id, project_id, store, metrics, gov_results):
        """Step 14: Generate evidence bundle."""
        evidence_dir = store._ensure_dir("evidence")

        # Collect all evidence files
        evidence_files = []

        # 1. Requirements trace
        req_trace = {"requirements": [], "specifications": []}
        async with async_session_factory() as session:
            specs = await session.execute(
                select(SpecificationVersion).where(SpecificationVersion.run_id == run_id)
            )
            for s in specs.scalars().all():
                req_trace["specifications"].append({
                    "id": s.id, "version": s.version, "status": s.status,
                    "content_hash": s.content_hash,
                })
        req_path = evidence_dir / "requirements_trace.json"
        req_path.write_text(json.dumps(req_trace, indent=2, default=str))
        evidence_files.append("requirements_trace.json")

        # 2. Design trace
        design_trace = {"architectures": [], "adrs": []}
        async with async_session_factory() as session:
            archs = await session.execute(
                select(ArchitectureVersion).where(ArchitectureVersion.run_id == run_id)
            )
            for a in archs.scalars().all():
                design_trace["architectures"].append({
                    "id": a.id, "version": a.version, "status": a.status,
                    "content_hash": a.content_hash,
                })
                if a.adrs:
                    design_trace["adrs"].extend(a.adrs)
        design_path = evidence_dir / "design_trace.json"
        design_path.write_text(json.dumps(design_trace, indent=2, default=str))
        evidence_files.append("design_trace.json")

        # 3. Governance trace
        gov_trace = gov_results or {}
        gov_path = evidence_dir / "governance_trace.json"
        gov_path.write_text(json.dumps(gov_trace, indent=2, default=str))
        evidence_files.append("governance_trace.json")

        # 4. Test trace
        test_trace = {"test_plans": [], "traceability": []}
        async with async_session_factory() as session:
            plans = await session.execute(
                select(TestPlan).where(TestPlan.run_id == run_id)
            )
            for p in plans.scalars().all():
                test_trace["test_plans"].append({
                    "id": p.id, "version": p.version, "status": p.status,
                })
        test_path = evidence_dir / "test_trace.json"
        test_path.write_text(json.dumps(test_trace, indent=2, default=str))
        evidence_files.append("test_trace.json")

        # 5. Artifact lineage
        manifest = store.get_manifest()
        lineage_path = evidence_dir / "artifact_lineage.json"
        lineage_path.write_text(json.dumps(manifest, indent=2, default=str))
        evidence_files.append("artifact_lineage.json")

        # 6. Run log
        async with async_session_factory() as session:
            logs = await session.execute(
                select(LogEvent).where(LogEvent.run_id == run_id).order_by(LogEvent.created_at)
            )
            log_lines = []
            for log in logs.scalars().all():
                log_lines.append(json.dumps({
                    "id": log.id,
                    "severity": log.severity,
                    "message": log.message,
                    "source_file": log.source_file,
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                }))
        log_path = evidence_dir / "run_log.jsonl"
        log_path.write_text("\n".join(log_lines))
        evidence_files.append("run_log.jsonl")

        # 7. Snapshot metadata
        async with async_session_factory() as session:
            snaps = await session.execute(
                select(RunSnapshot).where(RunSnapshot.run_id == run_id)
            )
            snap_data = []
            for s in snaps.scalars().all():
                snap_data.append({
                    "id": s.id, "type": s.snapshot_type,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                })
        snap_path = evidence_dir / "snapshot_metadata.json"
        snap_path.write_text(json.dumps(snap_data, indent=2, default=str))
        evidence_files.append("snapshot_metadata.json")

        # 8. Cost report
        async with async_session_factory() as session:
            costs = await session.execute(
                select(CostEvent).where(CostEvent.run_id == run_id)
            )
            cost_data = []
            total = 0
            for c in costs.scalars().all():
                cost_data.append({
                    "model": c.model_name, "tokens_in": c.tokens_in,
                    "tokens_out": c.tokens_out, "cost": c.estimated_cost,
                })
                total += c.estimated_cost or 0
        cost_report = {"total_cost": total, "entries": cost_data}
        cost_path = evidence_dir / "cost_report.json"
        cost_path.write_text(json.dumps(cost_report, indent=2, default=str))
        evidence_files.append("cost_report.json")

        # 9. Evidence bundle manifest
        bundle_manifest = {
            "run_id": run_id,
            "project_id": project_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": evidence_files,
            "total_files": len(evidence_files),
        }
        bundle_path = evidence_dir / "bundle_manifest.json"
        bundle_path.write_text(json.dumps(bundle_manifest, indent=2, default=str))

        # Create zip
        import zipfile
        zip_path = store.run_dir / "evidence-bundle.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in evidence_files + ["bundle_manifest.json"]:
                fpath = evidence_dir / fname
                if fpath.exists():
                    zf.write(fpath, f"evidence/{fname}")

        await publish_custom_event(
            run_id, "evidence.generated",
            f"Evidence bundle generated: {len(evidence_files)} files",
            data={"files": evidence_files, "zip_path": str(zip_path)},
        )

        return bundle_manifest

    async def _step_calculate_costs(self, run_id, metrics):
        """Step 15: Calculate and record pipeline costs."""
        async with async_session_factory() as session:
            costs = await session.execute(
                select(CostEvent).where(CostEvent.run_id == run_id)
            )
            total = sum(c.estimated_cost or 0 for c in costs.scalars().all())
            metrics.cost_total = total

        await publish_cost_event(
            run_id, "pipeline", 0, 0, total, True,
            data={"source": "pipeline_final"},
        )


# Global instance
full_pipeline = FullPipelineOrchestrator()
