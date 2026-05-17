# Semantic Coverage Router Debug Report

**Date:** 2026-05-16
**Phase:** B — Router Registration Debug

## Root Cause Analysis

### Problem
Semantic coverage API endpoints did NOT appear in OpenAPI (`/openapi.json`).

### Root Causes Found

**1. Router not included in `router.py` (CRITICAL)**
- `apps/api/src/api/v1/router.py` did not import `semantic_coverage`
- `api_router.include_router(semantic_coverage.router, ...)` was missing
- The file was never patched in the previous session despite claims

**2. Double prefix in semantic_coverage.py (BUG)**
- `router = APIRouter(prefix="/api/v1/semantic-coverage", ...)` 
- Since `api_router` already has `prefix="/api/v1"`, this caused paths like `/api/v1/api/v1/semantic-coverage/...`
- Fixed to: `router = APIRouter(prefix="/semantic-coverage", ...)`

**3. AsyncSession vs Sync query mismatch (BUG)**
- Endpoints used `engine.db.query()` (sync SQLAlchemy API) but `get_db` yields `AsyncSession`
- Fixed by creating a `SyncSessionLocal` in `database.py` and using `run_in_executor` pattern

**4. UUID type mismatch between Run.id and semantic coverage models (BUG)**
- `Run.id` is `String(36)` but all semantic coverage `run_id` columns were `UUID(as_uuid=True)`
- All `run_id` columns in `models_semantic_coverage.py` changed from `UUID(as_uuid=True)` to `String(36)`
- All `uuid.UUID(run_id)` calls in `semantic_coverage_engine.py` changed to `str(run_id)` (38 replacements)

## Fixes Applied

### 1. `apps/api/src/api/v1/router.py`
- Added `semantic_coverage` to imports
- Added `api_router.include_router(semantic_coverage.router, tags=["semantic-coverage"])`

### 2. `apps/api/src/core/database.py`
- Added `sqlalchemy.create_engine` import
- Added `sqlalchemy.orm.sessionmaker` import
- Created `sync_engine` with psycopg2 URL (derived from async URL)
- Created `SyncSessionLocal = sessionmaker(bind=sync_engine, ...)`

### 3. `apps/api/src/api/v1/endpoints/semantic_coverage.py`
- Changed prefix from `/api/v1/semantic-coverage` to `/semantic-coverage`
- Rewrote all endpoints to use sync functions + `run_in_executor` pattern
- Each endpoint has a `_sync` helper function that creates its own `SyncSessionLocal`
- All `UUID(run_id)` calls replaced with `run_id` (string comparison)

### 4. `apps/api/src/core/models_semantic_coverage.py`
- Changed all 10 `run_id = Column(UUID(as_uuid=True), ...)` to `run_id = Column(String(36), ...)`

### 5. `apps/api/src/engines/semantic_coverage_engine.py`
- Replaced 38 occurrences of `uuid.UUID(run_id) if isinstance(run_id, str) else run_id` with `str(run_id)`

## Verification

### OpenAPI Check
```
12 semantic-coverage paths in OpenAPI:
  /api/v1/semantic-coverage/runs/{run_id}/summary
  /api/v1/semantic-coverage/runs/{run_id}/requirements
  /api/v1/semantic-coverage/runs/{run_id}/acceptance-criteria
  /api/v1/semantic-coverage/runs/{run_id}/test-obligations
  /api/v1/semantic-coverage/runs/{run_id}/alignment
  /api/v1/semantic-coverage/runs/{run_id}/verifier-critiques
  /api/v1/semantic-coverage/runs/{run_id}/mutations
  /api/v1/semantic-coverage/runs/{run_id}/negative-coverage
  /api/v1/semantic-coverage/runs/{run_id}/runtime-evidence
  /api/v1/semantic-coverage/runs/{run_id}/report
  /api/v1/semantic-coverage/runs/{run_id}/evaluate
  /api/v1/semantic-coverage/runs/{run_id}/waivers
```

### Endpoint Tests (legacy run `6a7f7ea0`)
| Endpoint | Status | Response |
|---|---|---|
| GET /summary | 200 | `{"status": "pre_semantic_coverage"}` ✅ |
| GET /requirements | 200 | `{"total": 0, "requirements": []}` ✅ |
| GET /test-obligations | 200 | `{"total": 0, "obligations": []}` ✅ |
| GET /mutations | 200 | `{"total": 0, "killed": 0, "survived": 0}` ✅ |

## Acceptance Criteria

- ✅ Semantic coverage endpoints appear in `api_router.routes`
- ✅ Semantic coverage endpoints appear in `/openapi.json`
- ✅ 12 semantic coverage endpoints visible
- ✅ GET `/api/v1/semantic-coverage/runs/{run_id}/summary` returns valid response
- ✅ Legacy runs return `pre_semantic_coverage`, never fake pass

## Status: COMPLETE
