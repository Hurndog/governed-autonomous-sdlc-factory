# Release Notes

Alle significante releases van de Governed Autonomous SDLC Factory.

---

## v0.1.0 — Open Enterprise Release (2025-05-20)

### 🏛️ Public Release

Eerste publieke enterprise-grade release. Van prototype naar production-ready open source platform.

**Nieuw:**
- **Complete documentatie** — 21 docs, 150K+ content
- **Whitepaper** — "Loveable for the Enterprise" (62KB, 8 secties)
- **Master README** — Enterprise-grade met vision, architectuur, quickstart
- **Deployment guides** — Local, Docker, VPS, Apple Silicon
- **Security architecture** — RBAC, encryption, audit trails
- **Governance framework** — Policies, trust scoring, sovereignty
- **Runtime docs** — Lifecycle, drift detection, replay
- **API reference** — 27+ endpoints gedocumenteerd
- **Docker Compose** — Full service stack
- **Frontend Dockerfile** — Productie-klaar
- **Prometheus config** — Metrics collection
- **CONTRIBUTING.md + LICENSE** — Apache 2.0
- **Screenshot assets** — 4 UI panel visualisaties

**Verbeterd:**
- README herschreven van prototype naar enterprise
- Architectuur-diagrammen met Mermaid
- Functionele beschrijving per module
- Installation guide met troubleshooting

**Status:**
- Backend: 125/127 tests PASS
- Frontend: TypeScript 0 errors
- GitHub: gepusht + tag `v0.1.0-open-enterprise-release`

---

## v0.5 — Multi-Model Cognitive Governance (2025-05-19)

### 🧠 Phase 1: Model Router & Cognitive Arbitration

**Nieuw:**
- **Model Provider Abstraction Layer** — Unified interface voor Ollama, OpenAI, Anthropic, Gemini, OpenRouter
- **CognitiveModelRouter** — Dynamic model selection op task type, governance, sovereignty, cost
- **ModelCapabilityRegistry** — 16-dimension capability profiles per model
- **CognitiveArbitrationEngine** — Multi-model execution met consensus scoring en disagreement detection
- **Sovereignty-Aware Routing** — 5 sovereignty levels (local_only → frontier_only)
- **10 task types** — code_generation, architecture_reasoning, governance_analysis, etc.
- **5 API endpoints** — capabilities, route, arbitrate, health, sovereignty
- **ModelOperationsCenter.tsx** — Frontend UI met 3 tabs

**Verbeterd:**
- Provider-agnostic business logic
- Normalized response format (ModelResponse)
- Token accounting en latency metrics
- Confidence metadata

**Status:** 122/127 tests PASS, TS 0 errors

---

## v0.4 — Enterprise Cognitive Operations (2025-05-19)

### 📊 Pass 1-5: Operations, Telemetry, Interventions, Memory, Explainability

**Nieuw:**
- **Operations Summary** (`GET /api/v1/operations/summary`) — 8 health dimensions
- **SSE Telemetry Stream** (`GET /api/v1/operations/events/stream`) — Real-time events
- **Operator Intervention Console** — 8 intervention types, 10 RBAC permissions
- **Memory Lifecycle** — 7 states (active, stale, expired, archived, quarantined, pending_review, degraded)
- **Explainability Engine** — 8 explanation types grounded in evidence
- **OperationsCenter.tsx** — Real-time monitoring dashboard
- **OperatorConsole.tsx** — Intervention controls
- **MemoryOperations.tsx** — Lifecycle management UI
- **ExplainabilityRoom.tsx** — Forensic reconstruction UI

**Verbeterd:**
- 30+ nieuwe API endpoints
- 4 nieuwe frontend components
- Evidence-grounded explanations (geen hallucinaties)

**Status:** 122/127 tests PASS, TS 0 errors

---

## v0.3.5 — Integration Integrity Hardened (2025-05-17)

### 🔧 Drift Control + Metacognitive + Replay Integration

