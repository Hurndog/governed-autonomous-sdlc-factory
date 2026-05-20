# Technical Architecture

**Last updated:** 2025-05-20
**Validated against:** 128/128 backend tests PASS, full pipeline execution, TypeScript 0 errors

---

## 1. System Overview

### Validated Runtime State

| Component | Count | Status |
|-----------|-------|--------|
| Backend engines | 21 files | All operational |
| API endpoints | 26 modules | All operational |
| Frontend rooms | 30 components | 28 substantive, 2 thin wrappers |
| Frontend UI components | 10 | All operational |
| Database tables | 85+ | All created via SQLAlchemy models |
| Test files | 14 | 128/128 PASS |
| Evidence files | 112+ | Runtime-generated |

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | FastAPI | 0.115 | Web framework |
| Backend | Pydantic | 2.9 | Data validation |
| Backend | SQLAlchemy | 2.0.35 | ORM (async) |
| Backend | asyncpg | 0.29 | PostgreSQL driver |
| Backend | Alembic | 1.13 | Migrations (non-standard path: `src/core/migrations`) |
| Backend | structlog | 24.4 | Structured logging |
| Backend | OpenTelemetry | 1.27 | Observability |
| Backend | httpx | 0.27 | HTTP client |
| Backend | redis | 5.1 | Cache client |
| Frontend | Next.js | 14.2 | React framework |
| Frontend | React | 18.2 | UI library |
| Frontend | TypeScript | 5.3 | Type safety |
| Frontend | Tailwind CSS | 3.4 | Styling |
| Frontend | Zustand | 4.5 | State management |
| Frontend | Recharts | 2.12 | Charts |
| Database | PostgreSQL | 15 | Primary store |
| Cache | Redis | 7 | Cache + queue |
| Vector DB | Qdrant | Latest | Vector memory |
| Metrics | Prometheus | Latest | Metrics |
| Dashboards | Grafana | Latest | Visualization |
| Local LLM | Ollama | Latest | Model serving |

---

## 2. Backend Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (apps/api/src/api/v1/endpoints/)              │
│  - 26 endpoint modules                                   │
│  - Request validation (Pydantic)                         │
│  - Response serialization                                │
│  - Permission declarations                               │
├─────────────────────────────────────────────────────────┤
│  Service Layer (apps/api/src/services/)                   │
│  - FullPipelineOrchestrator (647 lines)                  │
│  - RunOrchestrator                                       │
│  - RunService, PhaseService, ProjectService              │
│  - ArtifactStore                                         │
├─────────────────────────────────────────────────────────┤
│  Engine Layer (apps/api/src/engines/)                     │
│  - SemanticCoverageEngine (1229 lines, 31 functions)     │
│  - DriftDetectionEngine (6 drift dimensions)             │
│  - ReplayIntegrityVerifier (hash chain)                  │
│  - MetacognitiveController (self-monitoring)             │
│  - RuntimeTrustScorer (5-component model)                │
│  - CognitiveModelRouter (406 lines)                      │
│  - ModelRegistry (211 lines)                             │
│  - GovernanceEngine (251 lines)                          │
│  - ReplayEngine (452 lines)                              │
│  - SpecificationEngine                                   │
│  - ArchitectureEngine                                    │
│  - InferenceTrace                                        │
│  - TraceabilityEngine                                    │
│  - DivergenceEngine                                      │
│  - SourceExtractor                                       │
│  - Snapshots                                             │
│  - ReplayTransactionManager                              │
│  - IntegrityRuntimeSync                                  │
│  - ReplayRuntimeSync                                     │
│  - ModelProviders (unified abstraction)                  │
│  - OllamaProvider (106 lines)                            │
│  - CognitiveGovernance                                   │
│  - TestEngine                                            │
├─────────────────────────────────────────────────────────┤
│  Core Layer (apps/api/src/core/)                          │
│  - auth.py (JWT + RBAC, 276 lines, 9 classes)            │
│  - config.py (Pydantic Settings)                         │
│  - database.py (SQLAlchemy async engine)                 │
│  - event_bus.py (internal pub/sub)                       │
│  - observability.py (OpenTelemetry + Prometheus)         │
│  - logging.py (structlog)                                │
│  - hashing.py (SHA-256)                                  │
│  - integrity.py (hash chain verification)                │
│  - normalization.py (response normalization)             │
│  - safety_guards.py (11 guard types)                     │
│  - conflict_detection.py (4 patterns)                    │
│  - hash_propagation.py (artifact hashing)                │
│  - startup_diagnostics.py (health checks)                │
│  - models.py (SQLAlchemy ORM models)                     │
│  - models_semantic_coverage.py (22 model classes)        │
├─────────────────────────────────────────────────────────┤
│  Schema Layer (apps/api/src/schemas/)                     │
│  - Pydantic v2 schemas for all API I/O                   │
├─────────────────────────────────────────────────────────┤
│  WebSocket Layer (apps/api/src/websocket/)                │
│  - run_events.py (WebSocket event broadcasting)          │
└─────────────────────────────────────────────────────────┘
```

### Middleware Stack

```
Request → CORS → Trace → Audit → Auth → Endpoint → Response
```

### Engine Communication Pattern

Engines communicate through the event bus, not directly:

```
Engine A ──publish──▶ Event Bus ──subscribe──▶ Engine B
                         │
                         ▼
                    Database (persist)
                         │
                         ▼
                    SSE Stream (notify frontend)
