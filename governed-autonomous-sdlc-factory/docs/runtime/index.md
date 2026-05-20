# Runtime Documentation

## Runtime Lifecycle

The runtime executes software development lifecycle phases with full governance, evidence capture, and observability.

### Phase Execution

Each phase follows this lifecycle:

```
┌─────────────┐
│  Initialize  │
│  Phase       │
└──────┬──────┘
       ▼
┌─────────────┐
│  Governance  │
│  Pre-Check   │
└──────┬──────┘
       ▼
┌─────────────┐
│  Model       │
│  Selection   │
└──────┬──────┘
       ▼
┌─────────────┐
│  Execute     │
│  Phase       │
└──────┬──────┘
       ▼
┌─────────────┐
│  Evidence    │
│  Capture     │
└──────┬──────┘
       ▼
┌─────────────┐
│  Integrity   │
│  Scoring     │
└──────┬──────┘
       ▼
┌─────────────┐
│  Governance  │
│  Gate        │
└──────┬──────┘
       ▼
┌─────────────┐
│  Snapshot    │
│  Capture     │
└──────┬──────┘
       ▼
┌─────────────┐
│  Next Phase  │
│  or Complete │
└─────────────┘
```

### Phase Types

| Phase | Description | Key Engines |
|-------|-------------|-------------|
| `specification` | Parse natural language into structured spec | SpecificationEngine |
| `planning` | Create execution plan | ArchitectureEngine |
| `implementation` | Generate code | CognitiveModelRouter, ArbitrationEngine |
| `verification` | Run tests and validate | TestEngine, SemanticCoverageEngine |
| `release` | Gate release based on integrity | GovernanceEngine |

## Trust Scoring

Trust scores range from 0.0 to 1.0 and are computed from multiple signals:

### Trust Components

| Component | Weight | Source |
|-----------|--------|--------|
| Historical accuracy | 0.30 | Past run outcomes |
| Hallucination rate | 0.25 | Hallucination containment engine |
| Replay stability | 0.20 | Replay verification results |
| Governance compliance | 0.15 | Policy evaluation results |
| Operator feedback | 0.10 | Manual operator ratings |

### Trust Levels

| Score | Level | Autonomy |
|-------|-------|----------|
| 0.9 - 1.0 | Excellent | Full autonomy |
| 0.7 - 0.9 | Good | High autonomy with post-hoc review |
| 0.5 - 0.7 | Fair | Moderate autonomy, approval for significant decisions |
| 0.3 - 0.5 | Low | Low autonomy, approval for all decisions |
| 0.0 - 0.3 | Critical | Minimal autonomy, human-in-the-loop |

## Drift Detection

The drift detection system monitors cognitive drift across multiple dimensions:

### Drift Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| Goal drift | System diverges from original goal | Intent comparison |
| Semantic drift | Output semantics shift | Embedding distance |
| Trust drift | Trust score changes unexpectedly | Statistical process control |
| Governance drift | Policy compliance degrades | Policy evaluation trend |
| Model drift | Model behavior changes | Output distribution analysis |

### Drift Response

| Severity | Response |
|----------|----------|
| Low | Log event, continue |
| Medium | Alert operator, increase scrutiny |
| High | Quarantine run, require review |
| Critical | Terminate run, full investigation |

## Replay System

The replay system enables deterministic reconstruction of any previous run.

### Snapshot Format

```json
{
  "snapshot_id": "uuid",
  "run_id": "uuid",
  "phase": "implementation",
  "timestamp": "2026-05-19T12:00:00Z",
  "state": { ... },
  "hash": "sha256-of-state",
  "previous_hash": "sha256-of-previous-snapshot"
}
```

### Replay Verification

1. Load snapshot sequence for the run
2. Verify hash chain integrity
3. Reconstruct run state at each phase
4. Compare with original evidence bundle
5. Report any discrepancies

## Event System

### Event Types

| Category | Events |
|----------|--------|
| Runtime | `phase.started`, `phase.completed`, `phase.failed`, `run.started`, `run.completed` |
| Governance | `policy.evaluated`, `trust.updated`, `drift.detected`, `gate.passed`, `gate.blocked` |
| Model | `model.selected`, `model.called`, `model.failed`, `arbitration.completed` |
| Intervention | `intervention.pause`, `intervention.resume`, `intervention.quarantine`, `intervention.rollback` |
| Memory | `memory.created`, `memory.aged`, `memory.archived`, `memory.quarantined` |
| Evidence | `evidence.captured`, `evidence.bundle.created`, `evidence.verified` |

### Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "phase.completed",
  "run_id": "uuid",
  "phase": "implementation",
  "timestamp": "2026-05-19T12:00:00.000Z",
  "payload": { ... },
  "hash_chain": "sha256",
  "trace_id": "uuid"
}
```
