"""Agent endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import Agent

router = APIRouter()


@router.get("/")
async def list_agents(is_active: Optional[bool] = None, db: AsyncSession = Depends(get_db)):
    query = select(Agent)
    if is_active is not None:
        query = query.where(Agent.is_active == is_active)
    result = await db.execute(query.order_by(Agent.name))
    return list(result.scalars().all())


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/")
async def create_agent(
    name: str,
    role: str,
    description: str = "",
    model_preference: str = "",
    max_retries: int = 3,
    db: AsyncSession = Depends(get_db),
):
    agent = Agent(
        name=name, role=role, description=description,
        model_preference=model_preference, max_retries=max_retries,
        allowed_tools=[], disallowed_tools=[],
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return agent


@router.patch("/{agent_id}")
async def update_agent(agent_id: str, name: Optional[str] = None, role: Optional[str] = None,
                        description: Optional[str] = None, model_preference: Optional[str] = None,
                        max_retries: Optional[int] = None, is_active: Optional[bool] = None,
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field in ["name", "role", "description", "model_preference", "max_retries", "is_active"]:
        val = locals()[field]
        if val is not None:
            setattr(agent, field, val)
    await db.flush()
    return agent
