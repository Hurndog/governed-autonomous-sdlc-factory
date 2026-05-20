# Technical Architecture

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Backend Architecture](#2-backend-architecture)
3. [Frontend Architecture](#3-frontend-architecture)
4. [Database Architecture](#4-database-architecture)
5. [Event System](#5-event-system)
6. [Security Architecture](#6-security-architecture)
7. [Model Provider Architecture](#7-model-provider-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Performance Characteristics](#9-performance-characteristics)

---

## 1. System Overview

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | FastAPI | 0.115 | Web framework |
| Backend | Pydantic | 2.9 | Data validation |
| Backend | SQLAlchemy | 2.0.35 | ORM (async) |
| Backend | asyncpg | 0.29 | PostgreSQL driver |
| Backend | Alembic | 1.13 | Migrations |
| Backend | structlog | 24.4 | Structured logging |
| Backend | OpenTelemetry | 1.27 | Observability |
| Backend | httpx | 0.27 | HTTP client |
| Backend | redis | 5.1 | Cache client |
| Frontend | Next.js | 14.2 | React framework |
| Frontend | React | 18.2 | UI library |
| Frontend | TypeScript | 5.3 | Type safety |
| Frontend | Tailwind CSS | 3.4 | Styling |
| Frontend | Zustand | 4.5 | State management |
| Frontend | Recharts | 2.12 | Charts |
| Database | PostgreSQL | 15 | Primary store |
| Cache | Redis | 7 | Cache + queue |
| Vector DB | Qdrant | Latest | Vector memory |
| Metrics | Prometheus | Latest | Metrics |
| Dashboards | Grafana | Latest | Visualization |
| Local LLM | Ollama | Latest | Model serving |
| Container | Docker | 24+ | Containerization |
| Orchestration | Docker Compose | 2.x | Multi-container |

### System Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SYSTEMS                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ OpenAI   │ │ Anthropic│ │ Gemini   │ │ OpenRouter       │  │
│  │ API      │ │ API      │ │ API      │ │ API              │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────────────┘  │
└───────┼────────────┼────────────┼──────────────┼────────────────┘
        │            │            │              │
┌───────▼────────────▼────────────▼──────────────▼────────────────┐
│                     API GATEWAY (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Middleware: Auth → Trace → Audit → CORS                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Endpoints: 27+ modules                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services: Orchestration, Runs, Projects                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Engines: 17+ specialized engines                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Core: Auth, Config, DB, Events, Observability           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
        │            │            │              │
┌───────▼────────────▼────────────▼──────────────▼────────────────┐
│                      DATA LAYER                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ PostgreSQL│ │ Redis    │ │ Qdrant   │ │ Ollama           │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Architecture

### Layered Architecture

The backend follows a strict layered architecture with dependency injection:

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (apps/api/src/api/v1/endpoints/)              │
│  - 27+ endpoint modules                                  │
│  - Request validation (Pydantic)                         │
│  - Response serialization                                │
│  - Permission declarations                               │
│  Dependencies: Services, Core                            │
├─────────────────────────────────────────────────────────┤
│  Service Layer (apps/api/src/services/)                   │
│  - FullPipelineOrchestrator                              │
│  - RunOrchestrator                                       │
│  - RunService, PhaseService, ProjectService              │
│  - ArtifactStore                                         │
│  Dependencies: Engines, Core                             │
├─────────────────────────────────────────────────────────┤
│  Engine Layer (apps/api/src/engines/)                     │
│  - CognitiveModelRouter                                  │
│  - CognitiveArbitrationEngine                            │
│  - DriftControlEngine                                    │
│  - GovernanceEngine                                      │
│  - ReplayEngine                                          │
│  - SemanticCoverageEngine                                │
│  - SpecificationEngine                                   │
│  - ArchitectureEngine                                    │
│  - InferenceTrace                                        │
│  - TraceabilityEngine                                    │
│  - DivergenceEngine                                      │
│  - SourceExtractor                                       │
│  - Snapshots                                             │
│  - ReplayTransactionManager                              │
│  - IntegrityRuntimeSync                                  │
│  - ReplayRuntimeSync                                     │
│  - ModelRegistry                                         │
│  - OllamaProvider                                        │
│  - ModelProviders (unified)                              │
│  - CognitiveGovernance                                   │
│  - TestEngine                                            │
│  Dependencies: Core                                      │
├─────────────────────────────────────────────────────────┤
│  Core Layer (apps/api/src/core/)                          │
│  - auth.py (JWT + RBAC)                                  │
│  - config.py (Pydantic Settings)                         │
│  - database.py (SQLAlchemy async engine)                 │
│  - event_bus.py (internal pub/sub)                       │
│  - observability.py (OpenTelemetry + Prometheus)         │
│  - logging.py (structlog)                                │
│  - hashing.py (SHA-256)                                  │
│  - integrity.py (hash chain verification)                │
│  - normalization.py (response normalization)             │
│  - safety_guards.py (11 guard types)                     │
│  - conflict_detection.py (4 patterns)                    │
│  - hash_propagation.py (artifact hashing)                │
│  - startup_diagnostics.py (health checks)                │
│  - models.py (SQLAlchemy ORM models)                     │
│  - models_semantic_coverage.py                           │
│  Dependencies: None (foundation layer)                   │
├─────────────────────────────────────────────────────────┤
│  Schema Layer (apps/api/src/schemas/)                     │
│  - Pydantic v2 schemas for all API I/O                   │
│  - Input validation                                      │
│  - Output serialization                                  │
│  - Common types (pagination, responses)                  │
├─────────────────────────────────────────────────────────┤
│  WebSocket Layer (apps/api/src/websocket/)                │
│  - run_events.py (WebSocket event broadcasting)          │
│  Dependencies: Core                                      │
└─────────────────────────────────────────────────────────┘
```

### Middleware Stack

Request processing order:

```
Request
  │
  ▼
┌─────────────────────┐
│  CORS Middleware     │  ← Handle cross-origin requests
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Trace Middleware    │  ← Assign trace_id, measure latency
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Audit Middleware    │  ← Log request/response for audit
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Auth Middleware     │  ← Verify JWT, extract user
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Endpoint Handler    │  ← Business logic
└──────────┬──────────┘
           ▼
        Response
```

### Engine Communication Pattern

Engines communicate through the event bus, not directly:

```
Engine A ──publish──▶ Event Bus ──subscribe──▶ Engine B
                         │
                         ▼
                    Database (persist)
                         │
                         ▼
                    SSE Stream (notify frontend)
```

This ensures:
- **Loose coupling**: Engines don't know about each other
- **Testability**: Each engine can be tested in isolation
- **Observability**: All inter-engine communication is visible
- **Replayability**: Events can be replayed to reconstruct state

---

## 3. Frontend Architecture

### Component Architecture

```
src/app/                          ← Next.js App Router
├── layout.tsx                    ← Root layout (auth, theme)
├── page.tsx                      ← Home page (redirect to dashboard)
├── login/page.tsx                ← Login page
└── globals.css                   ← Global styles

src/lib/                          ← Client libraries
├── api.ts                        ← REST API client
├── useApiData.ts                 ← Data fetching hook
├── useWebSocket.ts               ← WebSocket hook
├── authStore.ts                  ← Auth state (Zustand)
├── store.ts                      ← Global state (Zustand)
├── data-source.ts                ← Data source management
├── theme.ts                      ← Theme configuration
├── utils.ts                      ← Utility functions
├── types.ts                      ← TypeScript types
└── mock-data.ts                  ← Demo data

src/components/
├── AuthGuard.tsx                 ← Auth protection wrapper
├── ui/                           ← Shared UI components
│   ├── Badge.tsx
│   ├── Card.tsx
│   ├── DataSourceBadge.tsx
│   ├── GaugeChart.tsx
│   ├── MetricCard.tsx
│   ├── ProgressBar.tsx
│   ├── SectionHeader.tsx
│   ├── Sidebar.tsx
│   ├── StatusChip.tsx
│   └── TopBar.tsx
└── rooms/                        ← Feature rooms (35+)
    ├── CommandCenter.tsx
    ├── OperationsCenter.tsx
    ├── ExplainabilityRoom.tsx
    ├── ModelOperationsCenter.tsx
    ├── OperatorConsole.tsx
    ├── MemoryOperations.tsx
    ├── GovernanceGates.tsx
    ├── ReplayChamber.tsx
    ├── EvidenceCenter.tsx
    ├── ArchitectureRoom.tsx
    ├── SemanticCoverage.tsx
    ├── TraceabilityRoom.tsx
    ├── IntegrityRoom.tsx
    ├── LogsDiagnostics.tsx
    ├── ArtifactExplorer.tsx
    ├── RunControlRoom.tsx
    ├── AgentCommandCenter.tsx
    ├── ExecutiveCockpit.tsx
    ├── ProcessTimeline.tsx
    ├── BuildMap.tsx
    ├── BacklogChecklist.tsx
    ├── UserManagement.tsx
    ├── SettingsProviders.tsx
    ├── Tokenomics.tsx
    ├── SpecRoom.tsx
    ├── RunReplay.tsx
    ├── SDLCNavigator.tsx
    ├── ArchitectureIntelligence.tsx
    └── Dashboard.tsx
```

### State Management

The frontend uses Zustand for state management with the following stores:

```typescript
// Auth Store
interface AuthStore {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

// Data Store
interface DataStore {
  runs: Run[];
  projects: Project[];
  workspaces: Workspace[];
  activeRun: Run | null;
  setActiveRun: (run: Run) => void;
  refreshRuns: () => Promise<void>;
}

// Connection Store
interface ConnectionStore {
  sseConnected: boolean;
  wsConnected: boolean;
  lastEvent: Event | null;
  connectSSE: () => void;
  disconnectSSE: () => void;
}
```

### SSE Integration

The frontend connects to the SSE telemetry stream for real-time updates:

```typescript
// SSE connection management
const connectSSE = () => {
  const eventSource = new EventSource(
    `${API_URL}/api/v1/operations/events/stream`,
    { withCredentials: true }
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update stores based on event type
    handleEvent(data);
  };

  eventSource.onerror = () => {
    // Auto-reconnect with exponential backoff
    setTimeout(connectSSE, Math.min(retryDelay * 2, 30000));
  };
};
```

### API Client

The API client handles all backend communication:

```typescript
class ApiClient {
  private baseUrl: string;
  private token: string | null;

  async request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.json());
    }

    return response.json();
  }

  // Typed endpoints
  getRuns(): Promise<Run[]> { ... }
  startRun(spec: Specification): Promise<Run> { ... }
  pauseRun(runId: string): Promise<void> { ... }
  getExplanation(type: string, targetId: string): Promise<Explanation> { ... }
  // ... 27+ endpoint modules
}
```

---

## 4. Database Architecture

### Schema Organization

The database uses PostgreSQL with 85+ tables organized into domains:

#### Core Domain
- `workspaces` — Top-level organization units
- `projects` — Projects within workspaces
- `users` — User accounts
- `roles` — RBAC roles
- `permissions` — Granular permissions
- `user_roles` — User-role assignments
- `role_permissions` — Role-permission assignments

#### Run Domain
- `runs` — Pipeline execution runs
- `phases` — Phase executions within runs
- `tasks` — Individual tasks within phases
- `agents` — Agent configurations
- `artifacts` — Generated artifacts with SHA-256 hashes

#### Evidence Domain
- `evidence_bundles` — Immutable evidence collections
- `log_events` — Immutable event log with hash chain
- `snapshots` — Run state snapshots
- `hash_chains` — Hash chain verification data

#### Governance Domain
- `governance_policies` — OPA Rego policy definitions
- `trust_scores` — Trust score history
- `operator_interventions` — Intervention records
- `audit_trails` — Audit trail entries

#### Memory Domain
- `memory_versions` — Memory entry versions
- `memory_lifecycle` — Lifecycle state tracking
- `memory_quarantine` — Quarantined memory entries

#### Model Domain
- `model_capabilities` — Model capability profiles
- `routing_decisions` — Routing decision log
- `arbitration_results` — Arbitration result log
- `provider_health` — Provider health status

#### Economic Domain
- `cost_records` — Cost tracking per action
- `token_usage` — Token usage per model call
- `budget_alerts` — Budget threshold alerts

### Key Relationships

```
workspaces (1) ─── (N) projects (1) ─── (N) runs (1) ─── (N) phases
                                              │
                                              ├── (N) tasks
                                              ├── (N) artifacts
                                              ├── (N) log_events
                                              ├── (N) snapshots
                                              ├── (N) evidence_bundles
                                              ├── (N) trust_scores
                                              ├── (N) operator_interventions
                                              └── (N) routing_decisions
```

### Indexing Strategy

Critical indexes for performance:

```sql
-- Run queries
CREATE INDEX idx_runs_project_status ON runs(project_id, status);
CREATE INDEX idx_runs_created_at ON runs(created_at DESC);

-- Event queries
CREATE INDEX idx_log_events_run_type ON log_events(run_id, event_type);
CREATE INDEX idx_log_events_created_at ON log_events(created_at DESC);

-- Artifact queries
CREATE INDEX idx_artifacts_run_phase ON artifacts(run_id, phase_id);
CREATE INDEX idx_artifacts_hash ON artifacts(hash);

-- Trust queries
CREATE INDEX idx_trust_scores_model ON trust_scores(model_id, created_at DESC);

-- Routing queries
CREATE INDEX idx_routing_decisions_run ON routing_decisions(run_id);
```

---

## 5. Event System

### Event Bus Architecture

The internal event bus uses a pub/sub pattern:

```python
class EventBus:
    _subscribers: Dict[str, List[Callable]]

    def subscribe(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        self._subscribers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        # 1. Persist to database
        await self._persist(event)

        # 2. Add to hash chain
        await self._chain(event)

        # 3. Notify internal subscribers
        for handler in self._subscribers.get(event.type, []):
            await handler(event)

        # 4. Broadcast via SSE
        await self._broadcast(event)
```

### Event Types

| Category | Event Types |
|----------|-------------|
| Runtime | `run.started`, `run.completed`, `run.failed`, `phase.started`, `phase.completed`, `phase.failed` |
| Model | `model.selected`, `model.called`, `model.failed`, `model.timed_out` |
| Arbitration | `arbitration.started`, `arbitration.completed`, `arbitration.escalated` |
| Governance | `policy.evaluated`, `trust.updated`, `drift.detected`, `gate.passed`, `gate.blocked` |
| Intervention | `intervention.pause`, `intervention.resume`, `intervention.quarantine`, `intervention.rollback`, `intervention.escalate`, `intervention.throttle`, `intervention.override`, `intervention.terminate` |
| Memory | `memory.created`, `memory.updated`, `memory.aged`, `memory.archived`, `memory.quarantined`, `memory.restored` |
| Evidence | `evidence.captured`, `evidence.bundle.created`, `evidence.verified`, `evidence.tampered` |
| System | `system.startup`, `system.shutdown`, `system.health_check` |

### Hash Chain

Each event is hash-chained to the previous event for tamper detection:

```python
def compute_hash(event: Event, previous_hash: str) -> str:
    data = f"{previous_hash}:{event.type}:{event.timestamp}:{json.dumps(event.payload, sort_keys=True)}"
    return hashlib.sha256(data.encode()).hexdigest()
```

---

## 6. Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client   │────▶│  Auth    │────▶│  User    │
│  Login    │     │  Endpoint│     │  Store   │
└──────────┘◀────└──────────┘     └──────────┘
   access +
   refresh
   token

Token Claims:
{
  "sub": "user-uuid",
  "roles": ["developer", "operator"],
  "permissions": ["project:read", "project:write", ...],
  "workspace_id": "workspace-uuid",
  "exp": 1716120000,
  "iat": 1716119100
}
```

### RBAC Enforcement

```python
# Permission check decorator
def require_permission(permission: str):
    async def dependency(current_user = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {permission}"
            )
        return current_user
    return Depends(dependency)

# Usage
@router.post("/runs/{run_id}/pause")
async def pause_run(
    run_id: str,
    user = require_permission("intervention:pause")
):
    ...
```

### Data Protection

- **At Rest**: AES-256 encryption for sensitive fields (API keys, secrets)
- **In Transit**: TLS 1.3 for all connections
- **In Memory**: No plaintext secrets in logs or error messages
- **In DB**: Passwords hashed with bcrypt, API keys encrypted

---

## 7. Model Provider Architecture

### Provider Abstraction

```
┌─────────────────────────────────────────────────────────┐
│  CognitiveModelRouter                                    │
│  - Receives RoutingRequest                               │
│  - Queries CapabilityRegistry                            │
│  - Scores candidates                                     │
│  - Returns RoutingDecision                               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  BaseModelProvider (abstract)                            │
│  + generate(): ModelResponse                             │
│  + embeddings(): List[float]                             │
│  + classify(): Classification                            │
│  + evaluate(): Evaluation                                │
│  + health(): HealthStatus                                │
│  + cost_estimate(): CostEstimate                         │
│  + capabilities(): CapabilityProfile                     │
│  + context_window(): int                                 │
│  + provider_metadata(): Metadata                         │
├─────────────────────────────────────────────────────────┤
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │ Ollama     │ │ OpenAI     │ │ Anthropic  │          │
│  │ Provider   │ │ Provider   │ │ Provider   │          │
│  └────────────┘ └────────────┘ └────────────┘          │
│  ┌────────────┐ ┌────────────┐                          │
│  │ Gemini     │ │ OpenRouter │                          │
│  │ Provider   │ │ Provider   │                          │
│  └────────────┘ └────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

### Normalized Response

All providers return a normalized `ModelResponse`:

```python
class ModelResponse:
    provider: str           # "ollama", "openai", etc.
    model: str              # "qwen2.5-coder", "gpt-4o", etc.
    response_id: str        # Unique response ID
    output: str             # Generated text
    raw_output: dict        # Raw provider response
    latency_ms: float       # Response latency
    token_usage: dict       # {input: int, output: int, total: int}
    estimated_cost: float   # Estimated cost in USD
    confidence: float       # Confidence score (if available)
    finish_reason: str      # "stop", "length", "error", etc.
    error: Optional[str]    # Error message (if failed)
    warnings: List[str]     # Warnings (if any)
    timestamp: datetime     # Response timestamp
    trace_id: str           # Trace correlation ID
```

---

## 8. Deployment Architecture

### Docker Compose (Development)

```
┌─────────────────────────────────────────────────────────┐
│  Docker Network: sdlc-factory                            │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ api:8000 │  │ web:3000 │  │postgres  │              │
│  │ FastAPI  │  │ Next.js  │  │ :5432    │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                      │
│       └─────────────┼─────────────┘                      │
│                     │                                    │
│  ┌──────────┐  ┌───┴─────┐  ┌──────────┐              │
│  │ redis    │  │ qdrant  │  │prometheus│              │
│  │ :6379    │  │ :6333   │  │ :9090    │              │
│  └──────────┘  └─────────┘  └──────────┘              │
│                                                          │
│  ┌──────────┐                                           │
│  │ grafana  │                                           │
│  │ :3001    │                                           │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
```

### Production Deployment

```
┌─────────────────────────────────────────────────────────┐
│  Internet                                                │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │  Nginx   │  ← SSL termination, reverse proxy         │
│  │  :443    │                                           │
│  └────┬─────┘                                           │
│       │                                                  │
│       ├──────────────────┐                              │
│       ▼                  ▼                              │
│  ┌──────────┐      ┌──────────┐                        │
│  │ web:3000 │      │ api:8000 │                        │
│  │ Next.js  │      │ FastAPI  │                        │
│  └──────────┘      └────┬─────┘                        │
│                         │                               │
│       ┌─────────────────┼─────────────────┐            │
│       ▼                 ▼                 ▼            │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐    │
│  │postgres  │      │ redis    │      │ qdrant   │    │
│  │ :5432    │      │ :6379    │      │ :6333    │    │
│  └──────────┘      └──────────┘      └──────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Performance Characteristics

### Backend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| API response time (p50) | < 50ms | Simple queries |
| API response time (p95) | < 200ms | Complex queries |
| Model call latency (local) | 20-80ms | Ollama, depends on model |
| Model call latency (remote) | 80-150ms | OpenAI/Anthropic |
| Event processing | < 5ms | Persist + broadcast |
| SSE broadcast | < 1ms | Per connected client |
| Database queries (p95) | < 30ms | With proper indexing |
| Test suite | < 10s | 127 tests |

### Frontend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| First Contentful Paint | < 1.5s | Next.js SSR |
| Time to Interactive | < 2.5s | With hydration |
| SSE reconnection | < 3s | Exponential backoff |
| Bundle size | < 200KB | Initial JS (gzipped) |
| Lighthouse score | > 90 | Performance category |

### Scalability

| Dimension | Current | Scaling Strategy |
|-----------|---------|-----------------|
| Concurrent runs | 10 | Horizontal scaling with Redis queue |
| Concurrent users | 50 | Stateless API, scale horizontally |
| Model calls/min | 100 | Rate limiting per provider |
| Database size | 10GB | Partitioning by workspace |
| Event throughput | 1500/s | Batch inserts, async processing |

### Resource Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| API | 1 core | 512MB | 100MB |
| Web | 0.5 core | 256MB | 100MB |
| PostgreSQL | 2 cores | 2GB | 10GB |
| Redis | 0.5 core | 512MB | 100MB |
| Qdrant | 1 core | 1GB | 5GB |
| Ollama (phi3) | 2 cores | 4GB | 5GB |
| Ollama (qwen2.5) | 4 cores | 8GB | 10GB |
| **Total (minimal)** | **4 cores** | **4GB** | **15GB** |
| **Total (recommended)** | **8 cores** | **16GB** | **30GB** |
