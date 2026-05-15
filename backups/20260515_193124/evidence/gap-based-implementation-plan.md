# Gap-Based Implementation Plan

Ordered by dependency. Each task must be completed and validated before moving to the next.

---

## Phase 0: Make Repository Runnable

### Task 0.1: Fix Critical Bugs
- **Dependency:** None
- **Files to edit:** `apps/api/src/api/v1/endpoints/phases.py` (lines 391, 401)
- **Expected output:** `gmail_router` → `github_router`
- **Validation:** `PYTHONPATH=apps/api python3 -c "from src.main import app; print('OK')"`
- **Done criteria:** Main imports without errors

### Task 0.2: Fix Missing Model References
- **Dependency:** 0.1
- **Files to edit:** `apps/api/src/models.py`
- **Expected output:** Add missing models: SystemSetting, RunCheckpoint, ModelCall, ToolCall, McpTool, McpPermission, PolicyResult, FileArtifact, UserCommand
- **Validation:** `python3 -c "from apps.api.src.models import SystemSetting, RunCheckpoint, ModelCall, ToolCall; print('OK')"`
- **Done criteria:** All referenced models exist

### Task 0.3: Fix Router Imports
- **Dependency:** 0.2
- **Files to edit:** `apps/api/src/api/v1/router.py`, create separate endpoint files
- **Expected output:** Each router import resolves to a separate module file
- **Validation:** Router imports cleanly
- **Done criteria:** All 12 router imports resolve

### Task 0.4: Create Directory Structure
- **Dependency:** None
- **Files to create:** All missing directories per section 2.1
- **Expected output:** Full monorepo structure
- **Validation:** `ls` confirms all dirs exist
- **Done criteria:** All required directories present

### Task 0.5: Initialize Git Repository
- **Dependency:** None
- **Files to create:** `.gitignore`, initial commit
- **Expected output:** Git repo with all existing code committed
- **Validation:** `git log --oneline` shows commits
- **Done criteria:** Git initialized, initial commit done

---

## Phase 1: Make Backend API Runnable

### Task 1.1: Create docker-compose.yml
- **Dependency:** 0.4
- **Files to create:** `docker-compose.yml`
- **Expected output:** Postgres, Redis, Qdrant services defined
- **Validation:** `docker compose config` succeeds
- **Done criteria:** All infrastructure services defined

### Task 1.2: Add Alembic Migrations
- **Dependency:** 0.2
- **Files to create:** `alembic/`, `alembic.ini`
- **Expected output:** Migration for all tables
- **Validation:** `alembic upgrade head` succeeds (with running Postgres)
- **Done criteria:** Schema can be created from migrations

### Task 1.3: Create .env for Local Development
- **Dependency:** 1.1
- **Files to create:** `.env`
- **Expected output:** Local development environment configured
- **Validation:** Settings load without errors
- **Done criteria:** Backend can read config

### Task 1.4: Verify API Starts
- **Dependency:** 1.1, 1.2, 1.3
- **Expected output:** `uvicorn src.main:app` starts on port 8000
- **Validation:** `curl http://localhost:8000/health` returns 200
- **Done criteria:** Health endpoint responds

---

## Phase 2: Make UI Load

### Task 2.1: Create Next.js Frontend
- **Dependency:** 0.4
- **Files to create:** `apps/web/` — full Next.js app
- **Expected output:** `npm run dev` starts on port 3000
- **Validation:** Browser loads http://localhost:3000
- **Done criteria:** Frontend loads

### Task 2.2: Implement Three-Panel Layout
- **Dependency:** 2.1
- **Files to edit:** Layout components
- **Expected output:** Left (AI), Center (Workspace), Right (Inspector) panels
- **Validation:** Visual confirmation
- **Done criteria:** Layout renders

### Task 2.3: Implement Top Bar
- **Dependency:** 2.2
- **Files to create:** Top bar component
- **Expected output:** Project/run/phase/branch/cost/model info displayed
- **Validation:** Visual confirmation
- **Done criteria:** Top bar renders

### Task 2.4: Implement All 19 Screens
- **Dependency:** 2.2
- **Files to create:** All screen components
- **Expected output:** All screens accessible via navigation
- **Validation:** Each screen loads without errors
- **Done criteria:** All screens functional

---

## Phase 3: Make Live Events Work

### Task 3.1: Connect WebSocket to Frontend
- **Dependency:** 2.1, 1.4
- **Files to create:** WebSocket client in frontend
- **Expected output:** Live run events appear in UI
- **Validation:** Create a run, see events in UI
- **Done criteria:** WebSocket connected, events flowing

---

## Phase 4: Make Core Workflow Runnable

### Task 4.1: Implement Model Router
- **Dependency:** 1.4
- **Files to create:** `packages/local-model-router/`
- **Expected output:** LM Studio adapter working, fallback to Claude
- **Validation:** Model router can make a test call
- **Done criteria:** At least one model provider works

### Task 4.2: Implement Specification Engine
- **Dependency:** 4.1
- **Files to create:** `packages/spec-engine/`
- **Expected output:** Idea text → requirements.yaml + functional_spec.md + acceptance_criteria.yaml
- **Validation:** Generate specs for a test idea
- **Done criteria:** Spec files generated with proper labeling

### Task 4.3: Implement Functional Design Engine
- **Dependency:** 4.1
- **Files to create:** `packages/design-engine/`
- **Expected output:** Specs → functional_design.md
- **Validation:** Generate FD from test specs
- **Done criteria:** FD document generated

