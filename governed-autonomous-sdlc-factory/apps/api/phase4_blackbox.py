"""Run semantic coverage on the black-box run and validate results."""
import os, sys, json

os.chdir("/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api")
sys.path.insert(0, "src")

from src.core.database import SyncSessionLocal
from src.core.models_semantic_coverage import (
    RequirementNormalization, AcceptanceCriteriaContract, TestObligation,
    SemanticAlignmentEvaluation, VerifierCritique, MutationTest,
    NegativeTestRequirement, RuntimeEvidenceBinding, SemanticCoverageReport,
)
from src.engines.semantic_coverage_engine import SemanticCoverageEngine
from src.core.conflict_detection import ConflictDetector
from src.models import Artifact

RUN_ID = "7ff8a2fd-5e9f-4d68-8611-ef320da02627"
db = SyncSessionLocal()
engine = SemanticCoverageEngine(db)

results = {"run_id": RUN_ID, "phases": {}}

# ── Run full semantic coverage pipeline ──
print("=== Running Semantic Coverage Pipeline ===")
try:
    report = engine.run_full_semantic_coverage(RUN_ID)
    results["phases"]["full_pipeline"] = {
        "status": "ok",
        "score": report.overall_semantic_coverage_score,
        "gate": report.release_gate_status,
        "critical_passed": report.critical_requirements_passed,
    }
    print(f"  Score: {report.overall_semantic_coverage_score}, Gate: {report.release_gate_status}")
except Exception as e:
    results["phases"]["full_pipeline"] = {"status": "error", "error": str(e)}
    print(f"  ERROR: {e}")

# ── Count records ──
print("\n=== Record Counts ===")
tables = [
    ("requirements", RequirementNormalization),
    ("acceptance_criteria", AcceptanceCriteriaContract),
    ("test_obligations", TestObligation),
    ("alignment_evaluations", SemanticAlignmentEvaluation),
    ("verifier_critiques", VerifierCritique),
    ("mutation_tests", MutationTest),
    ("negative_requirements", NegativeTestRequirement),
    ("evidence_bindings", RuntimeEvidenceBinding),
    ("coverage_reports", SemanticCoverageReport),
]
for name, model in tables:
    count = db.query(model).filter(model.run_id == RUN_ID).count()
    results[f"count_{name}"] = count
    print(f"  {name}: {count}")

# ── Run conflict detection ──
print("\n=== Conflict Detection ===")
try:
    reqs = db.query(RequirementNormalization).filter(RequirementNormalization.run_id == RUN_ID).all()
    detector = ConflictDetector(RUN_ID)
    conflicts = detector.detect_conflicts(reqs)
    detector.persist_conflicts(conflicts)
    results["conflicts"] = {
        "count": len(conflicts),
        "findings": [{"type": c.conflict_type, "severity": c.severity, "req1": c.requirement_id_1, "req2": c.requirement_id_2} for c in conflicts],
    }
    print(f"  Conflicts found: {len(conflicts)}")
    for c in conflicts:
        print(f"    {c.conflict_type}: {c.requirement_id_1} vs {c.requirement_id_2} ({c.severity})")
except Exception as e:
    results["conflicts"] = {"error": str(e)}
    print(f"  ERROR: {e}")

# ── Check artifacts ──
print("\n=== Artifacts ===")
arts = db.query(Artifact).filter(Artifact.run_id == RUN_ID).all()
results["artifacts"] = [{"type": a.artifact_type, "name": a.name} for a in arts]
print(f"  Total: {len(arts)}")

# ── Idempotency check ──
print("\n=== Idempotency Check ===")
try:
    report2 = engine.run_full_semantic_coverage(RUN_ID)
    results["idempotency"] = {
        "status": "ok",
        "score": report2.overall_semantic_coverage_score,
        "gate": report2.release_gate_status,
    }
    print(f"  Score: {report2.overall_semantic_coverage_score}, Gate: {report2.release_gate_status}")
except Exception as e:
    results["idempotency"] = {"status": "error", "error": str(e)}
    print(f"  ERROR: {e}")

db.close()

# Write report
report_path = "../evidence/full-black-box-run-report.md"
with open(report_path, "w") as f:
    f.write("# Phase 4 — Full Black-Box Run Report\n\n")
    f.write(f"**Run ID**: {RUN_ID}\n\n")
    f.write(f"```json\n{json.dumps(results, indent=2, default=str)}\n```\n\n")
    f.write("## Verdict\n\n")
    if results["phases"].get("full_pipeline", {}).get("status") == "ok":
        f.write("✅ Full black-box run completed successfully.\n")
        f.write(f"- Semantic coverage score: {results['phases']['full_pipeline']['score']}\n")
        f.write(f"- Release gate: {results['phases']['full_pipeline']['gate']}\n")
        f.write(f"- Conflicts detected: {results.get('conflicts', {}).get('count', 0)}\n")
    else:
        f.write("❌ Pipeline failed.\n")

print(f"\n✅ Report written to {report_path}")
