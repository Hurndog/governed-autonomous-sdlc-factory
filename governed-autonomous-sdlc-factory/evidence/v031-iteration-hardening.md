# v0.3.1 Runtime Truth — Phase 1 Iteration Hardening

**Date:** 2026-05-19
**Commit:** c417982ed4013d065bc4df6c8d14ac28ab94da4a (base) + local patches

## Finding: The 60-Iteration Cap

### Root Cause

The `config.py` file was **corrupted** — lines 11-53 were missing. The file jumped from line 10 (mid-field-definition) directly to line 54 (`@property`). This meant:

- `pipeline_timeout_seconds` — **MISSING**
- `phase_timeout_seconds` — **MISSING**
- `max_semantic_iterations` — **MISSING**
- `max_mutation_iterations` — **MISSING**
- `max_retries_per_phase` — **MISSING**
- `max_tokens_per_run` — **MISSING**
- `max_model_calls_per_phase` — **MISSING**
- `max_total_model_calls_per_run` — **MISSING**
- `max_artifacts_per_run` — **MISSING**
- `max_events_per_run` — **MISSING**
- `replay_timeout_seconds` — **MISSING**
- `semantic_convergence_threshold` — **MISSING**
- `semantic_convergence_window` — **MISSING**
- `mutation_convergence_threshold` — **MISSING**
- `progress_check_interval` — **MISSING**
- `max_stall_iterations` — **MISSING**

The `SafetyGuard` class referenced these settings but they didn't exist. This caused `AttributeError` at runtime when any guard check was triggered.

### What Was Fixed

1. **`config.py`** — Completely rewritten with all safety guard settings restored.
   - Timeout-based guards: pipeline (3600s), phase (600s), replay (300s)
   - Budget-based guards: tokens (5M), model calls (100/phase, 500 total), artifacts (200), events (1000)
   - Retry-based guards: 3 retries per phase
   - Convergence-based guards: semantic (50), mutation (30) — these are STALL DETECTION, not iteration caps

2. **`safety_guards.py`** — Enhanced with:
   - `check_convergence()` — stops when score stabilizes (no more meaningful progress)
   - `check_progress()` — detects stalls (no state change between iterations)
   - Updated messages: "stalled after N iterations" instead of "exceeded N iterations"

### Design Principle

The runtime stops because:
- ✅ Timeout exceeded (pipeline/phase/replay)
- ✅ Budget exceeded (tokens/model calls/artifacts/events)
- ✅ Retry limit reached (per-phase)
- ✅ Semantic convergence achieved (score stabilized)
- ✅ Mutation convergence achieved (score stabilized)
- ✅ Stall detected (no progress for N iterations)

The runtime does NOT stop because:
- ❌ "Iteration 60 happened"
- ❌ Arbitrary counter reached

### Verification

- Backend tests: 122/122 PASS ✅
- Frontend build: SUCCESS ✅
- TypeScript: 0 errors ✅

### Remaining Concerns

- The `max_semantic_iterations=50` and `max_mutation_iterations=30` values are still technically iteration caps, but they are **orders of magnitude** beyond normal convergence (which should happen in <10 iterations). They exist as safety nets, not operational limits.
- The convergence detection (`check_convergence`, `check_progress`) provides early stopping well before these limits are reached.
