"""Memory endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import MemoryItem
from src.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/search")
async def search_memory(
    q: str = Query(..., min_length=1),
    memory_type: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(MemoryItem).where(MemoryItem.content.ilike(f"%{q}%"))
    if memory_type:
        query = query.where(MemoryItem.memory_type == memory_type)
    if project_id:
        query = query.where(MemoryItem.project_id == project_id)
    result = await db.execute(query.order_by(MemoryItem.created_at.desc()).limit(limit))
    items = result.scalars().all()
    return {"items": [
        {"id": m.id, "type": m.memory_type, "key": m.key, "content": m.content, "source": m.source}
        for m in items
    ]}


@router.get("/by-project/{project_id}")
async def list_memory_by_project(
    project_id: str,
    memory_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MemoryItem).where(MemoryItem.project_id == project_id)
    if memory_type:
        query = query.where(MemoryItem.memory_type == memory_type)
    result = await db.execute(query.order_by(MemoryItem.created_at.desc()))
    items = result.scalars().all()
    return {"items": [
        {"id": m.id, "type": m.memory_type, "key": m.key, "content": m.content}
        for m in items
    ]}


@router.post("/")
async def create_memory(
    key: str,
    content: str,
    memory_type: str = "project",
    project_id: Optional[str] = None,
    source: str = "system",
    db: AsyncSession = Depends(get_db),
):
    item = MemoryItem(
        key=key, content=content, memory_type=memory_type,
        project_id=project_id, source=source,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return {"id": item.id, "key": key, "type": memory_type}
