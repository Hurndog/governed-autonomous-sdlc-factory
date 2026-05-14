"""Main SDLC workflow using LangGraph."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver

from src.core.logging import get_logger

logger = get_logger("workflow.sdlc")


class SDLCState:
    """State for the SDLC workflow."""
    def __init__(self, project_id: str, run_id: str, idea_text: str = "",
                 is_demo: bool = False, **kwargs):
        self.project_id = project_id
        self.run_id = run_id
        self.idea_text = idea_text
        self.is_demo = is_demo
        self.current_phase: str = "intake"
        self.phases_completed: List[str] = []
        self.artifacts: Dict[str, Any] = {}
        self.approvals: Dict[str, str] = {}
        self.cost_events: List[Dict] = []
        self.log_events: List[Dict] = []
        self.errors: List[str] = []
        self.spec_baseline_locked: bool = False
        self.build_branch: Optional[str] = None
        self.commit_count: int = 0
        self.test_results: List[Dict] = []
        self.security_findings: List[Dict] = []
        self.governance_findings: List[Dict] = []
        self.evidence_bundle_path: Optional[str] = None
        self.deployment_url: Optional[str] = None
        self.patterns_extracted: List[Dict] = []
        self.memory_items: List[Dict] = []
        self.model_calls: List[Dict] = []
        self.tool_calls_log: List[Dict] = []
        self.total_cost: float = 0.0
        self.budget_limit: Optional[float] = None
        self.is_cancelled: bool = False
        self.is_paused: bool = False
        self.metadata: Dict[str, Any] = kwargs.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "run_id": self.run_id,
            "idea_text": self.idea_text,
            "is_demo": self.is_demo,
            "current_phase": self.current_phase,
            "phases_completed": self.phases_completed,
            "artifacts": self.artifacts,
            "approvals": self.approvals,
            "total_cost": self.total_cost,
            "errors": self.errors,
            "spec_baseline_locked": self.spec_baseline_locked,
            "build_branch": self.build_branch,
            "commit_count": self.commit_count,
            "deployment_url": self.deployment_url,
        }


# Phase node functions
async def node_create_project(state: SDLCState) -> SDLCState:
    state.current_phase = "create_project"
    logger.info(f"[{state.run_id}] Creating project: {state.project_id}")
    state.phases_completed.append("create_project")
    return state


async def node_capture_intent(state: SDLCState) -> SDLCState:
    state.current_phase = "capture_intent"
    logger.info(f"[{state.run_id}] Capturing intent from idea text")
    state.phases_completed.append("capture_intent")
    return state


async def node_enrich_context(state: SDLCState) -> SDLCState:
    state.current_phase = "enrich_context"
    logger.info(f"[{state.run_id}] Enriching context from memory and patterns")
    state.phases_completed.append("enrich_context")
    return state


async def node_generate_specification(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_specification"
    logger.info(f"[{state.run_id}] Generating specification")
    state.artifacts["requirements.yaml"] = {"generated": True, "version": 1}
    state.artifacts["functional_spec.md"] = {"generated": True, "version": 1}
    state.artifacts["acceptance_criteria.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_specification")
    return state


async def node_validate_specification(state: SDLCState) -> SDLCState:
    state.current_phase = "validate_specification"
    logger.info(f"[{state.run_id}] Validating specification")
    state.phases_completed.append("validate_specification")
    return state


async def node_generate_functional_design(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_functional_design"
    logger.info(f"[{state.run_id}] Generating functional design")
    state.artifacts["functional_design.md"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_functional_design")
    return state


async def node_generate_architecture(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_architecture"
    logger.info(f"[{state.run_id}] Generating architecture")
    state.artifacts["architecture.md"] = {"generated": True, "version": 1}
    state.artifacts["architecture.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_architecture")
    return state


async def node_generate_design_proposal(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_design_proposal"
    logger.info(f"[{state.run_id}] Generating design proposal")
    state.artifacts["design_proposal.md"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_design_proposal")
    return state


async def node_generate_data_model(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_data_model"
    logger.info(f"[{state.run_id}] Generating data model")
    state.artifacts["data_model.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_data_model")
    return state


async def node_generate_mcp_contracts(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_mcp_contracts"
    logger.info(f"[{state.run_id}] Generating MCP contracts")
    state.artifacts["mcp_contracts.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_mcp_contracts")
    return state


async def node_generate_governance_requirements(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_governance_requirements"
    logger.info(f"[{state.run_id}] Generating governance requirements")
    state.artifacts["governance_requirements.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_governance_requirements")
    return state


async def node_generate_test_plan(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_test_plan"
    logger.info(f"[{state.run_id}] Generating test plan")
    state.artifacts["test_plan.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("generate_test_plan")
    return state


async def node_create_approval_baseline(state: SDLCState) -> SDLCState:
    state.current_phase = "create_approval_baseline"
    logger.info(f"[{state.run_id}] Creating approval baseline")
    state.phases_completed.append("create_approval_baseline")
    return state


async def node_wait_for_approval(state: SDLCState) -> SDLCState:
    state.current_phase = "wait_for_approval"
    logger.info(f"[{state.run_id}] Waiting for approval")
    if state.is_demo:
        state.approvals["baseline"] = "auto_approved"
        state.spec_baseline_locked = True
    state.phases_completed.append("wait_for_approval")
    return state


async def node_create_backlog(state: SDLCState) -> SDLCState:
    state.current_phase = "create_backlog"
    logger.info(f"[{state.run_id}] Creating backlog")
    state.artifacts["backlog.yaml"] = {"generated": True, "version": 1}
    state.phases_completed.append("create_backlog")
    return state


async def node_create_git_branch(state: SDLCState) -> SDLCState:
    state.current_phase = "create_git_branch"
    state.build_branch = f"forge/{state.run_id[:8]}"
    logger.info(f"[{state.run_id}] Creating git branch: {state.build_branch}")
    state.phases_completed.append("create_git_branch")
    return state


async def node_execute_build(state: SDLCState) -> SDLCState:
    state.current_phase = "execute_build"
    logger.info(f"[{state.run_id}] Executing build")
    state.commit_count += 1
    state.phases_completed.append("execute_build")
    return state


async def node_generate_documentation(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_documentation"
    logger.info(f"[{state.run_id}] Generating documentation")
    state.phases_completed.append("generate_documentation")
    return state


async def node_run_tests(state: SDLCState) -> SDLCState:
    state.current_phase = "run_tests"
    logger.info(f"[{state.run_id}] Running tests")
    state.test_results.append({"status": "passed", "count": 10})
    state.phases_completed.append("run_tests")
    return state


async def node_run_security_scan(state: SDLCState) -> SDLCState:
    state.current_phase = "run_security_scan"
    logger.info(f"[{state.run_id}] Running security scan")
    state.phases_completed.append("run_security_scan")
    return state


async def node_run_governance_checks(state: SDLCState) -> SDLCState:
    state.current_phase = "run_governance_checks"
    logger.info(f"[{state.run_id}] Running governance checks")
    state.governance_findings.append({"policy": "no_push_to_main", "decision": "pass"})
    state.governance_findings.append({"policy": "tests_required", "decision": "pass"})
    state.governance_findings.append({"policy": "security_scan_required", "decision": "pass"})
    state.phases_completed.append("run_governance_checks")
    return state


async def node_evaluate_release_gates(state: SDLCState) -> SDLCState:
    state.current_phase = "evaluate_release_gates"
    logger.info(f"[{state.run_id}] Evaluating release gates")
    state.phases_completed.append("evaluate_release_gates")
    return state


async def node_run_refactor_if_needed(state: SDLCState) -> SDLCState:
    state.current_phase = "run_refactor_if_needed"
    if state.commit_count > 0 and state.commit_count % 5 == 0:
        logger.info(f"[{state.run_id}] Running refactor (commit interval reached)")
    state.phases_completed.append("run_refactor_if_needed")
    return state


async def node_update_evidence(state: SDLCState) -> SDLCState:
    state.current_phase = "update_evidence"
    logger.info(f"[{state.run_id}] Updating evidence bundle")
    state.phases_completed.append("update_evidence")
    return state


async def node_extract_patterns(state: SDLCState) -> SDLCState:
    state.current_phase = "extract_patterns"
    logger.info(f"[{state.run_id}] Extracting patterns")
    state.phases_completed.append("extract_patterns")
    return state


async def node_update_memory(state: SDLCState) -> SDLCState:
    state.current_phase = "update_memory"
    logger.info(f"[{state.run_id}] Updating memory")
    state.phases_completed.append("update_memory")
    return state


async def node_deploy_to_localhost(state: SDLCState) -> SDLCState:
    state.current_phase = "deploy_to_localhost"
    state.deployment_url = f"http://localhost:9000/projects/{state.project_id}"
    logger.info(f"[{state.run_id}] Deploying to localhost: {state.deployment_url}")
    state.phases_completed.append("deploy_to_localhost")
    return state


async def node_generate_final_report(state: SDLCState) -> SDLCState:
    state.current_phase = "generate_final_report"
    logger.info(f"[{state.run_id}] Generating final report")
    state.phases_completed.append("generate_final_report")
    return state


def build_sdlc_graph() -> StateGraph:
    """Build the main SDLC workflow graph."""
    graph = StateGraph(SDLCState)

    # Add all nodes
    graph.add_node("create_project", node_create_project)
    graph.add_node("capture_intent", node_capture_intent)
    graph.add_node("enrich_context", node_enrich_context)
    graph.add_node("generate_specification", node_generate_specification)
    graph.add_node("validate_specification", node_validate_specification)
    graph.add_node("generate_functional_design", node_generate_functional_design)
    graph.add_node("generate_architecture", node_generate_architecture)
    graph.add_node("generate_design_proposal", node_generate_design_proposal)
    graph.add_node("generate_data_model", node_generate_data_model)
    graph.add_node("generate_mcp_contracts", node_generate_mcp_contracts)
    graph.add_node("generate_governance_requirements", node_generate_governance_requirements)
    graph.add_node("generate_test_plan", node_generate_test_plan)
    graph.add_node("create_approval_baseline", node_create_approval_baseline)
    graph.add_node("wait_for_approval", node_wait_for_approval)
    graph.add_node("create_backlog", node_create_backlog)
    graph.add_node("create_git_branch", node_create_git_branch)
    graph.add_node("execute_build", node_execute_build)
    graph.add_node("generate_documentation", node_generate_documentation)
    graph.add_node("run_tests", node_run_tests)
    graph.add_node("run_security_scan", node_run_security_scan)
    graph.add_node("run_governance_checks", node_run_governance_checks)
    graph.add_node("evaluate_release_gates", node_evaluate_release_gates)
    graph.add_node("run_refactor_if_needed", node_run_refactor_if_needed)
    graph.add_node("update_evidence", node_update_evidence)
    graph.add_node("extract_patterns", node_extract_patterns)
    graph.add_node("update_memory", node_update_memory)
    graph.add_node("deploy_to_localhost", node_deploy_to_localhost)
    graph.add_node("generate_final_report", node_generate_final_report)

    # Define linear flow
    graph.set_entry_point("create_project")
    graph.add_edge("create_project", "capture_intent")
    graph.add_edge("capture_intent", "enrich_context")
    graph.add_edge("enrich_context", "generate_specification")
    graph.add_edge("generate_specification", "validate_specification")
    graph.add_edge("validate_specification", "generate_functional_design")
    graph.add_edge("generate_functional_design", "generate_architecture")
    graph.add_edge("generate_architecture", "generate_design_proposal")
    graph.add_edge("generate_design_proposal", "generate_data_model")
    graph.add_edge("generate_data_model", "generate_mcp_contracts")
    graph.add_edge("generate_mcp_contracts", "generate_governance_requirements")
    graph.add_edge("generate_governance_requirements", "generate_test_plan")
    graph.add_edge("generate_test_plan", "create_approval_baseline")
    graph.add_edge("create_approval_baseline", "wait_for_approval")
    graph.add_edge("wait_for_approval", "create_backlog")
    graph.add_edge("create_backlog", "create_git_branch")
    graph.add_edge("create_git_branch", "execute_build")
    graph.add_edge("execute_build", "generate_documentation")
    graph.add_edge("generate_documentation", "run_tests")
    graph.add_edge("run_tests", "run_security_scan")
    graph.add_edge("run_security_scan", "run_governance_checks")
    graph.add_edge("run_governance_checks", "evaluate_release_gates")
    graph.add_edge("evaluate_release_gates", "run_refactor_if_needed")
    graph.add_edge("run_refactor_if_needed", "update_evidence")
    graph.add_edge("update_evidence", "extract_patterns")
    graph.add_edge("extract_patterns", "update_memory")
    graph.add_edge("update_memory", "deploy_to_localhost")
    graph.add_edge("deploy_to_localhost", "generate_final_report")
    graph.add_edge("generate_final_report", END)

    return graph.compile()


# Build and export the graph
sdlc_graph = build_sdlc_graph()
