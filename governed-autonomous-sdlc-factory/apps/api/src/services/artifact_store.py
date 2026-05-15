"""Artifact persistence layer for the Cognitive Cortex.

Persists generated artifacts to:
1. Database (metadata + content preview)
2. Filesystem (full content, organized by run)
3. Structured artifact registry for lineage tracking
"""
import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.logging import get_logger
from src.core.event_bus import publish_custom_event, publish_artifact_created
from src.models import Artifact, ArtifactType, Run

logger = get_logger("artifact_store")

# Base directory for artifact storage
ARTIFACT_BASE_DIR = Path(os.environ.get("ARTIFACT_DIR", "/tmp/cortex-artifacts"))


class ArtifactStore:
    """Manages artifact persistence across database and filesystem."""

    def __init__(self, run_id: str, project_id: str):
        self.run_id = run_id
        self.project_id = project_id
        self._run_dir = ARTIFACT_BASE_DIR / run_id
        self._artifacts: list[dict] = []

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def _ensure_dir(self, subdir: str = "") -> Path:
        """Ensure directory exists and return path."""
        d = self._run_dir / subdir if subdir else self._run_dir
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    async def persist(
        self,
        name: str,
        content: str,
        artifact_type: str,
        phase_name: str = "",
        subdir: str = "",
        metadata: dict = None,
        source_engine: str = "",
        parent_artifact_id: str = None,
        task_id: str = None,
    ) -> dict:
        """Persist an artifact to filesystem and database."""
        # 1. Write to filesystem
        dir_path = self._ensure_dir(subdir)
        file_path = dir_path / name
        file_path.write_text(content, encoding="utf-8")

        # 2. Compute hashes
        content_hash = self._compute_hash(content)
        
        # Compute deterministic artifact hash (metadata-based, content-addressable)
        from src.core.hash_propagation import hash_artifact
        artifact_hash_input = {
            "artifact_type": artifact_type,
            "name": name,
            "content": content,
            "phase_name": phase_name or "",
            "metadata": {
                "phase_name": phase_name,
                "content_hash": content_hash,
                "size_bytes": len(content),
                "source_engine": source_engine,
                "parent_artifact_id": parent_artifact_id,
                "subdir": subdir,
                **(metadata or {}),
            },
        }
        from src.core.hashing import compute_hash
        artifact_hash = compute_hash(artifact_hash_input)

        # 3. Persist to database
        async with async_session_factory() as session:
            artifact = Artifact(
                run_id=self.run_id,
                name=name,
                artifact_type=artifact_type,
                phase_name=phase_name or None,
                content=content[:10000],  # Truncate for DB storage
                file_path=str(file_path),
                artifact_hash=artifact_hash,
                metadata_={
                    "phase_name": phase_name,
                    "content_hash": content_hash,
                    "artifact_hash": artifact_hash,
                    "size_bytes": len(content),
                    "source_engine": source_engine,
                    "parent_artifact_id": parent_artifact_id,
                    "subdir": subdir,
                    **(metadata or {}),
                },
            )
            session.add(artifact)
            await session.flush()

            artifact_record = {
                "id": artifact.id,
                "name": name,
                "type": artifact_type,
                "phase": phase_name,
                "file_path": str(file_path),
                "content_hash": content_hash,
                "size_bytes": len(content),
                "source_engine": source_engine,
                "parent_artifact_id": parent_artifact_id,
            }

            self._artifacts.append(artifact_record)
            await session.commit()

        # 4. Emit event
        await publish_artifact_created(
            self.run_id, name, artifact_type, phase_name,
            data={
                "artifact_id": artifact.id,
                "content_hash": content_hash,
                "size_bytes": len(content),
                "source_engine": source_engine,
            },
        )

        logger.info(f"Artifact persisted: {name} ({artifact_type}) [{len(content)} bytes]")
        return artifact_record

    async def persist_many(self, artifacts: list[dict]) -> list[dict]:
        """Persist multiple artifacts. Each dict: {name, content, type, phase, subdir, metadata, source_engine, parent_artifact_id}"""
        results = []
        for art in artifacts:
            result = await self.persist(
                name=art["name"],
                content=art["content"],
                artifact_type=art.get("type", "specification"),
                phase_name=art.get("phase", ""),
                subdir=art.get("subdir", ""),
                metadata=art.get("metadata", {}),
                source_engine=art.get("source_engine", ""),
                parent_artifact_id=art.get("parent_artifact_id"),
            )
            results.append(result)
        return results

    def get_manifest(self) -> dict:
        """Get manifest of all persisted artifacts."""
        return {
            "run_id": self.run_id,
            "project_id": self.project_id,
            "artifact_count": len(self._artifacts),
            "artifacts": self._artifacts,
            "storage_dir": str(self._run_dir),
        }

    async def write_manifest(self) -> dict:
        """Write manifest to filesystem and return it."""
        manifest = self.get_manifest()
        manifest_path = self._ensure_dir() / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
        return manifest