**Nieuw:**
- **DriftControlEngine** — Cognitive drift detection en metacognitive control plane
- **Persistent Runtime Memory** — 85+ DB tabellen
- **Replay Transaction Manager** — Transaction-safe replay operations

**Verbeterd:**
- SQL transaction issues opgelost (ON CONFLICT → session recovery)
- FK volgorde gecorrigeerd
- Session isolatie per test

**Status:** 8/8 drift/metacognitive/replay tests PASS

---

## v0.3.3 — Concurrency Stable Runtime (2025-05-16)

### 🔒 Long-Run Stability + Replay Forensics

**Nieuw:**
- **Concurrency validation** — 17/17 parallel runs PASS
- **Replay forensics** — 5/5 tampering detected
- **JWT hardening** — Token security verbeterd

**Status:** 25/25 long-run stability tests PASS

---

## v0.3.2 — Schema and Security Hardening (2025-05-16)

**Verbeterd:**
- Database schema hardening
- Security verbeteringen
- Pydantic v2 migratie

---

## v0.3.1 — Epistemic Hardening (2025-05-16)

**Nieuw:**
- **Iteration limits** — Bounded semantic iterations
- **Safety guard configuration** — Configureerbare safety guards
- **Schema fixes** — Database schema correcties

---

## v0.3 — Governed Runtime Observability Baseline (2025-05-15)

### 📡 6 LIVE Upgrades + TypeScript Stabilization

**Nieuw:**
- **Semantic Coverage Engine** — Real-time coverage scoring
- **Release Gate** — Automated release gating
- **Seven-Component Integrity** — 0.9508 overall score
- **Safety Guards** — 11 types geïmplementeerd
- **Conflict Detection** — 4 patterns
- **Evidence Capture** — 50+ evidence files
- **Backup & Restore** — Verified (9MB bundle)
- **Deterministic Replay** — Snapshot-based replay

**Verbeterd:**
- TypeScript strict mode — 0 errors
- Frontend build — 4 pages
- Frontend-backend API integration

**Status:** 82/82 tests PASS

---

## v0.2.0 — Evidence-Backed Runtime (2025-05-14)

### ✅ PASS Baseline

**Nieuw:**
- **Pipeline execution** (LangGraph-style orchestration)
- **Semantic coverage scoring** — Computed from real DB records
- **Release gate** — Blocks below threshold
- **Seven-component integrity** scoring
- **Safety guards** (11 types)
- **Conflict detection** (4 patterns)
- **Evidence capture** — 50+ evidence files
- **Backup & restore** — Verified
- **Deterministic replay** — Supported via snapshots

**Frontend:**
- Next.js 14 + React + Tailwind
- TypeScript strict mode
- 4 pages: Command Center, Governance, Architecture, Settings

**Backend:**
- FastAPI + Pydantic
- PostgreSQL (SQLAlchemy/asyncpg)
- 82/82 tests passing
- MCP tool integration

**Status:** PASS (evidence-backed operational acceptance)

---

## v0.1.0 — Golden Integrity Runtime (2025-05-14)

### 🏗️ Initial Baseline

**Nieuw:**
- **Artifact hashing** (SHA-256)
- **Event sourcing** with hash chain
- **Snapshot integrity**
- **Lineage tracking**
- **Evidence binding**
- **Replay verification**
- **Semantic coverage scoring**

**Status:** Golden integrity runtime established

---

## Pre-existing Known Issues

Deze issues bestaan sinds v0.3 en zijn buiten scope van huidige releases:

| Issue | Symptom | Root Cause | Planned Fix |
|-------|---------|------------|-------------|
| `test_mutation_execution` | `AttributeError: execute_mutation` | `SemanticCoverageEngine.execute_mutation()` niet geïmplementeerd | v0.6 |
| `test_release_gate_enforcement` | `TypeError: total_requirements` | `SemanticCoverageReport` schema mismatch | v0.6 |
