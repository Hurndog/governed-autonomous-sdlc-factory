# Observability Substrate Specification

## 1. Principle

Observability is NOT dashboards first. Observability is telemetry substrate first.

Before any visualization, the runtime must produce structured, queryable, replay-safe telemetry that enables:
- Runtime health monitoring
- Governance effectiveness tracking
- Replay divergence detection
- Forensic reconstruction
- Operational intelligence

---

## 2. Telemetry Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   TELEMETRY ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sources                                                    │
│  ├── Pipeline Orchestrator (step timing, transitions)       │
│  ├── Engines (generation time, artifact counts)             │
│  ├── Governance Engine (evaluation time, decisions)         │
│  ├── Persistence Layer (DB latency, flush counts)           │
│  ├── Event Bus (event throughput, subscriber counts)        │
│  └── Replay Engine (replay duration, divergence)            │
│                                                             │
│  ▼                                                          │
│                                                             │
│  Telemetry Collector                                        │
│  ├── Structured metrics (counters, gauges, histograms)      │
│  ├── Event traces (causal chains)                           │
│  ├── Resource metrics (DB, Redis, memory)                   │
│  └── Custom dimensions (run_id, phase, engine)              │
│                                                             │
│  ▼                                                          │
│                                                             │
│  Storage                                                    │
│  ├── In-memory ring buffer (recent metrics)                 │
│  ├── PostgreSQL (persistent telemetry)                      │
│  └── Export (Prometheus, JSONL)                             │
│                                                             │
│  ▼                                                          │
│                                                             │
│  Consumers                                                  │
│  ├── Replay Chamber (visualization)                         │
│  ├── Governance Dashboard                                   │
│  ├── Operational Alerts                                     │
│  └── Forensic Analysis                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Metric Categories

### 3.1 Runtime Metrics

```python
RUNTIME_METRICS = {
    # Pipeline execution
    "pipeline.duration_ms": Histogram,        # Total pipeline duration
    "pipeline.step.duration.ms": Histogram,   # Per-step duration
    "pipeline.step.transitions": Counter,     # Phase transitions
    "pipeline.retries": Counter,              # Retry count per step
    "pipeline.failures": Counter,             # Failure count per step
    
    # Orchestration
    "orchestration.branching_factor": Gauge,  # Parallel branches
    "orchestration.depth": Gauge,             # Max execution depth
    "orchestration.stalls": Counter,          # Orchestration stalls
    
    # Execution state
    "execution.active_runs": Gauge,           # Currently running pipelines
    "execution.queued_runs": Gauge,           # Queued pipelines
    "execution.completed_runs": Counter,      # Completed pipelines
    "execution.failed_runs": Counter,         # Failed pipelines
}
```

### 3.2 Artifact Metrics

```python
ARTIFACT_METRICS = {
    "artifacts.generated": Counter,           # Total artifacts generated
    "artifacts.persisted": Counter,           # Successfully persisted
    "artifacts.failed": Counter,              # Failed persistence
    "artifacts.size_bytes": Histogram,        # Artifact size distribution
    "artifacts.types": Counter,               # Per-type count
    "artifacts.orphan": Gauge,                # Orphan artifact count
    
    # Lineage
    "lineage.links_created": Counter,         # Traceability links
    "lineage.coverage_percent": Gauge,        # Requirement coverage
    "lineage.orphan_links": Gauge,            # Links to non-existent artifacts
    "lineage.cycles_detected": Counter,       # Cycle detection count
}
```

### 3.3 Governance Metrics

```python
GOVERNANCE_METRICS = {
    "governance.evaluations": Counter,        # Total evaluations
    "governance.pass": Counter,               # Pass decisions
    "governance.fail": Counter,               # Fail decisions
    "governance.warning": Counter,            # Warning decisions
    "governance.evaluation_time_ms": Histogram, # Evaluation latency
    "governance.policies_active": Gauge,      # Active policies
    "governance.overrides": Counter,          # Override count
    "governance.blocked_actions": Counter,    # Blocked deployments
    "governance.remediations_suggested": Counter, # Remediation suggestions
}
```

### 3.4 Cognitive Execution Metrics

```python
COGNITIVE_METRICS = {
    "cognitive.prompts_emitted": Counter,     # Prompts sent to engines
    "cognitive.tool_calls": Counter,          # Tool invocations
    "cognitive.branching_factor": Gauge,      # Decision branches
    "cognitive.context_size": Histogram,      # Context window usage
    "cognitive.execution_depth": Gauge,       # Max reasoning depth
}
```

