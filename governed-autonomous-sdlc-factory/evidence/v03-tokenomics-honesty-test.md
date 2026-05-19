# v03 Tokenomics Honesty Test

**Date**: 2026-05-19
**Phase**: 8 — Tokenomics Honesty Test

## Approach

Code-level audit of tokenomics/cost tracking to verify that costs are derived from real events, not fabricated.

## Tokenomics Architecture

### Cost Event Model
**File**: `src/models.py`

Cost events are persisted to the database with:
- `agent_id` — which agent generated the cost
- `input_tokens` — input token count
- `output_tokens` — output token count
- `cost` — computed cost
- `provider` — LLM provider
- `model` — LLM model
- `call_type` — type of call (generation, evaluation, etc.)
- `error` — whether the call errored
- `retry_count` — number of retries

### Cost Report Endpoint
**File**: `src/api/v1/endpoints/costs.py`

The `get_cost_report` endpoint:
1. Queries cost events from DB for a given run
2. Aggregates by phase, agent, provider
3. Computes waste summary (retry tokens, failed call tokens, etc.)
4. Returns structured report

### Aggregation Logic
```python
# By phase
by_phase = {
    phase: {
        "key": phase,
        "input_tokens": sum(...),
        "output_tokens": sum(...),
        "total_tokens": sum(...),
        "cost": sum(...),
        "call_count": count(...),
        "error_count": count(...),
        "retry_count": sum(...),
    }
}

# Waste summary
waste_summary = {
    "retry_tokens": sum(retry_tokens),
    "failed_call_tokens": sum(failed_tokens),
    "oversized_prompt_tokens": sum(oversized),
    "unused_context_tokens": sum(unused),
}
```

## Honesty Verification

### ✅ Costs Derived from Real Events
Cost data comes from DB-persisted cost events, not computed estimates.

### ✅ by_agent Aggregation Real
The `by_agent` aggregation sums real token counts from cost events.

### ✅ Retries Reflected
Retry counts are tracked per cost event and summed in aggregation.

### ✅ Failed Calls Reflected
Error counts and failed call tokens are tracked.

### ✅ Unattributed Tokens Surfaced
The `missing_fields` array in the response surfaces data quality issues.

### ⚠️ Test Coverage Weak
The cost report tests (`test_cost_report.py`) contain 3 tautological `assert True` tests. The substantive tests only verify field shapes, not actual computation correctness.

### ⚠️ No Cost Validation
The backend doesn't validate that token counts are reasonable (e.g., negative tokens, impossibly large counts).

## Frontend Tokenomics Display

### Tokenomics Screen
- **API**: `getCostReport`
- **Data**: Real cost events from DB
- **Aggregation**: By phase, by agent, by provider
- **Waste**: Retry tokens, failed tokens, oversized prompts
- **DataSourceBadge**: ✅ Shows LIVE

### Executive Cockpit
- **API**: `getCostReport`
- **Data**: Total cost, total tokens
- **Display**: Shows "—" when null
- **DataSourceBadge**: ✅ Shows LIVE/PARTIAL/MOCK

### Agent Command Center
- **API**: `getCostReport` → `by_agent` aggregation
- **Data**: Per-agent token usage from real cost events
- **Display**: Token count, retry count, error count
- **DataSourceBadge**: ✅ Shows LIVE

## Verdict

**Tokenomics Honesty**: ✅ **SOUND**

- Costs are derived from real DB-persisted cost events
- Aggregation logic is straightforward summation
- Retries and failed calls are tracked
- Frontend displays real data with proper DataSourceBadge
- Weakness: test coverage for cost computation is shallow
