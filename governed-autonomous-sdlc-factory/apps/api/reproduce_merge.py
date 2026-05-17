"""Reproduce: call compute_semantic_coverage_score twice (merge behavior)."""
import os
import sys

os.chdir("/Users/marcovanhurne/governed-autonomous-sdlc-factory/governed-autonomous-sdlc-factory/apps/api")
sys.path.insert(0, "src")

from sqlalchemy import text
from src.core.database import SyncSessionLocal
from src.core.models_semantic_coverage import SemanticCoverageReport
from src.engines.semantic_coverage_engine import SemanticCoverageEngine

RUN_ID = "6a7f7ea0-297f-435e-9bb2-899368c7d332"

db = SyncSessionLocal()
engine = SemanticCoverageEngine(db)

print("Test: compute_semantic_coverage_score called twice (no _clear_existing)")
print("=" * 60)

# Check existing report
existing = db.query(SemanticCoverageReport).filter(
    SemanticCoverageReport.run_id == RUN_ID
).all()
print(f"\nExisting reports: {len(existing)}")
for r in existing:
    print(f"  id={r.id}, score={r.overall_semantic_coverage_score}")

# Call compute_semantic_coverage_score again (without _clear_existing)
print("\nCalling compute_semantic_coverage_score again...")
try:
    report = engine.compute_semantic_coverage_score(RUN_ID)
    print(f"  OK: score={report.overall_semantic_coverage_score}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()

# Check reports again
db.expire_all()
reports = db.query(SemanticCoverageReport).filter(
    SemanticCoverageReport.run_id == RUN_ID
).all()
print(f"\nReports after second call: {len(reports)}")
for r in reports:
    print(f"  id={r.id}, score={r.overall_semantic_coverage_score}, created={r.created_at}")

if len(reports) > 1:
    print("\n  BUG CONFIRMED: merge created duplicate report!")
elif len(reports) == 1:
    print("\n  OK: Only 1 report (merge updated or was no-op)")

db.close()
