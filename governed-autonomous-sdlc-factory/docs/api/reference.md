# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/*`) require a Bearer token:

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout and invalidate tokens |
| GET | `/auth/me` | Get current user info |

## Projects

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/projects` | List projects | `project:read` |
| POST | `/projects` | Create project | `project:write` |
| GET | `/projects/{id}` | Get project | `project:read` |
| PUT | `/projects/{id}` | Update project | `project:write` |
| DELETE | `/projects/{id}` | Delete project | `project:delete` |

## Runs

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/runs` | List runs | `run:read` |
| POST | `/runs` | Start new run | `run:execute` |
| GET | `/runs/{id}` | Get run details | `run:read` |
| POST | `/runs/{id}/pause` | Pause run | `intervention:pause` |
| POST | `/runs/{id}/resume` | Resume run | `intervention:resume` |
| POST | `/runs/{id}/terminate` | Terminate run | `intervention:terminate` |

## Operations

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/operations/summary` | System health summary | `run:read` |
| GET | `/operations/events` | List events (filtered) | `run:read` |
| GET | `/operations/events/stream` | SSE telemetry stream | `run:read` |

## Explainability

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/explain/runtime/{run_id}` | Runtime explanation | `run:read` |
| GET | `/explain/trust/{run_id}` | Trust explanation | `run:read` |
| GET | `/explain/drift/{run_id}` | Drift explanation | `run:read` |
| GET | `/explain/replay/{run_id}` | Replay explanation | `run:read` |
| GET | `/explain/governance/{run_id}` | Governance explanation | `governance:read` |
| GET | `/explain/memory/{run_id}` | Memory explanation | `memory:read` |
| GET | `/explain/interventions/{run_id}` | Intervention explanation | `run:read` |
| GET | `/explain/autonomy/{run_id}` | Autonomy explanation | `run:read` |

## Model Router

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/model-router/capabilities` | List model capabilities | `model:read` |
| POST | `/model-router/route` | Get routing decision | `model:route` |
| POST | `/model-router/arbitrate` | Run arbitration | `model:arbitrate` |
| GET | `/model-router/health` | Provider health | `model:read` |
| GET | `/model-router/sovereignty` | Sovereignty status | `model:read` |

## Memory Lifecycle

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/memory` | List memory entries | `memory:read` |
| POST | `/memory/age` | Trigger aging | `memory:write` |
| POST | `/memory/archive` | Archive entries | `memory:archive` |
| POST | `/memory/quarantine` | Quarantine entries | `memory:quarantine` |
| POST | `/memory/restore` | Restore archived | `memory:write` |

## Operator Interventions

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| POST | `/interventions/pause` | Pause execution | `intervention:pause` |
| POST | `/interventions/resume` | Resume execution | `intervention:resume` |
| POST | `/interventions/quarantine` | Quarantine run | `intervention:quarantine` |
| POST | `/interventions/rollback` | Rollback run | `intervention:rollback` |
| POST | `/interventions/escalate` | Escalate scrutiny | `intervention:escalate` |
| POST | `/interventions/throttle` | Throttle execution | `intervention:throttle` |
| POST | `/interventions/override` | Override decision | `intervention:override` |
| POST | `/interventions/terminate` | Terminate execution | `intervention:terminate` |
| GET | `/interventions/history` | Intervention history | `run:read` |

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {},
    "trace_id": "uuid-for-debugging"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `GOVERNANCE_BLOCKED` | 409 | Action blocked by governance policy |
| `TRUST_TOO_LOW` | 409 | Trust score below threshold |
| `SOVEREIGNTY_VIOLATION` | 409 | Sovereignty constraint violated |
| `COST_LIMIT_EXCEEDED` | 409 | Cost budget exceeded |
| `PROVIDER_ERROR` | 502 | Model provider error |
| `INTERNAL_ERROR` | 500 | Internal server error |
