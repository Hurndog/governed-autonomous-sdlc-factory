"""Seed demo data.

Usage: python scripts/seed_demo.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "governed-autonomous-sdlc-factory", "apps", "api"))

from src.core.database import async_session_factory
from src.core.logging import setup_logging, get_logger
from src.models import Agent, SystemSetting

setup_logging("INFO", "text")
logger = get_logger("seed_demo")

DEMO_AGENTS = [
    {"name": "AI Control Assistant", "role": "orchestrator", "description": "Main user-facing AI assistant", "model_preference": "claude-sonnet-4"},
    {"name": "Intake Agent", "role": "intake", "description": "Captures and structures user ideas", "model_preference": "local-model"},
    {"name": "Specification Agent", "role": "specification", "description": "Generates requirements and specs", "model_preference": "claude-sonnet-4"},
    {"name": "Functional Design Agent", "role": "functional_design", "description": "Creates functional design documents", "model_preference": "claude-sonnet-4"},
    {"name": "Architecture Agent", "role": "architecture", "description": "Designs technical architecture", "model_preference": "claude-sonnet-4"},
    {"name": "Governance Agent", "role": "governance", "description": "Creates governance requirements", "model_preference": "local-model"},
    {"name": "Test Design Agent", "role": "test_design", "description": "Creates test plans and cases", "model_preference": "local-model"},
    {"name": "Builder Agent", "role": "builder", "description": "Generates code", "model_preference": "claude-sonnet-4"},
    {"name": "Security Agent", "role": "security", "description": "Runs security scans", "model_preference": "local-model"},
    {"name": "Refactor Agent", "role": "refactor", "description": "Refactors code", "model_preference": "claude-sonnet-4"},
    {"name": "Documentation Agent", "role": "documentation", "description": "Generates documentation", "model_preference": "local-model"},
    {"name": "GitHub Agent", "role": "github", "description": "Manages git operations", "model_preference": "local-model"},
    {"name": "Evidence Agent", "role": "evidence", "description": "Creates evidence bundles", "model_preference": "local-model"},
    {"name": "Cost Agent", "role": "cost", "description": "Tracks costs", "model_preference": "local-model"},
    {"name": "Deployment Agent", "role": "deployment", "description": "Manages deployments", "model_preference": "local-model"},
    {"name": "Pattern Agent", "role": "pattern_extraction", "description": "Extracts patterns", "model_preference": "local-model"},
    {"name": "Memory Agent", "role": "memory", "description": "Manages memory", "model_preference": "local-model"},
    {"name": "Backlog Agent", "role": "backlog", "description": "Creates backlogs", "model_preference": "local-model"},
]

DEFAULT_SETTINGS = [
    {"key": "cost_hard_limit", "value": "50.00", "value_type": "float", "description": "Hard cost limit in USD"},
    {"key": "cost_warning_threshold", "value": "0.8", "value_type": "float", "description": "Warning at this fraction of budget"},
    {"key": "local_only_mode", "value": "true", "value_type": "boolean", "description": "Use only local models"},
    {"key": "refactor_interval", "value": "5", "value_type": "integer", "description": "Refactor every N commits"},
    {"key": "default_model_provider", "value": "local", "value_type": "string", "description": "Default model provider"},
    {"key": "test_coverage_threshold", "value": "80.0", "value_type": "float", "description": "Minimum test coverage percentage"},
    {"key": "security_block_on_critical", "value": "true", "value_type": "boolean", "description": "Block deployment on critical findings"},
    {"key": "security_block_on_high", "value": "true", "value_type": "boolean", "description": "Block deployment on high findings"},
]


async def main():
    async with async_session_factory() as session:
        # Seed agents
        for agent_data in DEMO_AGENTS:
            agent = Agent(**agent_data, allowed_tools=[], disallowed_tools=[])
            session.add(agent)
        logger.info(f"Created {len(DEMO_AGENTS)} demo agents")

        # Seed settings
        for setting_data in DEFAULT_SETTINGS:
            setting = SystemSetting(**setting_data)
            session.add(setting)
        logger.info(f"Created {len(DEFAULT_SETTINGS)} default settings")

        await session.commit()
        logger.info("Demo data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
