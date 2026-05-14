"""Artifact schemas for the Governed Autonomous SDLC Factory API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Types of artifacts produced during SDLC runs."""

    SOURCE_CODE = "source_code"
    DOCUMENTATION = "documentation"
    TEST = "test"
    CONFIG = "config"
    SCHEMA = "schema"
    DIAGRAM = "diagram"
    REPORT = "report"
    EVIDENCE = "evidence"
    DIFF = "diff"
    LOG = "log"
    REQUIREMENTS = "requirements"
    DESIGN_DOC = "design_doc"
    DEPLOYMENT_PLAN = "deployment_plan"
    REVIEW_REPORT = "review_report"
    OTHER = "other"


class ArtifactCreate(BaseModel):
    """Schema for creating a new artifact."""

    run_id: str = Field(..., description="Run ID.")
    phase_id: str | None = Field(None, description="Phase ID.")
    name: str = Field(
        ..., min_length=1, max_length=500, description="Artifact name."
    )
    artifact_type: ArtifactType = Field(
        ..., description="Type of artifact."
    )
    content: str | None = Field(
        None, description="Text content of the artifact."
    )
    file_path: str | None = Field(
        None, description="File path if stored on disk."
    )
    mime_type: str | None = Field(
        None, description="MIME type of the artifact."
    )
    size_bytes: int | Field(
        None, ge=0, description="Size in bytes."
    )
    version: int = Field(
        default=1, ge=1, description="Artifact version number."
    )
    previous_version_id: str | None = Field(
        None, description="ID of the previous version."
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Arbitrary metadata."
    )
    tags: list[str] = Field(default_factory=list, description="Artifact tags.")


class ArtifactResponse(BaseModel):
    """Artifact response schema."""

    id: str = Field(..., description="Artifact ID (UUID).")
    run_id: str = Field(..., description="Run ID.")
    phase_id: str | None = Field(None)
    name: str = Field(..., description="Artifact name.")
    artifact_type: ArtifactType = Field(...)
    content: str | None = Field(None)
    file_path: str | None = Field(None)
    mime_type: str | None = Field(None)
    size_bytes: int | None = Field(None)
    version: int = Field(default=1)
    previous_version_id: str | None = Field(None)
    metadata: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    created_by: str | None = Field(None, description="Agent or user who created it.")


class ArtifactContentResponse(BaseModel):
    """Response for artifact content retrieval."""

    id: str = Field(...)
    name: str = Field(...)
    artifact_type: ArtifactType = Field(...)
    content: str | None = Field(None)
    mime_type: str | None = Field(None)
    size_bytes: int | None = Field(None)
