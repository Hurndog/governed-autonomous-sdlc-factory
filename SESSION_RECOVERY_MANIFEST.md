# SESSION_RECOVERY_MANIFEST.md

**Last Updated:** 2026-05-15T19:30:00+00:00
**Commit:** 3852c47
**Branch:** main

## Repository

- **Path:** `/Users/marcovanhurne/governed-autonomous-sdlc-factory`
- **Branch:** main
- **Commits:** 5 (3852c47, 8b82c1a, 2016f4b, 1a26ef7, 02d7486)
- **Remote:** NOT CONFIGURED (needs GITHUB_TOKEN)
- **Git User:** Hurndog <150154045+Hurndog@users.noreply.github.com>

## Runtime Ports

| Port | Service | Status |
|------|---------|--------|
| 5432 | Postgres (Docker) | ✅ healthy |
| 6379 | Redis (Docker) | ✅ healthy |
| 6333 | Qdrant (Docker) | ⚠️ unhealthy |
| 11434 | Ollama | ✅ running |
| 1234 | LM Studio | ❌ server disabled |
| 8000 | API (FastAPI) | ✅ starts successfully (114 routes) |
| 3000 | Frontend (Next.js) | ❌ not started |

## Infrastructure

- **Docker:** 29.4.3 — running
- **Python:** 3.11.15 (hermes-agent venv)
- **Node:** 22.22.2
- **pnpm:** 11.0.9
- **Git:** 2.50.1
- **Ollama:** 0.23.4 — running with 3 models
- **LM Studio:** installed, server disabled

## Ollama Models

| Model | Size | Context | Reasoning | Priority |
|-------|------|---------|-----------|----------|
| gpt-oss:20b | 13.8GB | 131072 | ✅ | 100 |
| qwen2.5:1.5b | 1.0GB | 32768 | ✅ | 50 |
| phi3:mini | 2.2GB | 4096 | ❌ | 25 |

## Model Router

- **Default Provider:** ollama
- **Default Model:** gpt-oss:20b
- **Fallback Chain:** ollama:gpt-oss:20b → ollama:qwen2.5:1.5b → lm_studio:local-model → openai:gpt-4o-mini → anthropic:claude-3-5-sonnet
- **Task Routing:**
  - architecture_reasoning → ollama:gpt-oss:20b
  - governance_reasoning → ollama:gpt-oss:20b
  - code_generation → ollama:gpt-oss:20b
  - specification_generation → ollama:gpt-oss:20b
  - test_generation → ollama:gpt-oss:20b
  - utility_tasks → ollama:qwen2.5:1.5b

## API Keys Status

| Key | Status |
|-----|--------|
| OPENAI_API_KEY | ❌ NOT SET |
| ANTHROPIC_API_KEY | ❌ NOT SET |
| GITHUB_TOKEN | ❌ NOT SET |
| MEM0_API_KEY | ✅ present |
| TWILIO_AUTH_TOKEN | ✅ present |

## Startup Commands

```bash
# Start infrastructure
cd /Users/marcovanhurne/governed-autonomous-sdlc-factory
docker compose up -d postgres redis qdrant

# Start API
cd governed-autonomous-sdlc-factory/apps/api
/Users/marcovanhurne/.hermes/hermes-agent/venv/bin/python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Start frontend (when ready)
cd apps/web
pnpm install && pnpm dev
```

## Recovery Instructions

1. **Repository:** Already on disk at `/Users/marcovanhurne/governed-autonomous-sdlc-factory`
2. **Database:** `docker compose up -d postgres` — data persisted in Docker volume
3. **Ollama models:** Already downloaded, will be auto-detected
4. **API keys:** Need to be set in `.env` file for OpenAI/Anthropic
5. **GitHub:** Run `scripts/github-setup.sh` after setting GITHUB_TOKEN

## Blockers

1. **GitHub remote not configured** — needs GITHUB_TOKEN
2. **LM Studio server disabled** — needs GUI interaction to enable
3. **No OpenAI/Anthropic API keys** — remote LLM inference unavailable
4. **Frontend not built** — only package.json exists
5. **Qdrant unhealthy** — memory service may not work

## Next Priorities

1. Configure GitHub remote (needs token from user)
2. Test cognitive endpoints with Ollama
3. Execute golden baseline run
4. Build frontend foundation
5. Enable LM Studio server (needs GUI)

## Backup

- **Script:** `scripts/backup.sh`
- **Location:** `backups/YYYYMMDD_HHMMSS/`
- **Last Backup:** 20260515_193124 (2.4M)
- **Contains:** git bundle, database dump, evidence, runtime manifests, config files

## Cognitive Execution Status

- **Replay Runtime:** ✅ operational (integrity score 1.0)
- **Integrity System:** ✅ operational
- **Model Router:** ✅ operational (Ollama integrated)
- **Specification Engine:** ✅ code complete
- **Architecture Engine:** ✅ code complete
- **Test Plan Engine:** ✅ code complete
- **Governance Engine:** ✅ code complete
- **Pipeline Orchestrator:** ✅ rewritten with real AI engines
- **Cognitive API Endpoints:** ✅ 5 endpoints at `/api/v1/cognitive/`
- **Total Routes:** 114
