# Tokenomics Agent Identity Audit

**Date:** 2026-05-18
**Phase:** 1 — Agent Identity Audit

## Key Findings

### 1. Cost Event Creation Points

**Primary**: `POST /costs/` endpoint — external callers create cost events manually.

**Missing**: The `FullPipelineOrchestrator` imports `publish_cost_event` but **never calls it**. Cost events are NOT automatically created during pipeline execution.

**Missing**: The `InferenceTracer` tracks tokens/cost in-memory but never persists to `CostEvent` records.

### 2. Where Agent Identity IS Available

| Location | Field | Notes |
|---|---|---|
| `FullPipelineOrchestrator.execute_full_pipeline()` | Engine objects | Each step creates a named engine (spec_engine, arch_engine, gov_engine, test_engine) |
| Engine `.generate_*()` methods | `self.__class__.__name__` | Engine class name identifies the agent |
| Artifact persistence | `source_engine` | Set to engine name like "specification-engine", "architecture-engine" |
| Phase creation | `phase.name` | Phase names like "specification", "architecture", "governance", "quality" |
| `publish_cost_event()` | `data` dict | Currently accepts model_name, tokens, cost — but NO agent_id |

### 3. Where Agent Identity is NOT Available

- `publish_cost_event()` — no agent_id parameter
- `CostEvent` model — has `agent_id` field (nullable) but it's never set by the pipeline
- `ModelCall` model — has `agent_id` field (nullable) but never set
- `InferenceTracer` — no agent_id concept

### 4. Reliable Derivation Rules

The pipeline orchestrator has explicit engine context at each step:

| Step | Engine | Reliable agent_id | Phase |
|---|---|---|---|
| 1 | SpecificationEngine | `specification_engine` | specification |
| 2 | ArchitectureEngine | `architecture_engine` | architecture |
| 3 | GovernanceEngine | `governance_engine` | governance |
| 4 | TestPlanEngine | `test_engine` | quality |
| 5 | TraceabilityManager | `traceability_engine` | traceability |
| 6 | SnapshotManager | `snapshot_engine` | snapshot |

These are **deterministic** — each step uses a known engine class.

### 5. What Cannot Be Attributed

- Direct API calls to `/costs/` endpoint (no engine context)
- Legacy records with null agent_id
- Any model calls outside the pipeline orchestrator

### 6. Recommended Approach

**Option A (Preferred)**: Modify `publish_cost_event()` to accept `agent_id` and call it from the pipeline orchestrator after each engine step, passing the engine class name as agent_id.

**Option B**: Create a new `record_model_call()` endpoint that accepts agent_id and persists both a ModelCall and CostEvent.

**Option C**: Add agent_id to the existing `POST /costs/` endpoint and have the orchestrator call it.

I'll go with **Option A** — modify `publish_cost_event()` to accept `agent_id` and call it from the pipeline orchestrator. This is the cleanest approach because:
1. The orchestrator already imports `publish_cost_event`
2. The orchestrator has engine context at each step
3. It doesn't require new endpoints
4. It preserves backward compatibility (agent_id is optional)
