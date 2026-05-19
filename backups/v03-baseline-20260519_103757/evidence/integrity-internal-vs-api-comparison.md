# Integrity Internal vs API Comparison

**Date:** 2026-05-16  
**Run:** `6a7f7ea0-297f-435e-9bb2-899368c7d332`  
**Status:** ✅ MATCH

---

## Internal Validation (Direct DB Queries)

| Component | Score | Status |
|-----------|-------|--------|
| Event Chain | 1.0 | ✅ PASS |
| Snapshot | 1.0 | ✅ PASS |
| Artifact | 1.0 | ✅ PASS |
| Timeline | 1.0 | ✅ PASS |
| Traceability | 1.0 | ✅ PASS |
| Governance | 1.0 | ✅ PASS |
| **Overall** | **1.0** | ✅ **PASS** |

## API Validation (POST /api/v1/pipeline/runs/{run_id}/verify-integrity)

| Component | Score | Status |
|-----------|-------|--------|
| Event Chain | 1.0 | ✅ PASS |
| Snapshot | 1.0 | ✅ PASS |
| Artifact | 1.0 | ✅ PASS |
| Timeline | 1.0 | ✅ PASS |
| Traceability | 1.0 | ✅ PASS |
| Governance | 1.0 | ✅ PASS |
| **Overall** | **1.0** | ✅ **PASS** |

## Comparison

| Metric | Internal | API | Match |
|--------|----------|-----|-------|
| Overall Score | 1.0 | 1.0 | ✅ |
| Event Chain | 1.0 | 1.0 | ✅ |
| Snapshot | 1.0 | 1.0 | ✅ |
| Artifact | 1.0 | 1.0 | ✅ |
| Timeline | 1.0 | 1.0 | ✅ |
| Traceability | 1.0 | 1.0 | ✅ |
| Governance | 1.0 | 1.0 | ✅ |

## Conclusion

Internal validation and API endpoint produce identical results. The sync integrity runtime correctly replicates the verification logic using synchronous database sessions, avoiding the async/greenlet conflicts that affected the previous implementation.
