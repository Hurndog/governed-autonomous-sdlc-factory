# Current Truth Matrix

**Last updated:** 2026-05-20
**Commit:** `f8e411b`
**Tag:** v0.5.1a-runtime-capability-closure

This document is the **canonical runtime truth reference** for the Governed Autonomous SDLC Factory. All claims are grounded in code, tests, or evidence files. No aspirational claims. Only evidence-grounded truth.

---

## Classification Schema

| Code | Meaning |
|------|---------|
| **FULLY OPERATIONAL** | Implemented, tested, validated with runtime evidence |
| **OPERATIONAL LIMITED** | Works but has known constraints |
| **EXPERIMENTAL** | Architecturally present, not operationally validated |
| **PRODUCTION-INCOMPLETE** | Works in dev, missing production hardening |
| **MISSING** | Not implemented |
| **UNVERIFIED** | Claimed but no evidence exists |

---

## 1. Backend Runtime Systems

| System | Classification | Evidence | Known Gaps |
|--------|---------------|----------|------------|
| **Test suite (142 tests)** | FULLY OPERATIONAL | `pytest` 142/142 PASS | No coverage metrics beyond pass/fail |
| **JWT Authentication** | FULLY OPERATIONAL | `test_security.py` 30+ tests PASS | Token refresh relies on client re-auth |
| **RBAC** | FULLY OPERATIONAL | 30+ permissions, endpoint-level enforcement | No dynamic role assignment UI |
| **API Router (28 endpoints)** | FULLY OPERATIONAL | All endpoints mounted, schema-validated | No rate limiting, no request size limits |
| **SSE Telemetry** | FULLY OPERATIONAL | `test_e2e_pipeline.py` PASS | No backpressure handling, no reconnect logic |
| **Operator Interventions** | FULLY OPERATIONAL | 8 types, RBAC-protected | No intervention audit trail export |
| **Memory Lifecycle** | FULLY OPERATIONAL | 7 states, archival, quarantine | No automatic stale-memory purging |
| **Explainability Engine** | OPERATIONAL LIMITED | 8 explanation types, template-based | Not LLM-generated; causal chains are structural not inferential |
| **Drift Detection** | OPERATIONAL LIMITED | 6 dimensions, metacognitive control | Rule-based thresholds, not adaptive; no historical baseline learning |
| **Trust Scoring** | OPERATIONAL LIMITED | 5-component model | Static weights, not learned; no trust decay |
| **Replay Integrity** | FULLY OPERATIONAL | Hash chain, tamper detection, 5/5 forensics tests | Single-instance only; no distributed federation |
| **Semantic Coverage Engine** | OPERATIONAL LIMITED | 31 functions, mutation testing | Deterministic/rule-based, not LLM-based semantic similarity |
| **Mutation Execution** | OPERATIONAL LIMITED | Plan → execute → score pipeline | Python-only; no multi-language support |
| **Pipeline Orchestrator** | FULLY OPERATIONAL | Full SDLC pipeline test PASS | No parallel phase execution |
| **Model Registry** | FULLY OPERATIONAL | Fixed in v0.5.1A; defaults visible, availability tracked | No automatic health probing |
| **Model Router** | OPERATIONAL LIMITED | Capability matching, sovereignty routing, real Ollama call validated | Only Ollama tested; OpenAI/Anthropic/Gemini untested (no keys) |
| **Model Providers** | OPERATIONAL LIMITED | 6 providers (Ollama, OpenAI, Anthropic, Gemini, OpenRouter, OllamaProvider) | Only Ollama with real keys; others are structural |
| **Cognitive Arbitration Engine** | OPERATIONAL LIMITED | 6 tests PASS (agreement, disagreement, contradiction, low-confidence, escalation, persistence) | Single-provider tested; real multi-provider disagreement untested |
| **Conflict Detection** | EXPERIMENTAL | Engine exists | No integration with arbitration engine |
| **Inference Tracing** | EXPERIMENTAL | Trace records exist | No visualization, no analysis tools |
| **Source Extraction** | OPERATIONAL LIMITED | Extracts from Python files | No multi-language parser |
| **Hash Propagation** | FULLY OPERATIONAL | Artifact chain integrity verified | N/A |
| **Safety Guards** | FULLY OPERATIONAL | 435 lines, timeout/budget/convergence limits | Guards exist but not tested under overload |
| **Database (SQLite dev / PostgreSQL prod)** | PRODUCTION-INCOMPLETE | 14 SQL migrations, schema stable | No connection pooling config; no read replicas |
| **Event Bus** | FULLY OPERABILITY | In-memory pub/sub | No persistence; events lost on restart |
| **Startup Diagnostics** | FULLY OPERATIONAL | Pre-flight checks at boot | No automated remediation |

