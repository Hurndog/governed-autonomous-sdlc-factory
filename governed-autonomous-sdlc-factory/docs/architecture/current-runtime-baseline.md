# Current Runtime Baseline — Architecture Status

**Tag:** `v0.3-governed-runtime-observability-baseline`
**Date:** 2026-05-19
**Status:** PASS — Governed Runtime Observability Baseline Sealed

---

## 1. Runtime Overview

The Governed Autonomous SDLC Factory is a **governed autonomous software engineering runtime** that transforms natural language software specifications into release-governed outputs through a series of orchestrated phases. Each phase is executed by AI agents operating under governance constraints, with full evidence capture, integrity verification, and runtime observability at every step.

The system is operated through a Next.js frontend (Command Center) and driven by a FastAPI backend with PostgreSQL persistence. All 18 command center screens are now **LIVE** — driven by real backend data with no fake telemetry, no fake governance, and no fabricated metrics.

## 2. Main Components

| Component | Technology | Role |
|---|---|---|
| Frontend Control Plane | Next.js 14, React, Tailwind, shadcn/ui | Operator interface (18 LIVE screens) |
| API Layer | FastAPI, Pydantic | HTTP API with JWT auth + RBAC |
| Orchestration | LangGraph | Pipeline phase execution |
| Persistence | PostgreSQL, SQLAlchemy/asyncpg | Structured data, evidence, audit trail |
| Vector Memory | Qdrant (configured) | Semantic search, embeddings |
| Governance | OPA Rego (configured) | Policy enforcement |
| Tool Protocol | MCP servers | Tool abstraction for agents |
| Hashing | SHA256 | Artifact/event/snapshot integrity |

## 3. Security & Access Control

| Capability | Status |
|------------|--------|
| JWT Authentication | ✅ COMPLETE |
| RBAC (7 roles) | ✅ COMPLETE |
| Workspace/Project Isolation | ✅ COMPLETE |
| Audit Logging | ✅ COMPLETE |
| Secret Redaction | ✅ COMPLETE |
| Bootstrap Admin | ✅ Environment-gated |

### Roles
- `admin` — Full management
- `architect` — Architecture + governance
- `engineer` — Development + execution
- `governance_reviewer` — Governance review
- `executive_viewer` — Read-only executive views
- `auditor` — Read-only audit views
- `operator` — Operations + monitoring

## 4. Runtime Observability

### 4.1 LIVE Screen Architecture (22 LIVE screens)

All screens use the **DataSourceBadge** pattern to indicate data provenance:
- **LIVE** — Data from backend API endpoints
- **PARTIAL** — Mixed backend + mock data
- **MOCK** — Fallback mock data only (clearly indicated)

### 4.2 Upgraded Screens (v0.3)

| Screen | Backend Endpoints | Key Metrics |
|--------|-------------------|-------------|
| SDLC Navigator | `/api/v1/runs/latest`, `/api/v1/timeline/`, governance, semantic, artifacts, evidence, costs | Phase progression, governance counts, coverage, token usage |
| Process Timeline | `/api/v1/timeline/{run_id}`, `/api/v1/governance/evaluations` | Event ordering, bottleneck detection, governance checkpoints |
| Build Map | `/api/v1/architecture/latest`, traceability, governance, artifacts, costs | Topology, traceability links, risk scoring, governance overlays |
| Executive Cockpit | 7 parallel endpoints (integrity, semantic, costs, artifacts, evidence, governance, traceability) | Aggregated metrics, release readiness, governance risks, tokenomics |
| Agent Command Center | Agents table, inference logs, cost report | Agent activity, token usage, retries, errors |
| Backlog Checklist | Requirements, test obligations, governance, mutation tests, verifier critiques | Uncovered requirements, blockers, mutation survival, verifier critiques |

### 4.3 Governance Overlays

Governance state is overlaid on multiple screens:
- **SDLC Navigator** — Per-phase governance pass/fail/warning counts
- **Build Map** — Per-component governance evaluations + risk scoring
- **Executive Cockpit** — Aggregated governance readiness + failing gates
- **Backlog Checklist** — Per-requirement governance blockers
- **Process Timeline** — Governance checkpoint events merged with runtime events

### 4.4 Semantic Coverage Integration

Semantic coverage is visible in:
- **SDLC Navigator** — Coverage bar per phase
- **Executive Cockpit** — Aggregated coverage score
- **Semantic Coverage** screen — Detailed coverage analysis + conflict detection
- **Backlog Checklist** — Per-requirement coverage status

### 4.5 Replay Integration

Replay functionality is integrated via:
- **Replay Chamber** — Session-based replay with play/pause/skip controls
- **Run Replay** — Run-level replay with evidence alignment
- **Process Timeline** — Replay event visualization

### 4.6 Tokenomics Integration

Tokenomics data is integrated in:
- **Tokenomics** screen — Full cost analysis by phase/agent/provider
- **SDLC Navigator** — Per-phase token usage + cost
- **Build Map** — Per-component token cost
- **Executive Cockpit** — Aggregated cost metrics
- **Agent Command Center** — Per-agent token attribution

### 4.7 Ownership Model

Ownership is tracked at:
- **Requirement level** — Owner per requirement
- **Component level** — Owner per architecture component
- **Governance gate level** — Owner per gate
- **Audit trail** — Actor attribution for all actions

## 5. API Endpoints

All endpoints protected via JWT auth (unless explicitly public):

| Endpoint Group | Protection | Description |
|----------------|------------|-------------|
| `/api/v1/auth/*` | Public | Login, token refresh, bootstrap |
| `/api/v1/runs/*` | JWT | Run management |
| `/api/v1/timeline/*` | JWT | Timeline events |
| `/api/v1/governance/*` | JWT | Governance evaluations + policies |
| `/api/v1/semantic/*` | JWT | Semantic coverage |
| `/api/v1/evidence/*` | JWT | Evidence items |
| `/api/v1/artifacts/*` | JWT | Artifact management |
| `/api/v1/costs/*` | JWT | Cost reports |
| `/api/v1/traceability/*` | JWT | Traceability links |
| `/api/v1/architecture/*` | JWT | Architecture documents |
| `/api/v1/users/*` | JWT + Admin | User management |
| `/api/v1/workspaces/*` | JWT | Workspace management |
| `/api/v1/projects/*` | JWT | Project management |

## 6. Remaining Limitations

1. **ArchitectureIntelligence** — MOCK (static topology visualization). Acceptable for current phase; upgrade to LIVE in future.
2. **Real-time updates** — No WebSocket/SSE. Data fetched on component mount + manual refresh button.
3. **Pagination** — Some lists may need pagination for large datasets.
4. **Search/filter** — Basic filtering available, advanced search not implemented.
5. **Internationalization** — UI is English-only.

## 7. Future Roadmap

### Recommended Next Phase: v0.4 — Real-Time Runtime Telemetry
- WebSocket/SSE for live updates
- Real-time governance alerts
- Live agent activity streaming
- Push-based evidence notifications

### v0.5 — Advanced Analytics
- Trend analysis across runs
- Predictive governance risk scoring
- Cost optimization recommendations
- Architecture drift detection

### v0.6 — Multi-Tenant Operations
- Organization-level isolation
- Cross-workspace analytics
- Team-based access controls
- SLA monitoring
