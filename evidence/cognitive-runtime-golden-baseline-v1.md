# Cognitive Runtime Golden Baseline v1.0

**Date:** 2026-05-16
**Tag:** v0.1.0-golden-integrity-runtime
**Status:** ✅ SEALED

---

## 1. Repository

| Field | Value |
|-------|-------|
| Path | `/Users/marcovanhurne/governed-autonomous-sdlc-factory` |
| Nested source | `governed-autonomous-sdlc-factory/` |
| Branch | `main` |
| HEAD | `f6dd264` |
| Working tree | Clean |

## 2. Active Services

| Service | Port | Status |
|---------|------|--------|
| FastAPI (SDLC Factory) | 8000 | ✅ Running (PID 77093) |
| PostgreSQL | 5432 | ✅ Connected (via API health) |
| Redis | 6379 | ✅ Connected (via API health) |
| Ollama | 11434 | ✅ Running (3 models) |
| LM Studio | 1234 | ✅ Running (2 models) |
| Qdrant | 6333 | Configured |

## 3. Model Providers & Routing

| Provider | Base URL | Model | Role |
|----------|----------|-------|------|
| LM Studio | http://localhost:1234/v1 | local-model | Primary |
| Ollama | http://localhost:11434 | — | Secondary |
| Anthropic | — | — | Configured via env |
| OpenAI | — | — | Configured via env |

## 4. Golden Run

| Field | Value |
|-------|-------|
| Run ID | `6a7f7ea0-297f-435e-9bb2-899368c7d332` |
| Events | 239 |
| Snapshots | 1 |
| Artifacts | 12 (all hash-verified) |
| Traceability Links | 215 |
| Governance Evaluations | 10 |
| Release Gates | 1 |
| Legacy Runs | 5 (marked `legacy_hash_contract`) |

## 5. Integrity API Response

```
POST /api/v1/pipeline/runs/6a7f7ea0/verify-integrity

{
  "run_id": "6a7f7ea0-297f-435e-9bb2-899368c7d332",
  "integrity_score": 1.0,
  "status": "pass",
  "checks": 6,
  "passed": 6,
  "failed": 0,
  "warnings": 0,
  "report": {
    "overall_score": 1.0,
    "results": {
      "event_chain":  { "score": 1.0, "status": "pass" },
      "snapshot":     { "score": 1.0, "status": "pass" },
      "artifact":     { "score": 1.0, "status": "pass" },
      "timeline":     { "score": 1.0, "status": "pass" },
      "traceability": { "score": 1.0, "status": "pass" },
      "governance":   { "score": 1.0, "status": "pass" }
    }
  }
}
```

Stability: ✅ 3/3 consecutive calls identical, no greenlet errors.

## 6. Replay Status

| Field | Value |
|-------|-------|
| Endpoint | `POST /api/v1/pipeline/runs/{id}/replay` |
| Status | Exists, returns null fields (not fully implemented) |
| Sync Runtime | `integrity_runtime_sync.py` — operational |

## 7. Test Results

| Suite | Tests | Status |
|-------|-------|--------|
| `test_artifact_hash_integrity.py` | 44/44 | ✅ All passing |

Test categories:
- Metadata sanitization (9 tests)
- Hashing contracts (12 tests)
- JSON/markdown extraction (7 tests)
- Traceability link creation (4 tests)
- Governance evaluation hashing (5 tests)
- Sync integrity runtime (5 tests)
- Filter/mutation tests (2 tests)

## 8. Evidence Reports

| File | Description |
|------|-------------|
| `evidence/golden-run-v3-integrity-report.md` | Final integrity validation |
| `evidence/integrity-api-greenlet-diagnosis.md` | Root cause analysis |
| `evidence/integrity-runtime-sync-design.md` | Sync runtime design |
| `evidence/integrity-api-validation.md` | API validation results |
| `evidence/integrity-api-test-results.md` | Test results |
| `evidence/integrity-internal-vs-api-comparison.md` | Internal vs API comparison |
| `evidence/operational-status.md` | Operational status |
| `evidence/current-state-report.md` | Current state |
| `evidence/github-sync-status.md` | GitHub sync status |

## 9. Database

| Field | Value |
|-------|-------|
| Engine | PostgreSQL 14+ |
| URL | `postgresql+asyncpg://governance:[REDACTED]@localhost:5432/sdlc_factory` |
| ORM | SQLAlchemy (async + sync) |
| Tables | events, snapshots, artifacts, traceability_links, governance_evaluations, release_gates, pipeline_runs, policies |

## 10. Commit Chain

```
f6dd264 Harden integrity verification API with sync runtime
6888ef9 Add traceability and governance persistence to golden pipeline
98299bb Fix artifact metadata sanitization and validate integrity repair
62635da docs: GitHub sync status — token invalid
63e3b64 feat(gemma4): Gemma 4 E4B primary model + golden pipeline + routing policy v2
6355969 feat(runtime): Full autonomous pipeline validation + model benchmarks + backup
fd462fc docs: SESSION_RECOVERY_MANIFEST — full runtime state + recovery instructions
24ef63a feat(ops): GitHub setup script + environment reports
21648a0 feat(frontend): Cognitive Command Center — 5 rooms + WebSocket + dark ops UI
8a86dc1 feat(operationalization): Ollama integration + startup diagnostics + golden baseline
```

## 11. Known Blockers

| Blocker | Status | Impact |
|---------|--------|--------|
| GitHub PAT invalid | 🔴 Blocked | Cannot push to remote |
| Pydantic v2 Config deprecated | 🟡 Fixed | `model_config` + `extra="allow"` |
| Replay endpoint returns nulls | 🟡 Known | Not critical for integrity |

## 12. Recovery Instructions

### Full Recovery from Backup
1. Restore git bundle: `git clone <bundle> restored-repo`
2. Restore database: `pg_restore -d sdlc_factory <dump>`
3. Install dependencies: `cd apps/api && pip install -r requirements.txt`
4. Start API: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
5. Verify: `curl http://localhost:8000/health`

### Integrity Verification
```bash
curl -X POST http://localhost:8000/api/v1/pipeline/runs/6a7f7ea0-297f-435e-9bb2-899368c7d332/verify-integrity
```

### Test Suite
```bash
cd governed-autonomous-sdlc-factory && python -m pytest apps/api/tests/test_artifact_hash_integrity.py -v
```

---

**Baseline sealed by:** OWL (Hermes Agent)
**Sealed at:** 2026-05-16T13:38:00+00:00