---

## 2. Frontend Systems

| System | Classification | Evidence | Known Gaps |
|--------|---------------|----------|------------|
| **Build** | FULLY OPERATIONAL | Next.js 14, TypeScript 0 errors | N/A |
| **Authentication UI** | FULLY OPERATIONAL | Login page, JWT storage, AuthGuard | No token refresh flow |
| **Dashboard** | OPERATIONAL LIMITED | 288 lines, real data from /operations | Limited widget configurability |
| **SDLC Navigator** | FULLY OPERATIONAL | 359 lines, full pipeline visualization | No drag-and-drop reordering |
| **Explainability Room** | OPERATIONAL LIMITED | 448 lines, 8 explanation types | Template narratives only |
| **Replay Chamber** | FULLY OPERATIONAL | 201 lines, replay visualization | No side-by-side diff view |
| **Model Operations Center** | OPERATIONAL LIMITED | 251 lines, provider/routing views | No live health probe integration |
| **Governance Room** | FULLY OPERATIONAL | 247 lines, governance state | No real-time gate updates |
| **Evidence Center** | OPERATIONAL LIMITED | 107 lines, evidence bundle view | No cryptographic signature verification |
| **Memory Operations** | FULLY OPERATIONAL | 247 lines, 7 lifecycle states | No bulk operations |
| **Operator Console** | OPERATIONAL LIMITED | 275 lines, 8 intervention types | No intervention history timeline |
| **Architecture Room** | PRODUCTION-INCOMPLETE | Thin wrapper (8 lines), redirects | Not a real implementation |
| **Command Center** | PRODUCTION-INCOMPLETE | Thin wrapper (9 lines), redirects | Not a real implementation |
| **API Client** | OPERATIONAL LIMITED | 827 lines, full backend integration | No request retry; limited error recovery |

---

## 3. Infrastructure & Deployment

| System | Classification | Evidence | Known Gaps |
|--------|---------------|----------|------------|
| **Docker Compose** | OPERATIONAL LIMITED | 7 services defined, health checks present | No resource limits; no logging drivers; no restart backoff |
| **Dockerfile (API)** | PRODUCTION-INCOMPLETE | Multi-stage build exists | No non-root user; no distroless base |
| **Dockerfile (Web)** | PRODUCTION-INCOMPLETE | Next.js build + serve | No non-root user |
| **Prometheus** | PRODUCTION-INCOMPLETE | Config exists, port 9090 | No custom metrics pipeline; no alerting rules |
| **Grafana** | PRODUCTION-INCOMPLETE | Deployed at port 3001 | No pre-built dashboards; default credentials |
| **Redis** | FULLY OPERATIONAL | Configured with persistence, maxmemory | No Redis Sentinel; no failover |
| **PostgreSQL (Docker)** | PRODUCTION-INCOMPLETE | Health check, persistent volume | No replication; no automated backups |
| **Qdrant** | PRODUCTION-INCOMPLETE | Health check, persistent volume | No collection backup strategy |
| **CI/CD** | MISSING | None | No GitHub Actions; no automated testing on push |
| **Rate Limiting** | MISSING | None | API vulnerable to abuse |
| **TLS/SSL** | MISSING | None | Must be added via reverse proxy (nginx/traefik) |
| **Security Headers** | MISSING | None | No HSTS, CSP, X-Frame-Options |
| **CSRF Protection** | MISSING | None | Stateless API mitigates but not eliminated |
| **Log Rotation** | MISSING | None | Container logs grow unbounded |
| **Automated Backups** | MISSING | None | Manual pg_dump only |
| **WAF** | MISSING | None | No web application firewall |
| **HA/Failover** | MISSING | None | Single-instance deployment only |
| **Load Balancing** | MISSING | None | No horizontal scaling |
| **Secrets Management** | PRODUCTION-INCOMPLETE | Env vars in docker-compose | Default credentials in plaintext; no vault integration |
| **Network Segmentation** | PRODUCTION-INCOMPLETE | All services on same Docker network | No isolated networks per tier |

