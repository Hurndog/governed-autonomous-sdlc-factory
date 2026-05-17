"""Reproduce: call individual methods twice without _clear_existing."""
import os
import sys

os.chdir("/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api")
sys.path.insert(0, "src")

from sqlalchemy import text
from src.core.database import SyncSessionLocal
from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
    NegativeTestRequirement, RuntimeEvidenceBinding, SemanticCoverageReport,
)
from src.engines.semantic_coverage_engine import SemanticCoverageEngine

RUN_ID = "6a7f7ea0-297f-435e-9bb2-899368c7d332"

db = SyncSessionLocal()
engine = SemanticCoverageEngine(db)

def count_all(label):
    models = [
        ("req_norm", RequirementNormalization),
        ("ac_contract", AcceptanceCriteriaContract),
        ("test_obl", TestObligation),
        ("sem_align", SemanticAlignmentEvaluation),
        ("ver_crit", VerifierCritique),
        ("mut_test", MutationTest),
        ("neg_req", NegativeTestRequirement),
        ("ev_bind", RuntimeEvidenceBinding),
        ("sem_report", SemanticCoverageReport),
    ]
    print(f"\n  {label}:")
    for name, model in models:
        c = db.query(model).filter(model.run_id == RUN_ID).count()
        print(f"    {name}: {c}")

print("=" * 60)
print("Test: Individual methods called twice WITHOUT _clear_existing")
print("=" * 60)

count_all("Before")

# Call each method once
print("\n[1] Calling each method once...")
engine.normalize_requirements(RUN_ID)
engine.validate_acceptance_criteria(RUN_ID)
engine.generate_test_obligations(RUN_ID)
engine.evaluate_test_alignment(RUN_ID)
engine.run_independent_verifier(RUN_ID)
engine.plan_mutation_tests(RUN_ID)
engine.evaluate_negative_test_coverage(RUN_ID)
engine.bind_runtime_evidence(RUN_ID)

count_all("After first call")

# Call each method again
print("\n[2] Calling each method again (no cleanup)...")
try:
    engine.normalize_requirements(RUN_ID)
    print("  normalize_requirements: OK")
except Exception as e:
    print(f"  normalize_requirements: ERROR - {e}")
    db.rollback()

try:
    engine.validate_acceptance_criteria(RUN_ID)
    print("  validate_acceptance_criteria: OK")
except Exception as e:
    print(f"  validate_acceptance_criteria: ERROR - {e}")
    db.rollback()

try:
    engine.generate_test_obligations(RUN_ID)
    print("  generate_test_obligations: OK")
except Exception as e:
    print(f"  generate_test_obligations: ERROR - {e}")
    db.rollback()

try:
    engine.evaluate_test_alignment(RUN_ID)
    print("  evaluate_test_alignment: OK")
except Exception as e:
    print(f"  evaluate_test_alignment: ERROR - {e}")
    db.rollback()

try:
    engine.run_independent_verifier(RUN_ID)
    print("  run_independent_verifier: OK")
except Exception as e:
    print(f"  run_independent_verifier: ERROR - {e}")
    db.rollback()

try:
    engine.plan_mutation_tests(RUN_ID)
    print("  plan_mutation_tests: OK")
except Exception as e:
    print(f"  plan_mutation_tests: ERROR - {e}")
    db.rollback()

try:
    engine.evaluate_negative_test_coverage(RUN_ID)
    print("  evaluate_negative_test_coverage: OK")
except Exception as e:
    print(f"  evaluate_negative_test_coverage: ERROR - {e}")
    db.rollback()

try:
    engine.bind_runtime_evidence(RUN_ID)
    print("  bind_runtime_evidence: OK")
except Exception as e:
    print(f"  bind_runtime_evidence: ERROR - {e}")
    db.rollback()

count_all("After second call")

db.close()
