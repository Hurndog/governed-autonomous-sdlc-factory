# Functional Description & Execution Overviews

**Last updated:** 2025-05-20
**Validated against:** 128/128 backend tests PASS, full pipeline execution test, TypeScript 0 errors

---

## 1. Platform Capabilities

### What the Platform Does

The Governed Autonomous SDLC Factory executes software development lifecycle phases — from natural language specification through planning, implementation, verification, and release gating. Every step is governed, observable, auditable, and replayable.

### Capability Matrix

| Capability | Status | Since | Description |
|------------|--------|-------|-------------|
| Pipeline Execution | ✅ Operational | v0.2 | Execute SDLC phases from spec to deployment |
| Semantic Coverage | ✅ Operational | v0.2 | Score completeness of implementation vs spec |
| Release Gating | ✅ Operational | v0.2 | Block releases below quality threshold |
| Integrity Scoring | ✅ Operational | v0.2 | 7-component integrity score |
| Safety Guards | ✅ Operational | v0.2 | 11 types of safety checks |
| Conflict Detection | ✅ Operational | v0.2 | 4 conflict pattern types |
| Evidence Capture | ✅ Operational | v0.2 | Capture all actions as evidence |
| Backup & Restore | ✅ Operational | v0.2 | Full system backup and restore |
| Deterministic Replay | ✅ Operational | v0.2 | Reconstruct any previous run |
| Authentication | ✅ Operational | v0.3 | JWT-based auth with RBAC |
| Authorization | ✅ Operational | v0.3 | 30+ granular permissions |
| Audit Trail | ✅ Operational | v0.3 | Immutable audit log with hash chains |
| Drift Detection | ✅ Operational | v0.3.4 | 6 drift dimensions |
| Metacognitive Control | ✅ Operational | v0.3.4 | Self-monitoring and adjustment |
| Persistent Memory | ✅ Operational | v0.3.4 | 85+ table database |
| Operations Monitoring | ✅ Operational | v0.4 | Real-time health dashboard |
| SSE Telemetry | ✅ Operational | v0.4 | Live event streaming |
| Operator Interventions | ✅ Operational | v0.4 | 8 intervention types |
| Memory Lifecycle | ✅ Operational | v0.4 | 7 lifecycle states |
| Explainability | ✅ Operational | v0.4 | 8 explanation types |
| Multi-Model Routing | ✅ Operational | v0.5 | Dynamic model selection |
| Cognitive Arbitration | ⚠️ Partial | v0.5 | Engine exists, limited real-provider testing |
| Sovereignty Routing | ⚠️ Partial | v0.5 | 5 levels defined, edge cases untested |
| Mutation Execution | ✅ Operational | v0.5.1 | Plan → execute → score pipeline |
| Full Pipeline E2E | ✅ Operational | v0.5.1 | Complete SDLC pipeline test PASS |

---

## 2. Execution Overviews

### 2.1 Full Pipeline Execution

```
User Input (Natural Language)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. SPECIFICATION PHASE                                       │
│    - Parse natural language → structured specification       │
│    - Extract requirements (RequirementNormalization)         │
│    - Create test obligations (TestObligation)                │
│    - Persist specification artifact                          │
│    - Output: Structured specification + requirements         │
└─────────────────────────┬───────────────────────────────────┘
                          │ Governance Gate
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PLANNING PHASE                                            │
│    - Generate architecture decisions                         │
│    - Persist architecture artifacts                           │
│    - Output: Architecture decisions + plan                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ Governance Gate
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SEMANTIC COVERAGE PHASE                                   │
│    - Plan mutation tests (plan_mutation_tests)               │
│    - Execute mutation tests (execute_mutation_tests)         │
│    - Compute mutation score (execute_mutation)               │
│    - Create SemanticCoverageReport                           │
│    - Output: Coverage report + mutation score                │
└─────────────────────────┬───────────────────────────────────┘
                          │ Governance Gate
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. GOVERNANCE EVALUATION                                     │
│    - Evaluate governance policies                            │
│    - Compute trust score                                     │
│    - Check drift status                                      │
│    - Output: Governance verdict + trust score                │
└─────────────────────────┬───────────────────────────────────┘
                          │ Governance Gate
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. EVIDENCE & REPLAY                                         │
│    - Capture all events as evidence                          │
│    - Create evidence bundle artifact                         │
│    - Generate replay snapshots                               │
│    - Output: Evidence bundle + replay data                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. RELEASE GATE                                              │
│    - Evaluate all quality thresholds                         │
│    - Check governance policies                               │
│    - PASS → Release / BLOCK → Return to implementation      │
│    - Output: Release verdict + evidence bundle               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Model Routing Execution

```
Task Request
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. ANALYZE TASK                                              │
│    - Determine task type (code_generation, reasoning, etc.)  │
│    - Identify required capabilities                         │
│    - Check governance requirements                           │
│    - Check sovereignty requirements                          │
│    - Set cost and latency budgets                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. QUERY CAPABILITY REGISTRY                                 │
│    - Get all registered models (ModelRegistry.list_models)   │
│    - Filter by availability (health check)                  │
│    - Filter by sovereignty (eliminate violating models)     │
│    - Filter by governance (eliminate insufficient models)   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SELECT MODEL                                              │
│    - _select_model() picks best match from registry          │
│    - Apply RoutingPolicy constraints                         │
│    - Build fallback chain                                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. EXECUTE WITH FALLBACK                                     │
│    - _execute_with_fallback() tries primary model            │
│    - On failure, tries fallback chain                        │
│    - Records InferenceTrace for every attempt               │
│    - Returns InferenceResult                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Mutation Execution

