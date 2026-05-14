"""Specification Engine for the Governed Autonomous SDLC Factory.

Generates structured, machine-readable specification artifacts:
- requirements.yaml (structured requirements with IDs, types, priorities)
- functional_spec.md (human-readable functional specification)
- acceptance_criteria.yaml (testable acceptance criteria per requirement)
- non_functional_requirements.yaml (performance, security, scalability, etc.)
- assumptions.md (explicit assumptions made during specification)
- cross-domain validation (consistency checks between artifacts)
- baseline versioning + revision support
- inferred/default/user-provided tagging per requirement

NO generic marketing text. NO fluff. Structured, traceable, validated.
"""
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import (
    EventBusManager, Event, publish_artifact_created,
    publish_governance_finding, publish_custom_event
)
from src.models import (
    SpecificationVersion, Artifact, ArtifactType, TraceabilityLink,
    ArtifactBaseline, ArtifactDiff, Run, Project
)
from src.core.logging import get_logger

logger = get_logger("spec_engine")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class Requirement:
    """Single structured requirement."""
    def __init__(self, req_id: str, title: str, description: str,
                 req_type: str = "functional", priority: str = "must",
                 source: str = "user-provided", acceptance_criteria: list = None,
                 dependencies: list = None, tags: list = None):
        self.id = req_id
        self.title = title
        self.description = description
        self.type = req_type  # functional, non-functional, constraint, assumption
        self.priority = priority  # must, should, could, wont
        self.source = source  # user-provided, inferred, default
        self.acceptance_criteria = acceptance_criteria or []
        self.dependencies = dependencies or []
        self.tags = tags or []
        self.traceability_id = f"REQ-{req_id}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "source": self.source,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "traceability_id": self.traceability_id,
        }


