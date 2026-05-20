# Release Notes

Alle significante releases van de Governed Autonomous SDLC Factory.

---

## v0.5.1 — Truth Closure (2025-05-20)

### 🔧 E2E Test Fixes + Mutation Execution Reconciliation

**Fixes:**
- **`test_mutation_execution`**: Test used wrong method name (`execute_mutation` vs `execute_mutation_tests`) and wrong model fields. Fixed by adding `execute_mutation()` convenience method to `SemanticCoverageEngine` and updating test to use correct `RequirementNormalization` seeding and `MutationTest` field names.
- **`test_release_gate_enforcement`**: Test passed non-existent fields (`total_requirements`, `covered_requirements`, `total_obligations`, `fulfilled_obligations`, `avg_alignment_score`) to `SemanticCoverageReport`. Fixed by removing invalid fields and correcting `id` type.
- **Engine bug fix**: `execute_mutation_tests` referenced `obl.test_code` but `TestObligation` has no such field — changed to `obl.proof_statement`.

**New:**
- `SemanticCoverageEngine.execute_mutation(run_id) → float` — convenience method that plans, executes, and scores mutations in one call
- `test_full_pipeline_execution` — full SDLC pipeline test covering specification → architecture → semantic coverage → drift → evidence → finalize
- `test_multi_model_validation` — model registry, router initialization, capability matching

**Test results:** 128/128 PASS (was 125/127 before fixes)

---

## v0.5 — Multi-Model Cognitive Governance (2025-05-19)

### 🧠 Phase 1: Model Router & Cognitive Arbitration

**Nieuw:**
- **CognitiveModelRouter** (`apps/api/src/engines/model_router.py`, 406 lines) — dynamic model selection based on task type, capability requirements, sovereignty constraints, cost budgets
- **ModelRegistry** (`apps/api/src/engines/model_registry.py`, 211 lines) — 16-dimension capability profiles, default model configurations, stats tracking
- **ModelProviders** (`apps/api/src/engines/model_providers.py`) — unified provider abstraction (Ollama, LM Studio, OpenAI, Anthropic)
- **Cognitive Arbitration Engine** — multi-model execution, consensus scoring, disagreement detection
- **Sovereignty-Aware Routing** — 5 levels (local_only, sovereign_preferred, sovereign_required, hybrid, frontier_only)
- **10 task types** — code_generation, architecture_reasoning, governance_analysis, etc.
- **5 API endpoints** — capabilities, route, arbitrate, health, sovereignty
- **ModelOperationsCenter.tsx** — frontend UI with capability cards, sovereignty dashboard, trust evolution

**Status:** Phase 1 delivered. Engine exists, capability registry populated with defaults. Real-provider testing limited (requires API keys).

---

## v0.4 — Enterprise Cognitive Operations (2025-05-19)

### 📊 Pass 1-5: Operations, Telemetry, Interventions, Memory, Explainability

**Nieuw:**
- **Operations Summary** (`GET /api/v1/operations/summary`) — 8 health dimensions, run counts, alerts
- **SSE Telemetry Stream** (`GET /api/v1/operations/events/stream`) — real-time event streaming via Server-Sent Events
- **Operator Intervention Console** — 8 intervention types (pause, resume, quarantine, rollback, escalate, throttle, override, terminate), 10 RBAC permissions
- **Memory Lifecycle** — 7 states (active, stale, expired, archived, quarantined, pending_review, degraded), aging logic, archival with evidence preservation
- **Explainability Engine** (`apps/api/src/api/v1/endpoints/explainability.py`, 970 lines) — 8 explanation types (runtime, trust, drift, replay, governance, memory, interventions, autonomy), causal chain construction, uncertainty disclosures
- **OperationsCenter.tsx** — real-time monitoring dashboard with SSE connection
- **OperatorConsole.tsx** — intervention controls with confirmation and audit trail
- **MemoryOperations.tsx** — lifecycle management UI
- **ExplainabilityRoom.tsx** — forensic reconstruction UI with 8 tabbed views

**Status:** All 5 passes delivered. 30+ new API endpoints. 4 new frontend components.

---

## v0.3.5 — Integration Integrity Hardened (2025-05-19)

### 🔧 Drift Control + Metacognitive + Replay Integration