```
execute_mutation(run_id) → float
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. PLAN MUTATIONS                                            │
│    - Query RequirementNormalization for critical reqs        │
│    - For each req × mutation_type, create MutationTest       │
│    - 5 mutation types: boundary_shift, null_injection,      │
│      type_confusion, logic_inversion, off_by_one             │
│    - Deterministic upsert by (run_id, mutation_id)           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EXECUTE MUTATIONS                                         │
│    - For each planned MutationTest:                          │
│      a. Load proof_statement from TestObligation             │
│      b. Apply mutation to code (_apply_mutation)             │
│      c. Write mutated code to temp file                      │
│      d. Run mutated code via subprocess (30s timeout)        │
│      e. Record: killed (test failed) / survived (passed)     │
│    - Max 50 mutations per run                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SCORE                                                     │
│    - mutation_score = killed / total_executed                │
│    - Returns float 0.0 - 1.0                                │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 Intervention Execution

```
Operator Initiates Intervention
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. AUTHENTICATE + AUTHORIZE                                  │
│    - Verify operator identity (JWT)                         │
│    - Check intervention permission (RBAC)                   │
│    - Validate target exists                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EXECUTE INTERVENTION                                      │
│    - Pause: Set run state to PAUSED                          │
│    - Resume: Restore from PAUSED                             │
│    - Quarantine: Isolate run, prevent further execution     │
│    - Rollback: Revert to previous snapshot                  │
│    - Escalate: Increase governance scrutiny level           │
│    - Throttle: Reduce execution speed                       │
│    - Override: Manually set a decision parameter            │
│    - Terminate: Stop execution immediately                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. RECORD + PROPAGATE                                        │
│    - Record in immutable audit trail (operator_interventions)│
│    - Broadcast SSE event to all connected clients           │
│    - Update frontend in real-time                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.5 Explainability Execution

