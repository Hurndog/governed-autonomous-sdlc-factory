-- Phase 3: Create requirement_conflicts table for conflict detection evidence

CREATE TABLE IF NOT EXISTS requirement_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(36) NOT NULL,
    requirement_id_1 VARCHAR(64) NOT NULL,
    requirement_id_2 VARCHAR(64) NOT NULL,
    conflict_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    explanation TEXT NOT NULL,
    recommended_resolution TEXT,
    release_gate_impact VARCHAR(16) NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_req_conflicts_run_id') THEN
        CREATE INDEX idx_req_conflicts_run_id ON requirement_conflicts(run_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_req_conflicts_type') THEN
        CREATE INDEX idx_req_conflicts_type ON requirement_conflicts(conflict_type);
    END IF;
END$$;