**Nieuw:**
- **DriftDetectionEngine** — 6 drift dimensions (semantic, governance, cost, evidence, context, cognitive/goal)
- **MetacognitiveController** — self-monitoring, operator intervention recording, runtime state evaluation
- **ReplayIntegrityVerifier** — hash chain validation, tamper detection
- **RuntimeTrustScorer** — 5-component trust model (accuracy, hallucination rate, replay stability, governance compliance, operator feedback)

**Verbeterd:**
- SQL transaction issues opgelost (ON CONFLICT → session recovery patterns)
- FK volgorde gecorrigeerd in test fixtures
- Session isolatie per test

**Status:** 8/8 drift/metacognitive/replay tests PASS

---

## v0.3.3 — Concurrency Stable Runtime (2025-05-19)

### 🔒 Long-Run Stability + Replay Forensics

**Nieuw:**
- **Concurrency validation** — 17/17 parallel runs PASS
- **Replay forensics** — 5/5 tampering attempts detected
- **JWT hardening** — token security improvements

**Status:** 25/25 long-run stability tests PASS

---

## v0.3.2 — Schema and Security Hardening (2025-05-19)

**Verbeterd:**
- Database schema hardening — constraints, indexes, FK relationships
- Security verbeteringen — input validation, output encoding
- Pydantic v2 migratie — `ConfigDict` replacing class-based `config`

---

## v0.3.1 — Epistemic Hardening (2025-05-19)

**Nieuw:**
- **Iteration limits** — bounded semantic iterations (max 5)
- **Safety guard configuration** — 11 configurable safety guard types
- **Schema fixes** — database schema corrections for production alignment

---

## v0.3 — Governed Runtime Observability Baseline (2025-05-19)

### 📡 Auth + RBAC + Frontend Integration + Tokenomics

**Nieuw:**
- **JWT Authentication** (`apps/api/src/core/auth.py`, 276 lines, 9 classes) — token generation, validation, refresh
- **RBAC** — 30+ granular permissions, role-permission assignments, middleware enforcement
- **Auth endpoints** — login, refresh, logout, me
- **Frontend auth store** (`authStore.ts`, 89 lines) — token management, auto-refresh
- **Tokenomics** — cost tracking per action, agent attribution, cost report endpoints
- **Frontend API integration** — all rooms connected to backend API
- **Premium frontend** — 30 room components, dark ops UI, WebSocket support

**Status:** 82/82 tests PASS. Frontend build PASS. TypeScript 0 errors.

---

## v0.2.0 — Evidence-Backed Runtime (2025-05-14)

### ✅ PASS Baseline

**Nieuw:**
- **Pipeline execution** — LangGraph-style orchestration, phase coordination
- **Semantic coverage scoring** — computed from real DB records
- **Release gate** — blocks releases below quality threshold
- **Seven-component integrity** — artifact hashing, event sourcing, snapshot integrity, lineage tracking, evidence binding, replay verification, semantic coverage
- **Safety guards** — 11 types implemented and persisted
- **Conflict detection** — 4 patterns (naming, dependency, temporal, semantic)
- **Evidence capture** — 50+ evidence files, per-run evidence bundles
- **Backup & restore** — verified (9MB bundle)
- **Deterministic replay** — snapshot-based reconstruction

**Frontend:**
- Next.js 14 + React + Tailwind + shadcn/ui
- TypeScript strict mode — 0 errors
- Build — 4 pages (Command Center, Governance, Architecture, Settings)

**Backend:**
- FastAPI + Pydantic + SQLAlchemy/asyncpg
- PostgreSQL — operational
- 82/82 tests passing
- MCP tool integration — filesystem, GitHub, memory, test runner

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

| Issue | Status | Notes |
|-------|--------|-------|
| `ModelRegistry.list_models()` returns empty when all models unavailable | 🐛 Known | Filtering bug — models with `is_available=False` are excluded from listing |
| Alembic migrations non-standard path | ⚠️ Known | Migrations in `src/core/migrations` instead of `alembic/` |
| No async pytest support | ⚠️ Known | `pytest-asyncio` not configured in `conftest.py` |
| Frontend rooms `ArchitectureRoom.tsx` and `CommandCenter.tsx` are thin wrappers | ℹ️ Intentional | Redirect to `Dashboard` and `GovernanceRoom` respectively |
