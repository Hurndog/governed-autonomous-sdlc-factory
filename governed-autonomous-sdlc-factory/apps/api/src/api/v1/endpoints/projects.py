"""Project endpoints."""
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Project
from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from src.schemas.common import PaginatedResponse

router = APIRouter()


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


@router.post("/", response_model=ProjectResponse)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    slug = body.slug or slugify(body.name)
    # Ensure unique slug
    existing = await db.execute(select(Project).where(Project.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{Project.__table__.name}"
    project = Project(
        name=body.name,
        slug=slug,
        description=body.description,
        idea_text=body.idea_text,
        config=body.config or {},
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    total = await db.execute(select(func.count(Project.id)))
    count = total.scalar()
    result = await db.execute(
        select(Project)
        .order_by(Project.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=list(items),
        total=count,
        page=page,
        page_size=page_size,
        has_next=count > page * page_size,
        has_prev=page > 1,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, body: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    return {"message": "Project deleted"}
