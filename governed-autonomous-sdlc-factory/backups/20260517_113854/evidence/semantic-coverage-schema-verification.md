# Semantic Coverage Schema Verification

**Date:** 2026-05-16
**Phase:** C — Schema and Model Verification

## Database Connection
- URL: `postgresql://governance:forge@localhost:5432/sdlc_factory`
- Total tables: 67

## Required Tables — All Present ✅

| Table | Status | run_id type |
|---|---|---|
| `requirement_normalizations` | ✅ | UUID |
| `acceptance_criteria_contracts` | ✅ | UUID |
| `test_obligations` | ✅ | UUID |
| `semantic_alignment_evaluations` | ✅ | UUID |
| `verifier_critiques` | ✅ | UUID |
| `mutation_tests` | ✅ | UUID |
| `negative_test_requirements` | ✅ | UUID |
| `runtime_evidence_bindings` | ✅ | UUID |
| `semantic_coverage_reports` | ✅ | UUID |
| `semantic_coverage_waivers` | ✅ | UUID |

## integrity_verifications — Semantic Columns ✅

| Column | Type | Default/Value |
|---|---|---|
| `semantic_coverage_score` | real | NULL |
| `semantic_coverage_status` | character varying | `pre_semantic_coverage` |

## SQLAlchemy Models — Import Check ✅

All 10 models import successfully with correct UUID run_id types.

## Insert/Read Test ✅

- Sync session insert into `requirement_normalizations`: OK
- Sync session read back: OK
- Cleanup (delete): OK

## Type Consistency Decision

**Decision**: Keep `run_id` as `UUID(as_uuid=True)` in SQLAlchemy models to match the actual database column type. The `Run.id` column is `String(36)` but the semantic coverage tables use `UUID` — this is intentional since semantic coverage tables are separate from the pipeline runs table and use native UUID type.

**Endpoint fix**: All endpoint filter comparisons use `UUID(run_id)` cast to convert the string path parameter to UUID for database queries.

## Status: COMPLETE ✅
