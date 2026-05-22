# Replay & Memory Pressure Analysis (v0.5.1B)

**Date:** 2026-05-20
**Scope:** Replay storage growth, evidence accumulation, memory system scaling risks.

---

## 1. Replay Architecture Summary

| Component | File | Purpose |
|-----------|------|---------|
| ReplayEngine | `engines/replay_engine.py` (452 lines) | Deterministic replay within FastAPI DI session |
| ReplayRuntime | `engines/replay_runtime.py` (282 lines) | Isolated thread-pool replay (separate DB engine) |
| ReplayRuntimeSync | `engines/replay_runtime_sync.py` (450+ lines) | Synchronous replay for non-async contexts |
| ReplayTransactionManager | `engines/replay_transaction_manager.py` (118 lines) | ACID replay transactions |
| IntegrityRuntimeSync | `engines/integrity_runtime_sync.py` (522 lines) | Hash chain verification |
| DriftControlEngine | `engines/drift_control_engine.py` (415 lines) | Drift detection during replay |
| Snapshots | `engines/snapshots.py` (130+ lines) | Run snapshot capture |

### Replay Event Model
Per replay, the following records are created:
- **ReplaySession** — 1 per replay (metadata: mode, status, timing)
- **ReplayEvent** — 1 per log event replayed (hash + content + sequence)
- **ReplayManifest** — 1 per replay (summary + integrity proof)

### Database Tables Involved
| Table | Growth Driver | Records per Run |
|-------|--------------|-----------------|
| `runs` | 1 per pipeline execution | 1 |
| `log_events` | Per phase step, per model call, per governance decision | 10-100+ |
| `artifacts` | Per generated output (spec, arch, code, test) | 5-50 |
| `run_snapshots` | Per phase transition | 5-10 |
| `traceability_links` | Per artifact-to-artifact link | 5-20 |
| `governance_evaluations` | Per governance gate | 3-10 |
| `replay_sessions` | 1 per replay action | 1-N |
| `replay_events` | Mirrors log_events for replayed run | 10-100+ |
| `replay_manifests` | 1 per replay | 1 |
| `semantic_graph_nodes` | Per requirement/entity extracted | 5-50 |
| `semantic_graph_edges` | Per relationship | 5-50 |
| `cost_events` | Per model call | 5-50 |

---

## 2. Storage Growth Estimates

### Per Single Pipeline Run (no replay)

| Category | Records | Est. Size (KB) |
|----------|---------|-----------------|
| runs | 1 | 0.5 |
| log_events (50 avg) | 50 | 25 |
| artifacts (20 avg) | 20 | 100 (content-heavy) |
| snapshots (8 avg) | 8 | 40 |
| traceability_links (15) | 15 | 3 |
| governance_evaluations (6) | 6 | 3 |
| semantic_graph (30 nodes + 30 edges) | 60 | 12 |
| cost_events (30 avg) | 30 | 6 |
| **Total per run** | **~199 records** | **~190 KB** |

### With Replay (1 replay)

| Category | Records | Est. Size (KB) |
|----------|---------|-----------------|
| All of the above | ~199 | ~190 |
| replay_sessions | 1 | 0.5 |
| replay_events (mirrors 50 log_events) | 50 | 30 |
| replay_manifests | 1 | 1 |
| **Total with 1 replay** | **~251 records** | **~222 KB** |

### Scaling Projections

| Runs | Replays/Run | Total Records | Storage (est.) |
|------|-------------|---------------|-----------------|
| 10 | 0 | ~1,990 | ~2 MB |
| 100 | 0 | ~19,900 | ~19 MB |
| 100 | 1 | ~25,100 | ~22 MB |
| 1,000 | 0 | ~199,000 | ~190 MB |
| 1,000 | 1 | ~251,000 | ~222 MB |
| 10,000 | 0 | ~1,990,000 | ~1.9 GB |
| 10,000 | 1 | ~2,510,000 | ~2.2 GB |

---

## 3. Identified Scaling Risks

### Risk 1: Replay Event Duplication (MEDIUM)
- ReplayEvents mirror LogEvents. Every replay doubles the event storage for that run.
- **Mitigation:** None currently. ReplayEvents are never purged.
- **Recommendation (future):** Implement replay archival or TTL-based cleanup.

### Risk 2: Artifact Content Bloat (MEDIUM)
- Artifacts store full content (generated specs, architecture documents, code).
- A single generated code artifact can be 50-100 KB.
- 10,000 runs × 20 artifacts × 50 KB avg = ~10 GB of artifact content alone.
- **Mitigation:** None currently. No content compression or summarization.
- **Recommendation (future):** Store artifact content as compressed blobs; summarize old artifacts.

### Risk 3: Snapshot Growth (LOW-MEDIUM)
- Snapshots capture full run state at phase transitions.
- Each snapshot can be 5-10 KB.
- 10,000 runs × 8 snapshots × 8 KB = ~640 MB.
- **Mitigation:** Low immediate risk. Monitor after 5,000+ runs.

### Risk 4: Semantic Graph Accumulation (LOW)
- Nodes and edges grow with each run's extracted requirements.
- Requirements may overlap across runs (same project).
- No deduplication of semantic entities across runs.
- **Mitigation:** Low risk for current scale. Becomes relevant at 5,000+ runs on same project.

### Risk 5: Cost Event Accumulation (LOW)
- Cost events per model call.
- At $0.0025/1K tokens (GPT-4o), each call is ~$0.01.
- Financial audit trail is valuable — don't purge.
- **Mitigation:** Low risk. Cost events are small records.

### Risk 6: In-Memory Event Bus (HIGH for restart resilience)
- Event bus is in-memory (`core/event_bus.py`).
- All SSE state is lost on restart.
- No event replay from bus after restart.
- **Mitigation:** None. This is a development-time limitation.

### Risk 7: Evidence File System Growth (MEDIUM)
- Evidence bundles are JSON files on the filesystem.
- Per-run evidence: ~5-10 KB.
- 10,000 runs = ~50-100 MB of evidence files.
- **Mitigation:** No evidence archival or cleanup.
- **Recommendation (future):** Compress old evidence bundles; implement retention policy.

---

## 4. Long-Horizon Instability Vectors

| Vector | Time to Impact | Severity |
|--------|----------------|----------|
| Unbounded log_event table growth | 5,000+ runs | MEDIUM |
| Artifact storage bloat | 3,000+ runs | MEDIUM |
| Replay chain accumulation | 1,000+ replays | LOW-MEDIUM |
| Evidence filesystem growth | 10,000+ runs | LOW |
| In-memory event bus data loss | Every restart | HIGH (for SSE) |
| No DB connection pooling config | Under concurrent load | HIGH (for multi-user) |

---

## 5. Recommendations (NOT implemented — analysis only)

1. **Implement run archival** — Mark old runs as archived; exclude from default queries.
2. **Add evidence retention policy** — Compress evidence older than N days; configurable TTL.
3. **Consider event bus persistence** — Redis Streams or database-backed event log for restart resilience.
4. **Connection pooling** — SQLAlchemy `pool_size`, `max_overflow`, `pool_recycle` configuration.
5. **Paginated queries** — All list endpoints should have cursor-based pagination for runs, events, artifacts.
6. **Content-addressable artifact storage** — Deduplicate identical artifacts via content hash.

---

*This is an analysis document, not an implementation plan. No code was changed.*
