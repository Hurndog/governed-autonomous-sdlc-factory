# Multi-Run Intelligence Specification

## 1. Purpose

The Cognitive Cortex currently operates as a single-run system. Future evolution requires understanding how cognition **across multiple runs** evolves, drifts, and improves.

This specification prepares the architecture for cross-run intelligence without implementing it yet.

## 2. Cross-Run Concepts

### 2.1 Lineage Comparison

Compare lineage graphs across runs to detect:
- **Structural drift** — lineage topology changed
- **Coverage drift** — requirement coverage changed
- **Governance drift** — policy outcomes changed
- **Artifact drift** — artifacts added/removed/changed

```python
class LineageComparator:
    """Compare lineage graphs across runs."""
    
    def compare(self, run_a: str, run_b: str) -> LineageDiff:
        graph_a = self.load_lineage(run_a)
        graph_b = self.load_lineage(run_b)
        
        return LineageDiff(
            added_edges=graph_b.edges - graph_a.edges,
            removed_edges=graph_a.edges - graph_b.edges,
            added_nodes=graph_b.nodes - graph_a.nodes,
            removed_nodes=graph_a.nodes - graph_b.nodes,
            coverage_change=self._compare_coverage(graph_a, graph_b),
            structural_similarity=self._graph_similarity(graph_a, graph_b)
        )
```

### 2.2 Governance Drift Analysis

Track how governance outcomes change across runs:

```python
class GovernanceDriftAnalyzer:
    """Analyze governance drift across runs."""
    
    def analyze(self, run_ids: list[str]) -> GovernanceDriftReport:
        evaluations = [self.load_governance(rid) for rid in run_ids]
        
        return GovernanceDriftReport(
            policy_stability=self._policy_stability(evaluations),
            outcome_trends=self._outcome_trends(evaluations),
            new_failures=self._new_failures(evaluations),
            resolved_failures=self._resolved_failures(evaluations),
            drift_score=self._drift_score(evaluations)
        )
```

### 2.3 Artifact Evolution

Track how artifacts evolve across runs:

```python
class ArtifactEvolutionTracker:
    """Track artifact evolution across runs."""
    
    def track(self, artifact_name: str, run_ids: list[str]) -> ArtifactEvolution:
        versions = []
        for run_id in run_ids:
            artifact = self.find_artifact(artifact_name, run_id)
            if artifact:
                versions.append(ArtifactVersion(
                    run_id=run_id,
                    content_hash=artifact.content_hash,
                    metadata=artifact.metadata_,
                    created_at=artifact.created_at
                ))
        
        return ArtifactEvolution(
            artifact_name=artifact_name,
            versions=versions,
            change_count=len(versions) - 1,
            stability_score=self._stability(versions),
            content_drift=self._content_drift(versions)
        )
```

### 2.4 Replay Divergence Analysis

Compare replay fidelity across runs:

```python
class ReplayDivergenceAnalyzer:
    """Analyze replay divergence patterns across runs."""
    
    def analyze(self, baseline_run: str, replay_runs: list[str]) -> DivergenceAnalysis:
        divergences = []
        for run_id in replay_runs:
            comparator = ReplayComparator()
            result = comparator.compare(baseline_run, run_id)
            divergences.append(result)
        
        return DivergenceAnalysis(
            baseline=baseline_run,
            replay_count=len(replay_runs),
            avg_integrity_score=mean(r.integrity_score for r in divergences),
            common_divergences=self._common_patterns(divergences),
            degradation_trend=self._degradation_trend(divergences),
            recommendations=self._recommendations(divergences)
        )
```

### 2.5 Policy Regression Analysis

Detect when policy changes cause unexpected failures:

```python
class PolicyRegressionAnalyzer:
    """Detect policy regressions across runs."""
    
    def analyze(self, policy_name: str, run_ids: list[str]) -> PolicyRegression:
        outcomes = []
        for run_id in run_ids:
            eval = self.find_evaluation(policy_name, run_id)
            if eval:
                outcomes.append(PolicyOutcome(
                    run_id=run_id,
                    decision=eval.decision,
                    findings=eval.findings,
                    policy_version=self.get_policy_version(policy_name, run_id)
                ))
        
        return PolicyRegression(
            policy_name=policy_name,
            outcomes=outcomes,
            regression_detected=self._detect_regression(outcomes),
            regression_cause=self._identify_cause(outcomes)
        )
```

## 3. Cross-Run Storage Schema

```sql
-- Cross-run comparison results
CREATE TABLE IF NOT EXISTS cross_run_comparisons (
    id VARCHAR(36) PRIMARY KEY,
    baseline_run_id VARCHAR(36) NOT NULL,
    comparison_run_id VARCHAR(36) NOT NULL,
    comparison_type VARCHAR(50) NOT NULL,  -- lineage, governance, artifact, replay
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Governance drift tracking
CREATE TABLE IF NOT EXISTS governance_drift (
    id VARCHAR(36) PRIMARY KEY,
    policy_name VARCHAR(200) NOT NULL,
    run_id VARCHAR(36) NOT NULL,
    decision VARCHAR(20) NOT NULL,
    findings JSONB DEFAULT '[]',
    policy_version INTEGER DEFAULT 1,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Artifact evolution tracking
CREATE TABLE IF NOT EXISTS artifact_evolution (
    id VARCHAR(36) PRIMARY KEY,
    artifact_name VARCHAR(255) NOT NULL,
    run_id VARCHAR(36) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL,
    version INTEGER DEFAULT 1,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 4. Implementation Phases

### Phase 1: Data Collection (Current)
- Ensure all run data is persisted with proper metadata
- Hash all artifacts for comparison
- Store governance outcomes with policy versions

### Phase 2: Comparison Engine (Next)
- Implement lineage comparison
- Implement governance drift analysis
- Implement artifact evolution tracking

### Phase 3: Intelligence Layer (Future)
- Pattern detection across runs
- Anomaly detection
- Predictive governance
- Automated regression detection

### Phase 4: Visualization (Future)
- Cross-run comparison views
- Drift visualization
- Evolution timelines
- Regression alerts
