# SESSION RECOVERY MANIFEST

**Last Updated:** 2026-05-16T10:15:00Z  
**Session:** Integrity Repair Validation  
**Status:** ✅ COMPLETE

---

## Current State

### Services
| Service | Status | Port | PID |
|---------|--------|------|-----|
| API (FastAPI) | ✅ Running | 8000 | 77294 |
| Frontend (Next.js) | ✅ Running | 3000 | - |
| PostgreSQL | ✅ Running | 5432 | - |
| Redis | ✅ Running | 6379 | - |

### Model Router
- **Primary:** `google/gemma-4-e4b` (LM Studio, `http://localhost:1234/v1`)
- **Fallback:** `gpt-oss:20b` (Ollama)

---

## Integrity Repair — COMPLETE

### Root Cause
Artifact hash mismatch caused by volatile derived fields (`artifact_hash`, `content_hash`, `size_bytes`) being stored in `metadata_`, making hash recomputation impossible.

### Fix Applied
1. `apps/api/src/services/artifact_store.py` — Added `sanitize_artifact_metadata()`, removed volatile fields from `metadata_`
2. `apps/api/src/core/hashing.py` — Added `_filter_metadata_for_hash()`, `compute_artifact_hash()`, `extract_structured_output()`
3. `apps/api/src/engines/model_providers.py` — LM Studio uses `extract_structured_output()`

### Validation
- **Golden Run:** `789c0b53-fc47-49d7-8c1c-354f7a7395f3`
- **Artifact Integrity:** 1.0 (12/12 verified)
- **Overall Integrity:** 0.67 (traceability/governance not populated by design)
- **Tests:** 30/30 passed

### Legacy Runs (marked in DB)
- `d6da6253`, `03a6ba18`, `e384da5b`, `f3069377`, `64b223fd` — all marked as `legacy_hash_contract`

---

## Key Files
- `apps/api/src/services/artifact_store.py` — Artifact persistence with metadata sanitization
- `apps/api/src/core/hashing.py` — Canonical hashing + structured output normalization
- `apps/api/src/core/integrity.py` — Integrity verification engine
- `apps/api/tests/test_artifact_hash_integrity.py` — 30 tests

## Evidence Reports
- `evidence/artifact-integrity-root-cause.md`
- `evidence/artifact-hash-contract.md`
- `evidence/artifact-integrity-validation.md`
- `evidence/structured-output-normalization.md`
- `evidence/legacy-hash-contract-runs.md`
- `evidence/artifact-hash-test-results.md`
- `evidence/integrity-repair-validation.md`

---

## Database
- **Connection:** `postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory`
- **Key tables:** runs, artifacts, log_events, run_snapshots, integrity_verifications

## Pending
- GitHub push blocked (invalid token)
- Traceability links not populated by pipeline (separate issue)
- Governance evaluations not populated by pipeline (separate issue)
