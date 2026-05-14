"""Project service."""
import re
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Project


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, description: str = None, idea_text: str = None, slug: str = None, config: dict = None) -> Project:
        base_slug = slug or slugify(name)
        # Ensure unique slug
        existing = await self.db.execute(select(Project).where(Project.slug == base_slug))
        final_slug = base_slug
        counter = 1
        while existing.scalar_one_or_none():
            final_slug = f"{base_slug}-{counter}"
            existing = await self.db.execute(select(Project).where(Project.slug == final_slug))
            counter += 1

        project = Project(
            name=name,
            slug=final_slug,
            description=description,
            idea_text=idea_text,
            config=config or {},
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def get(self, project_id: str) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def list_all(self, page: int = 1, page_size: int = 50) -> tuple:
        total = await self.db.execute(select(func.count(Project.id)))
        count = total.scalar()
        result = await self.db.execute(
            select(Project).order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return result.scalars().all(), count

    async def update(self, project_id: str, **kwargs) -> Optional[Project]:
        project = await self.get(project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: str) -> bool:
        project = await self.get(project_id)
        if not project:
            return False
        await self.db.delete(project)
        return True
