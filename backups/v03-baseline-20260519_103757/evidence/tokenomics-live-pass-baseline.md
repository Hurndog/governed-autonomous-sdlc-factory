# Tokenomics LIVE Pass — Baseline Report

**Date:** 2026-05-18
**Phase:** 0 — Baseline Verification

## Repository State

| Field | Value |
|---|---|
| **Path** | `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory` |
| **Branch** | main |
| **Local HEAD** | `83679252e71fec14fa4373a8d4cf31434650a9ba` |
| **Remote HEAD** | `83679252e71fec14fa4373a8d4cf31434650a9ba` |
| **Parity** | ✅ YES |
| **Working Tree** | Clean (only untracked backup/evidence files) |

## Current Tokenomics Status

| Field | Value |
|---|---|
| **Data Source** | PARTIAL |
| **File** | `apps/web/src/components/rooms/Tokenomics.tsx` |
| **Lines** | ~280 |
| **Backend Endpoints Used** | `/costs/report/{run_id}`, `/costs/events/{run_id}` |
| **Mock Fallback** | Yes — burn rate, agent breakdown, waste autopsy, phase breakdown |

## Existing Cost Endpoints

| Endpoint | Method | Status |
|---|---|---|
| `/costs/report/{run_id}` | GET | Exists — returns by_phase, by_agent, by_model |
| `/costs/events/{run_id}` | GET | Exists — returns individual cost events |
| `/costs/` | POST | Exists — records cost events |

## Existing Database Tables

| Table | Key Fields |
|---|---|
| cost_events | run_id, phase_id, agent_id, model_name, provider, tokens_in, tokens_out, estimated_cost, actual_cost, is_local, latency_ms |
| model_calls | run_id, phase_id, agent_id, model_name, provider, tokens_in, tokens_out, estimated_cost, actual_cost, latency_ms, is_success, retry_count |
| phases | run_id, name, status, agent_id, model_used, tokens_in, tokens_out, cost, retry_count, error_message |
| agents | id, name, role, is_active |

## Current Frontend Tokenomics Dependencies

- `api.getCostReport(runId)` → `CostReportResponse`
- `api.getCostEvents(runId)` → `CostEventsResponse`
- `mockTokenUsage` → burn rate, agent breakdown, waste autopsy, phase breakdown

## Known Limitations

- `CostReportResponse` has `total_cost_usd`, `by_provider`, `by_model` — but NOT `total_tokens`, `total_input_tokens`, `total_output_tokens`, `total_calls`, `total_errors`, `by_agent` (with agent names), `waste_summary`
- `cost_events` table has `agent_id` but it may be null
- No cached_tokens or reasoning_tokens stored anywhere
- No explicit token waste categories — must be derived

## Can Tokenomics Become LIVE?

**YES.** The backend has all primary data:
- Total tokens: derivable from `SUM(tokens_in + tokens_out)` on cost_events
- by_phase: from `cost_events.phase_id` → `phases.name`
- by_model: from `cost_events.model_name`
- by_provider: from `cost_events.provider`
- by_agent: from `cost_events.agent_id` → `agents.name` (when not null)
- Cost: from `SUM(estimated_cost)` on cost_events
- Call count, errors, retries: from `model_calls`
- Waste: derivable from retry_count + is_success

The existing `/costs/report/{run_id}` endpoint needs enhancement to return the full tokenomics aggregation.
