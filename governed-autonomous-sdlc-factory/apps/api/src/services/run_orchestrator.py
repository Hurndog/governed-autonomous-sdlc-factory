"""Run service with event bus integration and workflow execution."""
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.logging import get_logger
from src.core.event_bus import EventBusManager, publish_custom_event
from src.core.safety_guards import SafetyGuard, GuardActivationError, GuardStatus
from src.core.config import settings
from src.models import Run, RunStatus, Phase, Project
from src.services.run_service import RunService
from src.services.phase_service import PhaseService
from src.services.project_service import ProjectService
from workflows.sdlc_graph import build_sdlc_graph, SDLCState

logger = get_logger("run_orchestrator")


class RunOrchestrator:
    """Orchestrates SDLC runs with event broadcasting, persistence, and safety guards."""

    def __init__(self):
        self._active_runs: Dict[str, asyncio.Task] = {}
        self._safety_guards: Dict[str, SafetyGuard] = {}

    async def start_run(self, project_id: str, name: str, idea_text: str = "",
                        budget_limit: float = None, is_demo: bool = False) -> Run:
        """Start a new SDLC run."""
        async with async_session_factory() as session:
            run_service = RunService(session)
            run = await run_service.create(
                project_id=project_id,
                name=name,
                budget_limit=budget_limit,
                is_demo=is_demo,
            )
            await session.commit()

        # Initialize event bus and safety guard for this run
        EventBusManager.get_bus(run.id)
        self._safety_guards[run.id] = SafetyGuard(run.id)

        # Start workflow in background with pipeline timeout
        task = asyncio.create_task(
            self._execute_workflow_with_timeout(run.id, project_id, idea_text, is_demo)
        )
        self._active_runs[run.id] = task

        return run

    async def _execute_workflow_with_timeout(self, run_id: str, project_id: str, idea_text: str, is_demo: bool):
        """Execute workflow with pipeline-level timeout."""
        try:
            await asyncio.wait_for(
                self._execute_workflow(run_id, project_id, idea_text, is_demo),
                timeout=settings.pipeline_timeout_seconds,
            )
        except asyncio.TimeoutError:
            guard = self._safety_guards.get(run_id)
            if guard:
                guard._activate(
                    GuardStatus.STOPPED_BY_PIPELINE_TIMEOUT,
                    guard_name="pipeline_timeout",
                    limit=f"{settings.pipeline_timeout_seconds}s",
                    observed="timeout",
                    message=f"Pipeline timed out after {settings.pipeline_timeout_seconds}s",
                    recoverable=False,
                )
            await self._transition_run(run_id, RunStatus.FAILED.value)
            await publish_custom_event(run_id, "run.failed", f"Pipeline timed out after {settings.pipeline_timeout_seconds}s", severity="error")
        except GuardActivationError as e:
            logger.warning(f"Run {run_id} stopped by guard: {e.status}")
            await self._transition_run(run_id, RunStatus.FAILED.value)
        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}", exc_info=True)
            await self._transition_run(run_id, RunStatus.FAILED.value)
            await publish_custom_event(run_id, "run.failed", f"Run failed: {e}", severity="error", data={"error": str(e)})
        finally:
            self._active_runs.pop(run_id, None)
            self._safety_guards.pop(run_id, None)

    async def _execute_workflow(self, run_id: str, project_id: str, idea_text: str, is_demo: bool):
        """Execute the full SDLC workflow with per-phase safety checks."""
        guard = self._safety_guards.get(run_id)
        if not guard:
            guard = SafetyGuard(run_id)
            self._safety_guards[run_id] = guard

        try:
            # Transition to running
            await self._transition_run(run_id, RunStatus.RUNNING.value)

            await publish_custom_event(
                run_id, "run.started",
                f"Run started: {run_id}",
                data={"project_id": project_id, "is_demo": is_demo},
            )

            # Build initial state
            state = SDLCState(
                project_id=project_id,
                run_id=run_id,
                idea_text=idea_text,
                is_demo=is_demo,
            )

            # Execute each phase with safety checks
            phases = [
                "create_project", "capture_intent", "enrich_context",
                "generate_specification", "validate_specification",
                "generate_functional_design", "generate_architecture",
                "generate_design_proposal", "generate_data_model",
                "generate_mcp_contracts", "generate_governance_requirements",
                "generate_test_plan", "create_approval_baseline",
                "wait_for_approval", "create_backlog", "create_git_branch",
                "execute_build", "generate_documentation", "run_tests",
                "run_security_scan", "run_governance_checks",
                "evaluate_release_gates", "run_refactor_if_needed",
                "update_evidence", "extract_patterns", "update_memory",
                "deploy_to_localhost", "generate_final_report",
            ]

            graph = build_sdlc_graph()

            # Execute via LangGraph with safety wrapper
            guard.begin_phase("langgraph_execution")
            try:
                result = await asyncio.wait_for(
                    graph.ainvoke(state),
                    timeout=settings.pipeline_timeout_seconds,
                )
            except asyncio.TimeoutError:
                guard._activate(
                    GuardStatus.STOPPED_BY_PIPELINE_TIMEOUT,
                    guard_name="pipeline_timeout",
                    limit=f"{settings.pipeline_timeout_seconds}s",
                    observed="timeout",
                    message="LangGraph execution timed out",
                    recoverable=False,
                )
                raise GuardActivationError(guard)
            finally:
                guard.end_phase()

            # Check all guards post-execution
            status = guard.check_all()
            if status:
                raise GuardActivationError(guard)

            # Mark run as completed
            await self._transition_run(run_id, RunStatus.COMPLETED.value)

            await publish_custom_event(
                run_id, "run.completed",
                f"Run completed: {len(result.phases_completed)}/28 phases",
                data={"total_cost": result.total_cost, "artifacts": len(result.artifacts)},
            )

        except asyncio.CancelledError:
            await self._transition_run(run_id, RunStatus.CANCELLED.value)
            await publish_custom_event(run_id, "run.cancelled", "Run was cancelled", severity="warning")
            raise

        except GuardActivationError:
            await self._transition_run(run_id, RunStatus.FAILED.value)
            raise

        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}", exc_info=True)
            await self._transition_run(run_id, RunStatus.FAILED.value)
            await publish_custom_event(run_id, "run.failed", f"Run failed: {e}", severity="error", data={"error": str(e)})
            raise

    async def _transition_run(self, run_id: str, status: str):
        """Transition run status safely."""
        try:
            async with async_session_factory() as session:
                run_service = RunService(session)
                await run_service.transition(run_id, status)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to transition run {run_id} to {status}: {e}")

    async def pause_run(self, run_id: str):
        """Pause a running run."""
        if run_id in self._active_runs:
            await publish_custom_event(run_id, "run.pause_requested", "Pause requested", severity="warning")

    async def cancel_run(self, run_id: str):
        """Cancel a running run."""
        if run_id in self._active_runs:
            self._active_runs[run_id].cancel()
            await publish_custom_event(run_id, "run.cancelled", "Run cancelled", severity="warning")


# Global orchestrator instance
orchestrator = RunOrchestrator()
