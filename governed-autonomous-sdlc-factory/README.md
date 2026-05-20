# 🏛️ Governed Autonomous SDLC Factory

> **A governed cognitive runtime for autonomous enterprise systems.**
>
> Explainable. Controllable. Sovereign. Auditable.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org)

---

## What This Platform Is

The Governed Autonomous SDLC Factory is a **governed cognitive runtime** that executes software development lifecycle phases — from natural language specification through planning, implementation, verification, and release gating — with full observability, governance controls, evidence bundles, cost tracking, and multi-model cognitive arbitration.

This is not a chatbot. This is not a prompt chain. This is an **enterprise runtime** where every action is governed, every decision is auditable, and every run is replayable.

### Validated Runtime State

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Backend tests | ✅ 128/128 PASS | Full test suite including E2E pipeline |
| Frontend build | ✅ PASS | TypeScript strict, 0 errors |
| Pipeline execution | ✅ Validated | Full SDLC pipeline test passes |
| Replay integrity | ✅ Operational | Hash-chained snapshots, tamper detection |
| Drift detection | ✅ Operational | 6 drift dimensions, metacognitive control |
| Trust scoring | ✅ Operational | RuntimeTrustScorer, 5-component model |
| Explainability | ✅ Operational | 8 explanation types, evidence-grounded |
| JWT + RBAC | ✅ Operational | 30+ permissions, 8 intervention types |
| SSE telemetry | ✅ Operational | Real-time event streaming |
| Memory lifecycle | ✅ Operational | 7 states, archival with evidence preservation |
| Multi-model routing | ✅ Phase 1 | Capability registry, sovereignty routing |
| Operator intervention | ✅ Operational | 8 intervention types, audit trail |
| Mutation execution | ✅ Operational | Plan → execute → score pipeline |
| Semantic coverage | ✅ Operational | 1229-line engine, 31 functions |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js 14 + TypeScript + Tailwind)          │
│  30 Room Components • 10 UI Components • 10 Lib files   │
│  SSE • WebSocket • Recharts • Zustand                   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / SSE / WebSocket
┌────────────────────────▼────────────────────────────────┐
│  API Layer (FastAPI + Pydantic v2)                      │
│  26 Endpoint Modules • Middleware • SSE Streams         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Engine Layer (21 Engines)                              │
│  SemanticCoverage • Governance • DriftDetection         │
│  Replay • ModelRouter • TrustScorer • Metacognitive     │
│  Explainability • Arbitration • InferenceTrace          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Core Layer                                             │
│  Auth (JWT+RBAC) • Config • Database • Event Bus        │
│  Observability • Logging • Hashing • Safety Guards      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Infrastructure                                         │
│  PostgreSQL (85+ tables) • Redis • Qdrant • Ollama      │
└─────────────────────────────────────────────────────────┘
```

---

## Runtime Layers

### Execution Layer
- **Full Pipeline Orchestrator** (647 lines) — coordinates SDLC phases
- **Semantic Coverage Engine** (1229 lines) — requirement normalization, test obligation, mutation testing
- **Specification Engine** — natural language to structured specification
- **Architecture Engine** — architectural reasoning and decision support
- **Test Engine** — test execution and validation

### Governance Layer
- **Governance Engine** — policy evaluation, trust scoring, release gating
- **Drift Detection Engine** — 6 drift dimensions (semantic, governance, cost, evidence, context, cognitive)
- **Metacognitive Controller** — self-monitoring, operator intervention recording
- **Runtime Trust Scorer** — 5-component trust model (accuracy, hallucination, replay, governance, operator)
- **Replay Integrity Verifier** — hash chain validation, tamper detection

### Cognitive Layer
- **Cognitive Model Router** (406 lines) — dynamic model selection, capability matching, sovereignty routing
- **Model Registry** — 16-dimension capability profiles, default model configurations
- **Cognitive Arbitration Engine** — multi-model execution, consensus scoring, disagreement analysis
- **Inference Trace** — full trace of every model call

### Observability Layer
- **Operations Endpoints** — health summary, event log, SSE telemetry stream
- **Explainability Engine** (970 lines) — 8 explanation types, causal chain construction
- **Memory Lifecycle Manager** (601 lines) — 7 lifecycle states, aging, archival, quarantine
- **Operator Intervention Console** (569 lines) — 8 intervention types, RBAC-protected

### Evidence Layer
- **Evidence Capture** — every action produces immutable log events
- **Hash Chain** — tamper-evident event linking
- **Snapshot System** — deterministic run reconstruction
- **Evidence Bundles** — per-run evidence packages

---

## Documentation

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | This file — overview and quickstart |
| **[INSTALLATION.md](INSTALLATION.md)** | Complete installation + dependencies guide |
| **[FUNCTIONAL.md](FUNCTIONAL.md)** | Functional descriptions + execution overviews |
| **[TECHNICAL-ARCHITECTURE.md](TECHNICAL-ARCHITECTURE.md)** | Deep technical architecture |
| **[RELEASES.md](RELEASES.md)** | Release notes per version |
| **[CURRENT-TRUTH-MATRIX.md](CURRENT-TRUTH-MATRIX.md)** | Canonical runtime truth reference |
| **[Whitepaper](whitepaper/loveable-for-the-enterprise.md)** | Technical whitepaper |

### Architecture & Design
| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/overview.md) | System architecture with Mermaid diagrams |
| [Current Runtime Baseline](docs/architecture/current-runtime-baseline.md) | Runtime baseline assessment |
| [Security Access Control](docs/architecture/security-access-control-phase-1.md) | Security architecture |
| [Cognitive Cortex Philosophy](docs/cognitive-cortex-philosophy.md) | Design philosophy |
| [Deterministic Replay Spec](docs/deterministic-replay-spec.md) | Replay system specification |
| [Execution Integrity](docs/execution-integrity-architecture.md) | Integrity architecture |
| [Observability Substrate](docs/observability-substrate-spec.md) | Observability design |

### Operations & Governance
| Document | Description |
|----------|-------------|
| [API Reference](docs/api/reference.md) | Complete API endpoint reference |
| [Runtime](docs/runtime/index.md) | Runtime lifecycle, trust, drift, replay |
| [Governance](docs/governance/index.md) | Governance framework and policies |
| [Security](docs/security/architecture.md) | Security architecture |
| [Operations](docs/operations/) | Operations documentation |

### Deployment
| Document | Description |
|----------|-------------|
| [Local Deployment](docs/deployment/local.md) | Local installation guide |
| [Docker Deployment](docs/deployment/docker.md) | Docker deployment guide |
| [VPS Deployment](docs/deployment/vps.md) | VPS deployment guide |
| [Apple Silicon](docs/deployment/apple-silicon.md) | Apple Silicon optimized setup |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# 1. Clone
git clone https://github.com/Hurndog/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory

# 2. Configure
cp .env.example .env
# Edit .env with your settings (DATABASE_URL, REDIS_URL, API_SECRET required)

# 3. Backend
python -m venv venv && source venv/bin/activate
pip install -r apps/api/requirements.txt
cd apps/api && python -m alembic upgrade head && cd ../..

# 4. Frontend
cd apps/web && npm install && cd ../..

# 5. Start infrastructure
docker-compose up -d postgres redis qdrant

# 6. Start backend
cd apps/api && python -m uvicorn src.main:app --reload --port 8000

# 7. Start frontend (new terminal)
cd apps/web && npm run dev

# 8. Open Control Tower
open http://localhost:3000
```

