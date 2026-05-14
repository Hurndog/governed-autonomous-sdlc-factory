"""Evidence collection workflow graph."""
from langgraph.graph import StateGraph, END
from src.core.logging import get_logger

logger = get_logger("workflow.evidence")


async def node_collect_artifacts(state):
    logger.info("Collecting artifacts")
    return state


async def node_collect_test_results(state):
    logger.info("Collecting test results")
    return state


async def node_collect_security(state):
    logger.info("Collecting security results")
    return state


async def node_collect_governance(state):
    logger.info("Collecting governance results")
    return state


async def node_collect_costs(state):
    logger.info("Collecting cost data")
    return state


async def node_build_traceability(state):
    logger.info("Building traceability matrix")
    return state


async def node_create_bundle(state):
    logger.info("Creating evidence bundle")
    return state


def build_evidence_graph():
    graph = StateGraph(dict)
    graph.add_node("collect_artifacts", node_collect_artifacts)
    graph.add_node("collect_test_results", node_collect_test_results)
    graph.add_node("collect_security", node_collect_security)
    graph.add_node("collect_governance", node_collect_governance)
    graph.add_node("collect_costs", node_collect_costs)
    graph.add_node("build_traceability", node_build_traceability)
    graph.add_node("create_bundle", node_create_bundle)
    graph.set_entry_point("collect_artifacts")
    graph.add_edge("collect_artifacts", "collect_test_results")
    graph.add_edge("collect_test_results", "collect_security")
    graph.add_edge("collect_security", "collect_governance")
    graph.add_edge("collect_governance", "collect_costs")
    graph.add_edge("collect_costs", "build_traceability")
    graph.add_edge("build_traceability", "create_bundle")
    graph.add_edge("create_bundle", END)
    return graph.compile()


evidence_graph = build_evidence_graph()
