"""Run schemas."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=255)
    budget_limit: Optional[float] = None
    is_demo: bool = False


class RunUpdate(BaseModel):
    status: Optional[str] = None
    current_phase: Optional[str] = None
    branch_name: Optional[str] = None
    total_cost: Optional[float] = None


class RunResponse(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    branch_name: Optional[str]
    current_phase: Optional[str]
    total_cost: float
    budget_limit: Optional[float]
    is_demo: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RunStatusResponse(BaseModel):
    id: str
    status: str
    current_phase: Optional[str]
    total_cost: float
    active_model: Optional[str] = None
    deployment_status: Optional[str] = None


class RunListResponse(BaseModel):
    items: List[RunResponse]
    total: int
