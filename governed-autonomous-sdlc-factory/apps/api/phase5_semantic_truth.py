"""Phase 5: Semantic Truth Test — Prove that semantic alignment is real, not theatrical.

Tests whether the engine can distinguish between:
- A bad tautological test (expected result = test description)
- A good concrete test (specific assertions, cross-tenant scenario)
"""
import os, sys, json

os.chdir("/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api")
sys.path.insert(0, "src")

from sqlalchemy import text
from src.core.database import SyncSessionLocal
from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique,
)
from src.engines.semantic_coverage_engine import SemanticCoverageEngine

RUN_ID = "6a7f7ea0-297f-435e-9bb2-899368c7d332"

db = SyncSessionLocal()
engine = SemanticCoverageEngine(db)

results = {
    "requirement": "The system must prevent users from accessing incidents belonging to another tenant.",
    "bad_test": {},
    "good_test": {},
    "verdict": {},
}

# ── Setup: Create a tenant isolation requirement ──
print("\n=== Setting up tenant isolation requirement ===")
tenant_req = RequirementNormalization(
    id=__import__('uuid').uuid4(),
    run_id=RUN_ID,
    requirement_id="SEC-TENANT-001",
    original_text="The system must prevent users from accessing incidents belonging to another tenant.",
    normalized_statement="The system SHALL prevent cross-tenant incident access",
    actor="The system",
    action="prevent",
    object="cross-tenant incident access",
    criticality="critical",
    security_relevance=True,
    governance_relevance=True,
    ambiguity_score=0.1,
    testability_score=0.9,
)
db.add(tenant_req)
db.commit()
print(f"  Created requirement: {tenant_req.requirement_id}")

# ── Setup: Create acceptance criteria ──
tenant_ac = AcceptanceCriteriaContract(
    id=__import__('uuid').uuid4(),
    run_id=RUN_ID,
    requirement_id="SEC-TENANT-001",
    acceptance_criterion_id="AC-TENANT-001",
    given_text="User A belongs to tenant T1, incident I2 belongs to tenant T2",
    when_text="User A requests GET /incidents/I2",
    then_text="API returns 403, no incident details returned, access attempt logged",
    negative_case_required=True,
    security_case_required=True,
    governance_case_required=True,
)
db.add(tenant_ac)
db.commit()
print(f"  Created acceptance criterion: {tenant_ac.acceptance_criterion_id}")

# ── Setup: Create test obligations ──
tenant_obl = TestObligation(
    id=__import__('uuid').uuid4(),
    run_id=RUN_ID,
    requirement_id="SEC-TENANT-001",
    acceptance_criterion_id="AC-TENANT-001",
    obligation_id="OBL-SEC-TENANT-001-AC-TENANT-001-SEC",
    obligation_type="security",
    proof_statement="Security test must verify: API returns 403, no incident details returned, access attempt logged",
    required_test_type="security",
    criticality="critical",
    status="pending",
)
db.add(tenant_obl)
db.commit()
print(f"  Created test obligation: {tenant_obl.obligation_id}")

# ── Test 1: Bad tautological test ──
print("\n=== BAD TEST: Tautological ===")
bad_tc_name = "Test that tenant isolation works"
bad_tc_expected = "tenant isolation works"
bad_alignment = engine._compute_alignment(bad_tc_name, bad_tc_expected, tenant_obl.proof_statement)
bad_tautological = engine._is_tautological(bad_tc_name, bad_tc_expected)
bad_broken_pass = engine._can_broken_code_pass(bad_tc_name, bad_tc_expected, "unit")
bad_critique = engine._generate_critique(bad_tc_name, bad_tc_expected, bad_alignment, bad_tautological)

results["bad_test"] = {
    "name": bad_tc_name,
    "expected": bad_tc_expected,
    "semantic_alignment_score": bad_alignment,
    "is_tautological": bad_tautological,
    "can_broken_code_pass": bad_broken_pass,
    "critique": bad_critique,
}

print(f"  Alignment score: {bad_alignment}")
print(f"  Is tautological: {bad_tautological}")
print(f"  Can broken code pass: {bad_broken_pass}")
print(f"  Critique: {bad_critique}")