---

## 4. Multi-Model Governance

| Capability | Classification | Evidence | Known Gaps |
|-----------|---------------|----------|------------|
| **Model Registry** | FULLY OPERATIONAL | Defaults load correctly; availability tracked | No auto-health-probe |
| **Capability Profiles (16-dim)** | FULLY OPERATIONAL | Per-model capability registry | Static profiles; not learned from benchmark |
| **Cognitive Model Router** | OPERATIONAL LIMITED | Task routing, sovereignty levels, cost/latency constraints | Only Ollama tested live |
| **5 Sovereignty Levels** | FULLY OPERATIONAL | local_only → frontier_only | Edge cases untested |
| **Cognitive Arbitration Engine** | OPERATIONAL LIMITED | 6 tests PASS, disagreement detection, governance risk | No real multi-provider live test |
| **Provider: Ollama** | FULLY OPERATIONAL | Real phi3:mini inference validated | Auto-detect models missing |
| **Provider: OpenAI** | UNVERIFIED | Endpoint code exists | No API key configured |
| **Provider: Anthropic** | UNVERIFIED | Endpoint code exists | No API key configured |
| **Provider: Gemini** | UNVERIFIED | Endpoint code exists | No API key configured |
| **Provider: OpenRouter** | UNVERIFIED | Endpoint code exists | No API key configured |

---

## 5. Evidence & Replay

| Capability | Classification | Evidence | Known Gaps |
|-----------|---------------|----------|------------|
| **Evidence Bundles** | FULLY OPERATIONAL | Per-run evidence, JSON-serializable | No cryptographic signing |
| **Evidence Storage** | OPERATIONAL LIMITED | Filesystem-based | No deduplication; unbounded growth |
| **Replay Chain** | FULLY OPERATIONAL | Hash chain integrity verified | No compression; no archival policy |
| **Replay Forensics** | FULLY OPERATIONAL | 5/5 tampering detection tests | Single-instance only |
| **Replay Transaction Manager** | FULLY OPERATIONAL | ACID replay transactions | No multi-instance replay federation |
| **Drift-Aware Replay** | OPERATIONAL LIMITED | Drift detection integrated | Rule-based thresholds only |

---

## 6. Security Assessment

| Control | Status | Notes |
|---------|--------|-------|
| Authentication (JWT) | FULLY OPERATIONAL | HS256, 60-min expiry, 32-byte minimum secret |
| Authorization (RBAC) | FULLY OPERATIONAL | 30+ permissions, endpoint-level |
| Secrets at rest | PRODUCTION-INCOMPLETE | Default credentials in docker-compose.yml |
| Secrets rotation | MISSING | JWT secrets must be rotated manually |
| Rate limiting | MISSING | High risk |
| Security headers | MISSING | Medium risk (XSS, clickjacking) |
| CSRF protection | MISSING | Medium risk |
| Audit log export | MISSING | Audit trail exists internally but no export |
| Network segmentation | PRODUCTION-INCOMPLETE | Flat Docker network |
| WAF | MISSING | High risk |
| Input validation | OPERATIONAL LIMITED | Pydantic schemas only; no business logic validation |
| Request size limits | MISSING | No protection against large payloads |

---

## 7. Evidence Files

| File | What It Proves |
|------|----------------|
| `evidence/v036-real-llm-variability.md` | 30 real Ollama calls, drift detection validated |
| `evidence/v036-hallucination-containment.md` | 5/6 hallucination patterns detected |
| `evidence/v036-overload-replay-growth.md` | 1000 records, <1.33ms latency |
| `evidence/official-v04-enterprise-cognitive-operations-report.md` | v0.4 full validation |
| `evidence/v04-pass5-runtime-explainability.md` | 8 explanation types |
| `evidence/v04-pass4-memory-lifecycle-archival.md` | 7 lifecycle states |
| `evidence/v04-pass3-operator-intervention-console.md` | 8 intervention types |
| `evidence/v04-pass2-realtime-telemetry.md` | SSE stream |
| `evidence/v04-pass1-runtime-operations-baseline.md` | Operations summary |
| `evidence/v05-model-router-baseline.md` | Model router capability registry |
| `evidence/v051a-runtime-capability-closure.md` | v0.5.1A fixes: registry, router, arbitration, pipeline |

