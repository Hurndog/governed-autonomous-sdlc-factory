# Architecture Overview

## System Architecture

The Governed Autonomous SDLC Factory follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Next.js 14 Frontend (Forge Control Tower)                    │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐    │  │
│  │  │ 35+ Room    │ │ Shared UI    │ │ Client Libraries   │    │  │
│  │  │ Components  │ │ Components   │ │ (API, WS, Auth)    │    │  │
│  │  └─────────────┘ └──────────────┘ └────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP / SSE / WebSocket
┌──────────────────────────────▼──────────────────────────────────────┐
│                        API LAYER                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                           │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐    │  │
│  │  │ 27+ REST    │ │ SSE Streams  │ │ Middleware Stack    │    │  │
│  │  │ Endpoints   │ │ (Telemetry)  │ │ (Auth, Audit, Trace)│    │  │
│  │  └─────────────┘ └──────────────┘ └────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                     SERVICE LAYER                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐   │
│  │ Full Pipeline │ │ Run          │ │ Project                  │   │
│  │ Orchestrator  │ │ Orchestrator │ │ Service                  │   │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      ENGINE LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  17+ Specialized Engines                                      │   │
│  │                                                               │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐   │   │
│  │  │ Cognitive Engines    │  │ Governance Engines           │   │   │
│  │  │ - Model Router       │  │ - Governance Engine          │   │   │
│  │  │ - Arbitration Engine │  │ - Drift Control Engine       │   │   │
│  │  │ - Cognitive Gov.     │  │ - Safety Guards              │   │   │
│  │  └─────────────────────┘  └─────────────────────────────┘   │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐   │   │
│  │  │ Execution Engines    │  │ Memory Engines               │   │   │
│  │  │ - Replay Engine      │  │ - Evidence Engine            │   │   │
│  │  │ - Semantic Coverage  │  │ - Traceability Engine        │   │   │
│  │  │ - Specification      │  │ - Inference Trace            │   │   │
│  │  │ - Architecture       │  │ - Source Extractor           │   │   │
│  │  │ - Test Engine        │  │ - Divergence Engine          │   │   │
│  │  └─────────────────────┘  └─────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                       CORE LAYER                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │
│  │ Auth       │ │ Config     │ │ Database   │ │ Observability  │  │
│  │ (JWT+RBAC) │ │ (Pydantic) │ │ (SQLAlchemy│ │ (OTel+Prom.)   │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │
│  │ Event Bus  │ │ Logging    │ │ Hashing    │ │ Safety Guards  │  │
│  │ (Pub/Sub)  │ │ (structlog)│ │ (SHA-256)  │ │ (11 types)     │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │
│  │ PostgreSQL │ │ Redis      │ │ Qdrant     │ │ Ollama         │  │
│  │ (Primary)  │ │ (Cache)    │ │ (Vectors)  │ │ (Local Models) │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Runtime Execution Flow

```mermaid
flowchart TD
    A[Natural Language Input] --> B[Specification Engine]
    B --> C[Governance Check]
    C --> D{Policy Pass?}
    D -->|No| E[Block + Evidence]
    D -->|Yes| F[Model Router]
    F --> G[Sovereignty Check]
    G --> H{Local Only?}
    H -->|Yes| I[Ollama/llama.cpp]
    H -->|No| J[Select Provider]
    J --> K[Execute Task]
    I --> K
    K --> L{Multi-Model?}
    L -->|Yes| M[Arbitration Engine]
    L -->|No| N[Evidence Capture]
    M --> N
    N --> O[Integrity Scoring]
    O --> P{Gate Pass?}
    P -->|No| Q[Quarantine + Alert]
    P -->|Yes| R[Next Phase]
    R --> C
    R --> S[Release Gate]
    S --> T[Evidence Bundle]
```

## Governance Flow

```mermaid
flowchart TD
    A[Action Requested] --> B[RBAC Check]
    B --> C{Authorized?}
    C -->|No| D[Deny + Log]
    C -->|Yes| E[Trust Score Check]
    E --> F{Trust > θ?}
    F -->|No| G[Reduce Autonomy]
    F -->|Yes| H[Policy Evaluation]
    G --> H
    H --> I{Policy Pass?}
    I -->|No| J[Block + Reasoning]
    I -->|Yes| K[Sovereignty Check]
    K --> L{Sovereignty OK?}
    L -->|No| M[Reject Model]
    L -->|Yes| N[Execute]
    M --> O[Re-route]
    O --> H
    N --> P[Evidence Capture]
    P --> Q[Audit Trail]
    Q --> R[SSE Broadcast]
```

## Model Routing Flow

```mermaid
flowchart TD
    A[Routing Request] --> B[Capability Registry Query]
    B --> C[Filter by Sovereignty]
    C --> D[Filter by Governance]
    D --> E[Filter by Availability]
    E --> F[Score by Capabilities]
    F --> G[Apply Cost Constraints]
    G --> H[Apply Latency Constraints]
    H --> I[Rank Candidates]
    I --> J[Select Primary]
    J --> K[Build Fallback Chain]
    K --> L[Record Decision]
    L --> M[Routing Decision]
```

## Event Lifecycle

```mermaid
flowchart LR
    A[Action] --> B[Event Created]
    B --> C[Hash Chained]
    C --> D[Persisted to DB]
    D --> E[Published to Bus]
    E --> F[SSE Stream]
    E --> G[Internal Subscribers]
    F --> H[Frontend Update]
    G --> I[Engine Reactions]
```

## Memory Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active: Created
    Active --> Stale: Aging threshold
    Active --> Quarantined: Suspicious
    Active --> Archived: Manual/Policy
    Stale --> Expired: Expiration
    Stale --> Active: Accessed/Refreshed
    Stale --> Archived: Policy
    Expired --> Archived: Cleanup
    Quarantined --> Active: Cleared
    Quarantined --> Archived: Confirmed bad
    Archived --> Active: Restored
    Archived [*]: Terminal
    Expired [*]: Terminal
```

## Replay Architecture

```mermaid
flowchart TD
    A[Run Execution] --> B[Phase Transition]
    B --> C[Snapshot Capture]
    C --> D[Hash Chain Link]
    D --> E[Store Snapshot]
    E --> F{More Phases?}
    F -->|Yes| B
    F -->|No| G[Evidence Bundle]
    
    H[Replay Request] --> I[Load Snapshots]
    I --> J[Verify Hash Chain]
    J --> K{Integrity OK?}
    K -->|No| L[Tamper Alert]
    K -->|Yes| M[Reconstruct Run]
    M --> N[Bind Evidence]
    N --> O[Replay Result]
```

## Intervention Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Running: Start
    Running --> Paused: Pause
    Running --> Quarantined: Quarantine
    Running --> Terminated: Terminate
    Paused --> Running: Resume
    Paused --> Quarantined: Quarantine
    Paused --> Terminated: Terminate
    Quarantined --> Running: Release
    Quarantined --> RolledBack: Rollback
    Quarantined --> Terminated: Terminate
    RolledBack --> Running: Resume
    RolledBack [*]: Terminal
    Terminated [*]: Terminal
    
    note right of Running: All transitions\nare audit-trailed
    note right of Quarantined: Trust score\nauto-degraded
```

## Explainability Pipeline

```mermaid
flowchart TD
    A[Explanation Request] --> B[Identify Target]
    B --> C[Query Evidence Bundles]
    C --> D[Query Log Events]
    D --> D2[Query Trust Records]
    D2 --> E[Build Causal Chain]
    E --> F{Complete Evidence?}
    F -->|No| G[Mark Uncertainty]
    F -->|Yes| H[Generate Narrative]
    G --> H
    H --> I[Ground in Records]
    I --> J[Add Recommendations]
    J --> K[Explanation Response]
```

## Data Model Overview

```mermaid
erDiagram
    PROJECTS ||--o{ RUNS : has
    RUNS ||--o{ PHASES : contains
    RUNS ||--o{ TASKS : contains
    RUNS ||--o{ ARTIFACTS : produces
    RUNS ||--o{ EVIDENCE_BUNDLES : generates
    RUNS ||--o{ LOG_EVENTS : emits
    RUNS ||--o{ SNAPSHOTS : captures
    
    PROJECTS {
        uuid id
        string name
        string description
        jsonb config
        timestamp created_at
    }
    
    RUNS {
        uuid id
        uuid project_id
        string status
        float trust_score
        jsonb config
        timestamp started_at
        timestamp completed_at
    }
    
    LOG_EVENTS {
        uuid id
        uuid run_id
        string event_type
        jsonb payload
        string hash_chain
        timestamp created_at
    }
    
    EVIDENCE_BUNDLES {
        uuid id
        uuid run_id
        jsonb content
        string hash
        timestamp created_at
    }
    
    MODEL_CAPABILITIES {
        uuid id
        string provider
        string model
        jsonb capabilities
        float trust_weight
        timestamp updated_at
    }
    
    ROUTING_DECISIONS {
        uuid id
        uuid run_id
        string selected_model
        string routing_reason
        jsonb rejected_models
        timestamp created_at
    }
    
    OPERATOR_INTERVENTIONS {
        uuid id
        uuid run_id
        string intervention_type
        string operator_id
        string reasoning
        timestamp created_at
    }
```

## Component Dependency Map

```
Frontend (Next.js)
├── lib/api.ts → Backend REST API
├── lib/useWebSocket.ts → Backend WebSocket
├── lib/authStore.ts → /api/v1/auth/*
├── lib/data-source.ts → DataSourceBadge
├── components/rooms/* → lib/api.ts + lib/useWebSocket.ts
└── components/ui/* → Shared UI (no external deps)

Backend (FastAPI)
├── api/v1/endpoints/* → services/* + engines/*
├── services/* → engines/* + core/*
├── engines/* → core/* + models/*
├── core/database.py → PostgreSQL
├── core/event_bus.py → Internal pub/sub
├── core/observability.py → Prometheus
└── websocket/* → core/event_bus.py
```
