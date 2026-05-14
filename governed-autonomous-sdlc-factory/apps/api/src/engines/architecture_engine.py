"""Architecture Engine for the Governed Autonomous SDLC Factory.

Generates structured architecture artifacts:
- architecture.yaml (machine-readable architecture definition)
- architecture.md (human-readable architecture document)
- Mermaid diagrams (component, sequence, deployment)
- ADRs (Architecture Decision Records)
- Architecture constraints
- Architecture fitness functions
- Architecture drift metadata

All artifacts are validated against generated code structure.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.core.event_bus import (
    EventBusManager, Event, publish_artifact_created, publish_custom_event
)
from src.models import (
    ArchitectureVersion, Artifact, ArtifactType, TraceabilityLink,
    ArtifactBaseline, ArtifactDiff, Run, Project
)
from src.core.logging import get_logger

logger = get_logger("arch_engine")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class ArchitectureComponent:
    """Single architecture component."""
    def __init__(self, name: str, component_type: str, description: str,
                 responsibilities: list = None, dependencies: list = None,
                 technologies: list = None):
        self.id = f"COMP-{name.lower().replace(' ', '-')}"
        self.name = name
        self.type = component_type  # service, module, layer, database, queue, cache, gateway
        self.description = description
        self.responsibilities = responsibilities or []
        self.dependencies = dependencies or []
        self.technologies = technologies or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "dependencies": self.dependencies,
            "technologies": self.technologies,
        }


class ADR:
    """Architecture Decision Record."""
    def __init__(self, adr_id: str, title: str, context: str, decision: str,
                 consequences: list = None, status: str = "accepted",
                 alternatives: list = None):
        self.id = adr_id
        self.title = title
        self.context = context
        self.decision = decision
        self.consequences = consequences or []
        self.status = status  # proposed, accepted, deprecated, superseded
        self.alternatives = alternatives or []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "context": self.context,
            "decision": self.decision,
            "consequences": self.consequences,
            "status": self.status,
            "alternatives": self.alternatives,
            "created_at": self.created_at,
        }


class ArchitectureEngine:
    """Core architecture engine that generates all architecture artifacts."""

    def __init__(self, run_id: str, project_id: str):
        self.run_id = run_id
        self.project_id = project_id
        self.bus = EventBusManager.get_bus(run_id)
        self.components: list[ArchitectureComponent] = []
        self.adrs: list[ADR] = []
        self.constraints: list[dict] = []
        self.fitness_functions: list[dict] = []
        self.drift_metadata: dict = {}
        self._version: Optional[ArchitectureVersion] = None

    # -----------------------------------------------------------------
    # COMPONENT MANAGEMENT
    # -----------------------------------------------------------------

    def add_component(self, component: ArchitectureComponent):
        self.components.append(component)

    def add_adr(self, adr: ADR):
        self.adrs.append(adr)

    def add_constraint(self, name: str, description: str, enforcement: str = "build_time"):
        self.constraints.append({
            "id": f"CONST-{name.lower().replace(' ', '-')}",
            "name": name,
            "description": description,
            "enforcement": enforcement,  # build_time, runtime, review
        })

    def add_fitness_function(self, name: str, description: str, metric: str,
                              threshold: str, current_value: str = None):
        self.fitness_functions.append({
            "id": f"FF-{name.lower().replace(' ', '-')}",
            "name": name,
            "description": description,
            "metric": metric,
            "threshold": threshold,
            "current_value": current_value,
            "status": "unknown" if current_value is None else (
                "pass" if self._check_threshold(current_value, threshold) else "fail"
            ),
        })

    def _check_threshold(self, value: str, threshold: str) -> bool:
        """Simple threshold check. Supports '>', '<', '>=', '<=', '=='."""
        try:
            for op in [">=", "<=", ">", "<", "=="]:
                if threshold.startswith(op):
                    threshold_val = float(threshold[len(op):].strip())
                    value_val = float(value)
                    if op == ">=": return value_val >= threshold_val
                    if op == "<=": return value_val <= threshold_val
                    if op == ">": return value_val > threshold_val
                    if op == "<": return value_val < threshold_val
                    if op == "==": return value_val == threshold_val
            return True
        except (ValueError, TypeError):
            return True

    # -----------------------------------------------------------------
    # ARTIFACT GENERATION
    # -----------------------------------------------------------------

    def generate_architecture_yaml(self) -> dict:
        """Generate architecture.yaml — machine-readable architecture definition."""
        return {
            "metadata": {
                "version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
                "project_id": self.project_id,
                "total_components": len(self.components),
            },
            "system": {
                "name": "Governed Autonomous SDLC Factory",
                "description": "Autonomous software engineering runtime system",
                "architecture_style": "microservices",
                "communication_patterns": ["REST", "WebSocket", "Message Queue"],
            },
            "components": [c.to_dict() for c in self.components],
            "layers": self._group_by_layer(),
            "data_flows": self._derive_data_flows(),
            "constraints": self.constraints,
            "fitness_functions": self.fitness_functions,
        }

    def _group_by_layer(self) -> dict:
        """Group components by architectural layer."""
        layers = {}
        for comp in self.components:
            layer = self._infer_layer(comp)
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp.to_dict())
        return layers

    def _infer_layer(self, comp: ArchitectureComponent) -> str:
        """Infer architectural layer from component type."""
        layer_map = {
            "gateway": "presentation",
            "service": "application",
            "module": "domain",
            "database": "infrastructure",
            "queue": "infrastructure",
            "cache": "infrastructure",
        }
        return layer_map.get(comp.type, "application")

    def _derive_data_flows(self) -> list[dict]:
        """Derive data flows from component dependencies."""
        flows = []
        for comp in self.components:
            for dep in comp.dependencies:
                flows.append({
                    "from": comp.id,
                    "to": dep,
                    "type": "dependency",
                })
        return flows

    def generate_architecture_md(self) -> str:
        """Generate architecture.md — structured architecture document."""
        lines = [
            "# Architecture Document",
            "",
            f"**Run ID:** `{self.run_id}`",
            f"**Project ID:** `{self.project_id}`",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "---",
            "",
            "## System Overview",
            "",
            f"This system follows a **microservices architecture** with {len(self.components)} components.",
            "",
            "## Architecture Layers",
            "",
        ]

        layers = self._group_by_layer()
        for layer_name, components in layers.items():
            lines.extend([
                f"### {layer_name.title()} Layer",
                "",
            ])
            for comp in components:
                lines.extend([
                    f"#### {comp['name']} (`{comp['id']}`)",
                    "",
                    comp["description"],
                    "",
                ])
                if comp["responsibilities"]:
                    lines.append("**Responsibilities:**")
                    for r in comp["responsibilities"]:
                        lines.append(f"- {r}")
                    lines.append("")
                if comp["technologies"]:
                    lines.append(f"**Technologies:** {', '.join(comp['technologies'])}")
                    lines.append("")
                if comp["dependencies"]:
                    lines.append(f"**Depends on:** {', '.join(f'`{d}`' for d in comp['dependencies'])}")
                    lines.append("")

        if self.constraints:
            lines.extend([
                "---",
                "",
                "## Architecture Constraints",
                "",
                "| ID | Name | Enforcement | Description |",
                "|----|------|-------------|-------------|",
            ])
            for c in self.constraints:
                lines.append(f"| {c['id']} | {c['name']} | {c['enforcement']} | {c['description']} |")
            lines.append("")

        if self.fitness_functions:
            lines.extend([
                "---",
                "",
                "## Architecture Fitness Functions",
                "",
                "| ID | Name | Metric | Threshold | Current | Status |",
                "|----|------|--------|-----------|---------|--------|",
            ])
            for ff in self.fitness_functions:
                status_icon = "✅" if ff["status"] == "pass" else "❌" if ff["status"] == "fail" else "❓"
                lines.append(f"| {ff['id']} | {ff['name']} | {ff['metric']} | {ff['threshold']} | {ff.get('current_value', 'N/A')} | {status_icon} {ff['status']} |")
            lines.append("")

        if self.adrs:
            lines.extend([
                "---",
                "",
                "## Architecture Decision Records",
                "",
            ])
            for adr in self.adrs:
                lines.extend([
                    f"### ADR-{adr.id}: {adr.title}",
                    "",
                    f"**Status:** {adr.status}",
                    "",
                    f"**Context:** {adr.context}",
                    "",
                    f"**Decision:** {adr.decision}",
                    "",
                ])
                if adr.consequences:
                    lines.append("**Consequences:**")
                    for c in adr.consequences:
                        lines.append(f"- {c}")
                    lines.append("")
                if adr.alternatives:
                    lines.append("**Alternatives Considered:**")
                    for alt in adr.alternatives:
                        lines.append(f"- {alt}")
                    lines.append("")

        return "\n".join(lines)

    def generate_mermaid_diagrams(self) -> dict:
        """Generate Mermaid diagrams: component, sequence, deployment."""
        diagrams = {}

        # Component diagram
        comp_lines = ["graph TD"]
        for comp in self.components:
            safe_id = comp.id.replace("-", "_")
            comp_lines.append(f'    {safe_id}["{comp.name}<br/><small>{comp.type}</small>"]')
        for comp in self.components:
            safe_id = comp.id.replace("-", "_")
            for dep in comp.dependencies:
                dep_id = dep.replace("-", "_")
                comp_lines.append(f"    {safe_id} --> {dep_id}")
        diagrams["component"] = "\n".join(comp_lines)

        # Sequence diagram (typical request flow)
        seq_lines = [
            "sequenceDiagram",
            "    participant Client",
            "    participant API",
            "    participant Service",
            "    participant Database",
            "",
            "    Client->>API: HTTP Request",
            "    API->>Service: Process Request",
            "    Service->>Database: Query Data",
            "    Database-->>Service: Result",
            "    Service-->>API: Response",
            "    API-->>Client: HTTP Response",
        ]
        diagrams["sequence"] = "\n".join(seq_lines)

        # Deployment diagram
        deploy_lines = [
            "graph LR",
            "    subgraph Client Tier",
            "        Web[Web Browser]",
            "        Mobile[Mobile App]",
            "    end",
            "",
            "    subgraph Application Tier",
            "        API[API Gateway]",
            "        Auth[Auth Service]",
            "        Core[Core Service]",
            "    end",
            "",
            "    subgraph Data Tier",
            "        DB[(PostgreSQL)]",
            "        Cache[(Redis)]",
            "        Queue[Message Queue]",
            "    end",
            "",
            "    Web --> API",
            "    Mobile --> API",
            "    API --> Auth",
            "    API --> Core",
            "    Core --> DB",
            "    Core --> Cache",
            "    Core --> Queue",
        ]
        diagrams["deployment"] = "\n".join(deploy_lines)

        return diagrams

    # -----------------------------------------------------------------
    # PERSISTENCE
    # -----------------------------------------------------------------

    async def persist(self, session: AsyncSession, generated_by: str = "arch-engine") -> ArchitectureVersion:
        """Persist architecture to database."""
        content = json.dumps(self.generate_architecture_yaml(), sort_keys=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        result = await session.execute(
            select(ArchitectureVersion)
            .where(ArchitectureVersion.run_id == self.run_id)
            .order_by(ArchitectureVersion.version.desc())
        )
        latest = result.scalars().first()
        version_num = (latest.version + 1) if latest else 1
        parent_id = latest.id if latest else None

        mermaid = self.generate_mermaid_diagrams()

        arch = ArchitectureVersion(
            run_id=self.run_id,
            project_id=self.project_id,
            version=version_num,
            parent_version_id=parent_id,
            status="draft",
            architecture_yaml=self.generate_architecture_yaml(),
            architecture_md=self.generate_architecture_md(),
            mermaid_diagrams=mermaid,
            adrs=[a.to_dict() for a in self.adrs],
            constraints=self.constraints,
            fitness_functions=self.fitness_functions,
            drift_metadata=self.drift_metadata,
            generated_by=generated_by,
            content_hash=content_hash,
        )
        session.add(arch)
        await session.flush()

        # Create artifact records
        artifacts_data = [
            ("architecture.yaml", ArtifactType.ARCHITECTURE, json.dumps(self.generate_architecture_yaml())),
            ("architecture.md", ArtifactType.ARCHITECTURE, self.generate_architecture_md()),
            ("diagrams/component.mmd", ArtifactType.ARCHITECTURE, mermaid.get("component", "")),
            ("diagrams/sequence.mmd", ArtifactType.ARCHITECTURE, mermaid.get("sequence", "")),
            ("diagrams/deployment.mmd", ArtifactType.ARCHITECTURE, mermaid.get("deployment", "")),
        ]

        for name, atype, content in artifacts_data:
            artifact = Artifact(
                run_id=self.run_id,
                name=name,
                type=atype,
                phase_name="architecture",
                content=content[:10000],
                metadata_={"arch_version_id": arch.id, "version": version_num},
            )
            session.add(artifact)

        await session.commit()
        self._version = arch

        await publish_custom_event(
            self.run_id, "architecture.generated",
            f"Architecture v{version_num} generated: {len(self.components)} components, {len(self.adrs)} ADRs",
            data={"arch_version_id": arch.id, "version": version_num, "component_count": len(self.components)},
        )

        for adr in self.adrs:
            await publish_custom_event(
                self.run_id, "adr.created",
                f"ADR-{adr.id}: {adr.title} ({adr.status})",
                data={"adr_id": adr.id, "title": adr.title, "status": adr.status},
            )

        logger.info(f"Architecture v{version_num} persisted: {len(self.components)} components")
        return arch

    # -----------------------------------------------------------------
    # BASELINE LOCKING
    # -----------------------------------------------------------------

    async def lock_baseline(self, session: AsyncSession, locked_by: str = "governance") -> ArtifactBaseline:
        if not self._version:
            raise ValueError("No architecture version to lock. Call persist() first.")
        self._version.status = "locked"
        self._version.locked_at = datetime.now(timezone.utc)
        self._version.approved_by = locked_by

        baseline = ArtifactBaseline(
            run_id=self.run_id,
            artifact_type="architecture",
            artifact_id=self._version.id,
            version=self._version.version,
            locked_by=locked_by,
            content_hash=self._version.content_hash,
        )
        session.add(baseline)
        await session.commit()

        await publish_custom_event(
            self.run_id, "architecture.baseline_locked",
            f"Architecture v{self._version.version} locked as baseline",
            data={"arch_version_id": self._version.id, "version": self._version.version},
        )
        return baseline

    # -----------------------------------------------------------------
    # DRIFT DETECTION
    # -----------------------------------------------------------------

    def detect_drift(self, current_state: dict) -> dict:
        """Detect architecture drift between designed and actual state."""
        drift = {
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "drift_items": [],
            "severity": "none",
        }

        designed_components = {c.id: c for c in self.components}
        actual_components = current_state.get("components", {})

        # Check for missing components
        for comp_id, comp in designed_components.items():
            if comp_id not in actual_components:
                drift["drift_items"].append({
                    "type": "missing_component",
                    "component_id": comp_id,
                    "severity": "error",
                    "message": f"Designed component '{comp.name}' not found in actual system",
                })

        # Check for unauthorized components
        for comp_id in actual_components:
            if comp_id not in designed_components:
                drift["drift_items"].append({
                    "type": "unauthorized_component",
                    "component_id": comp_id,
                    "severity": "warning",
                    "message": f"Component '{comp_id}' exists but is not in architecture design",
                })

        # Check dependency drift
        for comp in self.components:
            actual_deps = set(actual_components.get(comp.id, {}).get("dependencies", []))
            designed_deps = set(comp.dependencies)
            extra_deps = actual_deps - designed_deps
            missing_deps = designed_deps - actual_deps
            if extra_deps:
                drift["drift_items"].append({
                    "type": "extra_dependency",
                    "component_id": comp.id,
                    "severity": "warning",
                    "message": f"Extra dependencies: {extra_deps}",
                })
            if missing_deps:
                drift["drift_items"].append({
                    "type": "missing_dependency",
                    "component_id": comp.id,
                    "severity": "error",
                    "message": f"Missing dependencies: {missing_deps}",
                })

        if drift["drift_items"]:
            severities = [d["severity"] for d in drift["drift_items"]]
            drift["severity"] = "error" if "error" in severities else "warning"

        self.drift_metadata = drift
        return drift

    # -----------------------------------------------------------------
    # DIFFING
    # -----------------------------------------------------------------

    async def diff_versions(self, session: AsyncSession, from_version_id: str, to_version_id: str) -> dict:
        from_arch = await session.get(ArchitectureVersion, from_version_id)
        to_arch = await session.get(ArchitectureVersion, to_version_id)
        if not from_arch or not to_arch:
            raise ValueError("One or both architecture versions not found")

        from_comps = {c["id"]: c for c in (from_arch.architecture_yaml or {}).get("components", [])}
        to_comps = {c["id"]: c for c in (to_arch.architecture_yaml or {}).get("components", [])}

        added = [c for cid, c in to_comps.items() if cid not in from_comps]
        removed = [c for cid, c in from_comps.items() if cid not in to_comps]
        modified = []
        for cid in set(from_comps.keys()) & set(to_comps.keys()):
            if from_comps[cid] != to_comps[cid]:
                modified.append({"id": cid, "from": from_comps[cid], "to": to_comps[cid]})

        diff_data = {
            "from_version": from_arch.version,
            "to_version": to_arch.version,
            "added": added,
            "removed": removed,
            "modified": modified,
            "summary": {"total_added": len(added), "total_removed": len(removed), "total_modified": len(modified)},
        }

        diff_record = ArtifactDiff(
            run_id=self.run_id,
            artifact_type="architecture",
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            diff_data=diff_data,
        )
        session.add(diff_record)
        await session.commit()
        return diff_data


# =============================================================================
# CONVENIENCE: Generate default architecture
# =============================================================================

async def generate_default_architecture(run_id: str, project_id: str,
                                         project_name: str) -> ArchitectureVersion:
    """Generate a default microservices architecture."""
    engine = ArchitectureEngine(run_id, project_id)

    # Core components
    components = [
        ArchitectureComponent("API Gateway", "gateway", "Entry point for all client requests. Handles routing, rate limiting, and authentication.",
                              ["Route requests to services", "Rate limiting", "Request validation", "Auth token verification"],
                              ["Auth Service", "Core Service"], ["FastAPI", "Python"]),
        ArchitectureComponent("Auth Service", "service", "Handles user authentication and authorization.",
                              ["User registration/login", "JWT token management", "OAuth2 integration", "RBAC enforcement"],
                              ["PostgreSQL", "Redis"], ["FastAPI", "SQLAlchemy", "PyJWT"]),
        ArchitectureComponent("Core Service", "service", "Core business logic and workflow orchestration.",
                              ["Workflow execution", "Event processing", "State management", "Agent coordination"],
                              ["PostgreSQL", "Redis", "Message Queue"], ["FastAPI", "LangGraph", "Celery"]),
        ArchitectureComponent("Governance Service", "service", "Policy evaluation and compliance checking.",
                              ["OPA policy evaluation", "Release gate management", "Compliance reporting", "Audit logging"],
                              ["PostgreSQL"], ["FastAPI", "OPA", "Rego"]),
        ArchitectureComponent("Specification Engine", "module", "Generates and validates specification artifacts.",
                              ["Requirements management", "Spec validation", "Version control", "Diff generation"],
                              ["Core Service"], ["Python", "PyYAML"]),
        ArchitectureComponent("Architecture Engine", "module", "Generates architecture artifacts and detects drift.",
                              ["Component modeling", "ADR management", "Drift detection", "Diagram generation"],
                              ["Core Service"], ["Python", "Mermaid"]),
        ArchitectureComponent("Test Engine", "module", "Generates test plans and strategies.",
                              ["Test plan generation", "Traceability mapping", "Coverage analysis"],
                              ["Core Service", "Specification Engine"], ["Python", "pytest"]),
        ArchitectureComponent("PostgreSQL", "database", "Primary relational database.",
                              ["Data persistence", "Transaction management", "Migration support"],
                              [], ["PostgreSQL", "Alembic"]),
        ArchitectureComponent("Redis", "cache", "In-memory cache and message broker.",
                              ["Session caching", "Rate limiting counters", "Pub/sub messaging"],
                              [], ["Redis"]),
        ArchitectureComponent("Message Queue", "queue", "Async message processing.",
                              ["Task queuing", "Event broadcasting", "Dead letter handling"],
                              [], ["Redis Streams", "RabbitMQ"]),
    ]

    for comp in components:
        engine.add_component(comp)

    # ADRs
    adrs = [
        ADR("001", "Microservices Architecture",
            "The system needs to support independent deployment and scaling of different capabilities.",
            "Adopt a microservices architecture with clear service boundaries and API contracts.",
            ["Independent deployment per service", "Technology flexibility per service", "Increased operational complexity", "Network latency between services"],
            "accepted", ["Monolithic architecture", "Serverless functions"]),
        ADR("002", "PostgreSQL as Primary Database",
            "The system requires ACID compliance and complex query support for workflow state.",
            "Use PostgreSQL as the primary relational database with SQLAlchemy ORM.",
            ["ACID transactions", "Rich query language", "Mature ecosystem", "Vertical scaling limits"],
            "accepted", ["MongoDB", "MySQL", "CockroachDB"]),
        ADR("003", "LangGraph for Workflow Orchestration",
            "Complex multi-step workflows with branching, retries, and state management are required.",
            "Use LangGraph for workflow orchestration with checkpoint-based state management.",
            ["Visual workflow representation", "Built-in checkpointing", "Conditional routing", "LangChain ecosystem coupling"],
            "accepted", ["Airflow", "Prefect", "Custom state machine"]),
        ADR("004", "OPA for Governance Policies",
            "Governance policies need to be declarative, testable, and separable from application code.",
            "Use Open Policy Agent (OPA) with Rego for all governance policy evaluation.",
            ["Declarative policies", "Testable rules", "Policy-as-code", "Performance overhead of external evaluation"],
            "accepted", ["Custom rule engine", "Hardcoded checks"]),
        ADR("005", "WebSocket for Real-time Updates",
            "The control tower UI requires real-time updates for workflow progress and events.",
            "Use WebSocket connections with automatic reconnection for live event streaming.",
            ["Low-latency updates", "Bidirectional communication", "Connection management complexity"],
            "accepted", ["Server-Sent Events", "Polling", "Long polling"]),
    ]

    for adr in adrs:
        engine.add_adr(adr)

    # Constraints
    engine.add_constraint("No Direct DB Access", "Services must not directly access another service's database.", "review")
    engine.add_constraint("API Versioning", "All API endpoints must include version in URL path.", "build_time")
    engine.add_constraint("Auth Required", "All API endpoints except health check require authentication.", "build_time")
    engine.add_constraint("No Circular Dependencies", "Service dependency graph must be acyclic.", "build_time")

    # Fitness functions
    engine.add_fitness_function("API Response Time", "P95 response time for API endpoints", "latency_p95_ms", "<= 200")
    engine.add_fitness_function("Test Coverage", "Minimum code coverage", "coverage_percent", ">= 80")
    engine.add_fitness_function("Dependency Count", "Maximum dependencies per service", "dependency_count", "<= 5")
    engine.add_fitness_function("Service Count", "Maximum number of services", "service_count", "<= 20")

    async with async_session_factory() as session:
        arch = await engine.persist(session, generated_by="arch-engine")
        return arch
