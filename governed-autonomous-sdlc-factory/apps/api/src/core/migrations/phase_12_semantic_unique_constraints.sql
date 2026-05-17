-- Phase E: Add missing unique constraints for semantic coverage tables
-- These protect against duplicate records at the database level
-- even if application-level upsert logic has race conditions.

-- semantic_alignment_evaluations: natural key = (run_id, test_case_id, obligation_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'uq_sem_align_run_tc_obl'
    ) THEN
        ALTER TABLE semantic_alignment_evaluations
            ADD CONSTRAINT uq_sem_align_run_tc_obl
            UNIQUE (run_id, test_case_id, obligation_id);
        RAISE NOTICE 'Added UQ on semantic_alignment_evaluations(run_id, test_case_id, obligation_id)';
    ELSE
        RAISE NOTICE 'UQ already exists on semantic_alignment_evaluations';
    END IF;
END$$;

-- verifier_critiques: natural key = (run_id, test_case_id, obligation_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'uq_ver_crit_run_tc_obl'
    ) THEN
        ALTER TABLE verifier_critiques
            ADD CONSTRAINT uq_ver_crit_run_tc_obl
            UNIQUE (run_id, test_case_id, obligation_id);
        RAISE NOTICE 'Added UQ on verifier_critiques(run_id, test_case_id, obligation_id)';
    ELSE
        RAISE NOTICE 'UQ already exists on verifier_critiques';
    END IF;
END$$;

-- negative_test_requirements: natural key = (run_id, requirement_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'uq_neg_req_run_req'
    ) THEN
        ALTER TABLE negative_test_requirements
            ADD CONSTRAINT uq_neg_req_run_req
            UNIQUE (run_id, requirement_id);
        RAISE NOTICE 'Added UQ on negative_test_requirements(run_id, requirement_id)';
    ELSE
        RAISE NOTICE 'UQ already exists on negative_test_requirements';
    END IF;
END$$;

-- runtime_evidence_bindings: natural key = (run_id, test_case_id, obligation_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'uq_ev_bind_run_tc_obl'
    ) THEN
        ALTER TABLE runtime_evidence_bindings
            ADD CONSTRAINT uq_ev_bind_run_tc_obl
            UNIQUE (run_id, test_case_id, obligation_id);
        RAISE NOTICE 'Added UQ on runtime_evidence_bindings(run_id, test_case_id, obligation_id)';
    ELSE
        RAISE NOTICE 'UQ already exists on runtime_evidence_bindings';
    END IF;
END$$;
