# Phase 3 — Minimal Conflict Detection Report

**Date**: 2026-05-17

## Files Changed

| File | Change |
|---|---|
| `apps/api/src/core/conflict_detection.py` | New module: ConflictDetector class, RequirementConflict model, 4 conflict patterns |
| `apps/api/src/core/migrations/phase_14_requirement_conflicts.sql` | New table: requirement_conflicts with indexes |
| `apps/api/tests/test_semantic_coverage.py` | Added 6 conflict detection tests |

## Implemented Conflict Types

| # | Type | Severity | Example | Gate Impact |
|---|---|---|---|---|
| 1 | `immutability_vs_editability` | critical | "All records must be immutable" vs "Admins can edit records" | fail |
| 2 | `retention_vs_deletion` | critical | "Retain for 7 years" vs "Users can permanently delete" | fail |
| 3 | `auditability_vs_no_logging` | high | "Must be auditable" vs "Must not store logs" | fail |
| 4 | `tenant_isolation_vs_cross_tenant_access` | critical | "Only own tenant" vs "Access all tenants without approval" | fail |

## Test Results

| Test | Result |
|---|---|
| `test_conflict_detection_immutability_vs_editability` | ✅ PASS |
| `test_conflict_detection_retention_vs_deletion` | ✅ PASS |
| `test_conflict_detection_auditability_vs_no_logging` | ✅ PASS |
| `test_conflict_detection_tenant_isolation_vs_cross_tenant` | ✅ PASS |
| `test_conflict_detection_no_false_positives` | ✅ PASS |
| `test_conflict_severity_and_gate_impact` | ✅ PASS |

## Persistence

Each conflict finding includes:
- run_id, requirement_id_1, requirement_id_2
- conflict_type, severity, explanation
- recommended_resolution, release_gate_impact
- detected_at timestamp

## Known Limitations

- Keyword-based detection (not semantic) — may miss conflicts expressed with different vocabulary
- Only detects pairwise conflicts (not N-way conflicts)
- Does not auto-resolve conflicts
- False positive rate unknown for production data
- Does not detect subtle logical contradictions

## Next Improvement Path

1. Add semantic similarity for conflict detection
2. Add N-way conflict detection
3. Integrate with release gate evaluation
4. Add conflict waiver workflow