---

## 8. Test Coverage

| Area | Test Files | Test Count | Status |
|------|-----------|------------|--------|
| Security (JWT, RBAC) | `test_security.py` | 30+ | PASS |
| E2E Pipeline | `test_e2e_pipeline.py` | 4+ | PASS |
| Full Pipeline Execution | `test_full_pipeline_execution.py` | 1+ | PASS |
| Semantic Coverage | `test_semantic_coverage.py` | multiple | PASS |
| Drift Control | `test_drift_control.py` | 8 | PASS |
| Multi-Model Validation | `test_multi_model_validation.py` | 4+ | PASS |
| Replay Forensics | `test_replay_forensics.py` | 5 | PASS |
| Concurrency | `test_concurrency.py` | 17 | PASS |
| Long-Run Stability | `test_long_run_stability.py` | 25 | PASS |
| Release Gate | `test_release_gate.py` | multiple | PASS |
| Cost Tracking | `test_cost_report.py` | multiple | PASS |
| Memory Schema | `test_memory_schema.py` | multiple | PASS |
| Artifact Integrity | `test_artifact_hash_integrity.py` | multiple | PASS |
| Model Registry v0.5.1A | `test_model_registry_fix.py` | 4 | PASS |
| Router v0.5.1A | `test_router_operational.py` | 3 | PASS |
| Arbitration v0.5.1A | `test_arbitration_validation.py` | 6 | PASS |
| **TOTAL** | **17+ files** | **142** | **142 PASS** |

---

## 9. Maturity by Dimension

No single percentage. No fake maturity scores.

| Dimension | Maturity | Evidence |
|-----------|----------|----------|
| **Governed cognitive runtime** | HIGH | 24 engines, 142 tests, full pipeline validated |
| **Autonomous SDLC execution** | MEDIUM-HIGH | Pipeline works; mutation limited to Python |
| **Enterprise operations** | MEDIUM-HIGH | SSE, interventions, memory lifecycle, explainability |
| **Production readiness** | LOW | No CI/CD, no HA, no TLS, no rate limiting, default credentials |
| **Multi-model governance** | MEDIUM | Router + registry work; only Ollama live-tested |
| **Frontend completeness** | MEDIUM-HIGH | 30 rooms; 2 thin wrappers; some mock data |
| **Security** | LOW-MEDIUM | JWT+RBAC works; no rate limiting, no headers, no WAF |
| **Observability** | MEDIUM-HIGH | SSE, Prometheus config, structured logging, evidence bundles |
| **Test coverage** | HIGH | 142/142 PASS, E2E pipeline tested |
| **Documentation** | MEDIUM | Was outdated; reconciled in v0.5.1; needs drift monitoring |

---

## 10. Honest Risk Statement

### What would break first in production:
1. **No rate limiting** → API flooding under load
2. **No TLS** → All traffic plaintext without reverse proxy
3. **Default Docker credentials** → Immediate compromise if exposed
4. **No CI/CD** → Every deploy is manual, error-prone
5. **No HA** → Single point of failure on one container host
6. **Event Bus in-memory only** → All SSE state lost on restart
7. **No connection pooling** → DB connection exhaustion under concurrent load

### What is genuinely solid:
1. **Governance pipeline** → 142 tests, replay integrity, evidence capture
2. **JWT + RBAC** → Properly implemented, well-tested
3. **Drift detection** → 6 dimensions, real Ollama variability tested
4. **Semantic coverage** → Deterministic but functional
5. **Frontend architecture** → 30 rooms, TypeScript-clean, Next.js 14

### What is overstated if claimed "production ready":
Everything. This is a development-validated research-grade runtime. Not production-hardened.

---

*This document must be updated whenever runtime capabilities change. No aspirational claims. Only evidence-grounded truth. Last audit: v0.5.1B.*