```

---

## 3. Frontend Architecture

### Component Architecture

```
src/app/                          ← Next.js App Router
├── layout.tsx                    ← Root layout (auth, theme)
├── page.tsx                      ← Home page
├── login/page.tsx                ← Login page
└── globals.css                   ← Global styles

src/lib/                          ← Client libraries (10 files)
├── api.ts (827 lines)            ← REST API client
├── useApiData.ts                 ← Data fetching hook
├── useWebSocket.ts               ← WebSocket hook
├── authStore.ts (89 lines)       ← Auth state (Zustand)
├── store.ts                      ← Global state (Zustand)
├── data-source.ts                ← Data source management
├── theme.ts                      ← Theme configuration
├── utils.ts                      ← Utility functions
├── types.ts (438 lines)          ← TypeScript types
└── mock-data.ts                  ← Demo data

src/components/
├── AuthGuard.tsx                 ← Auth protection wrapper
├── ui/ (10 components)           ← Shared UI components
│   ├── Badge.tsx, Card.tsx, DataSourceBadge.tsx
│   ├── GaugeChart.tsx, MetricCard.tsx, ProgressBar.tsx
│   ├── SectionHeader.tsx, Sidebar.tsx, StatusChip.tsx, TopBar.tsx
└── rooms/ (30 components)        ← Feature rooms
    ├── OperationsCenter.tsx (406 lines) ← SSE telemetry dashboard
    ├── ExplainabilityRoom.tsx (448 lines) ← Forensic reconstruction
    ├── OperatorConsole.tsx (275 lines) ← Intervention controls
    ├── MemoryOperations.tsx (247 lines) ← Lifecycle management
    ├── ModelOperationsCenter.tsx (251 lines) ← Multi-model routing
    ├── Dashboard.tsx (288 lines) ← Main dashboard
    ├── GovernanceGates.tsx (161 lines) ← Policy display
    ├── ReplayChamber.tsx (201 lines) ← Replay interface
    ├── EvidenceCenter.tsx (107 lines) ← Evidence explorer
    ├── Tokenomics.tsx (293 lines) ← Cost tracking
    ├── SDLCNavigator.tsx (359 lines) ← Phase navigation
    ├── BuildMap.tsx (448 lines) ← Build pipeline visualization
    ├── ProcessTimeline.tsx (306 lines) ← Visual timeline
    ├── SemanticCoverage.tsx (244 lines) ← Coverage analysis
    ├── TraceabilityRoom.tsx (144 lines) ← Lineage tracking
    ├── IntegrityRoom.tsx (137 lines) ← Integrity scoring
    ├── LogsDiagnostics.tsx (112 lines) ← Log exploration
    ├── ArtifactExplorer.tsx (180 lines) ← Artifact browser
    ├── RunControlRoom.tsx (173 lines) ← Run management
    ├── RunReplay.tsx (164 lines) ← Interactive replay
    ├── SpecRoom.tsx (160 lines) ← Specification management
    ├── SettingsProviders.tsx (156 lines) ← Provider config
    ├── UserManagement.tsx (299 lines) ← User admin
    ├── BacklogChecklist.tsx (247 lines) ← Task backlog
    ├── ExecutiveCockpit.tsx (288 lines) ← Executive dashboard
    ├── AgentCommandCenter.tsx (283 lines) ← Agent management
    ├── ArchitectureIntelligence.tsx (89 lines) ← AI architecture
    ├── GovernanceRoom.tsx (247 lines) ← Governance overview
    ├── CommandCenter.tsx (9 lines) ← Redirect to Dashboard
    └── ArchitectureRoom.tsx (8 lines) ← Redirect to GovernanceRoom
