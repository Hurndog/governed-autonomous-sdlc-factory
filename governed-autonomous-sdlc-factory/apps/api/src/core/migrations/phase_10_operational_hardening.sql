-- =============================================================================
-- MIGRATION: Phase 10-16 — Operational Hardening
-- =============================================================================
-- Adds hashing columns to existing tables
-- Creates replay session, integrity, and semantic graph tables
-- =============================================================================

-- =============================================================================
-- 1. HASHING COLUMNS ON EXISTING TABLES
-- =============================================================================

-- log_events: event_hash + parent_hash for chain integrity
ALTER TABLE log_events ADD COLUMN IF NOT EXISTS event_hash VARCHAR(64);
ALTER TABLE log_events ADD COLUMN IF NOT EXISTS parent_hash VARCHAR(64);
ALTER TABLE log_events ADD COLUMN IF NOT EXISTS chain_hash VARCHAR(64);

-- snapshots: snapshot_hash + chain_hash
ALTER TABLE run_snapshots ADD COLUMN IF NOT EXISTS snapshot_hash VARCHAR(64);
ALTER TABLE run_snapshots ADD COLUMN IF NOT EXISTS chain_hash VARCHAR(64);
ALTER TABLE run_snapshots ADD COLUMN IF NOT EXISTS parent_hash VARCHAR(64);

-- artifacts: artifact_hash (content-addressable)
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS artifact_hash VARCHAR(64);
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS parent_hash VARCHAR(64);

-- traceability_links: edge_hash
ALTER TABLE traceability_links ADD COLUMN IF NOT EXISTS edge_hash VARCHAR(64);

-- governance_evaluations: integrity_hash
ALTER TABLE governance_evaluations ADD COLUMN IF NOT EXISTS integrity_hash VARCHAR(64);

-- runs: chain_hash + integrity_hash for run-level integrity
ALTER TABLE runs ADD COLUMN IF NOT EXISTS chain_hash VARCHAR(64);
ALTER TABLE runs ADD COLUMN IF NOT EXISTS integrity_hash VARCHAR(64);

-- evidence_bundles: bundle_hash already exists, add chain_hash
ALTER TABLE evidence_bundles ADD COLUMN IF NOT EXISTS chain_hash VARCHAR(64);

-- run_checkpoints: state_hash
ALTER TABLE run_checkpoints ADD COLUMN IF NOT EXISTS state_hash VARCHAR(64);

