# Phase 1 — Operational Safety Guard Implementation Report

**Date**: 2020-05-17

## Files Changed

| File | Change |
|---|---|
| `apps/api/src/core/config.py` | Added 13 safety guard configuration settings with safe defaults |
| `apps/api/src/core/safety_guards.py` | New module: SafetyGuard class, GuardActivation model, GuardStatus enum, GuardActivationError |
| `apps/api/src/services/run_orchestrator.py` | Integrated safety guards: pipeline timeout, phase timeout, GuardActivationError handling |
| `apps/api/src/core/migrations/phase_13_guard_activations.sql` | New table: guard_activations with indexes |

## Guards Implemented

| Guard | Default | Description |
|---|---|---|
| `pipeline_timeout` | 900s | Hard limit on total pipeline duration |
| `phase_timeout` | 180s | Per-phase execution limit |
| `retry_limit` | 3 | Max retries per phase |
| `model_call_budget_per_phase` | 5 | Max model calls per phase |
| `model_call_budget_total` | 50 | Max total model calls per run |
| `token_budget` | 250,000 | Max tokens per run |
| `artifact_budget` | 500 | Max artifacts per run |
| `event_budget` | 10,000 | Max events per run |
| `semantic_iteration_limit` | 5 | Max semantic refinement iterations |
| `mutation_iteration_limit` | 5 | Max mutation test iterations |

## Persistence Behavior

Every guard activation:
1. Logs a WARNING message
2. Creates a `GuardActivation` record in the database with: run_id, phase_name, guard_name, configured_limit, observed_value, resulting_status, message, is_recoverable
3. Sets the run status to FAILED
4. Publishes a failure event

## Status Values

- `stopped_by_pipeline_timeout`
- `stopped_by_phase_timeout`
- `stopped_by_retry_limit`
- `stopped_by_model_call_budget`
- `stopped_by_token_budget`
- `stopped_by_artifact_budget`
- `stopped_by_event_budget`
- `stopped_by_semantic_iteration_limit`
- `stopped_by_mutation_iteration_limit`
- `stopped_by_replay_timeout`
- `stopped_by_background_task_lease_expiry`
- `stopped_by_policy`

## Remaining Risks

- Guards are configured but not yet tested with real model inference (tests use simulated values)
- The `background_task_lease_seconds` and `websocket_max_reconnect_attempts` configs exist but are not yet enforced in code (future work)
- Token counting depends on model provider integration
