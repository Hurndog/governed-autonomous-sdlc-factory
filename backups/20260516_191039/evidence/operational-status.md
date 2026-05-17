# Operational Status Report

**Date:** 2026-05-16T15:48:00+00:00
**Baseline:** v0.1.0-golden-integrity-runtime
**Status:** ✅ OPERATIONAL

---

## System Health

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI | ✅ Running | Port 8000, health ok, 114 routes |
| PostgreSQL | ✅ Connected | Port 5432, all tables populated |
| Redis | ✅ Connected | Port 6379 |
| Ollama | ✅ Running | 3 models loaded |
| LM Studio | ✅ Running | 2 models loaded |

## Integrity System

| Component | Score | Status |
|-----------|-------|--------|
| Event Chain | 1.0 | ✅ 239 events, 0 broken links |
| Snapshot | 1.0 | ✅ 1 snapshot verified |
| Artifact | 1.0 | ✅ 12/12 hash-verified |
| Timeline | 1.0 | ✅ 0 ordering violations |
| Traceability | 1.0 | ✅ 215 links verified |
| Governance | 1.0 | ✅ 10 evaluations verified |
| **Overall** | **1.0** | ✅ **PASS** |

## API Endpoints

| Endpoint | Method | Status |
|----------|--------|--------|
| `/health` | GET | ✅ Returns ok |
| `/api/v1/pipeline/runs/{id}/verify-integrity` | POST | ✅ Returns integrity 1.0 |
| `/api/v1/pipeline/runs/{id}/replay` | POST | ⚠️ Returns null fields |

## Test Suite

- **File:** `test_artifact_hash_integrity.py`
- **Total:** 44 tests
- **Passing:** 44
- **Failing:** 0
- **Coverage:** Metadata sanitization, hashing contracts, extraction, traceability, governance, sync runtime

## Backup

- **Latest:** `backups/20260516_154820/`
- **Size:** 5.7MB
- **Files:** 22
- **Contains:** git bundle, database dump, evidence, manifests, config, checksums

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| GitHub PAT invalid | 🔴 | Blocked — needs new token |
| Replay endpoint returns nulls | 🟡 | Known — not critical |
| No OpenAI/Anthropic keys | 🟡 | Remote LLM unavailable |

## Git Status

- **Branch:** main
- **HEAD:** f6dd264
- **Tag:** v0.1.0-golden-integrity-runtime
- **Working tree:** Clean
- **Unpushed:** 3 commits + 1 tag (GitHub blocked)
