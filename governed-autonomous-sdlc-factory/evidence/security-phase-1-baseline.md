# Security Phase 1 — Baseline Verification

## Repository State
- **Path**: `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
- **Branch**: `main`
- **Local HEAD**: `85ed4992675bc1003614d0876ea9e5328d634c33`
- **Remote HEAD**: `85ed4992675bc1003614d0876ea9e5328d634c33`
- **Parity**: ✅ YES
- **Working Tree**: Clean (only untracked evidence/backup dirs)

## Current Security State
- **No authentication**: All API endpoints are fully open
- **No user model**: No users table, no login, no sessions
- **No RBAC**: `core/auth.py` exists as a stub with hardcoded `local-admin` admin context
- **No JWT**: No token-based auth whatsoever
- **No audit logging**: No audit trail for user actions
- **No secret redaction**: Settings endpoint returns raw key-value pairs

## Existing Auth Stub (`core/auth.py`)
- Has `Role` enum: admin, architect, developer, reviewer, governance_reviewer, viewer
- Has `ROLE_PERMISSIONS` map with wildcard patterns
- Has `AuthContext` model with `user_id`, `role`, `is_authenticated`
- `get_current_auth()` always returns hardcoded admin context
- **Not used by any endpoint** — purely a stub

## Unauthenticated Endpoints (ALL endpoints)
- `GET /health` — health check (candidate for public)
- `GET /cognitive/model-status` — provider status
- `POST /runs` — create pipeline run
- `POST /runs/{id}/start|pause|resume|cancel` — run control
- `POST /pipeline/run-full-pipeline` — full pipeline execution
- `GET /engines/*` — all engine endpoints
- `GET /artifacts/*` — artifact access
- `GET /evidence/*` — evidence access
- `GET /costs/*` — cost data
- `GET /logs` — log access
- `GET /settings` — settings (⚠️ may expose secrets)
- `POST /costs/` — record cost events
- All other API routes

## Frontend Access Behavior
- No login screen — app loads directly
- `page.tsx` renders full Sidebar + TopBar + room content immediately
- API client (`lib/api.ts`) has no auth headers
- No session management
- All rooms accessible to anyone with the URL

## Secret Handling Risks
- `GET /settings` returns raw settings including potential API keys
- `GET /cognitive/model-status` exposes provider base URLs and model names
- No redaction anywhere in the API responses
- Frontend `SettingsProviders` screen shows provider status but doesn't display secrets (mock data fallback)

## Known Risks
1. **Full open access**: Anyone with network access can trigger pipelines, view all data, modify settings
2. **No audit trail**: No record of who did what
3. **Settings exposure**: API keys could be returned by settings endpoint
4. **No user isolation**: All users see all data
5. **No governance enforcement**: Governance engine exists but no approval workflow enforcement

## Implementation Plan
1. Add User, Workspace, WorkspaceMembership, AuditLog models
2. Implement JWT authentication with bcrypt password hashing
3. Implement RBAC with permission-based route protection
4. Add user management endpoints (admin only)
5. Add workspace/project scoping
6. Add audit logging for key actions
7. Add secret redaction to settings endpoint
8. Add frontend login screen and session handling
9. Add role-aware navigation
10. Comprehensive testing