### 3.5 System Metrics

```python
SYSTEM_METRICS = {
    # Database
    "db.query.duration_ms": Histogram,        # Query latency
    "db.query.count": Counter,                # Query count
    "db.connections.active": Gauge,           # Active connections
    "db.connections.idle": Gauge,             # Idle connections
    "db.transaction.commits": Counter,        # Commits
    "db.transaction.rollbacks": Counter,     # Rollbacks
    
    # Redis
    "redis.operation.duration.ms": Histogram, # Operation latency
    "redis.operation.count": Counter,         # Operation count
    "redis.memory_usage_bytes": Gauge,        # Memory usage
    
    # Event Bus
    "events.emitted": Counter,                # Events emitted
    "events.delivered": Counter,              # Events delivered
    "events.dropped": Counter,                # Events dropped
    "events.subscribers": Gauge,              # Active subscribers
    
    # Snapshot
    "snapshots.created": Counter,             # Snapshots created
    "snapshots.size_bytes": Histogram,        # Snapshot size
    "snapshots.restored": Counter,            # Snapshots restored
}
```

### 3.6 Replay Metrics

```python
REPLAY_METRICS = {
    "replay.attempts": Counter,               # Replay attempts
    "replay.success": Counter,                # Successful replays
    "replay.divergence_detected": Counter,    # Divergence events
    "replay.integrity_score": Gauge,         # Current integrity score
    "replay.duration_ms": Histogram,         # Replay duration
    "replay.artifacts_hydrated": Counter,    # Artifacts hydrated
    "replay.events_replayed": Counter,       # Events replayed
}
```

---

## 4. Telemetry Schema

### 4.1 Metric Point

```python
@dataclass
class MetricPoint:
    name: str                    # Metric name
    value: float                 # Metric value
    timestamp: datetime          # When recorded
    dimensions: dict             # {run_id, phase, engine, ...}
    type: str                    # counter, gauge, histogram
```

### 4.2 Event Trace

```python
@dataclass
class EventTrace:
    trace_id: str                # Unique trace ID
    span_id: str                 # Span within trace
    parent_span_id: Optional[str] # Parent span
    operation: str               # Operation name
    start_time: datetime
    end_time: datetime
    status: str                  # ok, error
    attributes: dict             # Custom attributes
```

---

## 5. Storage Schema

```sql
-- Metrics table
CREATE TABLE IF NOT EXISTS telemetry_metrics (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36),
    name VARCHAR(200) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    metric_type VARCHAR(20) NOT NULL,  -- counter, gauge, histogram
    dimensions JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    INDEX idx_metrics_run_name (run_id, name),
    INDEX idx_metrics_recorded (recorded_at)
);

-- Event traces table
CREATE TABLE IF NOT EXISTS telemetry_traces (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36),
    trace_id VARCHAR(36) NOT NULL,
    span_id VARCHAR(36) NOT NULL,
    parent_span_id VARCHAR(36),
    operation VARCHAR(200) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'ok',
    attributes JSONB DEFAULT '{}',
    INDEX idx_traces_run (run_id),
    INDEX idx_traces_trace (trace_id)
);
```

---

## 6. Collection Points

```python
# In pipeline_orchestrator.py
class FullPipelineOrchestrator:
    async def execute_full_pipeline(self, ...):
        with TelemetryContext(run_id=run_id, operation="full_pipeline") as ctx:
            for step_num, step_func in enumerate(self._steps, 1):
                with ctx.span(f"step_{step_num}", step=step_num):
                    result = await step_func(...)
                    ctx.metric("step_duration_ms", step_duration, step=step_num)
            
            ctx.metric("pipeline_duration_ms", total_duration)
            ctx.metric("artifacts_generated", metrics.artifacts_generated)
            ctx.metric("traceability_links", metrics.traceability_links)
            ctx.metric("governance_passed", metrics.governance_passed)
            ctx.metric("governance_failed", metrics.governance_failed)
```

---

## 7. Implementation Priority

### Priority 1: Core Metrics (Current Session)
- Pipeline duration per step
- Artifact counts per type
- Governance pass/fail counts
- DB query latency
- Event throughput

### Priority 2: Tracing (Next Session)
- Distributed tracing across engines
- Causal chain tracking
- Span-based performance analysis

### Priority 3: Alerting (Future)
- Threshold-based alerts
- Anomaly detection
- Governance failure alerts
- Replay divergence alerts

### Priority 4: Visualization (Future)
- Replay Chamber telemetry overlay
- Governance effectiveness dashboard
- Operational health dashboard
