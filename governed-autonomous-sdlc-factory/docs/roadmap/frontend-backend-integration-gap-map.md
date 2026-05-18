# Frontend-Backend Integration Gap Map

**Date:** 2026-05-17
**Pass:** 2 (after connecting all screens to existing endpoints)

## Summary

After Pass 2, all 18 screens have at least PARTIAL backend integration. No screens remain fully MOCK. However, several screens still rely on mock data for some panels because the backend lacks certain aggregation endpoints or structured data shapes.

## Gap Categories

### Category A — Local Demo Gaps
*These gaps prevent a fully live demo without mock fallback.*

| # | Screen | Gap | Desired Endpoint | Priority |
|---|---|---|---|---|
| A1 | **Dashboard** | No single aggregated dashboard endpoint; metrics scattered across `/health`, `/cognitive/model-status`, `/runs` | `GET /dashboard/summary` with run status, integrity, coverage, cost, artifact count | High |
| A2 | **Tokenomics** | ✅ Resolved — `by_agent` aggregation added to `/costs/report/{run_id}`. Tokenomics is now LIVE. Remaining: agent panel shows mock when agent_id is null in cost events. | Low |
| A3 | **Build Map** | Architecture YAML is unstructured; no component topology endpoint | `GET /engines/architecture/{run_id}/graph` returning nodes/edges | Medium |
| A4 | **Process Timeline** | No structured swimlane endpoint; timeline events exist but lack swimlane layout | `GET /pipeline/runs/{run_id}/swimlanes` | Medium |
| A5 | **Agent Command** | No real-time agent activity stream; agents table exists but no live status | `GET /agents/activity` or WebSocket `/ws/agents` | Medium |

### Category B — Product Maturity Gaps
*These gaps affect product completeness but don't block local demo.*

| # | Screen | Gap | Desired Endpoint | Priority |
|---|---|---|---|---|
| B1 | **SDLC Navigator** | Phase status exists but no artifact counts per phase; no phase duration tracking | `GET /phases/by-run/{run_id}` already exists but needs `artifact_count`, `duration_ms` | Medium |
| B2 | **Backlog Checklist** | No product-management fields (priority, story points, epic linkage) | `GET /backlog/items` with PM fields | Low |
| B3 | **Executive Cockpit** | No dedicated aggregate endpoint; all metrics computed frontend-side from 6+ endpoints | `GET /executive/summary` with all KPIs | Low |
| B4 | **Tokenomics** | No token waste autopsy data (retry waste, ambiguity waste) | `GET /costs/waste-analysis/{run_id}` | Low |

### Category C — Production Enterprise Gaps
*These gaps affect production readiness for enterprise use.*

| # | Screen | Gap | Desired Endpoint | Priority |
|---|---|---|---|---|
| C1 | **All screens** | No authentication/authorization; all endpoints are open | Auth middleware + per-user data isolation | High |
| C2 | **All screens** | No multi-project support in aggregated views | Project-scoped dashboard/executive endpoints | Medium |
| C3 | **Evidence Center** | No evidence bundle download streaming | `GET /evidence/download/{bundle_id}` with streaming response | Medium |
| C4 | **Run Replay** | No replay comparison visualization data | `GET /pipeline/runs/{run_id}/replay/{session_id}/compare` with structured diff | Low |
| C5 | **Traceability** | No traceability graph visualization | `GET /engines/traceability/{run_id}/graph` with nodes/edges | Low |

## Endpoint Enhancement Proposals

### 1. `GET /costs/report/{run_id}` — Add by_agent aggregation
**Current**: Returns `by_provider`, `by_model`  
**Needed**: Add `by_agent` field  
**Impacts**: Tokenomics screen → LIVE  
**Effort**: Low (backend already has `agent_id` in cost events)

### 2. `GET /engines/architecture/{run_id}/latest` — Structured components
**Current**: Returns `content` (markdown), `components` (array), `decisions` (array)  
**Needed**: Add `topology` field with nodes/edges for graph visualization  
**Impacts**: Build Map → LIVE  
**Effort**: Medium (requires graph extraction from architecture)

### 3. `GET /dashboard/summary` — New endpoint
**Current**: No such endpoint  
**Needed**: Single endpoint returning run status, integrity score, semantic coverage, cost, artifact count, evidence count, governance findings  
**Impacts**: Dashboard → LIVE  
**Effort**: Medium (aggregation of existing endpoints)

### 4. `GET /executive/summary` — New endpoint
**Current**: No such endpoint  
**Needed**: Aggregated KPIs for executive view  
**Impacts**: Executive Cockpit → LIVE  
**Effort**: Medium (aggregation of existing endpoints)

### 5. `GET /agents/activity` — New endpoint
**Current**: `GET /agents/` returns static agent list  
**Needed**: Real-time agent activity with status, current task, token usage  
**Impacts**: Agent Command → LIVE  
**Effort**: High (requires agent state tracking)

## Screens That Can Reach LIVE with Minimal Backend Changes

| Screen | Current | To LIVE | Required Change |
|---|---|---|---|
| Tokenomics | **LIVE** | ✅ | Enhanced `/costs/report` with full aggregation |
| Build Map | PARTIAL | LIVE | Add topology to architecture endpoint |
| Dashboard | PARTIAL | LIVE | Add dashboard summary endpoint |
| Executive Cockpit | PARTIAL | LIVE | Add executive summary endpoint |

## Screens That Need Significant Backend Work

| Screen | Current | Gap |
|---|---|---|
| Agent Command | PARTIAL | Needs real-time activity stream |
| Process Timeline | PARTIAL | Needs structured swimlane data |
| SDLC Navigator | PARTIAL | Needs artifact counts per phase |
| Backlog Checklist | PARTIAL | Needs PM fields |

## Recommendation

**Short term**: Implement `by_agent` aggregation in cost report (low effort, high impact — makes Tokenomics LIVE).

**Medium term**: Add `/dashboard/summary` and `/executive/summary` aggregation endpoints (makes 2 more screens LIVE).

**Long term**: Implement agent activity stream and architecture topology extraction for full LIVE coverage.
