# Replay Operational Status

**Date:** 2026-05-15

## Summary

The replay runtime has been redesigned from async to synchronous architecture to resolve greenlet conflicts. The new sync runtime is architecturally sound but has a known FK violation bug.

## Architecture

```
FastAPI Route (async)
→ loop.run_in_executor(_replay_executor, run_sync_replay, ...)
→ ReplayRuntimeSync.execute()
→ SyncSessionLocal (psycopg2 sync engine)
→ ReplayTransactionManager (phase-based transaction control)
→ 6 phases: reconstruct → validate → replay → persist → verify → finalize
```

## Components

### ReplayRuntimeSync (engines/replay_runtime_sync.py)
- **Status:** partially_operational
- **Lines:** ~494
- **Responsibilities:** Session lifecycle, phase execution, replay orchestration
- **Known Bug:** FK violation — `session.flush()` in reconstruct phase bypasses txn manager

### ReplayTransactionManager (engines/replay_transaction_manager.py)
- **Status:** operational
- **Lines:** ~170
- **Responsibilities:** Phase transitions, flush/commit control, checkpointing

### SyncDatabase (core/sync_database.py)
- **Status:** operational
- **Lines:** ~45
- **Responsibilities:** Dedicated sync SQLAlchemy engine with psycopg2

### ReplayContext
- **Status:** operational
- **Responsibilities:** Immutable replay state tracking

### run_sync_replay()
- **Status:** operational
- **Responsibilities:** Thread pool entry point

## Test Results

### Test 1: Replay endpoint call
```
POST /api/v1/pipeline/runs/0117b69b-3898-4ea4-83b0-8dc793c24d02/replay?replay_mode=full
```
**Result:** FK violation error
**Cause:** replay_events inserted before replay_session exists
**Fix Applied:** Create replay_session FIRST, flush, then insert events
**Status:** Fix applied but not yet re-tested (API needs restart)

### Test 2: Integrity endpoint
```
GET /api/v1/pipeline/runs/0117b69b-3898-4ea4-83b0-8dc793c24d02/integrity
```
**Result:** Score 0.3333 (expected for legacy run without hashes)
**Status:** operational

## Stale Components

| Component | File | Reason |
|-----------|------|--------|
| ReplayEngine | engines/replay_engine.py | Superseded by sync version |
| ReplayRuntime (async) | engines/replay_runtime.py | Superseded by sync version |

These should be archived or removed to avoid confusion.

## Replay Determinism

**Status:** Deterministic by design
- Events ordered by created_at
- Artifacts ordered by created_at
- Snapshots ordered by created_at
- Chain hash computed sequentially
- No async concurrency
- Single-threaded execution per replay

## Replay Idempotency

**Status:** NOT implemented
- Running replay twice creates duplicate ReplayEvent records
- Each replay gets a new ReplaySession ID
- No deduplication logic

## Replay Concurrency

**Status:** NOT implemented
- No locking on source run
- Two simultaneous replays will create conflicting data
- ThreadPoolExecutor has max_workers=2

## Replay Hash Verification

**Status:** Implemented
- Event hashes recomputed during replay
- Chain hashes recomputed
- Divergence detection compares stored vs recomputed hashes
- Artifact hashes recomputed
- Governance hashes recomputed
- Traceability hashes recomputed

## Database Tables

| Table | Status | Notes |
|-------|--------|-------|
| replay_sessions | operational | |
| replay_events | operational | |
| replay_manifests | operational | |
| replay_telemetry | operational | |
| integrity_verifications | operational | |
| divergence_records | operational | |
| execution_baselines | operational | |
| semantic_graph_nodes | operational | |
| semantic_graph_edges | operational | |

## Next Steps

1. Fix FK violation (replay_session must be flushed before events are inserted)
2. Restart API and re-test replay endpoint
3. Execute a new pipeline run with hash propagation
4. Replay the new run and verify integrity score >= 0.95
5. Generate FIRST_OPERATIONAL_VERTICAL_SLICE baseline package
6. Archive stale replay engines (replay_engine.py, replay_runtime.py)
