# Integrity API Greenlet Diagnosis

**Date:** 2026-05-16  
**Status:** DIAGNOSED

---

## Problem

The `/api/v1/pipeline/runs/{run_id}/verify-integrity` endpoint returns:
```
{"error": "Internal server error", "detail": "greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?"}
```

## Root Cause

The endpoint uses FastAPI's async dependency injection to provide an `AsyncSession`:
```python
@router.post("/runs/{run_id}/verify-integrity")
async def verify_run_integrity(
    run_id: str,
    db: AsyncSession = Depends(get_db_no_autoflush),
    user=Depends(get_current_user),
):
    integrity_mgr = IntegrityManager(run_id)
    report = await integrity_mgr.verify_all(db)
    return {...}
```

The `IntegrityManager.verify_all(db)` method receives the `AsyncSession` and performs multiple queries. The greenlet error occurs because the session is being used in a context where the async event loop and SQLAlchemy's async driver (asyncpg) have a greenlet conflict.

## Why Replay Works

The replay endpoint uses a completely different pattern:
```python
# FastAPI route (async) → thread pool → sync execution
loop = asyncio.get_running_loop()
ctx = await loop.run_in_executor(
    _replay_executor,
    run_sync_replay,  # Pure sync function
    run_id, replay_mode, from_timestamp, phase_name,
)
```

The `run_sync_replay` function creates its own `SyncSessionLocal` (using psycopg2, not asyncpg) and owns its complete session lifecycle. No FastAPI dependency injection. No greenlet conflicts.

## Solution Pattern

Apply the same pattern to integrity verification:
1. Create a `verify_integrity_sync(run_id)` function that uses `SyncSessionLocal`
2. Extract pure verification logic from `IntegrityManager` into sync-compatible functions
3. Call the sync function via `loop.run_in_executor()` from the FastAPI route
4. Return the structured report

## Files Involved
- `apps/api/src/api/v1/endpoints/pipeline.py` — verify-integrity endpoint
- `apps/api/src/core/integrity.py` — IntegrityManager.verify_all()
- `apps/api/src/core/database.py` — AsyncSession factory
- `apps/api/src/core/sync_database.py` — SyncSessionLocal factory
- `apps/api/src/engines/replay_runtime_sync.py` — Working sync pattern to follow
