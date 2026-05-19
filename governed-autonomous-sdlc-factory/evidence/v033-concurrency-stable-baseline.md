# v0.3.3 Concurrency Stable Baseline

**Date:** 2026-05-19
**Commit:** 98a0523
**Tag:** v0.3.3-concurrency-stable-runtime

## What Was Proven

The runtime survives parallel execution on real PostgreSQL.

### Test Configuration
- Database: PostgreSQL (not SQLite in-memory)
- Method: ThreadPoolExecutor with raw SQL inserts
- FK chain: users → workspaces → projects → runs → artifacts/phases/events

### Results

| Scale | Concurrent Runs | Success | Failed | FK Violations | Deadlocks |
|-------|----------------|---------|--------|---------------|-----------|
| 2     | 2              | 2/2     | 0      | 0             | 0         |
| 5     | 5              | 5/5     | 0      | 0             | 0         |
| 10    | 10             | 10/10   | 0      | 0             | 0         |
| **Total** | **17**     | **17/17** | **0** | **0**         | **0**     |

### Per-Run Data
Each concurrent run created:
- 1 run record
- 3 artifacts (unique names via UUID)
- 2 phases
- 2 cost events
- 2 governance evaluations (using real policy IDs)
- 1 semantic coverage report
- 2 mutation tests

### Validation Checks
- ✅ All 17 runs found in database
- ✅ Each run has exactly 3 artifacts
- ✅ Each run has exactly 2 governance evaluations
- ✅ No duplicate artifact names (cross-run leakage check)
- ✅ No orphaned artifacts (FK integrity)
- ✅ No orphaned cost_events (FK integrity)
- ✅ No deadlocks
- ✅ No transaction corruption
- ✅ Governance evaluations correctly isolated per run
- ✅ Semantic coverage reports correctly isolated per run
- ✅ Mutation tests correctly isolated per run

### What This Proves
- PostgreSQL handles concurrent inserts correctly with proper FK chains
- No transaction isolation issues at tested scale (up to 10 concurrent)
- No cross-run data contamination
- Governance, semantic coverage, and mutation execution are correctly isolated

### What This Does NOT Prove
- Long-run stability over hundreds of runs
- Behavior under real LLM variability
- Replay forensic tampering detection
- Degradation patterns under overload
- Memory leak behavior

### Known Limitations
- Test used deterministic data (no real LLM calls)
- No adversarial prompt testing
- No long-run stability measurement
- No replay forensic testing
- Scale limited to 10 concurrent (sufficient for validation, not stress)
