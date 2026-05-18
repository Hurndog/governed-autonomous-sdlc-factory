# Tokenomics Agent Attribution Contract

**Date:** 2026-05-18
**Version:** 1.0

## Purpose

Define a stable, machine-readable contract for agent attribution in cost events and model calls. This enables the Tokenomics screen to display per-agent token usage and cost breakdowns from real backend data.

## Agent Identity Fields

### CostEvent Model
| Field | Type | Required | Description |
|---|---|---|---|
| agent_id | String(36)? | No | Stable snake_case identifier for the agent/engine |
| phase_id | String(36)? | No | Phase during which the cost was incurred |
| model_name | String(255)? | No | Model used |
| provider | String(100)? | No | Provider used |
| tokens_in | Integer | Yes | Input tokens |
| tokens_out | Integer | Yes | Output tokens |
| estimated_cost | Float | Yes | Estimated cost in USD |
| actual_cost | Float? | No | Actual cost if different from estimate |
| is_local | Boolean | Yes | Whether the model is local/free |
| latency_ms | Float? | No | Call latency |

### Agent ID Naming Convention

Format: `{engine_name}` (snake_case, no spaces)

Examples:
- `specification_engine`
- `architecture_engine`
- `governance_engine`
- `test_engine`
- `semantic_coverage_engine`
- `traceability_engine`
- `snapshot_engine`
- `evidence_engine`
- `model_router`
- `utility_classifier`

## Derivation Rules

### Allowed (Deterministic)

1. **Engine class name** → `agent_id = engine.__class__.__name__.lower()`
2. **Phase name** → `phase_name = phase.name` (preserved as-is)
3. **Model router task type** → `agent_id = f"model_router_{task_type}"`

### Forbidden (Unreliable)

1. Display labels or frontend strings
2. Log message parsing
3. Heuristic inference from model names
4. Guessing from cost patterns

## Fallback Behavior

- If `agent_id` cannot be determined: set to `null`, include in `missing_fields`
- Cost report must still aggregate all records, including unattributed ones
- Unattributed calls must be reported in `data_quality_warnings`

## Data Quality Warnings

The cost report endpoint must include warnings when:
- `agent_id` is null for any cost event
- Some but not all events have `agent_id` set
- No cost events exist for a run

## Frontend Display Expectations

- Show per-agent breakdown when `by_agent` is non-empty
- Show "Unattributed" section for records without `agent_id`
- Show data quality warnings when agent attribution is incomplete
- Never show mock agent data as live
