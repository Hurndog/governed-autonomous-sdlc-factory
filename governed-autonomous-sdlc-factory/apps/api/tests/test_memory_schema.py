"""Persistent Runtime Memory & Drift Control Plane — Database Schema.

Creates the tables needed for:
1. Decision Memory
2. Case Memory
3. Semantic Memory
4. Governance Memory
5. Operator Intervention Memory
6. Drift Events
7. Metacognitive State
8. Runtime Trust Scores
9. Context Validity
10. Memory Versions

All tables are workspace-aware, project-aware, and version-aware.
"""
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import text
from src.core.sync_database import SyncSessionLocal, sync_engine
from src.core.database import init_sync_db


def create_memory_tables(db):
    """Create all memory and drift control tables."""

    # 1. Decision Memory
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS decision_memory (
            id VARCHAR(36) PRIMARY KEY,
            run_id VARCHAR(36),
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            decision_type VARCHAR(64) NOT NULL,
            decision_context JSONB DEFAULT '{}',
            rationale TEXT,
            governance_basis JSONB DEFAULT '[]',
            evidence_references JSONB DEFAULT '[]',
            confidence_score REAL DEFAULT 0.5,
            autonomy_level VARCHAR(32) DEFAULT 'full',
            operator_override BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            valid_until TIMESTAMPTZ,
            is_active BOOLEAN DEFAULT TRUE
        )
    """))

    # 2. Case Memory
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS case_memory (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            case_type VARCHAR(64) NOT NULL,
            case_context JSONB DEFAULT '{}',
            business_context TEXT,
            prior_state JSONB DEFAULT '{}',
            current_state JSONB DEFAULT '{}',
            state_transitions JSONB DEFAULT '[]',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE
        )
    """))

    # 3. Semantic Memory
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS semantic_memory (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            memory_type VARCHAR(64) NOT NULL,
            entity_type VARCHAR(64),
            entity_id VARCHAR(36),
            semantic_content JSONB DEFAULT '{}',
            ontology_version VARCHAR(32),
            specification_lineage JSONB DEFAULT '[]',
            requirement_evolution JSONB DEFAULT '[]',
            drift_score REAL DEFAULT 0.0,
            confidence REAL DEFAULT 1.0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            valid_until TIMESTAMPTZ,
            is_active BOOLEAN DEFAULT TRUE
        )
    """))

    # 4. Governance Memory
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS governance_memory (
            id VARCHAR(36) PRIMARY KEY,
            run_id VARCHAR(36),
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            event_type VARCHAR(64) NOT NULL,
            policy_id VARCHAR(36),
            escalation_level VARCHAR(32) DEFAULT 'none',
            override_reason TEXT,
            autonomy_before VARCHAR(32),
            autonomy_after VARCHAR(32),
            governance_basis JSONB DEFAULT '{}',
            evidence JSONB DEFAULT '{}',
            operator_id VARCHAR(36),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE
        )
    """))

    # 5. Operator Intervention Memory
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS operator_interventions (
            id VARCHAR(36) PRIMARY KEY,
            run_id VARCHAR(36),
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            operator_id VARCHAR(36),
            intervention_type VARCHAR(64) NOT NULL,
            intervention_context JSONB DEFAULT '{}',
            correction TEXT,
            prior_state JSONB DEFAULT '{}',
            corrected_state JSONB DEFAULT '{}',
            governance_impact JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # 6. Drift Events
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS drift_events (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            drift_type VARCHAR(64) NOT NULL,
            drift_category VARCHAR(64) NOT NULL,
            severity VARCHAR(32) NOT NULL DEFAULT 'low',
            drift_score REAL NOT NULL DEFAULT 0.0,
            threshold REAL NOT NULL DEFAULT 0.5,
            detection_context JSONB DEFAULT '{}',
            evidence JSONB DEFAULT '{}',
            prior_state JSONB DEFAULT '{}',
            current_state JSONB DEFAULT '{}',
            recommended_action TEXT,
            action_taken TEXT,
            autonomy_impact VARCHAR(32) DEFAULT 'none',
            detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            resolved_at TIMESTAMPTZ,
            is_resolved BOOLEAN DEFAULT FALSE
        )
    """))

    # 7. Metacognitive State
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS metacognitive_state (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            state_type VARCHAR(64) NOT NULL,
            overall_trust_score REAL DEFAULT 1.0,
            semantic_confidence REAL DEFAULT 1.0,
            governance_confidence REAL DEFAULT 1.0,
            memory_integrity_score REAL DEFAULT 1.0,
            replay_integrity_score REAL DEFAULT 1.0,
            autonomy_level VARCHAR(32) DEFAULT 'full',
            escalation_level VARCHAR(32) DEFAULT 'none',
            active_warnings JSONB DEFAULT '[]',
            active_restrictions JSONB DEFAULT '[]',
            drift_summary JSONB DEFAULT '{}',
            last_evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # 8. Runtime Trust Scores
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS runtime_trust_scores (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            run_id VARCHAR(36),
            trust_dimension VARCHAR(64) NOT NULL,
            score REAL NOT NULL DEFAULT 1.0,
            confidence REAL NOT NULL DEFAULT 1.0,
            evidence JSONB DEFAULT '{}',
            degradation_factors JSONB DEFAULT '[]',
            scoring_context JSONB DEFAULT '{}',
            scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            valid_until TIMESTAMPTZ
        )
    """))

    # 9. Context Validity
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS context_validity (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            context_type VARCHAR(64) NOT NULL,
            context_key VARCHAR(128) NOT NULL,
            context_value JSONB DEFAULT '{}',
            validity_status VARCHAR(32) DEFAULT 'valid',
            valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            valid_until TIMESTAMPTZ,
            staleness_score REAL DEFAULT 0.0,
            last_validated_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # 10. Memory Versions
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS memory_versions (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            workspace_id VARCHAR(36),
            memory_type VARCHAR(64) NOT NULL,
            version_number INTEGER NOT NULL,
            content_snapshot JSONB DEFAULT '{}',
            change_type VARCHAR(32) NOT NULL,
            change_context JSONB DEFAULT '{}',
            prior_version_id VARCHAR(36),
            integrity_hash VARCHAR(64),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by VARCHAR(36)
        )
    """))

    # Create indexes for common queries
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_decision_memory_project ON decision_memory(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_decision_memory_run ON decision_memory(run_id)",
        "CREATE INDEX IF NOT EXISTS idx_decision_memory_type ON decision_memory(decision_type)",
        "CREATE INDEX IF NOT EXISTS idx_case_memory_project ON case_memory(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_semantic_memory_project ON semantic_memory(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_semantic_memory_type ON semantic_memory(memory_type)",
        "CREATE INDEX IF NOT EXISTS idx_governance_memory_project ON governance_memory(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_governance_memory_run ON governance_memory(run_id)",
        "CREATE INDEX IF NOT EXISTS idx_operator_interventions_project ON operator_interventions(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_drift_events_project ON drift_events(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_drift_events_type ON drift_events(drift_type)",
        "CREATE INDEX IF NOT EXISTS idx_drift_events_severity ON drift_events(severity)",
        "CREATE INDEX IF NOT EXISTS idx_drift_events_unresolved ON drift_events(is_resolved) WHERE is_resolved = FALSE",
        "CREATE INDEX IF NOT EXISTS idx_metacognitive_state_project ON metacognitive_state(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_runtime_trust_project ON runtime_trust_scores(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_runtime_trust_dimension ON runtime_trust_scores(trust_dimension)",
        "CREATE INDEX IF NOT EXISTS idx_context_validity_project ON context_validity(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_context_validity_status ON context_validity(validity_status)",
        "CREATE INDEX IF NOT EXISTS idx_memory_versions_project ON memory_versions(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_memory_versions_type ON memory_versions(memory_type)",
    ]

    for idx_sql in indexes:
        db.execute(text(idx_sql))

    db.commit()


def verify_tables(db):
    """Verify all tables were created."""
    expected = [
        'decision_memory', 'case_memory', 'semantic_memory',
        'governance_memory', 'operator_interventions', 'drift_events',
        'metacognitive_state', 'runtime_trust_scores', 'context_validity',
        'memory_versions'
    ]

    result = db.execute(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = ANY(:tables)
    """), {"tables": expected})

    found = {r[0] for r in result}
    missing = set(expected) - found

    return found, missing


def main():
    print("=" * 60)
    print("v0.3.4 PERSISTENT RUNTIME MEMORY — Schema Creation")
    print("=" * 60)

    init_sync_db()
    db = SyncSessionLocal()

    try:
        print("\n── Creating memory tables ──")
        create_memory_tables(db)

        print("\n── Verifying tables ──")
        found, missing = verify_tables(db)

        print(f"\n  Created: {len(found)}/10 tables")
        for t in sorted(found):
            print(f"    ✅ {t}")

        if missing:
            print(f"\n  Missing: {len(missing)}")
            for t in sorted(missing):
                print(f"    ❌ {t}")

        # Count total tables
        result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        total = result.scalar()
        print(f"\n  Total DB tables: {total}")

        return len(missing) == 0

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
