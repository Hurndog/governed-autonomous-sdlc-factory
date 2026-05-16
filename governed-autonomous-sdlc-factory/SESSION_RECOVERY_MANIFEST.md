# SESSION RECOVERY MANIFEST
**Generated:** 2026-05-14 09:15
**Version:** 2.0.0

## Repository
- **Path:** `/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
- **Branch:** main
- **Latest commit:** `6355969` (runtime validation + benchmarks)
- **Total commits:** 9

## Runtime Ports
| Service | Port | Status |
|---------|------|--------|
| FastAPI | 8000 | ✅ |
| Next.js Frontend | 3000 | ✅ |
| PostgreSQL | 5432 | ✅ |
| Redis | 6379 | ✅ |
| Ollama | 11434 | ✅ (3 models) |
| LM Studio | 1234 | ✅ (Gemma 4 E4B) |

## Active Models
| Provider | Model | Role | Status |
|----------|-------|------|--------|
| LM Studio | google/gemma-4-e4b | Primary (arch, gov, spec, code) | ✅ Online |
| Ollama | gpt-oss:20b | Fallback (heavy reasoning) | ✅ Online |
| Ollama | qwen2.5:1.5b | Utility | ✅ Online |
| Ollama | phi3:mini | Lightweight | ✅ Online |
| LM Studio | nomic-embed-text-v1.5 | Embeddings | ✅ Online |

## Model Router Policy v2
- **Primary:** Gemma 4 E4B (LM Studio) — architecture, governance, spec, code
- **Fallback:** gpt-oss:20b (Ollama) — heavy reasoning, direct JSON
- **Utility:** qwen2.5:1.5b (Ollama) — classification, metadata
- **Lightweight:** phi3:mini (Ollama) — background checks
- **Embeddings:** nomic-embed-text-v1.5 (LM Studio)

## Golden Pipeline (Gemma 4 E4B)
- **Run ID:** 43dafe8e-0a6b-448e-bc1a-3ec9dd20b221
- **Project:** gemma4-golden-pipeline
- **Duration:** 216,333ms (3.6 min)
- **Status:** COMPLETED
- **Results:**
  - Spec: 6 FR, 4 NFR
  - Architecture: 7 components, 2 ADRs, Mermaid diagram
  - Governance: 5 concerns, 2 security findings
  - Tests: 6 test cases, 3 edge cases
  - 12 artifacts total
- **Integrity:** Event chain 1.0, Snapshot 1.0, Overall 0.4286
- **Replay:** 24 events, 12 artifacts, chain continuity VALID

## Blockers
1. **GitHub Token** — Need PAT to push
2. **Artifact integrity** — Hash mismatch (needs investigation)
3. **Replay divergences** — 36 divergences (timing-related, non-critical)

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

# Terminal 5: LM Studio
open -a "LM Studio"  # Then activate Local Server via GUI
```

## Recovery Instructions
1. `cd /Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory`
2. `git checkout main`
3. `docker compose up -d`
4. `cd apps/api && source .venv/bin/activate && uvicorn src.main:app --reload --port 8000 &`
5. `cd apps/web && pnpm dev &`
6. `ollama serve &`
7. `open -a "LM Studio"` → Activate Local Server
8. Open http://localhost:3000

## Next Priorities
1. GitHub push (needs token)
2. Fix artifact integrity hash computation
3. Investigate replay divergences
4. Add JSON extraction for Gemma markdown-wrapped output
5. Implement WebSocket event streaming to frontend
