# Runtime Operational Status

**Date:** 2026-05-15

## API Status

**Status:** operational
**Port:** 8000
**Routes:** 109
**Health Check:** `{"status":"ok","version":"1.0.0","database":"connected","redis":"connected"}`

## Infrastructure Status

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| Postgres | operational | 5432 | 57 tables |
| Redis | operational | 6379 | |
| Qdrant | configured | 6333 | Not tested |
| API | operational | 8000 | 109 routes |
| Web | **missing** | 3000 | No source files |
| Prometheus | configured | 9090 | Not wired |
| Grafana | configured | 3001 | No dashboards |
| Loki | configured | 3100 | Not wired |

## Component Status Matrix

### Core
| Component | Status |
|-----------|--------|
| Config | operational |
| Database (async) | operational |
| Database (sync) | operational |
| Logging | operational |
| Auth | **missing** |
| Event Bus | partially_operational |
| Hashing | operational |
| Hash Propagation | partially_operational |
| Integrity | partially_operational |
| Normalization | operational |
| Observability | operational |

### Engines
| Component | Status |
|-----------|--------|
| Replay Sync | partially_operational (FK bug) |
| Replay Transaction Manager | operational |
| Replay Async (old) | stale/orphaned |
| Governance | partially_implemented |
| Snapshots | partially_operational |
| Traceability | partially_operational |
| Divergence | partially_operational |
| Specification | stub |
| Architecture | stub |
| Test | stub |

### Services
| Component | Status |
|-----------|--------|
| Artifact Store | partially_operational |
| Full Pipeline Orchestrator | stub |
| Phase Service | partially_operational |
| Project Service | operational |
| Run Orchestrator | stub |
| Run Service | operational |

### Workflows
| Component | Status |
|-----------|--------|
| SDLC Graph | stub (28 nodes, all stubs) |
| Evidence Graph | stub |
| Refactor Graph | stub |
| Deployment Graph | stub |

### Routes (18 routers)
| Router | Status |
|--------|--------|
| projects | operational |
| runs | operational |
| phases | partially_operational |
| agents | partially_operational |
| tasks | partially_operational |
| artifacts | partially_operational |
| approvals | partially_operational |
| logs | partially_operational |
| evidence | partially_operational |
| costs | partially_operational |
| patterns | partially_operational |
| memory | partially_operational |
| github | **broken** |
| deployment | partially_operational |
| settings | partially_operational |
| engines | operational |
| pipeline | partially_operational |
| websocket | operational |

## Known Bugs

1. **Replay FK violation** — `session.flush()` bypasses txn manager in reconstruct phase
2. **GitHub router typo** — `gmail_router` instead of `github_router` in github.py
3. **No hash propagation on new runs** — Hash functions exist but aren't called during pipeline execution

## What Can Be Demonstrated

1. API boots and responds to health checks
2. All 109 routes are registered and accessible
3. Database has 57 tables with proper schema
4. Hashing functions produce deterministic results
5. Integrity verification produces scores (low for legacy, would be high for hashed runs)
6. Replay endpoint accepts requests (but hits FK bug)
7. WebSocket endpoint is registered
8. OpenAPI docs are auto-generated at /docs

## What Cannot Be Demonstrated

1. End-to-end pipeline execution (all workflow nodes are stubs)
2. Frontend UI (no files exist)
3. AI-powered generation (no model router)
4. Replay execution (FK bug)
5. Hash chain continuity (no hashes on any runs)
6. Evidence generation (stub)
7. Deployment (stub)
8. Testing (stub)
9. Security scanning (stub)
10. GitHub integration (broken)
