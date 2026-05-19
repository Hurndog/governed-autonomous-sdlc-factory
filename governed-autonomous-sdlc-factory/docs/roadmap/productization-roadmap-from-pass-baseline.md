# Productization Roadmap — From PASS Baseline

**Baseline Tag:** `v0.3-governed-runtime-observability-baseline`
**Date:** 2026-05-19

This roadmap defines the path from the current v0.3 Governed Runtime Observability Baseline to a production-ready enterprise system. Phases 1-3 are complete. Phase 4 is the next target.

---

## Phase 1: Security and Access Control

**Prerequisite for:** Any production deployment, multi-user operation, or external exposure.

### Authentication
- JWT-based authentication with refresh tokens
- Session-based alternative for browser clients
- OAuth2/OIDC integration for SSO (Google, GitHub, SAML)
- API key authentication for programmatic access
- Token expiration and revocation

### Authorization
- Role-Based Access Control (RBAC)
- Roles: Admin, Operator, Auditor, Viewer
- Permission matrix per role for all API endpoints
- Resource-level permissions (per-project, per-run)

### User/Project/Workspace Model
- **Workspace** — Top-level isolation boundary (organization/team)
- **Project** — Scoped set of runs, requirements, and artifacts within a workspace
- **User** — Identity with role assignments per workspace
- **Run** — Execution instance within a project
- Database schema: `workspaces`, `projects`, `users`, `workspace_members`, `project_members`

### Secrets Management
- Encrypted storage for API keys, database credentials, tokens
- Per-workspace secret scoping
- Rotation policies
- Integration with system keychain or external vault (HashiCorp Vault, AWS Secrets Manager)
- No secrets in environment variables or config files

### API Protection
- Rate limiting per user/workspace
- Input validation and sanitization on all endpoints
- CORS configuration
- CSRF protection for session-based auth
- Request size limits
- SQL injection prevention (already handled by SQLAlchemy parameterized queries)

### Audit Access Model
- Read-only audit log access for Auditor role
- Immutable audit trail for all authentication and authorization events
- Audit log export capability

---

## Phase 2: Production Deployment Hardening

**Prerequisite for:** Any production or staging deployment.

### Docker Compose / Deployment Scripts
- Production-grade Docker Compose with resource limits
- Separate containers: api, web, postgres, redis, qdrant
- Health check endpoints for all services
- Graceful shutdown handling
- Log aggregation configuration
- Volume persistence for database and evidence

### Environment Configuration
- `.env.production` template with all required variables
- Environment validation on startup
- Separate configs for: development, staging, production
- Feature flags for experimental capabilities

### Health Checks
- `/health` endpoint: basic liveness
- `/ready` endpoint: dependency checks (DB, Redis, Qdrant)
- `/metrics` endpoint: Prometheus-compatible metrics
- Startup probe and liveness probe for container orchestration

### Logging
- Structured JSON logging (already partially implemented)
- Log levels per component
- Correlation IDs for request tracing
- Log retention policies
- Integration with Loki or ELK stack

### Monitoring
- Prometheus metrics export
- Grafana dashboards for: pipeline runs, phase durations, model costs, error rates
- Alerting rules for: pipeline failures, guard activations, budget exhaustion
- Uptime monitoring

### Database Migrations
- Alembic migration automation (partially configured)
- Migration CI check: migrations must be generated for all model changes
- Rollback testing
- Migration documentation

### Backup Automation
- Scheduled database dumps (pg_dump)
- Evidence directory backup
- Offsite backup configuration
- Backup verification (automated restore test)

### Restore Drills
- Documented restore procedure
- Quarterly restore drill schedule
- Restore time target: < 30 minutes
- Verification checklist post-restore

---

## Phase 3: Autonomous Code Generation Under Governance

**Prerequisite for:** Automated software development workflows.

### Code Generation
- Integration with code generation models (Codex, Claude, etc.)
- Context-aware generation using project codebase
- Multi-file generation with dependency awareness
- Language-agnostic generation framework

### Test Generation
- Automatic test generation from requirements and acceptance criteria
- Unit test generation
- Integration test generation
- Edge case identification and test coverage

### Semantic Coverage Check
- Post-generation semantic coverage validation
- Requirement-to-code traceability
- Coverage gap identification
- Auto-remediation suggestions for low coverage

### Mutation Testing
- Automated mutation testing to verify test quality
- Mutation score tracking
- Integration with verification phase

### Security Scanning
- Static Application Security Testing (SAST)
- Dependency vulnerability scanning
- Secret detection in generated code
- Security report generation

### Release Gate
- Enhanced gate with code quality metrics
- Security scan results as gate criteria
- Mutation score threshold
- Combined score: integrity + coverage + security + quality

### Human Approval
- Human-in-the-loop approval step before release
- Approval UI in Control Tower
- Approval audit trail
- Configurable approval requirements per project

### Commit Proposal
- Automated commit message generation
- Pull request creation
- Code review assignment
- CI/CD pipeline integration

---

## Phase 4: Enterprise Evidence and Audit Exports

**Prerequisite for:** Compliance, audit, and enterprise reporting.

### Evidence Bundles
- ZIP export of all evidence for a run
- Structured evidence manifest
- Evidence integrity verification (hash check)
- Long-term evidence storage policy

### PDF / Markdown Export
- PDF generation for evidence reports
- Markdown export for audit trails
- Customizable report templates
- Executive summary generation

### Audit Trails
- Complete audit log for all system actions
- User action tracking
- Model decision logging
- Immutable audit storage

### Compliance Mapping
- SOC 2 control mapping
- ISO 27001 control mapping
- GDPR data handling documentation
- Compliance gap analysis

### Governance Reports
- Periodic governance reports (weekly, monthly)
- Risk assessment summaries
- Guard activation analysis
- Conflict resolution tracking

---

## Phase 5: Multi-Project and Multi-Tenant Operation

**Prerequisite for:** SaaS deployment or enterprise multi-team use.

### Project Isolation
- Database-level project isolation
- Per-project configuration
- Per-project evidence storage
- Cross-project data leakage prevention

### Tenant Isolation
- Tenant model: workspace = tenant
- Database schema isolation or row-level security
- Per-tenant resource limits
- Tenant-aware backup and recovery

### Run Permissions
- Per-run access control
- Run sharing between workspace members
- Run visibility settings (private, workspace, public within org)

### Provider Policies
- Per-workspace model provider configuration
- Provider allowlist/blocklist
- Custom model registration
- Provider health monitoring

### Cost Budgets
- Per-workspace cost tracking
- Per-project cost limits
- Per-run cost caps
- Cost alerting and automatic shutdown
- Cost reporting and analytics

### Model Usage Policies
- Model selection policies per workspace
- Token usage quotas
- Rate limiting per workspace
- Usage analytics and dashboards

---

## Recommended Execution Order

| Phase | Priority | Dependencies |
|---|---|---|
| Phase 1: Security | **Critical** | None (can start immediately) |
| Phase 2: Deployment | **High** | Phase 1 (auth for deployment) |
| Phase 3: Code Gen | **Medium** | Phase 1 + 2 (secure deployment) |
| Phase 4: Audit | **Medium** | Phase 1 + 2 (secure evidence) |
| Phase 5: Multi-tenant | **Lower** | Phase 1 + 2 + 4 (isolation + audit) |

Each phase should follow the same evidence-backed approach used for the PASS baseline: implement, test, verify, document, backup.
