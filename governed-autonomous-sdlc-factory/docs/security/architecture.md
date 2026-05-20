# Security Architecture

## Overview

The Governed Autonomous SDLC Factory implements defense-in-depth security across all layers. Security is not a module — it is a property of the entire system.

## Authentication

### JWT-Based Authentication

The platform uses JSON Web Tokens (JWT) for authentication:

- **Access Tokens**: Short-lived (15 minutes), used for API access
- **Refresh Tokens**: Long-lived (7 days), used to obtain new access tokens
- **Signing**: HMAC-SHA256 with configurable secret
- **Claims**: User ID, roles, permissions, workspace access

### Token Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client   │──(1)──▶│  Auth    │──(2)──▶│  Token   │
│  Login    │         │  Endpoint│         │  Store   │
└──────────┘◀─(3)────└──────────┘         └──────────┘
   Access +
   Refresh
   Token

┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client   │──(4)──▶│  API     │──(5)──▶│  Auth    │
│  Request  │         │  Endpoint│         │  Verify  │
│  + Token  │         │          │         │          │
└──────────┘◀─(6)────└──────────┘◀─(7)───└──────────┘
   Response              │
                    ┌────┘
                    ▼
              ┌──────────┐
              │  RBAC    │
              │  Check   │
              └──────────┘
```

## Authorization

### Role-Based Access Control (RBAC)

The platform implements granular RBAC with 30+ permissions:

**Project Permissions:**
- `project:read` — View project details
- `project:write` — Modify project configuration
- `project:delete` — Delete projects
- `project:admin` — Full project administration

**Run Permissions:**
- `run:read` — View run details and outputs
- `run:write` — Modify run configuration
- `run:execute` — Start new runs
- `run:terminate` — Stop running executions

**Model Permissions:**
- `model:read` — View model configurations
- `model:configure` — Modify model settings
- `model:route` — Change routing decisions
- `model:arbitrate` — Initiate arbitration

**Governance Permissions:**
- `governance:read` — View governance policies
- `governance:write` — Modify governance policies
- `governance:enforce` — Manually enforce policies

**Intervention Permissions:**
- `intervention:pause` — Pause execution
- `intervention:resume` — Resume execution
- `intervention:quarantine` — Quarantine runs
- `intervention:rollback` — Rollback to previous state
- `intervention:escalate` — Escalate governance scrutiny
- `intervention:throttle` — Throttle execution
- `intervention:override` — Override decisions
- `intervention:terminate` — Terminate execution

**Memory Permissions:**
- `memory:read` — View memory entries
- `memory:write` — Create/modify memory
- `memory:archive` — Archive memory
- `memory:quarantine` — Quarantine memory

**Evidence Permissions:**
- `evidence:read` — View evidence bundles
- `evidence:export` — Export evidence
- `evidence:verify` — Verify evidence integrity

### Default Roles

| Role | Permissions |
|------|-------------|
| `viewer` | `project:read`, `run:read`, `model:read`, `governance:read`, `memory:read`, `evidence:read` |
| `developer` | All viewer + `project:write`, `run:write`, `run:execute`, `model:configure`, `memory:write` |
| `operator` | All developer + all intervention permissions |
| `governance_officer` | All viewer + `governance:write`, `governance:enforce`, `evidence:export`, `evidence:verify` |
| `admin` | All permissions |

## Data Protection

### Encryption at Rest

- Database connections use TLS/SSL
- Sensitive fields (API keys, secrets) are encrypted at rest using AES-256
- Evidence bundles are hash-chained for integrity verification

### Encryption in Transit

- All API communication uses HTTPS/WSS
- Database connections use TLS
- Redis connections use TLS (when configured)

### Data Isolation

- Workspace-level isolation: data from one workspace is never visible to another
- Project-level access control within workspaces
- Row-level security policies in PostgreSQL

## API Security

### Rate Limiting

- 100 requests/minute per user (default)
- 1000 requests/minute per service account
- Configurable per-endpoint

### CORS

- Configurable allowed origins
- Credentials allowed only for trusted origins
- Preflight caching enabled

### Input Validation

- All inputs validated via Pydantic v2 schemas
- SQL injection prevention via SQLAlchemy parameterized queries
- XSS prevention via output encoding
- Path traversal prevention via input sanitization

## Audit Trail

Every security-relevant action produces an immutable audit entry:

```json
{
  "timestamp": "2026-05-19T12:00:00.000Z",
  "actor": "user-uuid",
  "action": "intervention:quarantine",
  "target": "run-uuid",
  "input": {"reason": "Trust score below threshold"},
  "result": {"status": "success"},
  "hash_chain": "sha256-of-previous-entry-plus-current"
}
```

## Security Best Practices

1. **Rotate API keys regularly** — Set calendar reminders every 90 days
2. **Use strong JWT secrets** — Minimum 256-bit random strings
3. **Enable LOCAL_ONLY_MODE** for sensitive deployments
4. **Review audit logs weekly** — Look for unusual patterns
5. **Keep dependencies updated** — Run `pip audit` and `npm audit` monthly
6. **Use network segmentation** — Isolate the runtime from public networks
7. **Enable database encryption** — Use PostgreSQL TDE for sensitive data
8. **Implement backup encryption** — Encrypt database backups at rest

## Security Disclaimer

This platform is designed for **governed autonomous operation within trusted environments**. It is not designed for direct exposure to untrusted users without additional security layers (WAF, API gateway, etc.). Always deploy behind a reverse proxy with proper SSL termination in production.
