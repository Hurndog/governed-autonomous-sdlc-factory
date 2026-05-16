# Control Plane Status

**Date:** 2026-05-16T15:42:00+00:00
**Status:** ✅ OPERATIONAL

## Frontend

| Field | Value |
|-------|-------|
| URL | http://localhost:3000 |
| Framework | Next.js 14.2.0 |
| Build | ✅ Successful (29.5kB First Load JS) |
| Typecheck | ✅ Passing |
| Dev Server | ✅ Running (PID 85420) |

## Backend

| Field | Value |
|-------|-------|
| URL | http://localhost:8000 |
| Framework | FastAPI 1.0.0 |
| Health | ✅ OK |
| Database | ✅ Connected |
| Redis | ✅ Connected |
| Endpoints | 94 total |

## Rooms Implemented

| Room | File | Status | API Endpoints Used |
|------|------|--------|-------------------|
| Command Center | `CommandCenter.tsx` | ✅ | `/health`, `/cognitive/model-status`, `/runs`, `/pipeline/run-full-pipeline` |
| Run Control | `RunControlRoom.tsx` | ✅ | `/runs`, `/runs/{id}`, `/runs/{id}/status`, `/runs/{id}/start`, `/pipeline/runs/{id}/timeline` |
| Integrity | `IntegrityRoom.tsx` | ✅ | `/pipeline/runs/{id}/verify-integrity` |
| Traceability | `TraceabilityRoom.tsx` | ✅ | `/engines/traceability/{run_id}` |
| Governance | `GovernanceRoom.tsx` | ✅ | `/engines/governance/evaluations/{run_id}`, `/engines/governance/policies` |
| Replay Chamber | `ReplayChamber.tsx` | ✅ | `/pipeline/runs/{id}/replay` |
| Artifact Explorer | `ArtifactExplorer.tsx` | ✅ | `/artifacts/by-run/{run_id}`, `/artifacts/{id}` |
| Evidence Center | `EvidenceCenter.tsx` | ✅ | `/evidence/by-run/{run_id}`, `/evidence/download/{id}` |
| Logs & Diagnostics | `LogsDiagnostics.tsx` | ✅ | `/logs` |
| Settings & Providers | `SettingsProviders.tsx` | ✅ | `/health`, `/cognitive/model-status`, `/github/status`, `/settings` |
| Spec Room | `SpecRoom.tsx` | ✅ (existing) | `/engines/specification/{run_id}` |
| Architecture Room | `ArchitectureRoom.tsx` | ✅ (existing) | `/engines/architecture/{run_id}` |

## Key Features

- **No fake data** — all rooms load from real API endpoints
- **No hardcoded success states** — all status from backend
- **Error handling** — loading, error, and empty states in every room
- **Integrity Room** — calls official `/verify-integrity` endpoint, shows component scores
- **Stability check** — 3 consecutive integrity calls with variance detection
- **Traceability filters** — by link type, source type, target type
- **Governance evaluations** — real policy evaluations with findings
- **Artifact content viewer** — expandable content with hash display
- **Evidence download** — view evidence bundle content
- **Log filtering** — by severity, error-only, run ID
- **Provider status** — real-time model provider status
- **API key presence** — shows true/false without exposing secrets

## Known Limitations

- Replay endpoint returns null fields (not fully implemented in backend)
- Evidence listing is by-run only (no global evidence file listing)
- No WebSocket live updates (wsConnected always false)
- Graph view for traceability not implemented (table only)
- No evidence file read endpoint (only download by bundle ID)

## Next Recommended Phase

1. Add evidence file listing endpoint to backend
2. Implement WebSocket live event streaming
3. Add traceability graph visualization (Mermaid)
4. Build and deploy frontend to production
