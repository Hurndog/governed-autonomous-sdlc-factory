"""Refactor workflow graph."""
from langgraph.graph import StateGraph, END
from src.core.logging import get_logger

logger = get_logger("workflow.refactor")


async def node_check_debt(state):
    logger.info("Checking technical debt")
    return state


async def node_generate_plan(state):
    logger.info("Generating refactor plan")
    return state


async def node_create_branch(state):
    logger.info("Creating refactor branch")
    return state


async def node_apply_refactors(state):
    logger.info("Applying refactors")
    return state


async def node_run_regression(state):
    logger.info("Running regression tests")
    return state


async def node_commit_refactors(state):
    logger.info("Committing refactors")
    return state


def build_refactor_graph():
    graph = StateGraph(dict)
    graph.add_node("check_debt", node_check_debt)
    graph.add_node("generate_plan", node_generate_plan)
    graph.add_node("create_branch", node_create_branch)
    graph.add_node("apply_refactors", node_apply_refactors)
    graph.add_node("run_regression", node_run_regression)
    graph.add_node("commit_refactors", node_commit_refactors)
    graph.set_entry_point("check_debt")
    graph.add_edge("check_debt", "generate_plan")
    graph.add_edge("generate_plan", "create_branch")
    graph.add_edge("create_branch", "apply_refactors")
    graph.add_edge("apply_refactors", "run_regression")
    graph.add_edge("run_regression", "commit_refactors")
    graph.add_edge("commit_refactors", END)
    return graph.compile()


refactor_graph = build_refactor_graph()
