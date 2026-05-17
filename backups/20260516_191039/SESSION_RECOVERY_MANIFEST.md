# SESSION_RECOVERY_MANIFEST.md

**Last Updated:** 2026-05-16T18:30:00+00:00
**Commit:** cbb52b9
**Tag:** v0.1.0-golden-integrity-runtime
**Branch:** main

## Repository

- **Path:** `/Users/marcovanhurne/governed-autonomous-sdlc-factory`
- **Branch:** main
- **HEAD:** cbb52b9 (Stabilize backups and GitHub recovery workflow)
- **Remote:** https://github.com/Hurndog/governed-autonomous-sdlc-factory.git ✅
- **Git User:** Hurndog <150154045+Hurndog@users.noreply.github.com>
- **Working tree:** Clean

## Runtime Ports

| Port | Service | Status |
|------|---------|--------|
| 5432 | PostgreSQL | ✅ connected (via API health) |
| 6379 | Redis | ✅ connected (via API health) |
| 6333 | Qdrant | Configured |
| 11434 | Ollama | ✅ running (3 models) |
| 1234 | LM Studio | ✅ running (2 models) |
| 8000 | API (FastAPI) | ✅ running (health ok) |
| 3000 | Frontend (Next.js) | ✅ running |

## Infrastructure

- **Python:** 3.11.15 (venv at `governed-autonomous-sdlc-factory/apps/api/venv`)
- **Node:** 22.22.2
- **pnpm:** 11.0.9
- **Git:** 2.50.1
- **Ollama:** 0.23.4 — running with 3 models
- **LM Studio:** running with 2 models
- **psycopg2-binary:** installed (for sync database access)

## Model Providers

| Provider | Base URL | Model | Status |
|----------|----------|-------|--------|
| LM Studio | http://localhost:1234/v1 | local-model | ✅ running |
| Ollama | http://localhost:11434 | gpt-oss:20b, qwen2.5:1.5b, phi3:mini | ✅ running |
| Anthropic | — | — | Configured via env |
| OpenAI | — | — | Configured via env |

## API Keys Status

| Key | Status |
|-----|--------|
| OPENAI_API_KEY | ❌ NOT SET |
| ANTHROPIC_API_KEY | ❌ NOT SET |
| GITHUB_TOKEN | ✅ Valid (Hurndog, repo scope) |

## Golden Run

- **Run ID:** `6a7f7ea0-297f-435e-9bb2-899368c7d332`
- **Integrity:** 1.0 (all 6 components pass)
- **Events:** 239
- **Artifacts:** 12 (all hash-verified)
- **Traceability Links:** 215
- **Governance Evaluations:** 10
- **Release Gates:** 1
- **Tests:** 44/44 passing

## Commit Chain (latest 15)

```
cbb52b9 Stabilize backups and GitHub recovery workflow
819a2ae Build cognitive command center control plane
0f14ce6 Fix Pydantic v2 Config deprecation in Settings
f6dd264 Harden integrity verification API with sync runtime
6888ef9 Add traceability and governance persistence to golden pipeline
98299bb Fix artifact metadata sanitization and validate integrity repair
62635da docs: GitHub sync status — token invalid
63e3b64 feat(gemma4): Gemma 4 E4B primary model + golden pipeline + routing policy v2
6355969 feat(runtime): Full autonomous pipeline validation + model benchmarks + backup
fd462fc docs: SESSION_RECOVERY_MANIFEST — full runtime state + recovery instructions
24ef63a feat(ops): GitHub setup script + environment reports
21648a0 feat(frontend): Cognitive Command Center — 5 rooms + WebSocket + dark ops UI
8a86dc1 feat(operationalization): Ollama integration + startup diagnostics + golden baseline
3852c47 feat(cognitive): model router + real AI execution engines
8b82c1a feat(forensic): sync replay runtime + transaction manager + completeness audit
```

## Key Files

| File | Description |
|------|-------------|
| `governed-autonomous-sdlc-factory/apps/api/src/services/full_pipeline_orchestrator.py` | Pipeline lifecycle with integrity persistence |
| `governed-autonomous-sdlc-factory/apps/api/src/services/artifact_store.py` | Sanitized artifact storage |
| `governed-autonomous-sdlc-factory/apps/api/src/core/hashing.py` | Deterministic SHA256 hashing |
| `governed-autonomous-sdlc-factory/apps/api/src/core/config.py` | Pydantic settings (v2 compatible) |
| `governed-autonomous-sdlc-factory/apps/api/src/engines/integrity_runtime_sync.py` | Sync integrity verification runtime |
| `governed-autonomous-sdlc-factory/apps/api/tests/test_artifact_hash_integrity.py` | 44 integrity tests |
| `governed-autonomous-sdlc-factory/apps/web/src/` | Next.js frontend with 10 rooms |

## Startup Commands

```bash
# Start API
cd /Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Start Frontend
cd /Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/web
npm run dev

# Verify
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/pipeline/runs/6a7f7ea0-297f-435e-9bb2-899368c7d332/verify-integrity
```

## Recovery Instructions

1. **Repository:** Already on disk + pushed to GitHub
2. **Database:** PostgreSQL running locally, data persisted
3. **Models:** Ollama + LM Studio running, models auto-detected
4. **API keys:** Set in `.env` file
5. **GitHub:** ✅ Configured — `https://github.com/Hurndog/governed-autonomous-sdlc-factory.git`
6. **Backup:** Latest at `backups/20260516_182041/`

## Blockers

1. **No OpenAI/Anthropic API keys** — remote LLM inference unavailable
2. **No Qdrant** — memory service may not work

## Next Priorities

1. Semantic Coverage and Test Alignment
2. Autonomous code generation with real LLM inference
3. Expand test coverage beyond integrity suite
4. WebSocket live event streaming

## Backup

- **Script:** `scripts/backup.sh` (hardened)
- **Location:** `backups/YYYYMMDD_HHMMSS/`
- **Last Backup:** 20260516_182041 (6.6MB, 36 files)
- **Contains:** git bundle (verified), evidence (26+ files), runtime manifests, config, checksums, RESTORE.md
- **Backup SHA256:** `9647b6fc4f73c3c20d1ae5cf04bfaa14d4654d5129112097798e753d1dd530da` (repo.bundle)
- **Restore tested:** ✅

## GitHub

- **Remote:** https://github.com/Hurndog/governed-autonomous-sdlc-factory.git
- **Parity:** ✅ Local HEAD == Remote HEAD == cbb52b9
- **All commits pushed:** ✅ 15 commits
- **Tags pushed:** ✅ v0.1.0-golden-integrity-runtime

## Operational Status

- **Integrity System:** ✅ API-verified, all components 1.0
- **Sync Runtime:** ✅ `integrity_runtime_sync.py` operational
- **Replay Runtime:** ✅ operational
- **Model Router:** ✅ operational
- **Pipeline Orchestrator:** ✅ operational with full traceability
- **Test Suite:** ✅ 44/44 passing
- **API:** ✅ healthy, all endpoints functional
- **Frontend:** ✅ http://localhost:3000, 10 rooms, build passing
- **GitHub:** ✅ synced with remote parity
