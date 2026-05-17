# Current Runtime Baseline — Architecture Status

**Tag:** `v0.2.0-evidence-backed-runtime-pass`
**Date:** 2026-05-14
**Status:** PASS — Evidence-Backed Operational Acceptance

---

## 1. Runtime Overview

The Governed Autonomous SDLC Factory is a pipeline-driven runtime that transforms natural language software specifications into release-governed outputs through a series of orchestrated phases. Each phase is executed by AI agents operating under governance constraints, with full evidence capture and integrity verification at every step.

The system is operated through a Next.js frontend (Forge Control Tower) and driven by a FastAPI + LangGraph backend with PostgreSQL persistence.

## 2. Main Components

| Component | Technology | Role |
|---|---|---|
| Frontend Control Plane | Next.js 14, React, Tailwind, shadcn/ui | Operator interface |
| API Layer | FastAPI, Pydantic | HTTP API, WebSocket |
| Orchestration | LangGraph | Pipeline phase execution |
| Persistence | PostgreSQL, SQLAlchemy/asyncpg | Structured data, evidence |
| Vector Memory | Qdrant (configured) | Semantic search, embeddings |
| Governance | OPA Rego (configured) | Policy enforcement |
| Tool Protocol | MCP servers | Tool abstraction for agents |
| Hashing | SHA256 | Artifact/event/snapshot integrity |

## 3. Pipeline Phases

The runtime executes the following phases in sequence:

1. **Ingest** — Parse natural language specification into structured requirements
2. **Plan** — Generate implementation plan with task decomposition
3. **Implement** — Execute code generation tasks
4. **Verify** — Run tests, static analysis, semantic coverage check
5. **Evidence** — Capture all artifacts, events, and metrics
6. **Gate** — Evaluate release readiness via integrity + semantic coverage
7. **Release** — Produce release artifacts (if gate passes)

Each phase is subject to safety guards (timeouts, retry limits, budget caps).

## 4. Model Router

- Multi-provider routing with configurable failover
- Per-phase model call budget: 5 calls
- Per-run model call budget: 50 calls
- Per-run token budget: 250,000 tokens
- Semantic iteration limit: 5 iterations per requirement
- Provider capability matching for task routing

## 5. Semantic Coverage Layer

The semantic coverage engine computes how well the generated artifacts (requirements, acceptance criteria, obligations) align with the original specification.

- **Input:** Persisted requirements, acceptance criteria, obligations from database
- **Scoring:** Weighted alignment score across requirement-AC-obligation triples
- **Threshold:** 0.8 (release gate blocks below this)
- **Current score:** 0.6559 (genuine computed result from black-box run)
- **Persistence:** All scores stored in `semantic_alignment_evaluations` table
- **Idempotency:** Engine v3 uses query-first upserts to prevent duplicate scoring

## 6. Integrity Runtime

Seven-component integrity scoring:

1. **Artifact Hashing** — SHA256 for all generated artifacts
2. **Event Sourcing** — Hash-chained event log for all state changes
3. **Snapshot Integrity** — Point-in-time snapshots with hash verification
4. **Lineage Tracking** — Full provenance from specification to release
5. **Evidence Binding** — Cryptographic binding of evidence to runs
6. **Replay Verification** — Deterministic replay with side-effect safety
7. **Semantic Coverage** — Alignment scoring (see section 5)

**Current overall integrity score:** 0.9508 (6 Pass, 1 Warning)

## 7. Release Gate

The release gate evaluates whether a run is ready for release:

- Checks semantic coverage score against threshold (0.8)
- Verifies seven-component integrity
- Checks for unresolved conflicts
- Produces a binary PASS/FAIL verdict
- **No bypass mechanism exists**
- **Current behavior:** Correctly fails when coverage is insufficient (0.6559 < 0.8)

## 8. Replay

- Snapshots captured at phase boundaries
- Deterministic replay supported via stored state
- Side-effect safety through isolated replay context
- Hash verification ensures replay integrity

## 9. Evidence and Backup

- All pipeline runs produce evidence bundles
- Evidence includes: artifacts, events, metrics, scores, conflicts, guard activations
- 50+ evidence files in `evidence/` directory
- Backup procedure: git bundle + evidence + manifest + checksums
- **Backup verified:** 9MB bundle, restore tested, HEAD match confirmed

## 10. Frontend Control Plane

- **Command Center** — Run monitoring, phase status, real-time updates
- **Governance Room** — Policy management, guard configuration, conflict review
- **Architecture Room** — System topology, component health, dependency graph
- **Settings/Providers** — Model provider configuration, API keys, thresholds
- **Build status:** TypeScript strict pass, Next.js build pass (4 pages)

## 11. Safety Guards

11 guard types enforce runtime boundaries:

| Guard | Limit | Persisted |
|---|---|---|
| Pipeline timeout | 900s | ✅ |
| Phase timeout | 180s | ✅ |
| Max retries per phase | 3 | ✅ |
| Model calls per phase | 5 | ✅ |
| Model calls per run | 50 | ✅ |
| Token budget per run | 250,000 | ✅ |
| Semantic iteration limit | 5 | ✅ |
| Run state guard | Valid transitions only | ✅ |
| Evidence budget guard | Configurable | ✅ |
| Provider failover guard | Auto-retry | ✅ |
| Conflict threshold guard | Configurable | ✅ |

All guard activations persisted in `guard_activations` table as forensic evidence.

## 12. Conflict Detection

4 patterns detect requirement contradictions:

1. **Immutability vs Editability** — Immutable requirement modified
2. **Budget Over-allocation** — Resource claims exceed available budget
3. **Temporal Contradiction** — Mutually exclusive time constraints
4. **Provider Capability Mismatch** — Required capability not available from any provider

Conflicts persisted in `requirement_conflicts` table. 1 conflict detected in black-box run.

## 13. Current Limitations

1. No authentication or authorization
2. No multi-tenant isolation
3. No production deployment configuration
4. No automated database migrations
5. No PDF/audit export
6. No human-in-the-loop approval workflow
7. ESLint not configured (pre-existing)
8. Semantic coverage score below threshold (genuine, requires engine improvement)

## 14. Next Architecture Phase

**Phase 1: Security and Access Control**
- JWT or session-based authentication
- RBAC authorization
- User/project/workspace model
- Secrets management
- API protection (rate limiting, input validation)
- Audit access model

This is the prerequisite for any production deployment or multi-user operation.