class SpecificationEngine:
    """Core specification engine that generates all spec artifacts."""

    def __init__(self, run_id: str, project_id: str):
        self.run_id = run_id
        self.project_id = project_id
        self.bus = EventBusManager.get_bus(run_id)
        self.requirements: list[Requirement] = []
        self.nfr: list[Requirement] = []
        self.assumptions: list[str] = []
        self.validation_errors: list[dict] = []
        self._version: Optional[SpecificationVersion] = None

    # -----------------------------------------------------------------
    # REQUIREMENT INGESTION
    # -----------------------------------------------------------------

    def add_requirement(self, req: Requirement):
        """Add a requirement to the specification."""
        self.requirements.append(req)
        if req.type == "non-functional":
            self.nfr.append(req)

    def add_assumption(self, text: str):
        """Add an explicit assumption."""
        self.assumptions.append(text)

    def ingest_from_dict(self, data: dict):
        """Ingest requirements from a structured dict (e.g. from API)."""
        for req_data in data.get("requirements", []):
            req = Requirement(
                req_id=req_data.get("id", str(uuid.uuid4())[:8]),
                title=req_data["title"],
                description=req_data["description"],
                req_type=req_data.get("type", "functional"),
                priority=req_data.get("priority", "must"),
                source=req_data.get("source", "user-provided"),
                acceptance_criteria=req_data.get("acceptance_criteria", []),
                dependencies=req_data.get("dependencies", []),
                tags=req_data.get("tags", []),
            )
            self.add_requirement(req)

        for nfr_data in data.get("non_functional_requirements", []):
            nfr = Requirement(
                req_id=nfr_data.get("id", f"NFR-{str(uuid.uuid4())[:6]}"),
                title=nfr_data["title"],
                description=nfr_data["description"],
                req_type="non-functional",
                priority=nfr_data.get("priority", "must"),
                source=nfr_data.get("source", "user-provided"),
                acceptance_criteria=nfr_data.get("acceptance_criteria", []),
                tags=nfr_data.get("tags", []),
            )
            self.nfr.append(nfr)
            self.requirements.append(nfr)

        for assumption in data.get("assumptions", []):
            self.add_assumption(assumption)

    # -----------------------------------------------------------------
    # CROSS-DOMAIN VALIDATION
    # -----------------------------------------------------------------

    def validate(self) -> list[dict]:
        """Run cross-domain validation on the specification."""
        self.validation_errors = []
        req_ids = set()

        for req in self.requirements:
            # Check duplicate IDs
            if req.id in req_ids:
                self.validation_errors.append({
                    "code": "DUP_REQ_ID",
                    "severity": "error",
                    "message": f"Duplicate requirement ID: {req.id}",
                    "requirement_id": req.id,
                })
            req_ids.add(req.id)

            # Check empty title/description
            if not req.title or len(req.title.strip()) < 3:
                self.validation_errors.append({
                    "code": "EMPTY_TITLE",
                    "severity": "error",
                    "message": f"Requirement {req.id}: title too short or empty",
                    "requirement_id": req.id,
                })
            if not req.description or len(req.description.strip()) < 10:
                self.validation_errors.append({
                    "code": "EMPTY_DESC",
                    "severity": "warning",
                    "message": f"Requirement {req.id}: description too short (< 10 chars)",
                    "requirement_id": req.id,
                })

            # Check acceptance criteria exist for must/should
            if req.priority in ("must", "should") and not req.acceptance_criteria:
                self.validation_errors.append({
                    "code": "MISSING_AC",
                    "severity": "warning",
                    "message": f"Requirement {req.id} ({req.priority}): no acceptance criteria defined",
                    "requirement_id": req.id,
                })

            # Check dependency references
            for dep in req.dependencies:
                if dep not in req_ids and dep != req.id:
                    # Will be checked after all ingested
                    pass

        # Second pass: dependency resolution
        for req in self.requirements:
            for dep in req.dependencies:
                if dep not in req_ids:
                    self.validation_errors.append({
                        "code": "UNRESOLVED_DEP",
                        "severity": "error",
                        "message": f"Requirement {req.id}: unresolved dependency '{dep}'",
                        "requirement_id": req.id,
                    })
                if dep == req.id:
                    self.validation_errors.append({
                        "code": "SELF_DEP",
                        "severity": "error",
                        "message": f"Requirement {req.id}: self-referencing dependency",
                        "requirement_id": req.id,
                    })

        # Check at least one requirement exists
        if not self.requirements:
            self.validation_errors.append({
                "code": "NO_REQUIREMENTS",
                "severity": "error",
                "message": "Specification contains no requirements",
            })

        # Check NFR coverage
        nfr_categories = set()
        for nfr in self.nfr:
            nfr_categories.update(nfr.tags)
        expected_nfr = {"performance", "security", "scalability", "reliability", "usability"}
        missing_nfr = expected_nfr - nfr_categories
        if missing_nfr:
            self.validation_errors.append({
                "code": "MISSING_NFR_CATEGORY",
                "severity": "warning",
                "message": f"Missing NFR categories: {', '.join(missing_nfr)}",
            })

        return self.validation_errors

    # -----------------------------------------------------------------
    # ARTIFACT GENERATION
    # -----------------------------------------------------------------

    def generate_requirements_yaml(self) -> dict:
        """Generate structured requirements.yaml content."""
        return {
            "metadata": {
                "version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
                "project_id": self.project_id,
                "total_requirements": len(self.requirements),
                "total_nfr": len(self.nfr),
            },
            "requirements": [r.to_dict() for r in self.requirements if r.type == "functional"],
            "non_functional_requirements": [r.to_dict() for r in self.nfr],
            "summary": {
                "must": len([r for r in self.requirements if r.priority == "must"]),
                "should": len([r for r in self.requirements if r.priority == "should"]),
                "could": len([r for r in self.requirements if r.priority == "could"]),
                "wont": len([r for r in self.requirements if r.priority == "wont"]),
                "user_provided": len([r for r in self.requirements if r.source == "user-provided"]),
                "inferred": len([r for r in self.requirements if r.source == "inferred"]),
                "default": len([r for r in self.requirements if r.source == "default"]),
            },
        }

    def generate_acceptance_criteria(self) -> dict:
        """Generate acceptance_criteria.yaml content."""
        criteria = {}
        for req in self.requirements:
            if req.acceptance_criteria:
                criteria[req.id] = {
                    "title": req.title,
                    "priority": req.priority,
                    "criteria": [
                        {
                            "id": f"AC-{req.id}-{i+1}",
                            "description": ac,
                            "type": "functional" if req.type == "functional" else "non-functional",
                        }
                        for i, ac in enumerate(req.acceptance_criteria)
                    ],
                }
        return {
            "metadata": {
                "version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_criteria": sum(len(v["criteria"]) for v in criteria.values()),
            },
            "acceptance_criteria": criteria,
        }

    def generate_nfr_yaml(self) -> dict:
        """Generate non_functional_requirements.yaml content."""
        categories = {}
        for nfr in self.nfr:
            primary_tag = nfr.tags[0] if nfr.tags else "general"
            if primary_tag not in categories:
                categories[primary_tag] = []
            categories[primary_tag].append(nfr.to_dict())

        return {
            "metadata": {
                "version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_nfr": len(self.nfr),
            },
            "categories": categories,
        }

    def generate_functional_spec_md(self) -> str:
        """Generate functional_spec.md — structured, not fluffy."""
        lines = [
            "# Functional Specification",
            "",
            f"**Run ID:** `{self.run_id}`",
            f"**Project ID:** `{self.project_id}`",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Version:** 1.0",
            "",
            "---",
            "",
            "## Overview",
            "",
            f"This specification contains **{len(self.requirements)} requirements** "
            f"({len([r for r in self.requirements if r.type == 'functional'])} functional, "
            f"{len(self.nfr)} non-functional).",
            "",
            "| Priority | Count |",
            "|----------|-------|",
            f"| Must | {len([r for r in self.requirements if r.priority == 'must'])} |",
            f"| Should | {len([r for r in self.requirements if r.priority == 'should'])} |",
            f"| Could | {len([r for r in self.requirements if r.priority == 'could'])} |",
            f"| Won't | {len([r for r in self.requirements if r.priority == 'wont'])} |",
            "",
            "---",
            "",
            "## Functional Requirements",
            "",
        ]

        func_reqs = [r for r in self.requirements if r.type == "functional"]
        for req in sorted(func_reqs, key=lambda r: ("must", "should", "could", "wont").index(r.priority) if r.priority in ("must", "should", "could", "wont") else 99):
            source_badge = f"`{req.source}`"
            lines.extend([
                f"### {req.traceability_id}: {req.title}",
                "",
                f"**Priority:** {req.priority} | **Source:** {source_badge}",
                "",
                req.description,
                "",
            ])
            if req.acceptance_criteria:
                lines.append("**Acceptance Criteria:**")
                for i, ac in enumerate(req.acceptance_criteria, 1):
                    lines.append(f"- [ ] AC-{req.id}-{i}: {ac}")
                lines.append("")
            if req.dependencies:
                lines.append(f"**Dependencies:** {', '.join(f'`{d}`' for d in req.dependencies)}")
                lines.append("")
            if req.tags:
                lines.append(f"**Tags:** {', '.join(f'`{t}`' for t in req.tags)}")
                lines.append("")
            lines.append("---")
            lines.append("")

        if self.nfr:
            lines.extend([
                "## Non-Functional Requirements",
                "",
            ])
            for nfr in self.nfr:
                lines.extend([
                    f"### {nfr.traceability_id}: {nfr.title}",
                    "",
                    f"**Priority:** {nfr.priority} | **Source:** `{nfr.source}`",
                    "",
                    nfr.description,
                    "",
                ])
                if nfr.acceptance_criteria:
                    lines.append("**Acceptance Criteria:**")
                    for i, ac in enumerate(nfr.acceptance_criteria, 1):
                        lines.append(f"- [ ] AC-{nfr.id}-{i}: {ac}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        if self.validation_errors:
            lines.extend([
                "## Validation Results",
                "",
                f"**{len(self.validation_errors)} issues found:**",
                "",
                "| Code | Severity | Message | Requirement |",
                "|------|----------|---------|-------------|",
            ])
            for err in self.validation_errors:
                lines.append(f"| {err['code']} | {err['severity']} | {err['message']} | {err.get('requirement_id', 'N/A')} |")
            lines.append("")

        return "\n".join(lines)

    def generate_assumptions_md(self) -> str:
        """Generate assumptions.md."""
        lines = [
            "# Assumptions",
            "",
            f"**Run ID:** `{self.run_id}`",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
        ]
        if self.assumptions:
            for i, assumption in enumerate(self.assumptions, 1):
                lines.append(f"{i}. {assumption}")
        else:
            lines.append("_No explicit assumptions recorded._")
        lines.append("")
        return "\n".join(lines)

    # -----------------------------------------------------------------
    # PERSISTENCE
    # -----------------------------------------------------------------

    async def persist(self, session: AsyncSession, generated_by: str = "spec-engine") -> SpecificationVersion:
        """Persist the specification to the database."""
        # Compute content hash
        content = json.dumps(self.generate_requirements_yaml(), sort_keys=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Get next version number
        result = await session.execute(
            select(SpecificationVersion)
            .where(SpecificationVersion.run_id == self.run_id)
            .order_by(SpecificationVersion.version.desc())
        )
        latest = result.scalars().first()
        version_num = (latest.version + 1) if latest else 1
        parent_id = latest.id if latest else None

        spec = SpecificationVersion(
            run_id=self.run_id,
            project_id=self.project_id,
            version=version_num,
            parent_version_id=parent_id,
            status="draft",
            requirements_yaml=self.generate_requirements_yaml(),
            functional_spec=self.generate_functional_spec_md(),
            acceptance_criteria=self.generate_acceptance_criteria(),
            non_functional_requirements=self.generate_nfr_yaml(),
            assumptions=self.generate_assumptions_md(),
            validation_errors=self.validation_errors,
            generated_by=generated_by,
            content_hash=content_hash,
        )
        session.add(spec)
        await session.flush()

        # Create artifact records
        artifacts_data = [
            ("requirements.yaml", ArtifactType.SPECIFICATION, json.dumps(self.generate_requirements_yaml())),
            ("functional_spec.md", ArtifactType.SPECIFICATION, self.generate_functional_spec_md()),
            ("acceptance_criteria.yaml", ArtifactType.SPECIFICATION, json.dumps(self.generate_acceptance_criteria())),
            ("non_functional_requirements.yaml", ArtifactType.SPECIFICATION, json.dumps(self.generate_nfr_yaml())),
            ("assumptions.md", ArtifactType.SPECIFICATION, self.generate_assumptions_md()),
        ]

        for name, atype, content in artifacts_data:
            artifact = Artifact(
                run_id=self.run_id,
                name=name,
                type=atype,
                phase_name="specification",
                content=content[:10000],  # Truncate for DB storage
                metadata_={"spec_version_id": spec.id, "version": version_num},
            )
            session.add(artifact)

        await session.commit()
        self._version = spec

        # Publish events
        await publish_custom_event(
            self.run_id, "spec.generated",
            f"Specification v{version_num} generated: {len(self.requirements)} requirements, {len(self.validation_errors)} validation issues",
            severity="info" if not any(e["severity"] == "error" for e in self.validation_errors) else "warning",
            data={"spec_version_id": spec.id, "version": version_num, "requirement_count": len(self.requirements)},
        )

        for err in self.validation_errors:
            await publish_custom_event(
                self.run_id, "spec.validation_issue",
                f"[{err['code']}] {err['message']}",
                severity=err["severity"],
                data={"code": err["code"], "requirement_id": err.get("requirement_id")},
            )

        logger.info(f"Specification v{version_num} persisted: {len(self.requirements)} requirements")
        return spec

    # -----------------------------------------------------------------
    # BASELINE LOCKING
    # -----------------------------------------------------------------

    async def lock_baseline(self, session: AsyncSession, locked_by: str = "governance") -> ArtifactBaseline:
        """Lock the current specification as an approved baseline."""
        if not self._version:
            raise ValueError("No specification version to lock. Call persist() first.")

        # Update version status
        self._version.status = "locked"
        self._version.locked_at = datetime.now(timezone.utc)
        self._version.approved_by = locked_by

        # Create baseline record
        baseline = ArtifactBaseline(
            run_id=self.run_id,
            artifact_type="specification",
            artifact_id=self._version.id,
            version=self._version.version,
            locked_by=locked_by,
            content_hash=self._version.content_hash,
        )
        session.add(baseline)
        await session.commit()

        await publish_custom_event(
            self.run_id, "spec.baseline_locked",
            f"Specification v{self._version.version} locked as baseline by {locked_by}",
            data={"spec_version_id": self._version.id, "version": self._version.version},
        )

        return baseline

    # -----------------------------------------------------------------
    # DIFFING
    # -----------------------------------------------------------------

    async def diff_versions(self, session: AsyncSession, from_version_id: str, to_version_id: str) -> dict:
        """Compute diff between two specification versions."""
        from_spec = await session.get(SpecificationVersion, from_version_id)
        to_spec = await session.get(SpecificationVersion, to_version_id)

        if not from_spec or not to_spec:
            raise ValueError("One or both specification versions not found")

        from_reqs = {r["id"]: r for r in (from_spec.requirements_yaml or {}).get("requirements", [])}
        to_reqs = {r["id"]: r for r in (to_spec.requirements_yaml or {}).get("requirements", [])}

        added = []
        removed = []
        modified = []

        for rid, req in to_reqs.items():
            if rid not in from_reqs:
                added.append(req)
            elif req != from_reqs[rid]:
                modified.append({
                    "id": rid,
                    "from": from_reqs[rid],
                    "to": req,
                })

        for rid, req in from_reqs.items():
            if rid not in to_reqs:
                removed.append(req)

        diff_data = {
            "from_version": from_spec.version,
            "to_version": to_spec.version,
            "added": added,
            "removed": removed,
            "modified": modified,
            "summary": {
                "total_added": len(added),
                "total_removed": len(removed),
                "total_modified": len(modified),
            },
        }

        # Persist diff
        diff_record = ArtifactDiff(
            run_id=self.run_id,
            artifact_type="specification",
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            diff_data=diff_data,
        )
        session.add(diff_record)
        await session.commit()

        return diff_data


# =============================================================================
# CONVENIENCE: Generate default specification for a project
# =============================================================================

async def generate_default_specification(run_id: str, project_id: str, project_name: str,
                                          project_description: str) -> SpecificationVersion:
    """Generate a default specification from a project description."""
    engine = SpecificationEngine(run_id, project_id)

    # Generate inferred requirements from project description
    engine.add_assumption(f"Project '{project_name}' is a software system requiring standard SDLC practices.")
    engine.add_assumption("All external integrations require authentication and authorization.")
    engine.add_assumption("The system must be deployable to a containerized environment.")
    engine.add_assumption("All user-facing features require input validation and error handling.")

    # Core functional requirements (inferred defaults)
    default_reqs = [
        Requirement("AUTH-001", "User Authentication", "The system shall provide secure user authentication with email/password and support for OAuth2 providers.", "functional", "must", "default",
                    ["Users can register with email and password", "Users can log in with valid credentials", "Users can authenticate via OAuth2 (Google, GitHub)", "Failed login attempts are rate-limited"]),
        Requirement("AUTH-002", "Authorization & Access Control", "The system shall enforce role-based access control (RBAC) for all protected resources.", "functional", "must", "default",
                    ["Roles can be assigned to users", "API endpoints enforce role permissions", "Unauthorized access returns 403"]),
        Requirement("API-001", "REST API", "The system shall expose a RESTful API with JSON request/response format.", "functional", "must", "default",
                    ["All endpoints return JSON", "API follows REST conventions", "API versioning is supported via URL path"]),
        Requirement("API-002", "API Documentation", "The system shall provide OpenAPI/Swagger documentation for all API endpoints.", "functional", "should", "default",
                    ["OpenAPI spec is auto-generated", "All endpoints have descriptions", "Request/response schemas are documented"]),
        Requirement("DATA-001", "Data Persistence", "The system shall persist all application data in a relational database with migration support.", "functional", "must", "default",
                    ["Database schema is versioned", "Migrations are reversible", "Data integrity constraints are enforced"]),
        Requirement("DATA-002", "Data Validation", "The system shall validate all input data before processing or storage.", "functional", "must", "default",
                    ["Invalid input returns 400 with error details", "SQL injection is prevented", "XSS is prevented in all user inputs"]),
        Requirement("ERR-001", "Error Handling", "The system shall provide consistent error responses with appropriate HTTP status codes.", "functional", "must", "default",
                    ["All errors return structured JSON", "500 errors do not leak stack traces", "Error codes are documented"]),
        Requirement("LOG-001", "Application Logging", "The system shall log all significant events with appropriate severity levels.", "functional", "should", "default",
                    ["Logs include timestamp, severity, and context", "Logs are structured (JSON format)", "Sensitive data is redacted in logs"]),
    ]

    # Non-functional requirements
    default_nfr = [
        Requirement("PERF-001", "Response Time", "API endpoints shall respond within 200ms for 95th percentile under normal load.", "non-functional", "must", "default",
                    ["P95 latency < 200ms at 100 RPS", "P99 latency < 500ms at 100 RPS"], ["performance"]),
        Requirement("PERF-002", "Throughput", "The system shall handle at least 1000 concurrent users.", "non-functional", "should", "default",
                    ["System supports 1000 concurrent connections", "No degradation under sustained load"], ["performance", "scalability"]),
        Requirement("SEC-001", "Data Encryption", "All sensitive data shall be encrypted at rest and in transit.", "non-functional", "must", "default",
                    ["TLS 1.3 for all connections", "AES-256 for data at rest", "Passwords hashed with bcrypt/argon2"], ["security"]),
        Requirement("SEC-002", "Security Headers", "The system shall implement standard security headers (CSP, HSTS, X-Frame-Options).", "non-functional", "must", "default",
                    ["CSP header is present", "HSTS header is present", "X-Frame-Options is DENY"], ["security"]),
        Requirement("REL-001", "Availability", "The system shall target 99.9% uptime.", "non-functional", "should", "default",
                    ["Health check endpoint exists", "Graceful shutdown is supported", "No single point of failure"], ["reliability"]),
        Requirement("USA-001", "Usability", "The API shall provide clear, consistent error messages and documentation.", "non-functional", "should", "default",
                    ["Error messages are human-readable", "API docs are accessible", "Examples are provided for all endpoints"], ["usability"]),
    ]

    for req in default_reqs:
        engine.add_requirement(req)
    for nfr in default_nfr:
        engine.add_requirement(nfr)

    # Validate
    engine.validate()

    # Persist
    async with async_session_factory() as session:
        spec = await engine.persist(session, generated_by="spec-engine")
        return spec
