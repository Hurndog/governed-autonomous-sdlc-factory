# Integrity API Validation

**Date:** 2026-05-16  
**Run:** `6a7f7ea0-297f-435e-9bb2-899368c7d332`  
**Status:** ✅ PASS

---

## Endpoint Test Results

### POST /api/v1/pipeline/runs/{run_id}/verify-integrity

| Call | Score | Status | Checks | Passed | Failed | Duration |
|------|-------|--------|--------|--------|--------|----------|
| 1 | 1.0 | pass | 6 | 6 | 0 | 123.58ms |
| 2 | 1.0 | pass | 6 | 6 | 0 | ~100ms |
| 3 | 1.0 | pass | 6 | 6 | 0 | ~100ms |

### Component Scores

| Component | Score | Status |
|-----------|-------|--------|
| Event Chain | 1.0 | ✅ PASS |
| Snapshot | 1.0 | ✅ PASS |
| Artifact | 1.0 | ✅ PASS |
| Timeline | 1.0 | ✅ PASS |
| Traceability | 1.0 | ✅ PASS |
| Governance | 1.0 | ✅ PASS |
| **Overall** | **1.0** | ✅ **PASS** |

### Stability
- 3 consecutive calls: all returned identical results
- No greenlet errors
- No async context errors
- No missing session errors
- Response time: ~100-125ms

### Fixes Applied
1. Created `integrity_runtime_sync.py` with sync `IntegrityVerifier` using `SyncSessionLocal`
2. Patched endpoint to use `loop.run_in_executor()` instead of `AsyncSession`
3. Fixed governance hash computation to match pipeline's `{"findings": findings}` structure
4. Installed `psycopg2-binary` for sync PostgreSQL driver
