# Phase B — Persistence Failure Reproduction Report

**Date**: 2026-05-17
**Run ID**: `6a7f7ea0-297f-435e-9bb2-899368c7d332`

---

## Failure 1: `compute_semantic_coverage_score` — merge creates duplicate

**Test**: Call `compute_semantic_coverage_score(RUN_ID)` twice without `_clear_existing`.

**Error**:
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
  "semantic_coverage_reports_run_id_key"
DETAIL: Key (run_id)=(6a7f7ea0-297f-435e-9bb2-899368c7d332) already exists.
```

**SQL emitted**: INSERT (not UPDATE) — because `self.db.merge(report)` creates a new UUID each time, SQLAlchemy treats it as transient and issues INSERT.

**Root cause**: Line 677 in `semantic_coverage_engine.py`:
```python
self.db.merge(report)  # report has new UUID → always INSERT
```

The `SemanticCoverageReport.run_id` has `unique=True`, so the second INSERT violates the constraint.

**Impact**: Any re-run of `compute_semantic_coverage_score` without prior `_clear_existing` crashes.

---

## Failure 2: `validate_acceptance_criteria` — add_all creates duplicate

**Test**: Call `validate_acceptance_criteria(RUN_ID)` twice without `_clear_existing`.

**Error**:
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
  "acceptance_criteria_contracts_run_id_acceptance_criterion_i_key"
DETAIL: Key (run_id, acceptance_criterion_id)=(6a7f7ea0-..., AC-001) already exists.
```

**SQL emitted**: INSERT (not UPDATE) — because `self.db.add_all(records)` always creates new objects with new UUIDs.

**Root cause**: Line 207 in `semantic_coverage_engine.py`:
```python
self.db.add_all(records)  # always new objects → always INSERT
```

**Impact**: Any re-run of `validate_acceptance_criteria` without prior `_clear_existing` crashes.

---

## Same pattern affects ALL methods except `normalize_requirements`

| Method | Line | Table | Pattern | Re-run safe? |
|---|---|---|---|---|
| `normalize_requirements` | 147-153 | `requirement_normalizations` | Query-first + conditional add | ✅ Yes |
| `validate_acceptance_criteria` | 207 | `acceptance_criteria_contracts` | `add_all` | ❌ No |
| `generate_test_obligations` | 288 | `test_obligations` | `add_all` | ❌ No |
| `evaluate_test_alignment` | 372 | `semantic_alignment_evaluations` | `add_all` | ❌ No |
| `run_independent_verifier` | 426 | `verifier_critiques` | `add_all` | ❌ No |
| `plan_mutation_tests` | 466 | `mutation_tests` | `add_all` | ❌ No |
| `evaluate_negative_test_coverage` | 528 | `negative_test_requirements` | `add_all` | ❌ No |
| `bind_runtime_evidence` | 560 | `runtime_evidence_bindings` | `add_all` | ❌ No |
| `compute_semantic_coverage_score` | 677 | `semantic_coverage_reports` | `merge` (new UUID) | ❌ No |

---

## Current workaround (accidental)

The `run_full_semantic_coverage` method calls `_clear_existing(run_id)` first, which does raw SQL DELETE for all tables. This makes the re-run work because the data is gone. But:

1. `_clear_existing` doesn't call `session.expire_all()` after commit — stale identity map
2. Individual methods are NOT safe to call twice
3. The `merge` on the report is fundamentally broken for re-runs

---

## Test suite passes because:

1. Test fixture `cleanup_semantic_coverage` runs before each test (raw SQL DELETE)
2. Tests don't call individual methods twice without cleanup
3. `test_full_pipeline_idempotent` calls `run_full_semantic_coverage` twice, which works because `_clear_existing` runs first

---

## Required fixes:

1. **Phase C**: Fix test fixture to properly invalidate session after raw SQL cleanup
2. **Phase D**: Replace ALL `add_all` with deterministic upsert (query-first pattern)
3. **Phase D**: Replace `merge` on report with deterministic upsert
4. **Phase E**: Verify unique constraints exist (they do — confirmed by error messages)
