# Security & Access Control — Phase 1 Architecture Contract

## 1. Authentication Model

### JWT-Based Authentication
- **Access tokens**: JWT with RS256 or HS256 signing
- **Secret**: Loaded from `JWT_SECRET_KEY` environment variable
- **Expiration**: 24 hours (configurable via `JWT_EXPIRY_HOURS`)
- **Claims**: `sub` (user_id), `email`, `role`, `iat`, `exp`
- **Refresh**: Not in Phase 1 — users re-login when token expires

### Password Handling
- **Hashing**: bcrypt with cost factor 12
- **Storage**: Only `password_hash` stored — never plaintext
- **Verification**: Constant-time comparison via bcrypt
- **Minimum length**: 8 characters

### Bootstrap Strategy
- `POST /api/v1/auth/bootstrap-admin` endpoint
- Only enabled when `ALLOW_BOOTSTRAP=true` environment variable is set
- Creates first admin user if and only if zero users exist
- Returns credentials once — client must store them
- After first admin exists, endpoint returns 404

## 2. Authorization Model

### Role-Based Access Control (RBAC)
- Roles are assigned at user creation and can be changed by admin
- Each role has a set of permissions
- Permissions are checked at the API endpoint level
- Frontend uses role to show/hide navigation and actions

### Roles
| Role | Description |
|------|-------------|
| `admin` | Full system access |
| `architect` | Architecture creation and inspection |
| `engineer` | Pipeline execution and development |
| `governance_reviewer` | Governance evaluation and approval |
| `executive_viewer` | Read-only dashboard and cockpit access |
| `auditor` | Read-only evidence, integrity, audit logs |
| `operator` | Runtime health, logs, run control |

### Permission Matrix
| Permission | admin | architect | engineer | gov_reviewer | exec_viewer | auditor | operator |
|---|---|---|---|---|---|---|---|
| `system.manage_users` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `system.manage_settings` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `system.view_health` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `system.view_audit_log` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `runs.create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `runs.view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `runs.control` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| `artifacts.view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `artifacts.edit` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `evidence.view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `evidence.export` | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| `governance.view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `governance.approve` | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `integrity.verify` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `tokenomics.view` | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `logs.view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `logs.view_sensitive` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `settings.view` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `settings.edit` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `providers.view` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| `providers.edit` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `workspaces.manage` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `projects.manage` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 3. User Model
- `id`: UUID primary key
- `email`: Unique email address
- `display_name`: Human-readable name
- `password_hash`: bcrypt hash
- `role`: One of the 7 roles
- `is_active`: Boolean, default true
- `created_at`, `updated_at`, `last_login_at`

## 4. Workspace Model
- `id`: UUID primary key
- `name`: Workspace name
- `description`: Optional description
- `created_by_user_id`: FK to users
- `created_at`, `updated_at`

## 5. Project Model
- Existing `projects` table already exists
- Add `workspace_id` FK to link projects to workspaces
- Existing projects without workspace_id remain accessible to admin

## 6. Workspace Membership Model
- `id`: UUID primary key
- `workspace_id`: FK to workspaces
- `user_id`: FK to users
- `role`: Role within this workspace (can differ from global role)
- `created_at`

## 7. Token/Session Model
- Stateless JWT — no server-side session storage
- Token contains user_id, email, role
- Expiration enforced by JWT library
- No revocation mechanism in Phase 1 (limitation documented)

## 8. Audit Log Model
- `id`: UUID primary key
- `user_id`: FK to users (nullable for unauthenticated actions)
- `workspace_id`: Optional FK
- `project_id`: Optional FK
- `action`: String action identifier (e.g., `login.success`, `run.create`)
- `resource_type`: Type of resource affected
- `resource_id`: Optional resource identifier
- `metadata_json`: Safe metadata (no secrets)
- `ip_address`: Optional
- `user_agent`: Optional
- `created_at`: Timestamp

## 9. Protected Route Strategy
- All API routes require authentication by default
- Public exceptions: `GET /health`, `POST /auth/login`, `POST /auth/bootstrap-admin`
- Each protected endpoint declares required permission
- Missing/invalid token → 401
- Valid token but insufficient permission → 403

## 10. Secret Redaction
- Settings endpoint returns `configured: boolean` instead of raw values for secrets
- Provider status shows availability, not API keys
- Logs never contain passwords, tokens, or API keys
- Audit log metadata never contains secrets

## 11. Local Development Bootstrap
- Set `ALLOW_BOOTSTRAP=true` in environment
- Call `POST /api/v1/auth/bootstrap-admin` with email and password
- Endpoint creates first admin user
- After creation, endpoint self-disables
- Document this in README

## 12. Limitations (Phase 1)
- No enterprise SSO/SAML/OIDC
- No token revocation (stateless JWT)
- No production secrets vault
- No tenant isolation beyond workspace/project scoping
- No advanced policy administration UI
- Local/internal controlled-use baseline only