### Task 4.4: Implement Architecture Engine
- **Dependency:** 4.1
- **Files to create:** `packages/architecture-engine/`
- **Expected output:** Specs → architecture.md + Mermaid diagrams + ADRs
- **Validation:** Generate architecture from test specs
- **Done criteria:** Architecture docs generated

### Task 4.5: Implement Governance Engine
- **Dependency:** 4.1
- **Files to create:** `packages/governance-engine/`, `policies/opa/`
- **Expected output:** 15 OPA Rego policies, governance-report.json
- **Validation:** Run governance checks on test data
- **Done criteria:** Policies evaluate, report generated

### Task 4.6: Implement Build Execution
- **Dependency:** 4.1, 4.2-4.4
- **Files to create:** Build execution service
- **Output:** Generated code files in generated-projects/
- **Validation:** Generate a simple app
- **Done criteria:** Code files created

### Task 4.7: Implement Test Runner
- **Dependency:** 4.6
- **Files to create:** `packages/test-runner/`
- **Output:** Test results stored in DB
- **Validation:** Run tests on generated code
- **Done criteria:** Tests execute, results stored

### Task 4.8: Implement Security Runner
- **Dependency:** 4.6
- **Files to create:** `packages/security-runner/`
- **Output:** security-report.json
- **Validation:** Run security scan on generated code
- **Done criteria:** Security findings recorded

### Task 4.9: Implement Evidence Engine
- **Dependency:** 4.2-4.8
- **Files to create:** `packages/evidence-engine/` (real implementation)
- **Output:** evidence-bundle.zip with all 15 trace files
- **Validation:** Generate evidence for a test run
- **Done criteria:** Complete evidence bundle

### Task 4.10: Implement Cost Ledger
- **Dependency:** 4.1
- **Files to create:** `packages/cost-ledger/` (real implementation)
- **Output:** cost-ledger.csv, cost-ledger.json, cost-report.md
- **Validation:** Cost tracking works end-to-end
- **Done criteria:** Cost reports generated

### Task 4.11: Implement Pattern Library
- **Dependency:** 4.9
- **Files to create:** `packages/pattern-library/` (real implementation)
- **Output:** Patterns extracted and stored
- **Validation:** Extract patterns from a completed run
- **Done criteria:** Patterns stored in DB

### Task 4.12: Implement Memory System
- **Dependency:** 1.4
- **Files to create:** `packages/memory-service/`, `packages/obsidian-connector/`, `packages/omi-connector/`
- **Output:** Memory search working, Obsidian connector, Omi connector abstraction
- **Validation:** Search memories, write to Obsidian
- **Done criteria:** Memory system functional

### Task 4.13: Implement Deployment Runner
- **Dependency:** 4.6
- **Files to create:** `packages/deployment-runner/`
- **Output:** Generated app deployed to localhost via Docker Compose
- **Validation:** Deploy demo app, health check passes
- **Done criteria:** App accessible at localhost URL

### Task 4.14: Implement GitHub Adapter
- **Dependency:** 4.6
- **Files to create:** `packages/github-adapter/`
- **Output:** Code committed to local git (or GitHub if creds available)
- **Validation:** Git log shows commits
- **Done criteria:** Git integration working

### Task 4.15: Implement AI Command Assistant
- **Dependency:** 2.4, 4.2-4.14
- **Files to create:** Chat UI + command parser + backend handlers
- **Output:** All 25 slash commands working
- **Validation:** Test each command
- **Done criteria:** All commands functional

---

## Phase 5: Demo App End-to-End

### Task 5.1: Generate demo-mcp-task-manager
- **Dependency:** All of Phase 4
- **Files to create:** Full demo app under generated-projects/demo-mcp-task-manager/
- **Output:** Complete app with DB, API, frontend, MCP, tests, docs, Docker Compose
- **Validation:** App deploys and runs at localhost
- **Done criteria:** Demo app fully functional

### Task 5.2: Generate Evidence Bundle for Demo
- **Dependency:** 5.1
- **Output:** Complete evidence bundle for demo run
- **Validation:** All 15 trace files present
- **Done criteria:** Evidence bundle complete

---

## Phase 6: Self-Check and Documentation

### Task 6.1: Run Full Self-Check
- **Dependency:** All above
- **Output:** evidence/system-completion-checklist.json updated
- **Validation:** All requirements checked
- **Done criteria:** Checklist complete

### Task 6.2: Generate Completion Report
- **Dependency:** 6.1
- **Output:** evidence/system-completion-report.md
- **Validation:** Report covers all 293 requirements
- **Done criteria:** Report generated

### Task 6.3: Update README
- **Dependency:** 6.2
- **Output:** README.md with exact commands, URLs, log locations
- **Validation:** README is accurate
- **Done criteria:** README complete

### Task 6.4: Create Operations Docs
- **Dependency:** 6.2
- **Output:** docs/operations/runbook.md, known-limitations.md, next-hardening-steps.md
- **Validation:** Docs exist and are accurate
- **Done criteria:** Operations docs complete

### Task 6.5: Create User Guide
- **Dependency:** 5.2
- **Output:** docs/user-guide/control-tower-user-guide.md
- **Validation:** Guide covers all UI screens
- **Done criteria:** User guide complete

### Task 6.6: Create Architecture Docs
- **Dependency:** 6.2
- **Output:** All 8 architecture docs (2.3-2.10)
- **Validation:** Docs exist
- **Done criteria:** Architecture docs complete

### Task 6.7: Final Git Commit
- **Dependency:** All above
- **Output:** Clean git history with meaningful commits
- **Validation:** `git log` shows all work
- **Done criteria:** All work committed