```
Explanation Request (type, target_id)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. IDENTIFY TARGET + RETRIEVE EVIDENCE                       │
│    - Query evidence_bundles for target                      │
│    - Query log_events for causal chain                      │
│    - Query trust_records for trust context                  │
│    - Query governance_decisions for policy context          │
│    - Query snapshots for state context                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BUILD CAUSAL CHAIN                                        │
│    - Order events chronologically                           │
│    - Link cause → effect                                    │
│    - Identify decision points                               │
│    - Mark evidence-backed vs inferred                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ASSESS UNCERTAINTY + GENERATE NARRATIVE                   │
│    - Identify gaps in evidence                              │
│    - Mark claims without DB backing                         │
│    - Construct human-readable explanation                   │
│    - Ground every claim in specific DB records              │
│    - Add uncertainty disclosures                            │
│    - Add recommendations                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Module Functional Descriptions

### 3.1 SemanticCoverageEngine

**Purpose:** Compute semantic coverage, plan and execute mutation tests.

**Location:** `apps/api/src/engines/semantic_coverage_engine.py` (1229 lines, 31 functions)

**Key methods:**
- `plan_mutation_tests(run_id) → List[MutationTest]` — creates mutation test plans for critical requirements
- `execute_mutation_tests(run_id) → List[MutationTest]` — executes planned mutations, records killed/survived
- `execute_mutation(run_id) → float` — convenience method: plan + execute + score

**Mutation types:** boundary_shift, null_injection, type_confusion, logic_inversion, off_by_one

**Scoring:** `killed / total_executed` — fraction of mutations detected by tests

### 3.2 CognitiveModelRouter

**Purpose:** Route inference requests to appropriate models based on capabilities, sovereignty, cost.

**Location:** `apps/api/src/engines/model_router.py` (406 lines, 11 functions)

**Key methods:**
- `complete(messages, model, provider, policy, ...) → InferenceResult` — main inference entry point
- `_select_model(provider, policy) → ModelEntry` — internal model selection
- `_execute_with_fallback(entry, provider, messages) → InferenceResult` — execution with fallback chain

**Routing policy:** `RoutingPolicy(prefer_local, max_cost, min_context, fallback_enabled, max_retries)`

### 3.3 DriftDetectionEngine

**Purpose:** Detect cognitive drift across 6 dimensions.

**Location:** `apps/api/src/engines/drift_control_engine.py` (415 lines)

**Key methods:**
- `detect_semantic_drift(project_id)` — embedding distance analysis
- `detect_governance_drift(project_id)` — policy compliance trend
- `detect_cost_drift(project_id)` — budget anomaly detection
- `detect_evidence_drift(project_id)` — evidence quality degradation
- `detect_context_drift(project_id)` — context window drift
- `detect_cognitive_drift(project_id)` — cognitive behavior change
- `detect_goal_drift(project_id)` — intent comparison
- `run_full_drift_scan(project_id)` — all dimensions

### 3.4 RuntimeTrustScorer

**Purpose:** Compute trust scores from 5 components.

**Location:** `apps/api/src/engines/drift_control_engine.py` (lines 320-415)

**Components:** historical accuracy (0.30), hallucination rate (0.25), replay stability (0.20), governance compliance (0.15), operator feedback (0.10)

**Key methods:**
- `compute_trust_scores(project_id) → Dict` — compute all trust components
- `persist_trust_scores(project_id, workspace_id, scores) → List[str]` — persist to DB

### 3.5 ReplayIntegrityVerifier

**Purpose:** Verify replay integrity via hash chains.

**Location:** `apps/api/src/engines/drift_control_engine.py` (lines 188-228)

**Key methods:**
- `verify_replay_integrity(replay_session_id) → Dict` — verify hash chain, detect tampering

### 3.6 MetacognitiveController

**Purpose:** Self-monitoring and operator intervention recording.

**Location:** `apps/api/src/engines/drift_control_engine.py` (lines 230-318)

**Key methods:**
- `evaluate_runtime_state(project_id, drift_report) → Dict` — evaluate runtime health
- `apply_metacognitive_state(project_id, workspace_id, ...)` — apply metacognitive adjustments
- `record_operator_intervention(project_id, workspace_id, ...)` — record operator actions

### 3.7 FullPipelineOrchestrator

**Purpose:** Coordinate SDLC phase execution.

**Location:** `apps/api/src/services/full_pipeline_orchestrator.py` (647 lines, 10 functions)

**Phases:** specification → planning → implementation → verification → release gating

### 3.8 ExplainabilityEngine (endpoints)

**Purpose:** Generate causal explanations grounded in evidence.

**Location:** `apps/api/src/api/v1/endpoints/explainability.py` (970 lines, 12 classes, 19 functions)

**Explanation types:** runtime, trust, drift, replay, governance, memory, interventions, autonomy

**Key endpoints:**
- `GET /api/v1/explain/runtime/{run_id}` — runtime explanation
- `GET /api/v1/explain/trust/{run_id}` — trust explanation
- `GET /api/v1/explain/drift/{run_id}` — drift explanation
- `GET /api/v1/explain/replay/{run_id}` — replay explanation
- `GET /api/v1/explain/governance/{run_id}` — governance explanation
- `GET /api/v1/explain/memory/{run_id}` — memory explanation
- `GET /api/v1/explain/interventions/{run_id}` — intervention explanation
- `GET /api/v1/explain/autonomy/{run_id}` — autonomy explanation

### 3.9 MemoryLifecycleManager (endpoints)

**Purpose:** Manage memory lifecycle states.

**Location:** `apps/api/src/api/v1/endpoints/memory_lifecycle.py` (601 lines, 3 classes, 11 functions)

**Lifecycle states:** active, stale, expired, archived, quarantined, pending_review, degraded

**Key endpoints:**
- `GET /api/v1/memory` — list memory entries
- `POST /api/v1/memory/age` — trigger aging
- `POST /api/v1/memory/archive` — archive entries
- `POST /api/v1/memory/quarantine` — quarantine entries
- `POST /api/v1/memory/restore` — restore archived entries

### 3.10 OperatorInterventionManager (endpoints)

**Purpose:** Execute operator interventions.

**Location:** `apps/api/src/api/v1/endpoints/operator_intervention.py` (569 lines, 3 classes, 11 functions)

**Intervention types:** pause, resume, quarantine, rollback, escalate, throttle, override, terminate

**Key endpoints:**
- `POST /api/v1/interventions/pause` — pause execution
- `POST /api/v1/interventions/resume` — resume execution
- `POST /api/v1/interventions/quarantine` — quarantine run
- `POST /api/v1/interventions/rollback` — rollback to snapshot
- `POST /api/v1/interventions/escalate` — escalate scrutiny
- `POST /api/v1/interventions/throttle` — throttle execution
- `POST /api/v1/interventions/override` — override decision
- `POST /api/v1/interventions/terminate` — terminate execution
- `GET /api/v1/interventions/history` — intervention history

### 3.11 OperationsCenter (endpoints)

**Purpose:** Real-time operations monitoring.

**Location:** `apps/api/src/api/v1/endpoints/operations.py` (560 lines, 6 classes, 19 functions)

**Key endpoints:**
- `GET /api/v1/operations/summary` — system health summary (8 dimensions)
- `GET /api/v1/operations/events` — event log (filterable)
- `GET /api/v1/operations/events/stream` — SSE telemetry stream

### 3.12 GovernanceEngine

**Purpose:** Evaluate governance policies.

**Location:** `apps/api/src/engines/governance_engine.py` (251 lines, 2 classes, 3 functions)

**Key methods:**
- `generate_governance(project_id, workspace_id, spec)` — generate governance policies

---

## 4. Frontend Room Functional Descriptions

### 4.1 OperationsCenter.tsx (406 lines)
Real-time monitoring dashboard. Connects to SSE stream. Displays health dimensions, event stream, alerts, provider status.

### 4.2 ExplainabilityRoom.tsx (448 lines)
Forensic reconstruction interface. 8 tabbed views for explanation types. Causal chain visualization. Evidence links.

### 4.3 OperatorConsole.tsx (275 lines)
Operator intervention controls. Active runs list. Intervention buttons with confirmation. Audit trail display.

### 4.4 MemoryOperations.tsx (247 lines)
Memory lifecycle management. Entry list with state indicators. Aging controls. Archive/quarantine/restore actions.

### 4.5 ModelOperationsCenter.tsx (251 lines)
Multi-model routing operations. Capability cards. Sovereignty dashboard. Trust evolution charts.

### 4.6 Dashboard.tsx (288 lines)
Main dashboard. System health overview. Active runs. Quick actions.

### 4.7 GovernanceGates.tsx (161 lines)
Governance policy display. Gate status. Threshold configuration.

### 4.8 ReplayChamber.tsx (201 lines)
Replay interface. Snapshot list. Integrity verification display.

### 4.9 EvidenceCenter.tsx (107 lines)
Evidence bundle explorer. Event list. Artifact browser.

### 4.10 Tokenomics.tsx (293 lines)
Cost tracking dashboard. Token usage charts. Agent attribution.

---

## 5. Data Flow

### 5.1 Run Data Flow

```
Specification → RequirementNormalization + TestObligation
    ↓
Planning → Architecture decisions (Artifact)
    ↓
Implementation → Code generation (model-dependent)
    ↓
Verification → SemanticCoverageEngine → MutationTest → SemanticCoverageReport
    ↓
Governance → GovernanceEngine → Trust score
    ↓
Evidence → LogEvent + Artifact + EvidenceBundle
    ↓
Release Gate → Release verdict
```

### 5.2 Event Data Flow

```
Action → EventBus → { Database (LogEvent), SSE Stream, Internal Subscribers }
    ↓
Database → AuditTrail (immutable, hash-chained)
SSE Stream → Frontend (real-time updates)
Internal Subscribers → Engines (reactive behavior)
```

### 5.3 Trust Data Flow

```
ModelCalls → AccuracyTracking → TrustScoreUpdate
DriftDetection → DriftSeverity → TrustScoreUpdate
GovernanceDecisions → ComplianceScore → TrustScoreUpdate
OperatorFeedback → ManualAdjustment → TrustScoreUpdate
    ↓
TrustScore → { ModelRouter, ArbitrationEngine, AutonomyManager }
```