-- =============================================================================
-- 2. REPLAY SESSION TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS replay_sessions (
    id VARCHAR(36) PRIMARY KEY,
    source_run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    replay_mode VARCHAR(30) NOT NULL DEFAULT 'full',  -- full, phase, event, snapshot, semantic
    status VARCHAR(30) NOT NULL DEFAULT 'pending',     -- pending, running, completed, failed, diverged
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    total_events_replayed INTEGER DEFAULT 0,
    total_artifacts_replayed INTEGER DEFAULT 0,
    total_governance_replayed INTEGER DEFAULT 0,
    divergence_count INTEGER DEFAULT 0,
    integrity_score FLOAT DEFAULT 0.0,
    replay_hash VARCHAR(64),
    parent_replay_id VARCHAR(36) REFERENCES replay_sessions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_replay_sessions_source_run ON replay_sessions(source_run_id);
CREATE INDEX IF NOT EXISTS idx_replay_sessions_status ON replay_sessions(status);

-- =============================================================================
-- 3. REPLAY EVENTS TABLE (captured during replay)
-- =============================================================================

CREATE TABLE IF NOT EXISTS replay_events (
    id VARCHAR(36) PRIMARY KEY,
    replay_session_id VARCHAR(36) NOT NULL REFERENCES replay_sessions(id),
    original_event_id VARCHAR(36),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    message TEXT NOT NULL,
    source_file VARCHAR(500),
    phase_id VARCHAR(36),
    trace_id VARCHAR(100),
    event_hash VARCHAR(64),
    parent_hash VARCHAR(64),
    replayed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    divergence_detected BOOLEAN DEFAULT FALSE,
    divergence_details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_replay_events_session ON replay_events(replay_session_id);
CREATE INDEX IF NOT EXISTS idx_replay_events_type ON replay_events(event_type);

-- =============================================================================
-- 4. INTEGRITY VERIFICATION TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS integrity_verifications (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    replay_session_id VARCHAR(36) REFERENCES replay_sessions(id),
    verification_type VARCHAR(50) NOT NULL,  -- event_chain, snapshot, artifact, replay, timeline
    status VARCHAR(20) NOT NULL,             -- pass, fail, warning
    integrity_score FLOAT DEFAULT 0.0,
    expected_hash VARCHAR(64),
    actual_hash VARCHAR(64),
    details JSONB DEFAULT '{}',
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_integrity_verifications_run ON integrity_verifications(run_id);
CREATE INDEX IF NOT EXISTS idx_integrity_verifications_type ON integrity_verifications(verification_type);
CREATE INDEX IF NOT EXISTS idx_integrity_verifications_status ON integrity_verifications(status);

-- =============================================================================
-- 5. DIVERGENCE RECORDS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS divergence_records (
    id VARCHAR(36) PRIMARY KEY,
    replay_session_id VARCHAR(36) NOT NULL REFERENCES replay_sessions(id),
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    divergence_type VARCHAR(50) NOT NULL,    -- event_sequence, artifact, governance, timing, topology
    severity VARCHAR(20) NOT NULL,           -- critical, high, medium, low, info
    divergence_location VARCHAR(200),
    expected_value JSONB,
    actual_value JSONB,
    causal_impact TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_divergence_replay_session ON divergence_records(replay_session_id);
CREATE INDEX IF NOT EXISTS idx_divergence_run ON divergence_records(run_id);
CREATE INDEX IF NOT EXISTS idx_divergence_severity ON divergence_records(severity);

-- =============================================================================
-- 6. SEMANTIC EXECUTION GRAPH NODES
-- =============================================================================

CREATE TABLE IF NOT EXISTS semantic_graph_nodes (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    node_type VARCHAR(50) NOT NULL,          -- artifact, phase, governance, event, snapshot, decision
    entity_id VARCHAR(36) NOT NULL,
    entity_name VARCHAR(500),
    semantic_type VARCHAR(100),              -- specification_evolution, architecture_evolution, governance_evolution
    from_state JSONB,
    to_state JSONB,
    transition_reason TEXT,
    node_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_semantic_nodes_run ON semantic_graph_nodes(run_id);
CREATE INDEX IF NOT EXISTS idx_semantic_nodes_type ON semantic_graph_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_semantic_nodes_entity ON semantic_graph_nodes(entity_id);

-- =============================================================================
-- 7. SEMANTIC EXECUTION GRAPH EDGES
-- =============================================================================

CREATE TABLE IF NOT EXISTS semantic_graph_edges (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    source_node_id VARCHAR(36) NOT NULL REFERENCES semantic_graph_nodes(id),
    target_node_id VARCHAR(36) NOT NULL REFERENCES semantic_graph_nodes(id),
    edge_type VARCHAR(50) NOT NULL,          -- causal, temporal, dependency, evolution, governance
    edge_label VARCHAR(200),
    edge_weight FLOAT DEFAULT 1.0,
    edge_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_semantic_edges_run ON semantic_graph_edges(run_id);
CREATE INDEX IF NOT EXISTS idx_semantic_edges_source ON semantic_graph_edges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_semantic_edges_target ON semantic_graph_edges(target_node_id);

-- =============================================================================
-- 8. REPLAY MANIFESTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS replay_manifests (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    replay_session_id VARCHAR(36) REFERENCES replay_sessions(id),
    manifest_type VARCHAR(30) NOT NULL,      -- full, phase, artifact, governance
    manifest_data JSONB NOT NULL DEFAULT '{}',
    manifest_hash VARCHAR(64),
    event_count INTEGER DEFAULT 0,
    artifact_count INTEGER DEFAULT 0,
    traceability_count INTEGER DEFAULT 0,
    governance_count INTEGER DEFAULT 0,
    snapshot_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_replay_manifests_run ON replay_manifests(run_id);
CREATE INDEX IF NOT EXISTS idx_replay_manifests_replay ON replay_manifests(replay_session_id);

-- =============================================================================
-- 9. EXECUTION BASELINE PACKAGES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS execution_baselines (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    baseline_name VARCHAR(200) NOT NULL,
    baseline_version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(30) DEFAULT 'generating',  -- generating, complete, verified, archived
    package_path VARCHAR(500),
    package_hash VARCHAR(64),
    artifact_count INTEGER DEFAULT 0,
    event_count INTEGER DEFAULT 0,
    traceability_count INTEGER DEFAULT 0,
    governance_count INTEGER DEFAULT 0,
    integrity_score FLOAT DEFAULT 0.0,
    baseline_manifest JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_execution_baselines_run ON execution_baselines(run_id);
CREATE INDEX IF NOT EXISTS idx_execution_baselines_name ON execution_baselines(baseline_name);

-- =============================================================================
-- 10. TELEMETRY TABLE FOR REPLAY/INTEGRITY METRICS
-- =============================================================================

CREATE TABLE IF NOT EXISTS replay_telemetry (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) REFERENCES runs(id),
    replay_session_id VARCHAR(36) REFERENCES replay_sessions(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    metric_labels JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_replay_telemetry_run ON replay_telemetry(run_id);
CREATE INDEX IF NOT EXISTS idx_replay_telemetry_name ON replay_telemetry(metric_name);
CREATE INDEX IF NOT EXISTS idx_replay_telemetry_replay ON replay_telemetry(replay_session_id);
