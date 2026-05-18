# Environment Operationalization Report
**Date:** 2026-05-14
**Status:** ✅ COMPLETE (except GitHub — requires token)

## Discovery Results

### Local Models (Ollama)
| Model | Size | Context | Quant | Role |
|-------|------|---------|-------|------|
| gpt-oss:20b | 13.8GB | 131K | MXFP4 | Architecture, Governance, Spec |
| qwen2.5:1.5b | 986MB | 32K | Q4_K_M | Utility, Classification |
| phi3:mini | 2.2GB | 4K | Q4_0 | Lightweight tasks |

### Providers
| Provider | Status | Models | Endpoint |
|----------|--------|--------|----------|
| Ollama | ✅ Online | 3 | localhost:11434 |
| LM Studio | ❌ Server off | Unknown | localhost:1234 |
| OpenAI | ❌ No key | 0 | api.openai.com |
| Anthropic | ❌ No key | 0 | api.anthropic.com |

### Infrastructure
| Component | Status | Port |
|-----------|--------|------|
| FastAPI | ✅ Running | 8000 |
| Next.js Frontend | ✅ Running | 3000 |
| PostgreSQL | ✅ Running | 5432 |
| Redis | ✅ Running | 6379 |
| Docker | ✅ Running | — |

## Golden Baseline Run
- **Model:** Ollama gpt-oss:20b
- **Task:** Specification generation
- **Result:** 7 functional requirements, 3 non-functional, 7 acceptance criteria, 2 governance areas
- **Tokens:** 2,344
- **Cost:** $0.00 (local inference)
- **Latency:** 42s
- **Errors:** 0

## Frontend
- **Framework:** Next.js 14 + TypeScript strict
- **State:** Zustand
- **Styling:** Tailwind + shadcn/ui patterns
- **Rooms:** 5 (Command Center, Spec Room, Architecture Room, Governance Room, Replay Chamber)
- **Build:** 20.7KB First Load JS
- **Status:** ✅ Live at http://localhost:3000

## Blockers
1. **GitHub Token** — Requires user PAT
2. **LM Studio Server** — Requires manual GUI activation
3. **OpenAI/Anthropic Keys** — Optional cloud fallback
