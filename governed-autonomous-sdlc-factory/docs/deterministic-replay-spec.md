# Deterministic Replay Specification

## 1. Purpose

Replay is the foundation of trust in the Cognitive Cortex. A runtime that cannot deterministically reconstruct its own execution history is not an enterprise cognitive system — it is probabilistic chaos with persistence.

This specification defines the replay architecture, validation criteria, and divergence detection mechanisms.

---

## 2. Replay Architecture

### 2.1 Replay Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Full Reconstruction** | Rebuild entire execution from events + artifacts | Forensic analysis, audit |
| **Partial Replay** | Replay from a specific timestamp or step | Debugging, incident analysis |
| **Artifact Hydration** | Reconstruct artifact state at a point in time | Evidence inspection |
| **Lineage Traversal** | Walk the lineage graph from any node | Explainability, governance |
| **Snapshot Restore** | Restore system state from a snapshot | Recovery, comparison |
| **Timeline Playback** | Chronological event replay | Operator review, training |

### 2.2 Replay Pipeline

```
Source Data
    │
    ├── Events (log_events table)
    ├── Artifacts (artifacts table + filesystem)
    ├── Snapshots (run_snapshots table)
    ├── Lineage (traceability_links table)
    └── Governance (governance_evaluations table)
    │
    ▼
Replay Engine
    │
    ├── Event Reconstructor
    │   ├── Chronological ordering
    │   ├── Deduplication
    │   └── Causality validation
    │
    ├── Artifact Hydrator
    │   ├── Content loading (filesystem)
    │   ├── Hash verification
    │   └── Metadata reconstruction
    │
    ├── Lineage Reconstructor
    │   ├── Graph building
    │   ├── Cycle detection
    │   └── Coverage validation
    │
    ├── Snapshot Reconstructor
    │   ├── State assembly
    │   ├── Artifact state binding
    │   └── Governance summary binding
    │
    └── Governance Reconstructor
        ├── Policy loading
        ├── Evaluation replay
        └── Decision verification
    │
    ▼
Replay Output
    │
    ├── Execution Timeline
    ├── Artifact Graph
    ├── Lineage Tree
    ├── Governance Report
    └── Divergence Report
```

---

## 3. Replay Comparator

### 3.1 Comparison Dimensions

```python
class ReplayComparator:
    """Validates replay fidelity against baseline."""
    
    def compare(self, baseline: dict, replay: dict) -> ComparisonResult:
        return ComparisonResult(
            artifact_count_match=self._compare_counts(baseline, replay),
            artifact_hashes_match=self._compare_hashes(baseline, replay),
            lineage_structure_match=self._compare_lineage(baseline, replay),
            event_sequence_match=self._compare_events(baseline, replay),
            governance_outcomes_match=self._compare_governance(baseline, replay),
            snapshot_equivalence=self._compare_snapshots(baseline, replay),
        )
    
    def _compare_counts(self, baseline, replay):
        """Artifact and link counts must match exactly."""
        return (
            baseline["artifacts_total"] == replay["artifacts_total"]
            and baseline["traceability_links_total"] == replay["traceability_links_total"]
            and baseline["timeline_events_total"] == replay["timeline_events_total"]
        )
    
    def _compare_hashes(self, baseline, replay):
        """Artifact content hashes must match for deterministic replay."""
        baseline_hashes = {a["id"]: a["content_hash"] for a in baseline["artifacts"]}
        replay_hashes = {a["id"]: a["content_hash"] for a in replay["artifacts"]}
        return baseline_hashes == replay_hashes
    
    def _compare_lineage(self, baseline, replay):
        """Lineage graph structure must be isomorphic."""
        baseline_edges = set(
            (l["source_type"], l["source_id"], l["target_type"], l["target_id"])
            for l in baseline["traceability_links"]
        )
        replay_edges = set(
            (l["source_type"], l["source_id"], l["target_type"], l["target_id"])
            for l in replay["traceability_links"]
        )
        return baseline_edges == replay_edges
    
    def _compare_events(self, baseline, replay):
        """Event sequence must be semantically equivalent."""
        baseline_sequence = [e["type"] for e in baseline["events"]]
        replay_sequence = [e["type"] for e in replay["events"]]
        return baseline_sequence == replay_sequence
    
    def _compare_governance(self, baseline, replay):
        """Governance decisions must be identical."""
        baseline_decisions = {
            e["policy_id"]: e["decision"]
            for e in baseline["governance_evaluations"]
        }
        replay_decisions = {
            e["policy_id"]: e["decision"]
            for e in replay["governance_evaluations"]
        }
        return baseline_decisions == replay_decisions
    
    def _compare_snapshots(self, baseline, replay):
        """Snapshot state must be equivalent."""
        return (
            baseline["snapshot"]["artifacts_total"] == replay["snapshot"]["artifacts_total"]
            and baseline["snapshot"]["governance_pass"] == replay["snapshot"]["governance_pass"]
            and baseline["snapshot"]["governance_fail"] == replay["snapshot"]["governance_fail"]
        )
```

