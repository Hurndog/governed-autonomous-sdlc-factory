# Phase A — Persistence Stabilization Status Report

**Date**: 2026-05-16
**Repo**: `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
**Branch**: `main`
**HEAD**: `38d8b4b`

---

## Baseline Status

| Component | Status |
|---|---|
| Previous runtime baseline | ✅ COMPLETE |
| Semantic Coverage architecture | ⚠️ Implemented but NOT operationally sealed |
| Backend imports | ✅ All 5 modules import correctly |
| Test suite | ✅ 70/70 passing (44 legacy + 26 semantic) |

## Import Verification

| Module | Status | Notes |
|---|---|---|
| `semantic_coverage_engine` | ✅ | Imports clean |
| `semantic_coverage_models` | ⚠️ | `extend_existing` warning on second import (MetaData conflict) — not a runtime blocker |
| `semantic_coverage_endpoints` | ✅ | Router registers correctly |
| `integrity_runtime` | ✅ | Class is `IntegrityVerifier` (not `IntegrityRuntime`) — no issue |
| `source_extractor` | ✅ | Imports clean |

## Identified Issues

### Issue 1: `_clear_existing` raw SQL DELETE without session invalidation (ENGINE)

**Location**: `apps/api/src/engines/semantic_coverage_engine.py:63-75`

The `_clear_existing` method uses raw SQL DELETE statements via `self.db.execute(text(...))` followed by `self.db.commit()`. After this:
- SQLAlchemy's identity map may still contain stale objects
- Subsequent queries may return cached results instead of hitting the DB
- The `merge` on line 677 may behave unpredictably

**Impact**: Potential for insert/update ambiguity on re-runs.

### Issue 2: `merge` used for SemanticCoverageReport persistence (ENGINE)

**Location**: `apps/api/src/engines/semantic_coverage_engine.py:677`

`self.db.merge(report)` is used for the final report. Since `report` is a new object with a freshly generated UUID, `merge` will always INSERT (not update), even if a report for this `run_id` already exists. The `SemanticCoverageReport` table has `unique=True` on `run_id`, so re-runs will hit a unique constraint violation.

**Impact**: Re-running `compute_semantic_coverage_score` will fail with integrity error.

### Issue 3: Multiple engine methods use `add_all` without upsert logic (ENGINE)

Only `normalize_requirements` has proper "query first, add if not exists" logic. These methods blindly `add_all`:

| Method | Line | Table | Has upsert? |
|---|---|---|---|
| `validate_acceptance_criteria` | 207 | `acceptance_criteria_contracts` | ❌ |
| `generate_test_obligations` | 288 | `test_obligations` | ❌ |
| `evaluate_test_alignment` | 372 | `semantic_alignment_evaluations` | ❌ |
| `run_independent_verifier` | 426 | `verifier_critiques` | ❌ |
| `plan_mutation_tests` | 466 | `mutation_tests` | ❌ |
| `evaluate_negative_test_coverage` | 528 | `negative_test_requirements` | ❌ |
| `bind_runtime_evidence` | 560 | `runtime_evidence_bindings` | ❌ |
| `compute_semantic_coverage_score` | 677 | `semantic_coverage_reports` | ❌ (uses merge) |

**Impact**: Without `_clear_existing` being called first, re-runs will create duplicates. With `_clear_existing`, the session stale state may cause issues.

### Issue 4: Test fixture cleanup uses raw SQL but `expire_all` may not be enough (TESTS)

**Location**: `apps/api/tests/test_semantic_coverage.py:73-93`

The `cleanup_semantic_coverage` fixture uses raw SQL DELETE + `db.expire_all()`. The `expire_all()` call should invalidate the identity map, but the fixture is `autouse=True` with default `function` scope while the `db` session is `scope="module"`. This means:
- The same session is shared across all tests
- `expire_all` marks all loaded objects as expired
- But if any test holds references to detached objects, they may cause issues

**Current status**: Tests pass (26/26), so this is not an active blocker for the test suite.

## Root Cause Summary

The core problem is **inconsistent persistence strategy**:
1. `_clear_existing` uses raw SQL (bypasses ORM identity map)
2. Most engine methods use `add_all` (no upsert, no duplicate check)
3. The report uses `merge` (fragile with new UUIDs)
4. Only `normalize_requirements` has proper upsert logic

The fix needs to:
1. Add `session.expire_all()` after `_clear_existing` commit in the engine
2. Replace `merge` with deterministic upsert for the report
3. Add upsert logic to all 7 other persistence methods
4. Ensure the test fixture properly handles session state

## Current Test Results

```
70 passed, 1 warning in 2.31s
```

All tests pass currently because:
- The test fixture cleans up before each test
- Tests don't call `run_full_semantic_coverage` twice in the same test
- The `test_full_pipeline_idempotent` test does call it twice but within the same session

## Next Steps

1. **Phase B**: Reproduce the actual failure (run pipeline twice, check for duplicates)
2. **Phase C**: Fix test fixture session invalidation
3. **Phase D**: Replace all `add_all` with deterministic upsert
4. **Phase E**: Verify unique constraints
5. **Phase F**: Rerun tests
