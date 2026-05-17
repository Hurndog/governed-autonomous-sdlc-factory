# Governed Autonomous SDLC Factory

## Forge Control Tower — UI-Operated Autonomous Software Factory

A governed, autonomous SDLC runtime that transforms natural language software ideas into
complete, tested, documented, and deployed applications — with full observability,
governance controls, evidence bundles, cost tracking, and MCP-based tool abstraction.

### Quick Start

```bash
# 1. Clone and enter
cd governed-autonomous-sdlc-factory

# 2. Copy environment
cp .env.example .env

# 3. Launch infrastructure
docker-compose up -d postgres redis qdrant

# 4. Run migrations
cd apps/api && python -m alembic upgrade head

# 5. Seed demo data
python -m scripts.seed_demo

# 6. Start backend
python -m uvicorn src.main:app --reload --port 8000

# 7. Start frontend (new terminal)
cd apps/web && npm install && npm run dev

# 8. Open Control Tower
open http://localhost:3000
```

### Architecture

- **Frontend**: Next.js + React + Tailwind + shadcn/ui (Forge Control Tower)
- **Backend**: FastAPI + Pydantic + SQLAlchemy
- **Workflow**: LangGraph orchestration
- **Database**: PostgreSQL
- **Queue**: Redis
- **Vector Memory**: Qdrant
- **Governance**: OPA Rego policies
- **Tool Protocol**: MCP servers for all tool access
- **Observability**: OpenTelemetry + Prometheus + Loki-compatible logs
- **Deployment**: Docker Compose localhost

### Key URLs

| Service | URL |
|---------|-----|
| Forge Control Tower (UI) | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs (OpenAPI) | http://localhost:8000/docs |
| Prometheus | http://localhost:9000 |
| Grafana | http://localhost:3001 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

### Logs

- Build log: `logs/overnight-build-log.md`
- Run logs: `logs/runs/<run-id>/run-log.jsonl`
- Agent traces: `logs/runs/<run-id>/agent-traces.jsonl`
- Tool calls: `logs/runs/<run-id>/tool-calls.jsonl`
- Model calls: `logs/runs/<run-id>/model-calls.jsonl`

### Evidence

- Completion checklist: `evidence/system-completion-checklist.json`
- Completion report: `evidence/system-completion-report.md`
- Run evidence bundles: `evidence/runs/<run-id>/evidence-bundle.zip`

### Demo

See `docs/user-guide/control-tower-user-guide.md` for full demo walkthrough.

### Requirements Completion

See `evidence/system-completion-report.md` for the full requirement-by-requirement status table.

---

## Current Baseline Status

**Tag:** `v0.2.0-evidence-backed-runtime-pass`
**Verdict:** PASS (evidence-backed operational acceptance)
**Date:** 2026-05-14
**Commit:** `e2fc386`

### What This System Does

The Governed Autonomous SDLC Factory is a governed runtime that executes software development pipeline phases — from natural language specification through planning, implementation, verification, and release gating — with full evidence capture, integrity scoring, and safety controls. It is operated through a Next.js control plane UI and driven by a FastAPI + LangGraph backend.

This is a **governed runtime baseline**, not a finished enterprise product.

### Core Runtime Capabilities

| Capability | Status |
|---|---|
| Pipeline execution (LangGraph) | ✅ Operational |
| Semantic coverage scoring | ✅ Computed from real DB records |
| Release gate | ✅ Functional (blocks below threshold) |
| Seven-component integrity | ✅ 0.9508 overall score |
| Safety guards (11 types) | ✅ Implemented and persisted |
| Conflict detection (4 patterns) | ✅ Implemented and tested |
| Evidence capture | ✅ 50+ evidence files |
| Backup & restore | ✅ Verified (9MB bundle) |
| Deterministic replay | ✅ Supported via snapshots |

### Frontend Control Plane

| Component | Status |
|---|---|
| Next.js 14 + React + Tailwind | ✅ |
| TypeScript strict mode | ✅ Pass |
| Build | ✅ Pass (4 pages) |
| Rooms: Command Center, Governance, Architecture, Settings | ✅ |

### Backend

| Component | Status |
|---|---|
| FastAPI + Pydantic | ✅ |
| PostgreSQL (SQLAlchemy/asyncpg) | ✅ |
| Test suite | ✅ 82/82 passing |
| API endpoints | ✅ Operational |
| MCP tool integration | ✅ |

### Model Runtime Support

- Multi-provider routing (configurable per environment)
- Model call budgets (5/phase, 50/run)
- Token budgets (250,000/run)
- Provider failover guard
- Semantic iteration limit (5)

### Integrity Components

1. Artifact hashing (SHA256)
2. Event sourcing with hash chain
3. Snapshot integrity
4. Lineage tracking
5. Evidence binding
6. Replay verification
7. Semantic coverage scoring

### Known Limitations

- **No authentication or authorization** — API is not exposed to untrusted users
- **No multi-tenant isolation** — single-scope operation only
- **No production deployment configuration** — no Docker Compose for production, no health checks, no monitoring
- **No automated database migrations** — schema changes applied manually
- **No PDF/audit export** — evidence exists as markdown only
- **No human-in-the-loop approval** — release gate produces verdict without human approval step
- **ESLint not configured** — build and typecheck pass without it
- **Semantic coverage score below threshold (0.6559)** — genuine result, not a bug; improving it requires engine logic changes

### Next Roadmap Phase

**Phase 1: Security and Access Control** — Authentication, authorization, RBAC, user/project/workspace model, secrets management, API protection, audit access model.

See `docs/roadmap/productization-roadmap-from-pass-baseline.md` for the full roadmap.