### 3.2 Divergence Detection

```python
class DivergenceReport:
    """Reports replay drift from baseline."""
    
    def __init__(self):
        self.divergences: list[Divergence] = []
        self.severity: str = "none"  # none, low, medium, high, critical
        self.replay_integrity_score: float = 1.0
    
    def add_divergence(self, dimension: str, expected: Any, actual: Any):
        self.divergences.append(Divergence(
            dimension=dimension,
            expected=expected,
            actual=actual,
            severity=self._classify(dimension, expected, actual)
        ))
        self._recalculate_score()
    
    def _classify(self, dimension, expected, actual):
        if dimension == "artifact_hashes":
            return "critical"  # Content changed = tampering or non-determinism
        if dimension == "governance_outcomes":
            return "high"  # Policy decisions changed
        if dimension == "lineage_structure":
            return "high"  # Traceability broken
        if dimension == "event_sequence":
            return "medium"  # Ordering changed
        if dimension == "artifact_count":
            return "medium"  # Missing or extra artifacts
        return "low"
    
    def _recalculate_score(self):
        weights = {"critical": 0.0, "high": 0.25, "medium": 0.5, "low": 0.75, "none": 1.0}
        if not self.divergences:
            self.replay_integrity_score = 1.0
            return
        scores = [weights[d.severity] for d in self.divergences]
        self.replay_integrity_score = sum(scores) / len(scores)
```

---

## 4. Replay API Endpoints

### 4.1 Full Replay
```
GET /api/v1/replay/runs/{run_id}/full
```
Returns complete execution reconstruction.

### 4.2 Partial Replay
```
GET /api/v1/replay/runs/{run_id}/partial?from_step=5&to_step=10
```
Returns execution fragment.

### 4.3 Artifact Hydration
```
GET /api/v1/replay/artifacts/{artifact_id}/hydrate
```
Returns artifact with full content and lineage.

### 4.4 Lineage Traversal
```
GET /api/v1/replay/lineage/{artifact_id}/traverse?direction=upstream&depth=5
```
Returns lineage subtree.

### 4.5 Timeline Playback
```
GET /api/v1/replay/runs/{run_id}/timeline?speed=1.0&from=0&to=84
```
Returns ordered events for playback.

### 4.6 Replay Comparison
```
POST /api/v1/replay/compare
Body: { "baseline_run_id": "...", "replay_run_id": "..." }
```
Returns divergence report.

---

## 5. Replay Integrity Score

The replay integrity score measures how faithfully a replay reconstructs the baseline:

| Score | Meaning |
|-------|---------|
| 1.000 | Perfect replay — no divergence |
| 0.900-0.999 | Minor divergence — acceptable for non-critical analysis |
| 0.700-0.899 | Moderate divergence — investigation required |
| 0.500-0.699 | Significant divergence — replay unreliable |
| 0.000-0.499 | Critical divergence — replay failed |

---

## 6. Baseline Replay Validation

For the FIRST_OPERATIONAL_VERTICAL_SLICE baseline, the following must hold:

```python
BASELINE_REPLAY_CONTRACT = {
    "run_id": "0117b69b-3898-4ea4-83b0-8dc793c24d02",
    "expected_artifacts": 41,
    "expected_traceability_links": 76,
    "expected_governance_pass": 6,
    "expected_governance_fail": 4,
    "expected_timeline_events": 84,
    "expected_requirements_covered": 14,
    "expected_snapshots": 1,
    "minimum_integrity_score": 1.0,  # Perfect replay required for baseline
}
```
