# Tokenomics Cost and Inference Data Audit

**Date:** 2026-05-18
**Phase:** 1 — Cost and Inference Data Audit

## Database Tables

### cost_events
| Field | Type | Notes |
|---|---|---|
| id | String(36) PK | |
| run_id | String(36) FK | → runs.id |
| phase_id | String(36) FK? | → phases.id, nullable |
| agent_id | String(36) FK? | → agents.id, nullable |
| event_type | String(50) | |
| model_name | String(255)? | nullable |
| provider | String(100)? | nullable |
| tokens_in | Integer | default 0 |
| tokens_out | Integer | default 0 |
| estimated_cost | Float | default 0.0 |
| actual_cost | Float? | nullable |
| is_local | Boolean | default True |
| latency_ms | Float? | nullable |
| created_at | DateTime | server default now |

### model_calls
| Field | Type | Notes |
|---|---|---|
| id | String(36) PK | |
| run_id | String(36) FK | → runs.id |
| phase_id | String(36) FK? | → phases.id, nullable |
| agent_id | String(36) FK? | → agents.id, nullable |
| model_name | String(255) | NOT NULL |
| provider | String(100) | NOT NULL |
| tokens_in | Integer | default 0 |
| tokens_out | Integer | default 0 |
| estimated_cost | Float | default 0.0 |
| actual_cost | Float? | nullable |
| latency_ms | Float? | nullable |
| is_success | Boolean | default True |
| retry_count | Integer | default 0 |
| trace_id | String(100)? | nullable |
| created_at | DateTime | server default now |

### phases
| Field | Type | Notes |
|---|---|---|
| id | String(36) PK | |
| run_id | String(36) FK | → runs.id |
| name | String(100) | NOT NULL — phase name |
| status | String(50) | |
| order_index | Integer | |
| agent_id | String(36) FK? | → agents.id, nullable |
| model_used | String(255)? | nullable |
| tokens_in | Integer | default 0 |
| tokens_out | Integer | default 0 |
| cost | Float | default 0.0 |
| retry_count | Integer | default 0 |
| error_message | Text? | nullable |

### agents
| Field | Type | Notes |
|---|---|---|
| id | String(36) PK | |
| name | String(255) | NOT NULL |
| role | String(100) | |
| is_active | Boolean | default True |

## Audit Answers

| # | Question | Answer |
|---|---|---|
| 1 | Input tokens stored? | ✅ Yes — `tokens_in` in cost_events, model_calls, phases |
| 2 | Output tokens stored? | ✅ Yes — `tokens_out` in cost_events, model_calls, phases |
| 3 | Total tokens stored/derivable? | ✅ Derivable: `tokens_in + tokens_out` |
| 4 | Provider stored? | ✅ Yes — `provider` in cost_events, model_calls |
| 5 | Model stored? | ✅ Yes — `model_name` in cost_events, model_calls |
| 6 | Phase stored? | ✅ Yes — `phase_id` in cost_events, model_calls; `name` in phases table |
| 7 | Engine stored? | ❌ No explicit engine field |
| 8 | source_engine stored? | ❌ No explicit source_engine field |
| 9 | Agent identity stored? | ✅ Yes — `agent_id` in cost_events, model_calls, phases → agents table |
| 10 | Agent derivable if missing? | ⚠️ Partially — phase.name can hint at agent, but not deterministic |
| 11 | Retries stored? | ✅ Yes — `retry_count` in model_calls, phases |
| 12 | Failed calls stored? | ✅ Yes — `is_success=false` in model_calls; `error_message` in phases |
| 13 | Cost stored/derivable? | ✅ Yes — `estimated_cost` and `actual_cost` in cost_events, model_calls |
| 14 | Timestamps stored? | ✅ Yes — `created_at` in all tables |
| 15 | Latency/duration stored? | ✅ Yes — `latency_ms` in cost_events, model_calls |
| 16 | Cached tokens stored? | ❌ No explicit cached_tokens field |
| 17 | Reasoning tokens stored? | ❌ No explicit reasoning_tokens field |
| 18 | Token waste categories stored? | ❌ No — must be derived from retry_count, error_message, is_success |

## Existing Cost Endpoint

`GET /costs/report/{run_id}` exists and returns:
- run_id, total_cost, budget_limit, remaining_budget, warning_threshold, is_near_limit, is_hard_limit_reached, local_cost, paid_cost, estimated_savings, by_phase, by_agent, by_model

The existing endpoint already has `by_agent` aggregation! But it uses `CostEvent.agent_id` which may be null.

## Data Quality Assessment

### What's Available
- ✅ Token totals (input + output) from cost_events and model_calls
- ✅ Cost from cost_events and model_calls
- ✅ Phase aggregation via phase_id → phases.name
- ✅ Model aggregation via model_name
- ✅ Provider aggregation via provider
- ✅ Agent aggregation via agent_id → agents.name (when agent_id is not null)
- ✅ Retry counts from model_calls.retry_count and phases.retry_count
- ✅ Error tracking via model_calls.is_success and phases.error_message
- ✅ Latency via latency_ms
- ✅ Timestamps via created_at

### What's Missing
- ❌ Cached tokens — not stored anywhere
- ❌ Reasoning tokens — not stored anywhere
- ❌ Token waste categories — must be derived
- ❌ Engine/source_engine — not stored
- ❌ Agent identity when agent_id is null — cannot be reliably derived

## Recommendation

**Tokenomics can become LIVE.** The backend has all the primary data needed:
- Total tokens, by_phase, by_model, by_provider: ✅ from cost_events
- by_agent: ✅ from cost_events (when agent_id is set)
- Cost: ✅ from cost_events
- Call count, error count, retry count: ✅ from model_calls
- Waste summary: ⚠️ derivable from retry_count + is_success (retry waste + failed call waste)

The enhanced cost report should use `cost_events` as the primary source (it has all needed fields) and `model_calls` for call-level detail (is_success, retry_count).
