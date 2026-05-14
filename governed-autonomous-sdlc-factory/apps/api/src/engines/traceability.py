"""Traceability management for the Governed Autonomous SDLC Factory.

Manages the full traceability chain:
requirement → design → architecture → test → governance → code → deployment

Provides linking, querying, and validation of traceability chains.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import publish_custom_event
from src.models import TraceabilityLink, Run
from src.core.logging import get_logger

logger = get_logger("traceability")


class TraceabilityManager:
    """Manages traceability links for a run."""

    def __init__(self, run_id: str):
        self.run_id = run_id

    async def link(self, session: AsyncSession, source_type: str, source_id: str,
                   target_type: str, target_id: str, link_type: str = "implements") -> TraceabilityLink:
        """Create a traceability link."""
        # Check for existing
        result = await session.execute(
            select(TraceabilityLink).where(
                TraceabilityLink.run_id == self.run_id,
                TraceabilityLink.source_type == source_type,
                TraceabilityLink.source_id == source_id,
                TraceabilityLink.target_type == target_type,
                TraceabilityLink.target_id == target_id,
                TraceabilityLink.link_type == link_type,
            )
        )
        existing = result.scalars().first()
        if existing:
            return existing

        link = TraceabilityLink(
            run_id=self.run_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            link_type=link_type,
        )
        session.add(link)
        await session.flush()

        await publish_custom_event(
            self.run_id, "traceability.linked",
            f"Traceability: {source_type}:{source_id} --[{link_type}]--> {target_type}:{target_id}",
            data={
                "link_id": link.id,
                "source_type": source_type,
                "source_id": source_id,
                "target_type": target_type,
                "target_id": target_id,
                "link_type": link_type,
            },
        )
        return link

    async def get_chain(self, session: AsyncSession, source_type: str, source_id: str) -> list[dict]:
        """Get the full traceability chain from a source."""
        result = await session.execute(
            select(TraceabilityLink).where(
                TraceabilityLink.run_id == self.run_id,
                TraceabilityLink.source_type == source_type,
                TraceabilityLink.source_id == source_id,
            )
        )
        links = result.scalars().all()
        return [
            {
                "link_id": link.id,
                "from": f"{link.source_type}:{link.source_id}",
                "to": f"{link.target_type}:{link.target_id}",
                "type": link.link_type,
            }
            for link in links
        ]

    async def get_full_chain(self, session: AsyncSession) -> list[dict]:
        """Get all traceability links for the run."""
        result = await session.execute(
            select(TraceabilityLink).where(TraceabilityLink.run_id == self.run_id)
        )
        links = result.scalars().all()
        return [
            {
                "link_id": link.id,
                "source_type": link.source_type,
                "source_id": link.source_id,
                "target_type": link.target_type,
                "target_id": link.target_id,
                "link_type": link.link_type,
            }
            for link in links
        ]

    async def validate_coverage(self, session: AsyncSession, requirements: list[dict]) -> dict:
        """Validate that all requirements have traceability to tests."""
        result = await session.execute(
            select(TraceabilityLink).where(
                TraceabilityLink.run_id == self.run_id,
                TraceabilityLink.source_type == "requirement",
            )
        )
        links = result.scalars().all()

        covered_reqs = {link.source_id for link in links if link.target_type == "test"}
        all_req_ids = {r.get("id") for r in requirements}
        uncovered = all_req_ids - covered_reqs

        return {
            "total_requirements": len(all_req_ids),
            "covered_requirements": len(covered_reqs),
            "uncovered_requirements": list(uncovered),
            "coverage_percent": (len(covered_reqs) / len(all_req_ids) * 100) if all_req_ids else 100,
        }
