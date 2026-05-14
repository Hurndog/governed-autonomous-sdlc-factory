# Governed Autonomous SDLC Factory

## Forge Control Tower — UI-Operated Autonomous Software Factory

A governed, autonomous SDLC runtime that transforms natural language software ideas into
complete, tested, documented, and deployed applications — with full observability,
governance controls, evidence bundles, cost tracking, and MCP-based tool abstraction.

### Quick Start

```bash
# 1. Clone and enter
cd governed-autonomous-sdlc-factory

# 2. Copy environment
cp .env.example .env

# 3. Launch infrastructure
docker-compose up -d postgres redis qdrant

# 4. Run migrations
cd apps/api && python -m alembic upgrade head

# 5. Seed demo data
python -m scripts.seed_demo

# 6. Start backend
python -m uvicorn src.main:app --reload --port 8000

# 7. Start frontend (new terminal)
cd apps/web && npm install && npm run dev

# 8. Open Control Tower
open http://localhost:3000
```

### Architecture

- **Frontend**: Next.js + React + Tailwind + shadcn/ui (Forge Control Tower)
- **Backend**: FastAPI + Pydantic + SQLAlchemy
- **Workflow**: LangGraph orchestration
- **Database**: PostgreSQL
- **Queue**: Redis
- **Vector Memory**: Qdrant
- **Governance**: OPA Rego policies
- **Tool Protocol**: MCP servers for all tool access
- **Observability**: OpenTelemetry + Prometheus + Loki-compatible logs
- **Deployment**: Docker Compose localhost

### Key URLs

| Service | URL |
|---------|-----|
| Forge Control Tower (UI) | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs (OpenAPI) | http://localhost:8000/docs |
| Prometheus | http://localhost:9000 |
| Grafana | http://localhost:3001 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

### Logs

- Build log: `logs/overnight-build-log.md`
- Run logs: `logs/runs/<run-id>/run-log.jsonl`
- Agent traces: `logs/runs/<run-id>/agent-traces.jsonl`
- Tool calls: `logs/runs/<run-id>/tool-calls.jsonl`
- Model calls: `logs/runs/<run-id>/model-calls.jsonl`

### Evidence

- Completion checklist: `evidence/system-completion-checklist.json`
- Completion report: `evidence/system-completion-report.md`
- Run evidence bundles: `evidence/runs/<run-id>/evidence-bundle.zip`

### Demo

See `docs/user-guide/control-tower-user-guide.md` for full demo walkthrough.

### Requirements Completion

See `evidence/system-completion-report.md` for the full requirement-by-requirement status table.