### Docker Quick Start

```bash
git clone https://github.com/Hurndog/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory
cp .env.example .env
docker-compose up -d
docker-compose exec api python -m alembic upgrade head
open http://localhost:3000
```

---

## Key URLs

| Service | URL |
|---------|-----|
| Forge Control Tower (UI) | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs (OpenAPI) | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## Release History

| Version | Date | Description |
|---------|------|-------------|
| [v0.5.1](RELEASES.md#v051) | 2025-05-20 | Truth Closure — E2E fixes, mutation execution, 128/128 tests |
| [v0.5](RELEASES.md#v05) | 2025-05-19 | Multi-Model Cognitive Governance — router, arbitration, sovereignty |
| [v0.4](RELEASES.md#v04) | 2025-05-19 | Enterprise Cognitive Operations — monitoring, interventions, explainability |
| [v0.3.5](RELEASES.md#v035) | 2025-05-19 | Integration Integrity — drift control, metacognitive, replay |
| [v0.3.3](RELEASES.md#v033) | 2025-05-19 | Concurrency Stable — 25/25 stability, 5/5 tamper detection |
| [v0.3](RELEASES.md#v03) | 2025-05-19 | Observability Baseline — auth, RBAC, semantic coverage |
| [v0.2.0](RELEASES.md#v020) | 2025-05-14 | Evidence-Backed Runtime — pipeline, integrity, evidence |
| [v0.1.0](RELEASES.md#v010) | 2025-05-14 | Golden Integrity Runtime — initial baseline |

See [RELEASES.md](RELEASES.md) for detailed release notes.

---

## Operational Reality

### What Is Production-Ready
- Backend runtime with 128/128 passing tests
- Frontend with 30 room components, TypeScript strict
- JWT authentication and RBAC authorization
- SSE telemetry streaming
- Evidence capture with hash chains
- Deterministic replay with tamper detection
- Drift detection across 6 dimensions
- Trust scoring with 5-component model
- Mutation testing (plan → execute → score)
- Operator intervention framework
- Memory lifecycle management
- Multi-model routing with capability registry

### What Is NOT Production-Ready
- **No CI/CD pipeline** — no `.github/workflows/`
- **No automated backups** — manual backup scripts only
- **No TLS/SSL configuration** — must be added via reverse proxy
- **No rate limiting** — API is unprotected against abuse
- **No security headers** — no HSTS, CSP, or X-Frame-Options
- **No container health checks** — Docker Compose has no health checks
- **No log rotation** — logs grow unbounded
- **No database connection pooling** — default SQLAlchemy pool only
- **No production deployment validation** — not tested at enterprise scale
- **No HA/failover** — single-instance deployment only
- **No enterprise-scale load testing** — validated for development workloads only

### What Is Experimental
- **Multi-model arbitration** — engine exists but limited real-provider testing
- **Sovereignty routing** — 5 levels defined, edge cases untested
- **Semantic coverage scoring** — deterministic scoring, not LLM-based
- **Mutation execution** — works for Python test code, limited language support
- **Explainability narratives** — template-based, not LLM-generated
- **Drift detection** — rule-based thresholds, not adaptive

### Known Limitations
- Frontend rooms `ArchitectureRoom.tsx` (8 lines) and `CommandCenter.tsx` (9 lines) are thin wrappers/redirects
- `ModelRegistry.list_models()` returns empty when all models have `is_available=False` — filtering bug
- Alembic migrations use non-standard path (`src/core/migrations` not `alembic/`)
- No async test support in pytest (missing `pytest-asyncio` marker config)
- Ollama provider requires local Ollama instance; remote providers require API keys

---

## Security Disclaimer

This platform is designed for **governed autonomous operation within trusted environments**. It is not designed for direct exposure to untrusted users without additional security layers (WAF, API gateway, etc.).

**Required for production:**
- Reverse proxy with SSL termination (nginx, traefik)
- Strong JWT secrets (256-bit minimum, rotated regularly)
- API key rotation policy
- Rate limiting middleware
- Security headers (HSTS, CSP, X-Frame-Options)
- Database encryption at rest
- Log rotation and monitoring
- Regular dependency updates (`pip audit`, `npm audit`)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `cd apps/api && python -m pytest tests/ -v`
5. Run type check: `cd apps/web && npm run typecheck`
6. Submit a pull request

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

> *"Governance is not a constraint on AI capability. It is a prerequisite for AI deployment in any environment where decisions have consequences."*
