# Tokenomics Agent Attribution Hardening — Final Report

**Date:** 2026-05-18

## Commit

| Field | Value |
|---|---|
| **Hash** | `85ed4992675bc1003614d0876ea9e5328d634c33` |
| **Branch** | main |
| **Files Changed** | 5 |
| **Insertions** | 228 |
| **Deletions** | 16 |

## GitHub Parity

| Field | Value |
|---|---|
| **Local HEAD** | `85ed4992675bc1003614d0876ea9e5328d634c33` |
| **Remote HEAD** | `85ed4992675bc1003614d0876ea9e5328d634c33` |
| **Parity** | ✅ YES |

## Backup

| Field | Value |
|---|---|
| **Path** | `../backups/tokenomics-agent-20260518-121548/` |
| **Checksum** | `6288226655a210c0e2be2e06effb5bd0880f21351123d5901b7751cf8b3d9098` |
| **Verify** | ✅ Complete history |

## Validation Results

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Frontend build | ✅ PASS (4 pages, 136kB) |
| Backend tests | ✅ 91/91 passing |

## Tokenomics Status: **LIVE** ✅ (unchanged)

Tokenomics remains LIVE. Agent attribution is now backend-driven for pipeline-executed runs.

## Agent Attribution Behavior

### What Changed
- `publish_cost_event()` now accepts `agent_id` and `phase_name` parameters
- `FullPipelineOrchestrator` calls `publish_cost_event()` after each engine step with deterministic agent_id:

| Engine Step | agent_id | phase_name |
|---|---|---|
| SpecificationEngine | `specification_engine` | specification |
| ArchitectureEngine | `architecture_engine` | architecture |
| GovernanceEngine | `governance_engine` | governance |
| TestPlanEngine | `test_engine` | quality |

### Cost Report by_agent Aggregation
- Resolves `agent_id` → agent name via `Agent` table (for UUID-based IDs)
- Falls back to using `agent_id` as the label (for engine-name-based IDs like `specification_engine`)
- Unattributed tokens (null agent_id) shown as "Unattributed" entry with percentage
- Data quality warnings when partial attribution exists

### Backward Compatibility
- Existing cost events with null agent_id are handled gracefully
- No database schema changes required (agent_id field already exists and is nullable)
- Legacy records remain intact

## Final Screen Counts

| Status | Count |
|---|---|
| **LIVE** | 12 |
| **PARTIAL** | 6 |
| **MOCK** | 0 |

## Remaining Tokenomics Gaps

| Gap | Status |
|---|---|
| Agent attribution for pipeline runs | ✅ Fixed |
| Agent attribution for direct API calls to `/costs/` | ⚠️ Still requires caller to pass agent_id |
| Burn rate chart (time-series) | ❌ Still mock — needs time-series data |
| Cached/reasoning tokens | ❌ Still not tracked by backend |
| Legacy records with null agent_id | ⚠️ Remain unless backfilled |

## Recommended Next Action

1. **Add agent_id to `/costs/` POST endpoint** — allow callers to pass agent_id directly
2. **Add time-series cost tracking** — for burn rate chart
3. **Add cached/reasoning token fields** — to cost_events table
4. **Proceed to Security & Access Control** phase
