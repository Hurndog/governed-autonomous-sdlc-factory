"""Pattern endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Pattern
from src.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict])
async def list_patterns(
    pattern_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Pattern)
    if pattern_type:
        query = query.where(Pattern.pattern_type == pattern_type)
    total = await db.execute(select(func.count()).select_from(query.subquery()))
    count = total.scalar()
    result = await db.execute(
        query.order_by(Pattern.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=[{"id": p.id, "name": p.name, "type": p.pattern_type, "problem": p.problem_solved} for p in items],
        total=count,
        page=page,
        page_size=page_size,
        has_next=count > page * page_size,
        has_prev=page > 1,
    )


@router.get("/{pattern_id}")
async def get_pattern(pattern_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return {
        "id": pattern.id, "name": pattern.name, "type": pattern.pattern_type,
        "problem_solved": pattern.problem_solved, "applicability": pattern.applicability,
        "implementation_notes": pattern.implementation_notes, "source_project": pattern.source_project,
        "related_files": pattern.related_files, "evidence_reference": pattern.evidence_reference,
        "cost_profile": pattern.cost_profile, "success_notes": pattern.success_notes,
    }


@router.post("/")
async def create_pattern(
    name: str,
    pattern_type: str,
    problem_solved: str = "",
    applicability: str = "",
    implementation_notes: str = "",
    source_project: str = "",
    db: AsyncSession = Depends(get_db),
):
    pattern = Pattern(
        name=name, pattern_type=pattern_type, problem_solved=problem_solved,
        applicability=applicability, implementation_notes=implementation_notes,
        source_project=source_project,
    )
    db.add(pattern)
    await db.flush()
    await db.refresh(pattern)
    return {"id": pattern.id, "name": name, "type": pattern_type}
