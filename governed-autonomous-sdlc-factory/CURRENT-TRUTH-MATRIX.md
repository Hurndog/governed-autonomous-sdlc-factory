# Current Truth Matrix

**Last updated:** 2025-05-20
**Commit:** `f41dcf5`
**Tag:** v0.5.1-truth-reconciled-runtime (pending)

This document is the **canonical runtime truth reference** for the Governed Autonomous SDLC Factory. All claims are grounded in code, tests, or evidence files.

---

## 1. Fully Operational Systems

These systems are implemented, tested, and validated:

| System | Location | Evidence |
|--------|----------|----------|
| **Backend test suite** | `apps/api/tests/` (14 files) | 128/128 PASS |
| **Frontend build** | `apps/web/` | TypeScript 0 errors, Next.js 14 build PASS |
| **JWT Authentication** | `apps/api/src/core/auth.py` (276 lines, 9 classes) | `test_security.py` PASS |
| **RBAC** | `apps/api/src/core/auth.py` + middleware | 30+ permissions, endpoint-level enforcement |
| **SSE Telemetry** | `apps/api/src/api/v1/endpoints/operations.py` (560 lines) | `test_e2e_pipeline.py` PASS |
| **Operator Interventions** | `apps/api/src/api/v1/endpoints/operator_intervention.py` (569 lines) | 8 types, RBAC-protected |
| **Memory Lifecycle** | `apps/api/src/api/v1/endpoints/memory_lifecycle.py` (601 lines) | 7 states, archival, quarantine |
| **Explainability Engine** | `apps/api/src/api/v1/endpoints/explainability.py` (970 lines) | 8 explanation types |
| **Drift Detection** | `apps/api/src/engines/drift_control_engine.py` (415 lines) | 6 dimensions, metacognitive control |
| **Trust Scoring** | `apps/api/src/engines/drift_control_engine.py` (RuntimeTrustScorer) | 5-component model |
| **Replay Integrity** | `apps/api/src/engines/drift_control_engine.py` (ReplayIntegrityVerifier) | Hash chain, tamper detection |
| **Semantic Coverage** | `apps/api/src/engines/semantic_coverage_engine.py` (1229 lines) | 31 functions, mutation testing |
| **Mutation Execution** | `SemanticCoverageEngine.execute_mutation()` | Plan → execute → score pipeline |
| **Pipeline Orchestration** | `apps/api/src/services/full_pipeline_orchestrator.py` (647 lines) | Full SDLC test PASS |
| **Model Router** | `apps/api/src/engines/model_router.py` (406 lines) | Capability matching, sovereignty routing |
| **Model Registry** | `apps/api/src/engines/model_registry.py` (211 lines) | Default configurations, stats tracking |
| **Evidence Capture** | `apps/api/src/api/v1/endpoints/evidence.py` | Per-run evidence bundles |
| **Cost Tracking** | `apps/api/src/api/v1/endpoints/costs.py` | Tokenomics, agent attribution |
| **Frontend Rooms** | `apps/web/src/components/rooms/` (30 components) | OperationsCenter, ExplainabilityRoom, etc. |
| **Frontend UI** | `apps/web/src/components/ui/` (10 components) | Cards, charts, badges, gauges |
| **Frontend API Client** | `apps/web/src/lib/api.ts` (827 lines) | Full backend integration |
| **Docker Compose** | `docker-compose.yml` | 7 services (API, Web, PostgreSQL, Redis, Qdrant, Prometheus, Grafana) |

---

## 2. Operational but Limited Systems

These systems work but have known limitations:

| System | Limitation |
|--------|------------|
| **Multi-model routing** | Registry populates defaults but `list_models()` returns empty when all models have `is_available=False` — filtering bug |
| **Mutation execution** | Works for Python test code only; no multi-language support |
| **Semantic coverage scoring** | Deterministic/rule-based, not LLM-based. Real semantic similarity not computed. |
| **Explainability narratives** | Template-based, not LLM-generated. Causal chains are structural, not inferential. |
| **Drift detection** | Rule-based thresholds, not adaptive. No historical baseline learning. |
| **Frontend-backend integration** | API client exists but E2E integration tests are limited. Some rooms use mock data. |
| **Ollama provider** | Requires local Ollama instance. No auto-detection of available models. |
| **Remote providers** | OpenAI/Anthropic/Gemini endpoints exist but require API keys. Not tested with live keys. |

---

## 3. Experimental Systems

These systems are architecturally present but not operationally validated:

| System | Status |
|--------|--------|
| **Cognitive Arbitration Engine** | Engine exists, multi-model execution path defined. No real-provider disagreement testing. |
| **Sovereignty routing** | 5 levels defined in code. Edge cases (fallback, mixed-mode) untested. |
| **Semantic execution memory** | Planned. Not yet implemented. |
| **Ontology-constrained execution** | Planned. Not yet implemented. |
| **Trust decay scoring** | Planned. Not yet implemented. |
| **Deception detection** | Planned. Not yet implemented. |
| **Constitutional governance** | Planned. Not yet implemented. |