```

### State Management

- **Auth Store** (`authStore.ts`) — JWT token management, auto-refresh
- **Data Store** (`store.ts`) — Runs, projects, workspaces via Zustand
- **Connection Store** — SSE connection state, WebSocket state

### SSE Integration

The frontend connects to `GET /api/v1/operations/events/stream` for real-time updates. Auto-reconnect with exponential backoff.

---

## 4. Database Architecture

### Schema Organization

85+ tables in PostgreSQL:

| Domain | Tables |
|--------|--------|
| Core | workspaces, projects, users, roles, permissions, user_roles, role_permissions |
| Run | runs, phases, tasks, agents, artifacts |
| Evidence | evidence_bundles, log_events, snapshots, hash_chains |
| Governance | governance_policies, trust_scores, operator_interventions, audit_trails |
| Memory | memory_versions, memory_lifecycle, memory_quarantine |
| Model | model_capabilities, routing_decisions, arbitration_results, provider_health |
| Economic | cost_records, token_usage, budget_alerts |
| Semantic | requirement_normalizations, acceptance_criteria_contracts, test_obligations, semantic_alignment_evaluations, verifier_critiques, mutation_tests, negative_test_requirements, runtime_evidence_bindings, semantic_coverage_reports, semantic_coverage_waivers |

### Key Relationships

```
workspaces (1) ─── (N) projects (1) ─── (N) runs (1) ─── (N) phases
                                              │
                                              ├── (N) tasks
                                              ├── (N) artifacts
                                              ├── (N) log_events
                                              ├── (N) snapshots
                                              ├── (N) evidence_bundles
                                              ├── (N) trust_scores
                                              ├── (N) operator_interventions
                                              └── (N) routing_decisions
```

---

## 5. Event System

### Event Bus

Internal pub/sub pattern. Every significant action produces an event that is:
1. Persisted to `log_events` table
2. Published to internal subscribers
3. Broadcast via SSE to connected frontend clients
4. Hash-chained for tamper detection

### Event Categories

| Category | Events |
|----------|--------|
| Runtime | run.started, run.completed, run.failed, phase.started, phase.completed |
| Model | model.selected, model.called, model.failed, model.timed_out |
| Governance | policy.evaluated, trust.updated, drift.detected, gate.passed, gate.blocked |
| Intervention | intervention.pause, intervention.resume, intervention.quarantine, intervention.rollback |
| Memory | memory.created, memory.aged, memory.archived, memory.quarantined, memory.restored |
| Evidence | evidence.captured, evidence.bundle.created, evidence.verified |

### Hash Chain

Each event is hash-chained to the previous event for tamper detection:
```
hash_n = SHA256(hash_{n-1} + event_type + timestamp + payload)
```

---

## 6. Security Architecture

### Authentication

- JWT-based with access + refresh tokens
- Access tokens: short-lived (15 min default)
- Refresh tokens: long-lived (7 days default)
- HMAC-SHA256 signing

### Authorization

- RBAC with 30+ granular permissions
- Endpoint-level permission declarations
- Middleware enforcement

### Permission Domains

| Domain | Permissions |
|--------|-------------|
| Project | project:read, project:write, project:delete, project:admin |
| Run | run:read, run:write, run:execute, run:terminate |
| Model | model:read, model:configure, model:route, model:arbitrate |
| Governance | governance:read, governance:write, governance:enforce |
| Intervention | intervention:pause, resume, quarantine, rollback, escalate, throttle, override, terminate |
| Memory | memory:read, memory:write, memory:archive, memory:quarantine |
| Evidence | evidence:read, evidence:export, evidence:verify |

### Security Gaps (Known)

- No rate limiting
- No security headers (HSTS, CSP, X-Frame-Options)
- No CSRF protection
- No request size limits
- No WAF
- No automated secrets rotation

---

## 7. Model Provider Architecture

### Provider Abstraction

```
CognitiveModelRouter
    │
    ├── ModelRegistry (capability profiles)
    │
    ├── BaseProvider (abstract)
    │   ├── OllamaProvider (local)
    │   ├── LMStudioProvider (local)
    │   ├── OpenAIProvider (remote)
    │   └── AnthropicProvider (remote)
    │
    └── RoutingPolicy
        ├── prefer_local
        ├── max_cost_per_request
        ├── min_context_length
        ├── fallback_enabled
        └── max_retries
