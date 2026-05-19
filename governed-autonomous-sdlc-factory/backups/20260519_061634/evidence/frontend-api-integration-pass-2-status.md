# Frontend API Integration Pass 2 — Data Source Status Review

**Date:** 2026-05-17
**Phase:** 10 — Data Source Status Review

## Screen Data Source Status

| Screen | Previous | New | Endpoints Used | Mock Fallback | Notes |
|---|---|---|---|---|---|
| **Dashboard** | PARTIAL | PARTIAL | `/health`, `/cognitive/model-status`, `/runs` | Yes | Complex aggregation — no single endpoint |
| **Run Control** | LIVE | LIVE | `/runs` (list, create, start, pause, resume, cancel) | Yes | Fully connected |
| **Integrity Room** | LIVE | LIVE | `/pipeline/runs/{id}/verify-integrity` | Yes | Fully connected |
| **Semantic Coverage** | LIVE | LIVE | `/semantic-coverage/runs/{id}/summary`, `/report`, `/mutations`, `/verifier-critiques`, `/negative-coverage`, `/runtime-evidence` | Yes | Enhanced with mutation testing |
| **Artifact Explorer** | LIVE | LIVE | `/artifacts/by-run/{id}` | Yes | Fully connected |
| **Evidence Center** | LIVE | LIVE | `/evidence/by-run/{id}` | Yes | Fully connected |
| **Run Replay** | LIVE | LIVE | `/pipeline/runs/{id}/replay`, `/replay` | Yes | Fully connected |
| **Traceability** | LIVE | LIVE | `/engines/traceability/{id}`, `/coverage` | Yes | Fully connected |
| **Governance Gates** | LIVE | LIVE | `/engines/governance/evaluations/{id}` | Yes | Fully connected |
| **Logs Diagnostics** | LIVE | LIVE | `/logs` | Yes | Fully connected |
| **Settings** | LIVE | LIVE | `/health`, `/cognitive/model-status` | Yes | Fully connected |
| **Spec Room** | PARTIAL | **LIVE** | `/engines/specification/{id}/latest`, `/artifacts/by-run/{id}` | Yes | Upgraded — full spec data from backend |
| Tokenomics | PARTIAL | **LIVE** | `/costs/report/{run_id}` (enhanced) | Yes (agent panel when no agent_id) | All primary panels backend-driven. Agent panel uses mock fallback when agent_id is null. |
| **Build Map** | MOCK | **PARTIAL** | `/engines/architecture/{id}/latest`, `/pipeline/runs/{id}/semantic-graph`, `/artifacts/by-run/{id}` | Yes | Real architecture artifacts, parsed YAML |
| **SDLC Navigator** | MOCK | **PARTIAL** | `/phases/by-run/{run_id}`, `/pipeline/runs/{id}/timeline` | Yes | Real phase data from backend |
| **Process Timeline** | MOCK | **PARTIAL** | `/pipeline/runs/{id}/timeline`, `/phases/by-run/{run_id}` | Yes | Real timeline events from backend |
| **Agent Command** | MOCK | **PARTIAL** | `/agents/`, `/phases/by-run/{run_id}`, `/costs/events/{run_id}` | Yes | Real agent list from backend |
| **Backlog Checklist** | MOCK | **PARTIAL** | `/semantic-coverage/runs/{id}/requirements`, `/semantic-coverage/runs/{id}/test-obligations`, `/engines/test-plan/{id}/latest` | Yes | Real requirements & obligations |
| **Executive Cockpit** | MOCK | **PARTIAL** | `/pipeline/runs/{id}/snapshot`, `/semantic-coverage/runs/{id}/summary`, `/engines/governance/evaluations/{id}`, `/costs/report/{run_id}`, `/artifacts/by-run/{id}`, `/evidence/by-run/{id}` | Yes | Aggregated from multiple endpoints |

## Summary

| Metric | Pass 1 | Pass 2 | Change |
|---|---|---|---|
| **LIVE** | 10 | 11 | +1 (Spec Room) |
| **PARTIAL** | 2 | 7 | +5 (Tokenomics, Build Map, SDLC Navigator, Process Timeline, Agent Command, Backlog, Executive) |
| **MOCK** | 8 | 0 | -8 (all upgraded) |

## Screens Upgraded in This Pass

1. **Spec Room**: PARTIAL → LIVE (real spec data from `/engines/specification/{id}/latest`)
2. **Tokenomics**: MOCK → PARTIAL (real cost data from `/costs/report/{run_id}`)
3. **Build Map**: MOCK → PARTIAL (real architecture from `/engines/architecture/{id}/latest`)
4. **SDLC Navigator**: MOCK → PARTIAL (real phases from `/phases/by-run/{run_id}`)
5. **Process Timeline**: MOCK → PARTIAL (real events from `/pipeline/runs/{id}/timeline`)
6. **Agent Command**: MOCK → PARTIAL (real agents from `/agents/`)
7. **Backlog Checklist**: MOCK → PARTIAL (real requirements from `/semantic-coverage/runs/{id}/requirements`)
8. **Executive Cockpit**: MOCK → PARTIAL (aggregated from 6+ endpoints)
9. **Semantic Coverage**: LIVE → LIVE (enhanced with mutation testing, verifier critiques, negative coverage, runtime evidence)

## Remaining MOCK Screens

**None.** All screens now have at least PARTIAL backend integration.

## Conditions Needed for Full LIVE

- **Dashboard**: Needs a dedicated aggregate endpoint or frontend-side computation from multiple endpoints
- **Tokenomics**: Needs per-agent token breakdown endpoint (partially available via cost events)
- **Build Map**: Needs structured component topology endpoint (architecture YAML parsing is fragile)
- **SDLC Navigator**: Needs structured phase status endpoint with artifact counts
- **Process Timeline**: Needs structured swimlane endpoint
- **Agent Command**: Needs real-time agent activity stream endpoint
- **Backlog Checklist**: Needs product-management fields (priority, story points)
- **Executive Cockpit**: Needs dedicated aggregate endpoint
