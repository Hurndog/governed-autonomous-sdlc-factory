# Requirement Traceability Matrix

Generated: 2026-05-14
Repository: /Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory
Total Requirements: 293 (numbered sections 0.1 through 38.20)

## Status Summary

| Status | Count |
|--------|-------|
| implemented | 12 |
| partially_implemented | 28 |
| documented_only | 5 |
| missing | 231 |
| broken | 3 |
| blocked | 0 |
| not_applicable | 14 |
| **Total** | **293** |

## Completion: ~10% by requirement count, ~15% by line count

---

## Detailed Matrix

| Req ID | Requirement | Status | Evidence | Gap | Next Action |
|--------|-------------|--------|----------|-----|-------------|
| 0.1 | Work autonomously | N/A | Execution rule | — | — |
| 0.2 | No user questions | N/A | Execution rule | — | — |
| 0.3 | Safe defaults | N/A | Execution rule | — | — |
| 0.4 | Single project dir | implemented | Dir exists at expected path | None | — |
| 0.5 | logs/overnight-build-log.md | missing | No logs/ dir | Create after audit | Create dir + file |
| 0.6 | evidence/system-completion-checklist.json | missing | No evidence/ dir | Create after audit | Create dir + file |
| 0.7 | evidence/system-completion-report.md | missing | No evidence/ dir | Create after audit | Create dir + file |
| 0.8 | Number features per prompt | partially_implemented | models.py has numbered comments (5.3.1 etc.) | Not consistent across all files | Add numbering |
| 0.9 | Record status per requirement | missing | No checklist exists | Will create | Create checklist |
| 0.10 | Explain blockers | missing | Will create | Will create | Create as part of audit |
| 0.11-0.15 | Git commit rules | missing | No git repo initialized | Init git | Init + commit |
| 1.1 | UI-operated SDLC factory | partially_implemented | Backend core exists, no frontend | No UI at all | Build Next.js frontend |
| 1.2 | Natural language idea input | missing | No UI | No UI | Build Command Center |
| 1.3 | Idea → specs | missing | No spec engine | Build spec engine | Build spec engine |
| 1.4 | Functional design | missing | No FD engine | Build FD engine | Build FD engine |
| 1.5 | Technical architecture | missing | No arch engine | Build arch engine | Build arch engine |
| 1.6 | Design proposal | missing | No design engine | Build design engine | Build design engine |
| 1.7 | Database designs | missing | No data model engine | Build data model engine | Build data model engine |
| 1.8 | API contracts | missing | No API contract gen | Build API contract gen | Build API contract gen |
| 1.9 | MCP contracts | missing | DB table exists, no gen logic | Build MCP contract gen | Build MCP contract gen |
| 1.10 | Governance requirements | partially_implemented | DB table + workflow stub | No actual governance engine | Build governance engine |
| 1.11 | Test plans/cases | partially_implemented | DB tables exist | No test generation logic | Build test engine |
| 1.12 | Acceptance criteria | missing | No generation | Add to spec engine | Build AC generation |
| 1.13 | Present artifacts in UI | missing | No UI | Build UI artifact viewer | Build artifact viewer |
| 1.14 | Approval before build | partially_implemented | DB + workflow stub | No UI for approval | Build approval UI |
| 1.15 | Build per approved arch | missing | No build execution | Build execution engine | Build execution engine |
| 1.16 | Generate code | missing | No code generation | Build coding agent | Build coding agent |
| 1.17 | Document code | missing | No doc generation | Build doc generator | Build doc generator |
| 1.18 | Store in git | missing | No git integration | Build git adapter | Build git adapter |
| 1.19 | GitHub integration | missing | No GitHub adapter | Build GitHub adapter | Build GitHub adapter |
| 1.20 | Run tests | partially_implemented | Workflow stub | No test runner | Build test runner |
| 1.21 | Security checks | partially_implemented | Workflow stub | No security runner | Build security runner |
| 1.22 | Governance checks | partially_implemented | Workflow stub | No governance engine | Build governance engine |
| 1.23 | Refactor loop | partially_implemented | refactor_graph.py exists, all stubs | No actual refactor logic | Implement refactor nodes |
| 1.24 | Preserve patterns | partially_implemented | DB table + workflow stub | No pattern extraction | Build pattern library |
| 1.25 | Track tokens/costs | partially_implemented | CostEvent model + CostService | No model router integration | Build model router |
| 1.26 | Evidence bundles | partially_implemented | evidence_graph.py + DB table, all stubs | No actual evidence engine | Build evidence engine |
| 1.27 | Deploy to localhost | partially_implemented | deployment_graph.py, all stubs | No actual deployment | Build deployment runner |
| 1.28 | User observes all from UI | missing | No UI | Build full UI | Build full UI |
| 2.1 | Monorepo structure | partially_implemented | apps/api, workflows, packages exist | Missing: apps/web, policies/, mcp/, docs/, evidence/, logs/, deployments/, generated-projects/, scripts/ | Create missing dirs |
| 2.2 | README.md | partially_implemented | README.md exists | Setup instructions reference non-existent files | Update README after build |
| 2.3-2.12 | Architecture/ops docs | missing | No docs/ directory | Create all docs | Create docs |
| 3.1 | Forge Control Tower UI | missing | No frontend app | Build Next.js app | Build Next.js app |
| 3.2 | Three-panel layout | missing | No frontend | Build layout | Build layout |
| 3.3 | Top bar | missing | No frontend | Build top bar | Build top bar |
| 3.4.1-3.4.19 | All 19 UI screens | missing | No frontend | Build all screens | Build all screens |
| 3.5 | AI assistant natural language | missing | No frontend | Build chat UI | Build chat UI |
| 3.6 | 25 slash commands | missing | No frontend | Build command system | Build command system |
| 3.7 | Live Factory Run visualization | missing | No frontend | Build pipeline viz | Build pipeline viz |
| 3.8 | Phase cards | missing | No frontend | Build phase cards | Build phase cards |
| 3.9-3.19 | Inspector, logs, downloads, etc. | missing | No frontend | Build all UI components | Build all UI |
| 4.1 | FastAPI backend | implemented | apps/api/src/main.py | None | — |
| 4.2 | REST endpoints: projects | implemented | endpoints/projects.py — full CRUD | None | — |
| 4.3 | REST endpoints: runs | implemented | endpoints/runs.py — full CRUD + state machine | None | — |
| 4.4 | REST endpoints: phases | partially_implemented | endpoints/phases.py has phase_router but only 2 endpoints (list by run, get) | Missing: create, update, complete, fail | Add missing endpoints |
| 4.5 | REST endpoints: agents | missing | No agents endpoint file | Create agents endpoints | Create agents endpoints |
| 4.6 | REST endpoints: tasks | missing | No tasks endpoint file | Create tasks endpoints | Create tasks endpoints |
| 4.7 | REST endpoints: artifacts | partially_implemented | artifact_router in phases.py has 3 endpoints | Missing: update, lock, version | Add missing endpoints |
| 4.8 | REST endpoints: approvals | partially_implemented | approval_router in phases.py has 4 endpoints | Missing: list all, get by id | Add missing endpoints |
| 4.9 | REST endpoints: logs | partially_implemented | log_router in phases.py has 2 endpoints | Missing: create log entry | Add missing endpoints |
| 4.10 | REST endpoints: evidence | partially_implemented | evidence_router in phases.py has 2 endpoints | Missing: create bundle, export | Add missing endpoints |
| 4.11 | REST endpoints: costs | partially_implemented | cost_router in phases.py has 2 endpoints | Missing: record event | Add missing endpoints |
| 4.12 | REST endpoints: patterns | partially_implemented | pattern_router in phases.py has 2 endpoints | Missing: create, update | Add missing endpoints |
| 4.13 | REST endpoints: memory | partially_implemented | memory_router in phases.py has 2 endpoints | Missing: create, update, delete | Add missing endpoints |
| 4.14 | REST endpoints: GitHub | partially_implemented | github_router in phases.py has 2 endpoints (with bug) | Bug: gmail_router instead of github_router | Fix bug |
| 4.15 | REST endpoints: deployment | partially_implemented | deployment_router in phases.py has 4 endpoints | Missing: rollback | Add missing endpoints |
| 4.16 | REST endpoints: settings | partially_implemented | settings_router in phases.py has 2 endpoints | Missing: delete, bulk update | Add missing endpoints |
| 4.17 | WebSocket for live events | implemented | websocket/run_events.py | None | — |
| 4.18 | OpenAPI docs | implemented | FastAPI auto-generates at /docs | None | — |
| 4.19 | Auth stub | missing | No auth system | Add auth stub | Add auth stub |
| 4.20 | Role model | missing | No roles defined | Define roles | Define roles |
| 4.21 | Audit middleware | implemented | api/middleware/audit.py | None | — |
| 4.22 | Trace ID middleware | implemented | api/middleware/trace.py | None | — |
| 4.23 | Structured JSON logging | implemented | core/logging.py | None | — |
| 5.1 | Postgres | implemented | database.py uses asyncpg | No migrations | Add Alembic |
| 5.2 | Migrations | missing | No Alembic config | Add Alembic | Add Alembic |
| 5.3 | 39 tables | partially_implemented | 29 tables in models.py | Missing: MemoryItem (exists but as alias), RunCheckpoint, ModelCall, ToolCall, SystemSetting (referenced but not defined), McpTool, McpPermission, PolicyResult, FileArtifact, UserCommand | Add missing models |
| 5.4 | Relationships | partially_implemented | Basic relationships in models.py | Missing: req→design, req→code, req→test, req→governance, commit→artifact, deployment→evidence | Add relationships |
| 5.5 | Seed data | missing | No seed script | Create seed script | Create seed script |
| 6.1-6.25 | Specification engine | missing | No spec engine | Build spec engine | Build spec engine |
| 7.1-7.15 | Functional design engine | missing | No FD engine | Build FD engine | Build FD engine |
| 8.1-8.20 | Architecture engine | missing | No arch engine | Build arch engine | Build arch engine |
| 9.1-9.12 | Design proposal engine | missing | No design engine | Build design engine | Build design engine |
| 10.1-10.14 | Data/database engine | missing | No data model engine | Build data model engine | Build data model engine |
| 11.1-11.14 | MCP architecture | missing | No MCP servers directory | Build MCP servers | Build MCP servers |
| 12.1-12.12 | Agent system | missing | Agent model exists, no agent registry service | Build agent registry | Build agent registry |
| 13.1-13.27 | Model router | missing | No model router | Build model router | Build model router |
| 14.1-14.23 | Memory system | partially_implemented | MemoryItem model exists, memory endpoints exist | No Qdrant integration, no Obsidian connector, no Omi connector | Build memory connectors |
| 15.1-15.17 | Workflow orchestration | partially_implemented | sdlc_graph.py has all 28 nodes, all are stubs | No real logic in any node | Implement node logic |
| 16.1-16.15 | Backlog generation | missing | No backlog engine | Build backlog engine | Build backlog engine |
| 17.1-17.22 | Build execution | missing | No build execution | Build execution engine | Build execution engine |
| 18.1-18.17 | GitHub integration | partially_implemented | GitHub endpoints exist (with bug), no actual adapter | Build GitHub adapter | Build GitHub adapter |
| 19.1-19.18 | Test system | missing | No test runner | Build test runner | Build test runner |
| 20.1-20.17 | Security system | missing | No security runner | Build security runner | Build security runner |
| 21.1-21.10 | Governance system | missing | No OPA policies, no governance engine | Build governance engine | Build governance engine |
| 22.1-22.12 | Technical debt checks | missing | No debt scanner | Build debt scanner | Build debt scanner |
| 23.1-23.15 | Refactor loop | partially_implemented | refactor_graph.py exists, all stubs | No actual refactor logic | Implement refactor logic |
| 24.1-24.8.7 | Evidence system | partially_implemented | evidence_graph.py + DB table, all stubs | No actual evidence engine | Build evidence engine |
| 25.1-25.20 | Cost ledger | partially_implemented | CostEvent model + CostService + cost endpoints | No model router integration, no CSV export | Build cost ledger |
| 26.1-26.13 | Pattern library | partially_implemented | Pattern model + pattern endpoints | No pattern extraction logic | Build pattern library |
| 27.1-27.19 | Logging/downloads | partially_implemented | LogEvent model + LogService + log endpoints | No file-based logging, no download bundles | Build log exporter |
| 28.1-28.18 | Localhost deployment | partially_implemented | deployment_graph.py, all stubs | No actual deployment logic | Build deployment runner |
| 29.1-29.15 | Observability | partially_implemented | Prometheus metrics exist | No OpenTelemetry instrumentation, no Grafana dashboards | Add OTel + dashboards |
| 30.1-30.6 | Configuration | implemented | .env.example + config.py | None | — |
| 31.1-31.16 | Docker Compose | missing | No docker-compose.yml | Create docker-compose.yml | Create docker-compose.yml |
| 32.1-32.9 | User approval model | partially_implemented | Approval model + endpoints exist | No UI for approval | Build approval UI |
| 33.1-33.13 | Demo app (demo-mcp-task-manager) | missing | No generated-projects/ dir | Build demo app | Build demo app |
| 34.1-34.13 | Quality bar | broken | Cannot run — missing deps, no docker-compose, no frontend | Fix all blockers | Fix all blockers |
| 35.1-35.13 | Self-check | missing | No self-check system | Build self-check | Build self-check |
| 36.1-36.12 | Commands | missing | No scripts/ dir | Create scripts | Create scripts |
| 37.1-37.15 | Final output format | missing | No final report | Generate after build | Generate after build |
| 38.1-38.20 | Non-negotiables | partially_implemented | Backend core exists | Most of system missing | Continue building |
