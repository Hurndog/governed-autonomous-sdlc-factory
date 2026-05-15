# SESSION RECOVERY MANIFEST
**Generated:** 2026-05-14 08:15
**Version:** 1.0.0

## Repository
- **Path:** `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
- **Branch:** main
- **Latest commits:**
  - `24ef63a` — feat(ops): GitHub setup script + environment reports
  - `21648a0` — feat(frontend): Cognitive Command Center — 5 rooms + WebSocket + dark ops UI
  - `8a86dc1` — feat(operationalization): Ollama integration + startup diagnostics + golden baseline
  - `3852c47` — feat(cognitive): model router + real AI execution engines
  - `8b82c1a` — feat(forensic): sync replay runtime + transaction manager

## Runtime Ports
| Service | Port | Status |
|---------|------|--------|
| FastAPI | 8000 | ✅ |
| Next.js Frontend | 3000 | ✅ |
| PostgreSQL | 5432 | ✅ |
| Redis | 6379 | ✅ |
| Ollama | 11434 | ✅ |
| LM Studio | 1234 | ❌ Server off |

## Active Branches
- main (HEAD)
- develop
- recovery/baseline
- replay/hardening

## Tags
- first-operational-slice
- replay-runtime-stable
- cognitive-execution-enabled
- first-real-spec-generation
- frontend-command-center

## Runtime State
- **API:** Running (PID ~29011), 114 routes
- **Frontend:** Running (Next.js dev server)
- **Database:** 57 tables, including inference_traces, model_configs
- **Replay:** Stable, integrity score 1.0
- **Models:** 3 Ollama models (gpt-oss:20b, qwen2.5:1.5b, phi3:mini)

## Blockers
1. **GitHub Token** — Need PAT to push
2. **LM Studio Server** — Manual GUI activation required
3. **OpenAI/Anthropic Keys** — Optional cloud fallback

## Startup Commands
```bash
# Terminal 1: Database
docker compose up -d postgres redis

# Terminal 2: API
cd apps/api && source .venv/bin/activate && uvicorn src.main:app --reload --port 8000

# Terminal 3: Frontend
cd apps/web && pnpm dev

# Terminal 4: Ollama (if not running)
ollama serve
```

## Recovery Instructions
1. `cd /Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
2. `git checkout main`
3. `docker compose up -d`
4. `cd apps/api && source .venv/bin/activate && uvicorn src.main:app --reload --port 8000 &`
5. `cd apps/web && pnpm dev &`
6. Open http://localhost:3000

## Next Priorities
1. GitHub push (needs token)
2. LM Studio server activation
3. Full autonomous pipeline execution
4. Autonomous code generation
5. WebSocket event streaming from API to frontend
