"""Run service with event bus integration and workflow execution."""
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.logging import get_logger
from src.core.event_bus import EventBusManager, publish_custom_event
from src.models import Run, RunStatus, Phase, Project
from src.services.run_service import RunService
from src.services.phase_service import PhaseService
from src.services.project_service import ProjectService
from workflows.sdlc_graph import build_sdlc_graph, SDLCState

logger = get_logger("run_orchestrator")


class RunOrchestrator:
    """Orchestrates SDLC runs with event broadcasting and persistence."""

    def __init__(self):
        self._active_runs: Dict[str, asyncio.Task] = {}

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

        # Initialize event bus for this run
        EventBusManager.get_bus(run.id)

        # Start workflow in background
        task = asyncio.create_task(
            self._execute_workflow(run.id, project_id, idea_text, is_demo)
        )
        self._active_runs[run.id] = task

        return run

    async def _execute_workflow(self, run_id: str, project_id: str, idea_text: str, is_demo: bool):
        """Execute the full SDLC workflow."""
        try:
            # Transition to running
            async with async_session_factory() as session:
                run_service = RunService(session)
                await run_service.transition(run_id, RunStatus.RUNNING.value)
                await session.commit()

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

            # Execute each phase sequentially (simplified — no LangGraph checkpointing for now)
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

            # Execute via LangGraph
            result = await graph.ainvoke(state)

            # Mark run as completed
            async with async_session_factory() as session:
                run_service = RunService(session)
                await run_service.transition(run_id, RunStatus.COMPLETED.value)
                await session.commit()

            await publish_custom_event(
                run_id, "run.completed",
                f"Run completed: {len(result.phases_completed)}/28 phases",
                data={"total_cost": result.total_cost, "artifacts": len(result.artifacts)},
            )

        except asyncio.CancelledError:
            async with async_session_factory() as session:
                run_service = RunService(session)
                await run_service.transition(run_id, RunStatus.CANCELLED.value)
                await session.commit()
            await publish_custom_event(run_id, "run.cancelled", "Run was cancelled", severity="warning")

        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}", exc_info=True)
            async with async_session_factory() as session:
                run_service = RunService(session)
                await run_service.transition(run_id, RunStatus.FAILED.value)
                await session.commit()
            await publish_custom_event(run_id, "run.failed", f"Run failed: {e}", severity="error", data={"error": str(e)})

        finally:
            self._active_runs.pop(run_id, None)

    async def pause_run(self, run_id: str):
        """Pause a running run."""
        if run_id in self._active_runs:
            # Note: True pausing requires checkpoint support
            await publish_custom_event(run_id, "run.pause_requested", "Pause requested", severity="warning")

    async def cancel_run(self, run_id: str):
        """Cancel a running run."""
        if run_id in self._active_runs:
            self._active_runs[run_id].cancel()
            await publish_custom_event(run_id, "run.cancelled", "Run cancelled", severity="warning")


# Global orchestrator instance
orchestrator = RunOrchestrator()
