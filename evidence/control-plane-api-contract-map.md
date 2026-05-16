# Control Plane API Contract Map

**Date:** 2026-05-16
**Backend:** FastAPI v1.0.0 on port 8000
**Total Endpoints:** 94

## Domain: Health & Status

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/health` | GET | Runtime health | — | `{status, version, database, redis, uptime_seconds}` | CommandCenter, SettingsProviders, TopBar |
| `/api/v1/cognitive/model-status` | GET | Model provider status | — | `{providers[], routing_policy, default_provider, default_model}` | CommandCenter, SettingsProviders |
| `/api/v1/github/status` | GET | GitHub sync status | — | `{configured, token_valid, owner?, repo?, error?}` | SettingsProviders |
| `/api/v1/settings` | GET | System settings | — | `{settings[]}` | SettingsProviders |

## Domain: Runs

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/runs` | GET | List runs | `?project_id, status, page, page_size` | `{items[], total, page, page_size}` | CommandCenter, RunControlRoom |
| `/api/v1/runs/{run_id}` | GET | Get run detail | — | `RunDetail` | RunControlRoom |
| `/api/v1/runs/{run_id}/status` | GET | Run status | — | `RunStatus` | RunControlRoom |
| `/api/v1/runs` | POST | Create run | `{intent, project_name?, project_id?, budget_limit?}` | `RunDetail` | RunControlRoom |
| `/api/v1/runs/{run_id}/start` | POST | Start run | — | `RunDetail` | RunControlRoom |
| `/api/v1/runs/{run_id}/pause` | POST | Pause run | — | `RunDetail` | RunControlRoom |
| `/api/v1/runs/{run_id}/resume` | POST | Resume run | — | `RunDetail` | RunControlRoom |
| `/api/v1/runs/{run_id}/cancel` | POST | Cancel run | — | `RunDetail` | RunControlRoom |

## Domain: Pipeline

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/pipeline/run-full-pipeline` | POST | Launch pipeline | `?intent, project_name?, project_id?, budget_limit?` | `{run_id, status}` | CommandCenter, RunControlRoom |
| `/api/v1/pipeline/runs/{run_id}/timeline` | GET | Run timeline | — | `{events[], total}` | RunControlRoom |
| `/api/v1/pipeline/runs/{run_id}/snapshot` | GET | Run snapshots | — | `{snapshots[]}` | — |
| `/api/v1/pipeline/runs/{run_id}/divergence` | GET | Divergence records | `?replay_session_id` | `{divergences[], total}` | ReplayChamber |
| `/api/v1/pipeline/runs/{run_id}/compare` | POST | Compare run/replay | `?replay_session_id` | `{match, differences[]}` | ReplayChamber |
| `/api/v1/pipeline/runs/{run_id}/semantic-graph` | GET | Semantic graph | — | `{nodes[], edges[]}` | — |

## Domain: Integrity

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/pipeline/runs/{run_id}/verify-integrity` | POST | Verify integrity | — | `IntegrityResponse` | IntegrityRoom |
| `/api/v1/pipeline/runs/{run_id}/integrity` | GET | Get cached integrity | — | `IntegrityResponse` | IntegrityRoom |

## Domain: Replay

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/pipeline/runs/{run_id}/replay` | POST | Execute replay | `?replay_mode, from_timestamp, phase_name` | `ReplayResponse` | ReplayChamber |
| `/api/v1/pipeline/runs/{run_id}/replay` | GET | List replay sessions | — | `{sessions[]}` | ReplayChamber |

## Domain: Traceability

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/engines/traceability/{run_id}` | GET | Get traceability links | — | `{links[], total}` | TraceabilityRoom |
| `/api/v1/engines/traceability/{run_id}/coverage` | GET | Coverage analysis | — | `{total_requirements, covered_requirements, coverage_pct, by_phase}` | TraceabilityRoom |
| `/api/v1/pipeline/traceability/lineage/{artifact_id}` | GET | Artifact lineage | — | `{upstream[], downstream[]}` | ArtifactExplorer |

## Domain: Governance

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/engines/governance/evaluations/{run_id}` | GET | Get evaluations | — | `{evaluations[], total}` | GovernanceRoom |
| `/api/v1/engines/governance/policies` | GET | Get policies | `?active_only` | `{policies[]}` | GovernanceRoom |
| `/api/v1/engines/governance/evaluate/{run_id}` | POST | Evaluate governance | `{spec_id?, arch_id?}` | `{evaluations[]}` | GovernanceRoom |
| `/api/v1/engines/governance/release-gates/{run_id}` | POST | Create release gate | `?gate_name, required_policy_ids` | `ReleaseGateResponse` | GovernanceRoom |
| `/api/v1/engines/governance/release-gates/{run_id}/evaluate/{gate_id}` | POST | Evaluate gate | — | `ReleaseGateResponse` | GovernanceRoom |

## Domain: Artifacts

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/artifacts/by-run/{run_id}` | GET | List artifacts | `?artifact_type` | `{artifacts[], total}` | ArtifactExplorer |
| `/api/v1/artifacts/{artifact_id}` | GET | Get artifact detail | — | `ArtifactDetail` | ArtifactExplorer |
| `/api/v1/artifacts/{artifact_id}/lock` | POST | Lock artifact | — | `ArtifactDetail` | ArtifactExplorer |

## Domain: Evidence

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/evidence/by-run/{run_id}` | GET | Get evidence bundles | — | `{bundles[]}` | EvidenceCenter |
| `/api/v1/evidence/create/{run_id}` | POST | Create evidence bundle | — | `EvidenceBundleResponse` | EvidenceCenter |
| `/api/v1/evidence/download/{bundle_id}` | GET | Download evidence | — | Raw text content | EvidenceCenter |

## Domain: Logs

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/logs` | GET | List logs | `?run_id, phase_id, agent_id, severity, error_only, limit, offset` | `{logs[], total}` | LogsDiagnostics |

## Domain: Costs

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/costs/events/{run_id}` | GET | Cost events | — | `{events[]}` | — |
| `/api/v1/costs/report/{run_id}` | GET | Cost report | — | `{total_tokens, total_cost_usd, by_provider, by_model}` | — |

## Domain: Engines (Spec, Arch, Test)

| Endpoint | Method | Purpose | Request | Response | UI Consumer |
|----------|--------|---------|---------|----------|-------------|
| `/api/v1/engines/specification/{run_id}` | GET | Get specs | — | `{specifications[]}` | SpecRoom |
| `/api/v1/engines/specification/{run_id}/latest` | GET | Latest spec | — | `SpecificationDetail` | SpecRoom |
| `/api/v1/engines/architecture/{run_id}` | GET | Get architectures | — | `{architectures[]}` | ArchitectureRoom |
| `/api/v1/engines/architecture/{run_id}/latest` | GET | Latest arch | — | `ArchitectureDetail` | ArchitectureRoom |
| `/api/v1/engines/test-plan/{run_id}` | GET | Get test plans | — | `{test_plans[]}` | — |
| `/api/v1/engines/test-plan/{run_id}/latest` | GET | Latest test plan | — | `TestPlanDetail` | — |

## Missing Endpoints (documented for future)

| Domain | Needed Endpoint | Purpose |
|--------|----------------|---------|
| Evidence | `GET /api/v1/evidence/list` | List all evidence files (not just by-run) |
| Evidence | `GET /api/v1/evidence/file/{path}` | Read individual evidence file |
| Replay | `GET /api/v1/pipeline/runs/{run_id}/replay/{session_id}` | Get replay session detail with events |
| Settings | `GET /api/v1/evidence/reports` | List evidence reports for Evidence Center |
