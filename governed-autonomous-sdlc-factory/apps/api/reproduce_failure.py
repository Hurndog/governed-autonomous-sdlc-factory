"""Reproduce the persistence failure: run full pipeline twice, check for duplicates."""
import os
import sys

os.chdir("/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api")
sys.path.insert(0, "src")

from sqlalchemy import text
from src.core.database import SyncSessionLocal, engine as sa_engine
from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
    NegativeTestRequirement, RuntimeEvidenceBinding, SemanticCoverageReport,
    SemanticCoverageWaiver,
)
from src.engines.semantic_coverage_engine import SemanticCoverageEngine

RUN_ID = "6a7f7ea0-297f-435e-9bb2-899368c7d332"

TABLES = [
    ("requirement_normalizations", RequirementNormalization),
    ("acceptance_criteria_contracts", AcceptanceCriteriaContract),
    ("test_obligations", TestObligation),
    ("semantic_alignment_evaluations", SemanticAlignmentEvaluation),
    ("verifier_critiques", VerifierCritique),
    ("mutation_tests", MutationTest),
    ("negative_test_requirements", NegativeTestRequirement),
    ("runtime_evidence_bindings", RuntimeEvidenceBinding),
    ("semantic_coverage_reports", SemanticCoverageReport),
    ("semantic_coverage_waivers", SemanticCoverageWaiver),
]


def count_records(db, run_id):
    counts = {}
    for table_name, model in TABLES:
        count = db.query(model).filter(model.run_id == run_id).count()
        counts[table_name] = count
    return counts


def count_records_raw(db, run_id):
    counts = {}
    for table_name, _ in TABLES:
        result = db.execute(
            text(f"SELECT COUNT(*) FROM {table_name} WHERE run_id = :rid"),
            {"rid": run_id}
        )
        counts[table_name] = result.scalar()
    return counts


def main():
    db = SyncSessionLocal()
    engine = SemanticCoverageEngine(db)

    print("=" * 60)
    print("REPRODUCTION: Full pipeline run twice")
    print("=" * 60)

    # Clean slate
    print("\n[1] Cleaning all semantic records...")
    for table_name, _ in TABLES:
        db.execute(text(f"DELETE FROM {table_name} WHERE run_id = :rid"), {"rid": RUN_ID})
    db.commit()
    db.expire_all()
    print("  Cleaned.")

    # First run
    print("\n[2] First full pipeline run...")
    try:
        report1 = engine.run_full_semantic_coverage(RUN_ID)
        print(f"  Report: score={report1.overall_semantic_coverage_score}, gate={report1.release_gate_status}")
    except Exception as e:
        print(f"  ERROR on first run: {e}")
        db.rollback()
        return

    counts_after_first = count_records(db, RUN_ID)
    print("\n  Counts after first run:")
    for t, c in counts_after_first.items():
        print(f"    {t}: {c}")

    # Second run (idempotency test)
    print("\n[3] Second full pipeline run (idempotency)...")
    try:
        report2 = engine.run_full_semantic_coverage(RUN_ID)
        print(f"  Report: score={report2.overall_semantic_coverage_score}, gate={report2.release_gate_status}")
    except Exception as e:
        print(f"  ERROR on second run: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

        # Check raw counts after failure
        db.expire_all()
        counts_after_fail = count_records_raw(db, RUN_ID)
        print("\n  Raw counts after failure:")
        for t, c in counts_after_fail.items():
            print(f"    {t}: {c}")
        return

    counts_after_second = count_records(db, RUN_ID)
    print("\n  Counts after second run:")
    for t, c in counts_after_second.items():
        print(f"    {t}: {c}")

    # Compare
    print("\n[4] Idempotency check:")
    issues = []
    for t, c1 in counts_after_first.items():
        c2 = counts_after_second.get(t, 0)
        if c1 != c2:
            issues.append(f"  DUPLICATE: {t}: {c1} -> {c2} (delta: {c2 - c1})")
        else:
            print(f"  OK: {t}: {c1} == {c2}")

    if issues:
        print("\n  FAILURES:")
        for i in issues:
            print(i)
    else:
        print("\n  ALL COUNTS STABLE — idempotency confirmed.")

    # Check report table specifically
    print("\n[5] Report table check:")
    reports = db.query(SemanticCoverageReport).filter(
        SemanticCoverageReport.run_id == RUN_ID
    ).all()
    print(f"  Reports for run_id: {len(reports)}")
    if len(reports) > 1:
        print("  ERROR: Multiple reports for same run_id!")
        for r in reports:
            print(f"    id={r.id}, score={r.overall_semantic_coverage_score}, created={r.created_at}")

    db.close()


if __name__ == "__main__":
    main()
