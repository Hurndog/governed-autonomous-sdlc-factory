# Engine Router Debug Report

**Date**: 2026-05-14
**Status**: RESOLVED

## Root Cause Analysis

### Problem
Engine routes (26 endpoints) were not loading during FastAPI startup. The app started without errors but engine routes were missing from `/docs` and `/openapi.json`.

### Cascade of Import Failures

1. **`get_session` → `get_db`** — `engines.py` imported non-existent `get_session`. Canonical function is `get_db`.
2. **`ArtifactType` enum missing** — Engines referenced `ArtifactType.SPECIFICATION` etc. but enum didn't exist in `models.py`.
3. **`CostEntry` → `CostEvent`** — `snapshots.py` imported `CostEntry` which doesn't exist. Model is named `CostEvent`.
4. **Phase 4 relationships in wrong class** — 9 relationships (`spec_versions`, `arch_versions`, etc.) were placed in `ToolCall` class instead of `Run` class.
5. **Project class missing relationships** — `Project` class lacked `spec_versions`, `arch_versions`, `test_plans` relationships.

## Fixes Applied

### 1. `apps/api/src/api/v1/endpoints/engines.py`
- Changed `from src.core.database import get_session` → `from src.core.database import get_db`
- Changed all `Depends(get_session)` → `Depends(get_db)` (26 occurrences)

### 2. `apps/api/src/models.py`
- Added `ArtifactType` enum with 9 values (SPECIFICATION, ARCHITECTURE, TEST_PLAN, EVIDENCE, CODE, DEPLOYMENT, GOVERNANCE, TRACEABILITY, SNAPSHOT)
- Moved 9 Phase 4 relationships from `ToolCall` class to `Run` class
- Added 3 relationships to `Project` class: `spec_versions`, `arch_versions`, `test_plans`
- Removed orphaned relationship block from `ToolCall` class

### 3. `apps/api/src/engines/snapshots.py`
- Changed `CostEntry` → `CostEvent` in import and usage
- Changed `c.total_cost` → `c.estimated_cost` to match `CostEvent` model

## Verification

### Import Check
All 7 engine modules import successfully:
- `src.api.v1.endpoints.engines` ✓
- `src.engines.specification_engine` ✓
- `src.engines.architecture_engine` ✓
- `src.engines.governance_engine` ✓
- `src.engines.test_engine` ✓
- `src.engines.traceability` ✓
- `src.engines.snapshots` ✓

### Route Count
- Total routes: 97
- Engine routes: 26
- All engine route groups present: /specifications, /architecture, /governance, /tests, /traceability, /snapshots

### Health Check
```json
{"status":"ok","version":"1.0.0","database":"connected","redis":"connected"}
```

## Route Registry

| Method | Path | Name |
|--------|------|------|
| POST | /api/v1/engines/specification/generate/{run_id} | generate_specification |
| GET | /api/v1/engines/specification/{run_id} | get_specifications |
| GET | /api/v1/engines/specification/{run_id}/latest | get_latest_specification |
| POST | /api/v1/engines/specification/{run_id}/lock/{version_id} | lock_specification |
| GET | /api/v1/engines/specification/{run_id}/diff | diff_specifications |
| POST | /api/v1/engines/architecture/generate/{run_id} | generate_architecture |
| GET | /api/v1/engines/architecture/{run_id} | get_architectures |
| GET | /api/v1/engines/architecture/{run_id}/latest | get_latest_architecture |
| POST | /api/v1/engines/architecture/{run_id}/lock/{version_id} | lock_architecture |
| POST | /api/v1/engines/architecture/{run_id}/drift-check | check_architecture_drift |
| POST | /api/v1/engines/governance/seed | seed_policies |
| GET | /api/v1/engines/governance/policies | get_policies |
| POST | /api/v1/engines/governance/evaluate/{run_id} | evaluate_governance |
| GET | /api/v1/engines/governance/evaluations/{run_id} | get_evaluations |
| POST | /api/v1/engines/governance/release-gates/{run_id} | create_release_gate |
| POST | /api/v1/engines/governance/release-gates/{run_id}/evaluate/{gate_id} | evaluate_release_gate |
| POST | /api/v1/engines/governance/release-gates/{run_id}/waive/{gate_id} | waive_release_gate |
| POST | /api/v1/engines/test-plan/generate/{run_id} | generate_test_plan |
| GET | /api/v1/engines/test-plan/{run_id} | get_test_plans |
| GET | /api/v1/engines/test-plan/{run_id}/latest | get_latest_test_plan |
| GET | /api/v1/engines/traceability/{run_id} | get_traceability |
| POST | /api/v1/engines/traceability/{run_id}/link | create_traceability_link |
| GET | /api/v1/engines/traceability/{run_id}/coverage | get_traceability_coverage |
| POST | /api/v1/engines/snapshots/{run_id} | create_snapshot |
| GET | /api/v1/engines/snapshots/{run_id} | get_snapshots |
| GET | /api/v1/engines/snapshots/{run_id}/export/{snapshot_id} | export_snapshot |