```

### Normalized Response

All providers return `InferenceResult` with: provider, model, response_text, latency_ms, token_usage, estimated_cost, finish_reason, trace_id

### Known Limitations

- `ModelRegistry.list_models()` returns empty when all models have `is_available=False` (filtering bug)
- Remote providers require API keys (not tested with live keys)
- Ollama provider requires local Ollama instance

---

## 8. Deployment Architecture

### Docker Compose (Development)

7 services: api (8000), web (3000), postgres (5432), redis (6379), qdrant (6333), prometheus (9090), grafana (3001)

### Production Deployment (Not Validated)

```
Internet → Nginx (SSL termination) → { web:3000, api:8000 }
                                              │
                                    ┌─────────┼─────────┐
                                    ▼         ▼         ▼
                                PostgreSQL  Redis    Qdrant
```

### Production Gaps

- No CI/CD pipeline
- No container health checks
- No automated backups
- No TLS/SSL configuration
- No rate limiting
- No HA/failover

---

## 9. Performance Characteristics

### Backend

| Metric | Value | Notes |
|--------|-------|-------|
| API response time (p50) | < 50ms | Simple queries |
| API response time (p95) | < 200ms | Complex queries |
| Event processing | < 5ms | Persist + broadcast |
| Test suite | < 10s | 128 tests |

### Frontend

| Metric | Value | Notes |
|--------|-------|-------|
| First Contentful Paint | < 1.5s | Next.js SSR |
| Time to Interactive | < 2.5s | With hydration |
| SSE reconnection | < 3s | Exponential backoff |

### Resource Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| API | 1 core | 512MB | 100MB |
| Web | 0.5 core | 256MB | 100MB |
| PostgreSQL | 2 cores | 2GB | 10GB |
| Redis | 0.5 core | 512MB | 100MB |
| **Total (minimal)** | **4 cores** | **4GB** | **15GB** |
| **Total (recommended)** | **8 cores** | **16GB** | **30GB** |

---

## 10. Architecture Truth Notes

### What Is Real

These systems are **genuinely implemented and tested**:

- 21 engine files with substantive implementations (100-1229 lines each)
- 26 API endpoint modules covering all major domains
- 30 frontend room components (28 substantive, 2 intentional thin wrappers)
- 128/128 backend tests passing
- Full SDLC pipeline execution validated
- JWT + RBAC authentication and authorization
- SSE telemetry streaming
- Evidence capture with hash chains
- Deterministic replay with tamper detection
- Drift detection across 6 dimensions
- Trust scoring with 5-component model
- Mutation testing (plan → execute → score)
- Memory lifecycle management (7 states)
- Multi-model routing with capability registry
- Operator intervention framework (8 types)
- Explainability engine (8 explanation types)

### What Is Not Real

These are **planned but not implemented**:

- CI/CD pipeline
- Production HA/failover
- Distributed replay federation
- Multi-language mutation testing
- LLM-based explainability narratives
- Adaptive drift detection
- Semantic execution memory
- Ontology-constrained execution
- Trust decay scoring
- Deception detection
- Constitutional governance
- Evidence signing

### Known Bugs

- `ModelRegistry.list_models()` returns empty when all models have `is_available=False`
- Alembic migrations use non-standard path (`src/core/migrations` not `alembic/`)
- No async pytest support (missing `pytest-asyncio` marker config)

### Honest Assessment

This is a **functional governed cognitive runtime** with comprehensive test coverage and operational frontend. It is **not production-hardened** — it lacks CI/CD, HA, security hardening, and enterprise-scale validation. The architecture is sound but the operational maturity is development-grade.
