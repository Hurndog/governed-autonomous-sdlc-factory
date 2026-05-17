# Phase 1 — Baseline Verification Report

**Date**: 2026-05-17

## Repository

| Item | Value |
|---|---|
| Path | `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory` |
| Branch | `main` |
| Local HEAD | `38d8b4b` — "Complete GitHub recovery and remote parity verification" |
| Remote URL | `https://github.com/Hurndog/governed-autonomous-sdlc-factory.git` |
| Remote HEAD | `38d8b4bbbc3857657d038b0c207b78422c7393f5` |
| Local == Remote | ✅ YES |
| Working tree | ⚠️ NOT CLEAN — staged backup files + unstaged engine/test changes |

## Backend

| Item | Value |
|---|---|
| Database | ✅ PostgreSQL connected |
| API routes | 117 total |
| Semantic coverage routes | 12 (`/api/v1/semantic-coverage/...`) |
| Test suite | ✅ 70/70 passing |
| Redis | ❌ Not installed (`redis-cli` not found) |

## Model Runtime

| Item | Value |
|---|---|
| Ollama | ✅ Running — phi3:mini, qwen2.5:1.5b, gpt-oss:20b |
| LM Studio | ✅ Running — models available at :1234 |

## Frontend

| Item | Value |
|---|---|
| Build | ❌ No `.next` directory — not built in this session |
| Types | ✅ Semantic coverage types in `apps/web/src/lib/types.ts` |
| API client | ✅ Semantic coverage methods in `apps/web/src/lib/api.ts` |

## Backup

| Item | Value |
|---|---|
| Latest backup | `backups/20260516_074806/` |
| Has manifest | ❌ No `manifest.json` (has `SESSION_RECOVERY_MANIFEST.md` instead) |
| Has checksums | ✅ `checksums.sha256` |
| Has restore instructions | ✅ `RESTORE.md` |
| Has DB dump | ✅ `db.sql.gz` |
| Has repo bundle | ✅ `repo.bundle` |

## Golden Run

| Item | Value |
|---|---|
| ID | `6a7f7ea0-297f-435e-9bb2-899368c7d332` |
| Name | "Pipeline Run: Traceability Governance Validation" |
| Status | `completed` |
| Semantic coverage | ✅ Persisted (score: 0.6772) |

## Immediate Blockers

1. **Working tree not clean** — unstaged changes to engine + test files from previous session need commit
2. **Frontend not built** — needs `npm run build` (non-blocking for backend truth test)
3. **Redis not installed** — non-blocking (system uses PostgreSQL + sync runtime)

## Verdict

✅ Baseline is solid enough to proceed with forensic testing.
