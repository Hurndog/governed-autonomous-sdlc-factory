-- Phase 11: Semantic Coverage and Test Alignment
-- Database migration for semantic coverage tables

-- 1. Requirement Normalizations
CREATE TABLE IF NOT EXISTS requirement_normalizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    original_text TEXT,
    normalized_statement TEXT NOT NULL,
    actor VARCHAR(128),
    action VARCHAR(256),
    object VARCHAR(256),
    constraints_json JSONB DEFAULT '{}',
    expected_behavior TEXT,
    failure_behavior TEXT,
    governance_relevance BOOLEAN DEFAULT FALSE,
    security_relevance BOOLEAN DEFAULT FALSE,
    evidence_required_json JSONB DEFAULT '[]',
    criticality VARCHAR(32) DEFAULT 'medium',
    ambiguity_score REAL DEFAULT 0.0,
    testability_score REAL DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(run_id, requirement_id)
);

CREATE INDEX IF NOT EXISTS idx_req_norm_run ON requirement_normalizations(run_id);
CREATE INDEX IF NOT EXISTS idx_req_norm_criticality ON requirement_normalizations(criticality);

-- 2. Acceptance Criteria Contracts
CREATE TABLE IF NOT EXISTS acceptance_criteria_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    acceptance_criterion_id VARCHAR(64) NOT NULL,
    given_text TEXT,
    when_text TEXT,
    then_text TEXT NOT NULL,
    and_conditions_json JSONB DEFAULT '[]',
    evidence_required_json JSONB DEFAULT '[]',
    negative_case_required BOOLEAN DEFAULT FALSE,
    governance_case_required BOOLEAN DEFAULT FALSE,
    security_case_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(run_id, acceptance_criterion_id)
);

CREATE INDEX IF NOT EXISTS idx_ac_run ON acceptance_criteria_contracts(run_id);
CREATE INDEX IF NOT EXISTS idx_ac_requirement ON acceptance_criteria_contracts(requirement_id);

-- 3. Test Obligations
CREATE TABLE IF NOT EXISTS test_obligations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    acceptance_criterion_id VARCHAR(64),
    obligation_id VARCHAR(64) NOT NULL,
    obligation_type VARCHAR(64) NOT NULL,
    proof_statement TEXT NOT NULL,
    required_test_type VARCHAR(32),
    required_evidence_type VARCHAR(64),
    criticality VARCHAR(32) DEFAULT 'medium',
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(run_id, obligation_id)
);

CREATE INDEX IF NOT EXISTS idx_to_run ON test_obligations(run_id);
CREATE INDEX IF NOT EXISTS idx_to_requirement ON test_obligations(requirement_id);
CREATE INDEX IF NOT EXISTS idx_to_status ON test_obligations(status);

-- 4. Semantic Alignment Evaluations
CREATE TABLE IF NOT EXISTS semantic_alignment_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    test_case_id VARCHAR(64) NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    acceptance_criterion_id VARCHAR(64),
    obligation_id VARCHAR(64) NOT NULL,
    semantic_alignment_score REAL DEFAULT 0.0,
    coverage_score REAL DEFAULT 0.0,
    evidence_score REAL DEFAULT 0.0,
    verifier_verdict VARCHAR(32),
    critique TEXT,
    missing_assertions_json JSONB DEFAULT '[]',
    missing_edge_cases_json JSONB DEFAULT '[]',
    can_broken_code_pass BOOLEAN DEFAULT TRUE,
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sae_run ON semantic_alignment_evaluations(run_id);
CREATE INDEX IF NOT EXISTS idx_sae_test ON semantic_alignment_evaluations(test_case_id);

-- 5. Verifier Critiques
CREATE TABLE IF NOT EXISTS verifier_critiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    test_case_id VARCHAR(64) NOT NULL,
    obligation_id VARCHAR(64) NOT NULL,
    verifier_model VARCHAR(64) DEFAULT 'deterministic',
    prompt_hash VARCHAR(64),
    response_hash VARCHAR(64),
    verdict VARCHAR(32),
    confidence REAL DEFAULT 0.0,
    critique TEXT,
    recommendations_json JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vc_run ON verifier_critiques(run_id);

-- 6. Mutation Tests
CREATE TABLE IF NOT EXISTS mutation_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    obligation_id VARCHAR(64),
    mutation_id VARCHAR(64) NOT NULL,
    mutation_type VARCHAR(64) NOT NULL,
    mutated_component VARCHAR(128),
    mutation_description TEXT,
    expected_test_failure BOOLEAN DEFAULT TRUE,
    actual_test_result VARCHAR(32),
    killed BOOLEAN DEFAULT FALSE,
    survived BOOLEAN DEFAULT FALSE,
    mutation_score_impact REAL DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(run_id, mutation_id)
);

CREATE INDEX IF NOT EXISTS idx_mt_run ON mutation_tests(run_id);
CREATE INDEX IF NOT EXISTS idx_mt_survived ON mutation_tests(survived);

-- 7. Negative Test Requirements
CREATE TABLE IF NOT EXISTS negative_test_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    acceptance_criterion_id VARCHAR(64),
    required_negative_case TEXT NOT NULL,
    generated_test_id VARCHAR(64),
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ntr_run ON negative_test_requirements(run_id);

-- 8. Runtime Evidence Bindings
CREATE TABLE IF NOT EXISTS runtime_evidence_bindings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    test_case_id VARCHAR(64) NOT NULL,
    obligation_id VARCHAR(64),
    evidence_type VARCHAR(64) NOT NULL,
    evidence_ref VARCHAR(256),
    evidence_hash VARCHAR(64),
    binding_status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reb_run ON runtime_evidence_bindings(run_id);

-- 9. Semantic Coverage Reports
CREATE TABLE IF NOT EXISTS semantic_coverage_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL UNIQUE,
    obligation_coverage_score REAL DEFAULT 0.0,
    semantic_alignment_score REAL DEFAULT 0.0,
    mutation_score REAL DEFAULT 0.0,
    negative_coverage_score REAL DEFAULT 0.0,
    runtime_evidence_score REAL DEFAULT 0.0,
    verifier_confidence_score REAL DEFAULT 0.0,
    overall_semantic_coverage_score REAL DEFAULT 0.0,
    critical_requirements_passed BOOLEAN DEFAULT FALSE,
    release_gate_status VARCHAR(32) DEFAULT 'pending',
    report_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scr_run ON semantic_coverage_reports(run_id);
CREATE INDEX IF NOT EXISTS idx_scr_gate ON semantic_coverage_reports(release_gate_status);

-- 10. Semantic Coverage Waivers
CREATE TABLE IF NOT EXISTS semantic_coverage_waivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    requirement_id VARCHAR(64) NOT NULL,
    obligation_id VARCHAR(64),
    waiver_reason TEXT NOT NULL,
    waiver_scope VARCHAR(32) DEFAULT 'obligation',
    approved_by VARCHAR(128),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scw_run ON semantic_coverage_waivers(run_id);

-- Add semantic_coverage columns to integrity_verifications
ALTER TABLE integrity_verifications ADD COLUMN IF NOT EXISTS semantic_coverage_score REAL DEFAULT NULL;
ALTER TABLE integrity_verifications ADD COLUMN IF NOT EXISTS semantic_coverage_status VARCHAR(32) DEFAULT 'pre_semantic_coverage';