---

## 4. Production Hardening Gaps

These are required for production deployment but are **not yet implemented**:

| Gap | Impact | Effort |
|-----|--------|--------|
| **No CI/CD pipeline** | No automated testing on push/PR. Manual test runs only. | Medium |
| **No rate limiting** | API vulnerable to abuse. | Low |
| **No security headers** | No HSTS, CSP, X-Frame-Options. | Low |
| **No TLS/SSL config** | Must be added via reverse proxy. | Low |
| **No container health checks** | Docker Compose services have no health checks. | Low |
| **No log rotation** | Logs grow unbounded. | Low |
| **No automated backups** | Manual backup scripts only. | Medium |
| **No DB connection pooling** | Default SQLAlchemy pool only. | Low |
| **No HA/failover** | Single-instance deployment only. | High |
| **No enterprise load testing** | Validated for development workloads only. | Medium |
| **No CSRF protection** | API is stateless (JWT) but frontend has no CSRF tokens. | Low |
| **No request size limits** | No protection against large payloads. | Low |

---

## 5. Security Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No rate limiting | High | API can be flooded |
| No security headers | Medium | XSS, clickjacking possible |
| No CSRF protection | Medium | Stateless API mitigates but not eliminated |
| No request validation beyond Pydantic | Medium | Business logic validation incomplete |
| No audit log export | Medium | Audit trail exists but no export mechanism |
| No secrets rotation | High | JWT secrets must be rotated manually |
| No network segmentation | Medium | All services on same Docker network |
| No WAF | High | No web application firewall |

---

## 6. Operational Limitations

| Limitation | Details |
|------------|---------|
| **No enterprise-scale deployment proof** | Validated on single Mac Studio only |
| **Limited long-horizon validation** | 25 sequential runs tested, no multi-day soak test |
| **Limited larger-model validation** | Tested with phi3:mini (2.3GB), not 70B+ models |
| **No distributed replay federation** | Single-instance replay only |
| **No mature CI/CD pipeline** | No automated testing, linting, or deployment |
| **No enterprise HA validation** | No failover, no load balancing |
| **Limited multi-tenant testing** | Workspace isolation exists but not stress-tested |
| **No production monitoring** | Prometheus config exists, Grafana dashboards not pre-built |

---

## 7. Runtime Validation Evidence

| Evidence File | What It Proves |
|---------------|----------------|
| `evidence/v036-real-llm-variability.md` | 30 real Ollama calls, drift detection validated |
| `evidence/v036-hallucination-containment.md` | 5/6 hallucination patterns detected |
| `evidence/v036-overload-replay-growth.md` | 1000 records, <1.33ms latency, ~1540 events/s |
| `evidence/official-v04-enterprise-cognitive-operations-report.md` | v0.4 full validation report |
| `evidence/v04-pass5-runtime-explainability.md` | 8 explanation types validated |
| `evidence/v04-pass4-memory-lifecycle-archival.md` | 7 lifecycle states, archival verified |
| `evidence/v04-pass3-operator-intervention-console.md` | 8 intervention types, RBAC verified |
| `evidence/v04-pass2-realtime-telemetry.md` | SSE stream validated |
| `evidence/v04-pass1-runtime-operations-baseline.md` | Operations summary endpoint validated |
| `evidence/v05-model-router-baseline.md` | Model router capability registry validated |

---

