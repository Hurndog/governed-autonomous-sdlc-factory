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

## Vision

The AI industry has a governance problem.

Current agentic systems optimize for capability demonstrations while treating governance, observability, and controllability as afterthoughts. The result: agents that cannot explain themselves, cannot be stopped, cannot be audited, and cannot be trusted.

**The Governed Autonomous SDLC Factory is different.**

This is not a chatbot. This is not a prompt chain. This is an **enterprise cognitive runtime** designed for environments where AI decisions have consequences.

We believe that **governance is not a constraint on AI capability — it is a prerequisite for AI deployment in any environment where decisions have consequences.**

---

## What This Platform Is

The Governed Autonomous SDLC Factory transforms natural language software specifications into complete, tested, documented, and deployed applications — with:

- 🔍 **Full observability** — Real-time telemetry via SSE streams
- 🏛️ **Governance by default** — Every action is governed, every decision is auditable
- 🧠 **Multi-model cognition** — Arbitrated decisions across multiple AI models
- 🔒 **Sovereignty-aware routing** — Control over where cognition happens
- 📜 **Immutable evidence** — Forensic reconstruction of any decision
- 🛑 **Operator intervention** — Humans can intervene at any point
- 🔄 **Deterministic replay** — Any run can be reconstructed and verified
- 💰 **Cost governance** — Budget controls with hard limits and alerts

---

## Why Enterprise AI Needs Governance

| Problem | Traditional Agents | This Platform |
|---------|-------------------|---------------|
| Explainability | ❌ Black box | ✅ Causal narratives from evidence |
| Auditability | ❌ No audit trail | ✅ Immutable audit trail with hash chains |
| Controllability | ❌ Run until done | ✅ 8 intervention types |
| Sovereignty | ❌ Data leaves premises | ✅ Sovereignty-aware routing |
| Trust | ❌ Faith-based | ✅ Computed trust scores |
| Cost | ❌ Unbounded | ✅ Budget controls with limits |
| Replay | ❌ Cannot reconstruct | ✅ Deterministic replay |
| Disagreement | ❌ Suppressed | ✅ Surfaced and analyzed |

---

## Core Features

### 🧠 Multi-Model Cognitive Governance
Dynamic model selection based on task type, governance requirements, sovereignty constraints, and cost budgets. Supports Ollama, OpenAI, Anthropic, Gemini, and OpenRouter.

### ⚖️ Cognitive Arbitration Engine
Execute tasks across multiple models, analyze disagreement, and produce governed decisions. Disagreement is surfaced, never suppressed.

### 🔍 Explainability Engine
Causal narratives grounded in actual database records. Eight explanation types: runtime, trust, drift, replay, governance, memory, interventions, autonomy.

### 🏛️ Governance Layer
OPA Rego policies enforced at every layer. RBAC with 30+ granular permissions. Trust scores that affect autonomy levels.

### 🔒 Sovereignty-Aware Routing
Five sovereignty levels from `local_only` to `frontier_only`. Control over where data is processed and which models are used.

### 📜 Evidence & Replay
Immutable evidence bundles with hash-chained integrity. Deterministic replay of any previous run with tamper detection.

### 🛑 Operator Intervention
Eight intervention types: pause, resume, quarantine, rollback, escalate, throttle, override, terminate. All recorded in the audit trail.

### 🧠 Memory Lifecycle
Seven lifecycle states: active, stale, expired, archived, quarantined, pending_review, degraded. Archival preserves evidence links.

### 📊 Real-Time Telemetry
SSE streams for live event telemetry. Prometheus metrics. Structured logging with trace correlation.

---