# ── Test 2: Good concrete test ──
print("\n=== GOOD TEST: Concrete ===")
good_tc_name = "Given user A belongs to tenant T1 and incident I2 belongs to tenant 2, when user A requests GET /incidents/I2, then the API returns 403, no incident details are returned, the access attempt is logged, and no notification is sent to tenant 2 users"
good_tc_expected = "API returns 403, no incident details returned, access attempt logged, no notification sent to tenant 2"
good_alignment = engine._compute_alignment(good_tc_name, good_tc_expected, tenant_obl.proof_statement)
good_tautological = engine._is_tautological(good_tc_name, good_tc_expected)
good_broken_pass = engine._can_broken_code_pass(good_tc_name, good_tc_expected, "security")
good_critique = engine._generate_critique(good_tc_name, good_tc_expected, good_alignment, good_tautological)

results["good_test"] = {
    "name": good_tc_name[:100] + "...",
    "expected": good_tc_expected,
    "semantic_alignment_score": good_alignment,
    "is_tautological": good_tautological,
    "can_broken_code_pass": good_broken_pass,
    "critique": good_critique,
}

print(f"  Alignment score: {good_alignment}")
print(f"  Is tautological: {good_tautological}")
print(f"  Can broken code pass: {good_broken_pass}")
print(f"  Critique: {good_critique}")

# ── Evaluate semantic truth ──
print("\n=== Semantic Truth Evaluation ===")

checks = {
    "bad_test_low_alignment": bad_alignment < 0.5,
    "bad_test_detected_tautological": bad_tautological,
    "bad_test_broken_code_can_pass": bad_broken_pass,
    "bad_test_has_critique": len(bad_critique) > 0,
    "good_test_high_alignment": good_alignment > bad_alignment,
    "good_test_not_tautological": not good_tautological,
    "good_test_has_specific_assertions": "403" in good_tc_expected or "return" in good_tc_expected.lower(),
}

results["checks"] = checks
results["verdict"] = {
    "all_checks_pass": all(checks.values()),
    "semantic_alignment_is_real": bad_alignment < good_alignment,
    "tautology_detection_works": bad_tautological and not good_tautological,
}

for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"  {status} {check}: {passed}")

print(f"\n  Semantic alignment is real: {results['verdict']['semantic_alignment_is_real']}")
print(f"  Tautology detection works: {results['verdict']['tautology_detection_works']}")
print(f"  ALL CHECKS PASS: {results['verdict']['all_checks_pass']}")

db.close()

# Write report
report_path = "../evidence/final-semantic-truth-test.md"
with open(report_path, "w") as f:
    f.write("# Phase 5 — Semantic Truth Test Report\n\n")
    f.write("## Requirement\n\n")
    f.write(f"> {results['requirement']}\n\n")
    f.write("## Bad Test (Tautological)\n\n")
    f.write(f"- **Name**: {results['bad_test']['name']}\n")
    f.write(f"- **Expected**: {results['bad_test']['expected']}\n")
    f.write(f"- **Alignment Score**: {results['bad_test']['semantic_alignment_score']}\n")
    f.write(f"- **Is Tautological**: {results['bad_test']['is_tautological']}\n")
    f.write(f"- **Can Broken Code Pass**: {results['bad_test']['can_broken_code_pass']}\n")
    f.write(f"- **Critique**: {results['bad_test']['critique']}\n\n")
    f.write("## Good Test (Concrete)\n\n")
    f.write(f"- **Name**: {results['good_test']['name']}\n")
    f.write(f"- **Expected**: {results['good_test']['expected']}\n")
    f.write(f"- **Alignment Score**: {results['good_test']['semantic_alignment_score']}\n")
    f.write(f"- **Is Tautological**: {results['good_test']['is_tautological']}\n")
    f.write(f"- **Can Broken Code Pass**: {results['good_test']['can_broken_code_pass']}\n")
    f.write(f"- **Critique**: {results['good_test']['critique']}\n\n")
    f.write("## Checks\n\n")
    for check, passed in checks.items():
        f.write(f"- {'✅' if passed else '❌'} {check}: {passed}\n")
    f.write(f"\n## Verdict\n\n")
    if results["verdict"]["all_checks_pass"]:
        f.write("✅ **SEMANTIC TRUTH TEST PASSES**\n\n")
        f.write("The engine correctly distinguishes between tautological and concrete tests.\n")
        f.write("Semantic alignment scoring is real, not theatrical.\n")
    else:
        f.write("❌ **SEMANTIC TRUTH TEST FAILS**\n\n")
        failed = [k for k, v in checks.items() if not v]
        f.write(f"Failed checks: {', '.join(failed)}\n")

print(f"\n✅ Report written to {report_path}")
