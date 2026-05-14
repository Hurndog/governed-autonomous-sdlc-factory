"""Deployment workflow graph."""
from langgraph.graph import StateGraph, END
from src.core.logging import get_logger

logger = get_logger("workflow.deployment")


async def node_check_gates(state):
    logger.info("Checking release gates")
    return state


async def node_generate_compose(state):
    logger.info("Generating docker-compose")
    return state


async def node_build_containers(state):
    logger.info("Building containers")
    return state


async def node_run_containers(state):
    logger.info("Running containers")
    return state


async def node_health_check(state):
    logger.info("Running health checks")
    return state


async def node_smoke_test(state):
    logger.info("Running smoke tests")
    return state


def build_deployment_graph():
    graph = StateGraph(dict)
    graph.add_node("check_gates", node_check_gates)
    graph.add_node("generate_compose", node_generate_compose)
    graph.add_node("build_containers", node_build_containers)
    graph.add_node("run_containers", node_run_containers)
    graph.add_node("health_check", node_health_check)
    graph.add_node("smoke_test", node_smoke_test)
    graph.set_entry_point("check_gates")
    graph.add_edge("check_gates", "generate_compose")
    graph.add_edge("generate_compose", "build_containers")
    graph.add_edge("build_containers", "run_containers")
    graph.add_edge("run_containers", "health_check")
    graph.add_edge("health_check", "smoke_test")
    graph.add_edge("smoke_test", END)
    return graph.compile()


deployment_graph = build_deployment_graph()