## Documentation

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | This file — overview and quickstart |
| **[INSTALLATION.md](INSTALLATION.md)** | Complete installation + dependencies guide |
| **[FUNCTIONAL.md](FUNCTIONAL.md)** | Functional descriptions + execution overviews |
| **[TECHNICAL-ARCHITECTURE.md](TECHNICAL-ARCHITECTURE.md)** | Deep technical architecture |
| **[RELEASES.md](RELEASES.md)** | Release notes per version |
| **[Whitepaper](whitepaper/loveable-for-the-enterprise.md)** | 5000+ word technical whitepaper |
| **[Architecture](docs/architecture/overview.md)** | Architecture diagrams (Mermaid) |
| **[API Reference](docs/api/reference.md)** | Complete API endpoint reference |
| **[Runtime](docs/runtime/index.md)** | Runtime lifecycle, trust, drift, replay |
| **[Governance](docs/governance/index.md)** | Governance framework and policies |
| **[Security](docs/security/architecture.md)** | Security architecture |
| **[Deployment: Local](docs/deployment/local.md)** | Local installation guide |
| **[Deployment: Docker](docs/deployment/docker.md)** | Docker deployment guide |
| **[Deployment: VPS](docs/deployment/vps.md)** | VPS deployment guide |
| **[Deployment: Apple Silicon](docs/deployment/apple-silicon.md)** | Apple Silicon optimized setup |
| **[Examples](examples/README.md)** | Runnable example workflows |
| **[Contributing](CONTRIBUTING.md)** | Contribution guidelines |
| **[License](LICENSE)** | Apache 2.0 |

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
# Edit .env with your settings

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

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js 14 + TypeScript + Tailwind)          │
│  35+ Room Components • SSE • WebSocket • Recharts       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / SSE / WebSocket
┌────────────────────────▼────────────────────────────────┐
│  API Layer (FastAPI + Pydantic v2)                      │
│  27+ Endpoint Modules • Middleware • SSE Streams        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Engine Layer (17+ Specialized Engines)                 │
│  Model Router • Arbitration • Governance • Replay       │
│  Drift Control • Semantic Coverage • Evidence           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Infrastructure                                         │
│  PostgreSQL • Redis • Qdrant • Ollama • Prometheus      │
└─────────────────────────────────────────────────────────┘
```

See [TECHNICAL-ARCHITECTURE.md](TECHNICAL-ARCHITECTURE.md) for detailed architecture.

---

## Supported Providers

### Local

| Provider | Models | Sovereignty |
|----------|--------|-------------|
| Ollama | phi3, qwen2.5-coder, llama3.1, deepseek-r1 | ✅ Local |
| llama.cpp | Any GGUF model | ✅ Local |

### Remote

| Provider | Models | Sovereignty |
|----------|--------|-------------|
| OpenAI | GPT-4o, GPT-4o-mini, o1 | ☁️ Frontier |
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | ☁️ Frontier |
| Google | Gemini 1.5 Pro, Gemini 1.5 Flash | ☁️ Frontier |
| OpenRouter | 100+ models | ☁️ Frontier |

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

## API Overview

### Authentication
- `POST /api/v1/auth/login` — Login
- `POST /api/v1/auth/refresh` — Refresh token

### Projects & Runs
- `GET /api/v1/projects` — List projects
- `POST /api/v1/runs` — Start run
- `GET /api/v1/runs/{id}` — Get run details

### Operations
- `GET /api/v1/operations/summary` — System health
- `GET /api/v1/operations/events` — Event log
- `GET /api/v1/operations/events/stream` — SSE telemetry

### Explainability
- `GET /api/v1/explain/runtime/{id}` — Runtime explanation
- `GET /api/v1/explain/trust/{id}` — Trust explanation
- `GET /api/v1/explain/drift/{id}` — Drift explanation

### Model Router
- `GET /api/v1/model-router/capabilities` — Model capabilities
- `POST /api/v1/model-router/route` — Get routing decision
- `POST /api/v1/model-router/arbitrate` — Run arbitration

### Interventions
- `POST /api/v1/interventions/pause` — Pause
- `POST /api/v1/interventions/resume` — Resume
- `POST /api/v1/interventions/quarantine` — Quarantine
- `POST /api/v1/interventions/rollback` — Rollback

See [API Reference](docs/api/reference.md) for complete documentation.

---

## Release History

| Version | Date | Description |
|---------|------|-------------|
| [v0.1.0](RELEASES.md#v010--open-enterprise-release-2025-05-20) | 2025-05-20 | Open Enterprise Release — complete docs, deployment, whitepaper |
| [v0.5](RELEASES.md#v05--multi-model-cognitive-governance-2025-05-19) | 2025-05-19 | Multi-Model Cognitive Governance — router, arbitration, sovereignty |
| [v0.4](RELEASES.md#v04--enterprise-cognitive-operations-2025-05-19) | 2025-05-19 | Enterprise Cognitive Operations — monitoring, interventions, explainability |
| [v0.3.5](RELEASES.md#v035--integration-integrity-hardened-2025-05-17) | 2025-05-17 | Integration Integrity Hardened — drift control, metacognitive |
| [v0.3.3](RELEASES.md#v033--concurrency-stable-runtime-2025-05-16) | 2025-05-16 | Concurrency Stable — 25/25 stability, 5/5 tamper detection |
| [v0.3](RELEASES.md#v03--governed-runtime-observability-baseline-2025-05-15) | 2025-05-15 | Observability Baseline — 6 LIVE upgrades |
| [v0.2.0](RELEASES.md#v020--evidence-backed-runtime-2025-05-14) | 2025-05-14 | Evidence-Backed Runtime — PASS baseline |
| [v0.1.0](RELEASES.md#v010--golden-integrity-runtime-2025-05-14) | 2025-05-14 | Golden Integrity Runtime — initial baseline |

See [RELEASES.md](RELEASES.md) for detailed release notes.

---

## Roadmap

### v0.6 — Semantic Execution Memory
- Semantic execution patterns (not just facts)
- Learning from past runs
- Improved routing based on historical performance

### v0.7 — Ontology-Constrained Execution
- Formal domain models
- Constrained valid operations
- Ontology-aware governance

### v0.8 — Trust Decay Scoring
- Natural trust decay over time
- Reinforcement through success
- Prevention of stale trust

### v0.9 — Deception Detection
- Detect technically correct but misleading outputs
- Identify governance avoidance patterns
- Surface hidden biases

### v1.0 — Constitutional Governance
- Immutable constitutional principles
- Unoverrideable boundaries
- External audit support
- Evidence signing

---

## Security Disclaimer

This platform is designed for **governed autonomous operation within trusted environments**. It is not designed for direct exposure to untrusted users without additional security layers (WAF, API gateway, etc.).

**Always:**
- Deploy behind a reverse proxy with SSL termination
- Use strong JWT secrets (256-bit minimum)
- Rotate API keys regularly
- Review audit logs weekly
- Keep dependencies updated

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Run type check: `cd apps/web && npm run typecheck`
6. Submit a pull request

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com) — Web framework
- [Next.js](https://nextjs.org) — React framework
- [PostgreSQL](https://postgresql.org) — Database
- [Redis](https://redis.io) — Cache and queue
- [Qdrant](https://qdrant.tech) — Vector memory
- [Ollama](https://ollama.ai) — Local model serving
- [OpenTelemetry](https://opentelemetry.io) — Observability
- [OPA](https://openpolicyagent.org) — Policy engine

---

> *"Governance is not a constraint on AI capability. It is a prerequisite for AI deployment in any environment where decisions have consequences."*
