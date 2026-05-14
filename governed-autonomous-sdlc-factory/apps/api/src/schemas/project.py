"""Project schemas."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = None
    description: Optional[str] = None
    idea_text: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    idea_text: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    idea_text: Optional[str]
    status: str
    github_repo_url: Optional[str]
    local_path: Optional[str]
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
