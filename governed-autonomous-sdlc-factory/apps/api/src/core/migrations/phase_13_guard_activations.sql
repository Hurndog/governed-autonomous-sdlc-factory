-- Phase 13: Create guard_activations table for operational safety evidence

-- Enable pgcrypto for gen_random_uuid() if not already enabled
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the guard activations table
CREATE TABLE IF NOT EXISTS guard_activations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(36) NOT NULL,
    phase_name VARCHAR(128),
    guard_name VARCHAR(64) NOT NULL,
    configured_limit VARCHAR(256) NOT NULL,
    observed_value VARCHAR(256) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resulting_status VARCHAR(64) NOT NULL,
    message TEXT,
    is_recoverable BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Create indexes separately so they don't fail if the table already exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_guard_activations_run_id') THEN
        CREATE INDEX idx_guard_activations_run_id ON guard_activations(run_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_guard_activations_guard_name') THEN
        CREATE INDEX idx_guard_activations_guard_name ON guard_activations(guard_name);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_guard_activations_timestamp') THEN
        CREATE INDEX idx_guard_activations_timestamp ON guard_activations(timestamp);
    END IF;
END$$;