## 8. Test Coverage

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_artifact_hash_integrity.py` | Artifact hashing, chain integrity | PASS |
| `test_concurrency.py` | 17/17 parallel runs | PASS |
| `test_cost_report.py` | Cost tracking, tokenomics | PASS |
| `test_drift_control.py` | 8/8 drift/metacognitive/replay | PASS |
| `test_e2e_pipeline.py` | Full pipeline E2E (4 tests) | PASS |
| `test_full_pipeline_execution.py` | Complete SDLC pipeline (1 test) | PASS |
| `test_long_run_stability.py` | 25/25 sequential runs | PASS |
| `test_memory_schema.py` | Memory lifecycle schema | PASS |
| `test_multi_model_validation.py` | Registry, router, capabilities (4 tests) | PASS |
| `test_release_gate.py` | Release gate enforcement | PASS |
| `test_replay_forensics.py` | 5/5 tampering detection | PASS |
| `test_security.py` | JWT auth, RBAC | PASS |
| `test_semantic_coverage.py` | Semantic coverage engine | PASS |
| **Total** | **128 tests** | **128 PASS** |

---

## 9. Frontend Component Reality

### Fully Implemented Rooms (substantive implementations)
`AgentCommandCenter.tsx` (283 lines), `ArtifactExplorer.tsx` (180), `BacklogChecklist.tsx` (247), `BuildMap.tsx` (448), `Dashboard.tsx` (288), `EvidenceCenter.tsx` (107), `ExecutiveCockpit.tsx` (288), `ExplainabilityRoom.tsx` (448), `GovernanceGates.tsx` (161), `GovernanceRoom.tsx` (247), `IntegrityRoom.tsx` (137), `LogsDiagnostics.tsx` (112), `MemoryOperations.tsx` (247), `ModelOperationsCenter.tsx` (251), `OperationsCenter.tsx` (406), `OperatorConsole.tsx` (275), `ProcessTimeline.tsx` (306), `ReplayChamber.tsx` (201), `RunControlRoom.tsx` (173), `RunReplay.tsx` (164), `SDLCNavigator.tsx` (359), `SemanticCoverage.tsx` (244), `SettingsProviders.tsx` (156), `SpecRoom.tsx` (160), `Tokenomics.tsx` (293), `TraceabilityRoom.tsx` (144), `UserManagement.tsx` (299), `ArchitectureIntelligence.tsx` (89)

### Thin Wrappers (intentional)
`ArchitectureRoom.tsx` (8 lines) — redirects to `GovernanceRoom`
`CommandCenter.tsx` (9 lines) — redirects to `Dashboard`

---

## 10. Backend Engine Reality

### Core Engines (substantive implementations)
| Engine | Lines | Functions | Classes |
|--------|-------|-----------|---------|
| `semantic_coverage_engine.py` | 1229 | 31 | 1 |
| `full_pipeline_orchestrator.py` | 647 | 10 | 2 |
| `explainability.py` (endpoints) | 970 | 19 | 12 |
| `memory_lifecycle.py` (endpoints) | 601 | 11 | 3 |
| `operator_intervention.py` (endpoints) | 569 | 11 | 3 |
| `operations.py` (endpoints) | 560 | 19 | 6 |
| `model_router.py` | 406 | 11 | 3 |
| `drift_control_engine.py` | 415 | 19 | 4 |
| `replay_engine.py` | 452 | 12 | 2 |
| `governance_engine.py` | 251 | 3 | 2 |
| `traceability.py` | 200+ | 10+ | 1+ |
| `specification_engine.py` | 150+ | 5+ | 1+ |
| `architecture_engine.py` | 150+ | 5+ | 1+ |
| `inference_trace.py` | 100+ | 5+ | 2+ |
| `divergence.py` | 100+ | 5+ | 1+ |
| `snapshots.py` | 100+ | 5+ | 1+ |
| `source_extractor.py` | 100+ | 5+ | 1+ |
| `test_engine.py` | 100+ | 5+ | 1+ |
| `model_registry.py` | 211 | 10 | 2 |
| `model_providers.py` | 200+ | 10+ | 3+ |
| `ollama_provider.py` | 106 | 3 | 1 |

---

## 11. Remaining Missing Capabilities

These are **genuinely not implemented**:

| Capability | Planned In | Notes |
|------------|------------|-------|
| Semantic execution memory | v0.6 | Learning from past runs |
| Ontology-constrained execution | v0.7 | Formal domain models |
| Trust decay scoring | v0.8 | Natural trust decay over time |
| Deception detection | v0.9 | Detect misleading outputs |
| Constitutional governance | v1.0 | Immutable principles |
| Evidence signing | v1.0 | Cryptographic evidence signing |
| Distributed replay federation | Future | Cross-instance replay |
| Multi-language mutation testing | Future | Beyond Python |
| LLM-based explainability | Future | Narrative generation |
| Adaptive drift detection | Future | ML-based thresholds |
| Production CI/CD | Future | GitHub Actions |
| Enterprise HA | Future | Multi-instance deployment |

---

## 12. Maturity Assessment by Dimension

No single percentage. Dimension-specific assessment:

| Dimension | Maturity | Notes |
|-----------|----------|-------|
| **Governed cognitive runtime** | High | 21 engines, 128 tests, full pipeline validated |
| **Autonomous SDLC execution** | Medium-High | Pipeline works, mutation testing limited to Python |
| **Enterprise operations** | High | 5 operational frontend rooms, SSE, interventions |
| **Production readiness** | Low-Medium | No CI/CD, no HA, no security hardening |
| **Multi-model governance** | Medium | Router + registry work, arbitration untested with real providers |
| **Frontend completeness** | Medium-High | 30 rooms, some thin wrappers, mock data in places |
| **Security** | Medium | JWT+RBAC works, no rate limiting, no headers |
| **Observability** | High | SSE, Prometheus, structured logging, evidence bundles |
| **Test coverage** | High | 128/128 PASS, E2E pipeline tested |
| **Documentation** | Medium | Comprehensive but was outdated (being reconciled now) |

---

*This document must be updated whenever runtime capabilities change. No aspirational claims. Only evidence-grounded truth.*
