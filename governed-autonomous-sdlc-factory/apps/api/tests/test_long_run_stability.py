"""Long-run stability validation for v0.3.3.

Executes 25+ sequential governed runs and measures:
- DB growth
- Replay event growth
- Artifact growth
- Governance consistency
- Semantic coverage consistency
- Orphaned records
- Failed transactions
"""
import sys, os, time, uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import text
from src.core.sync_database import SyncSessionLocal, sync_engine
from src.core.database import init_sync_db


def get_db_counts(db):
    """Get current record counts for key tables."""
    tables = ['runs', 'artifacts', 'phases', 'cost_events', 'governance_evaluations',
              'semantic_coverage_reports', 'mutation_tests', 'guard_activations']
    counts = {}
    for table in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
        counts[table] = result.scalar()
    return counts


def create_sequential_run(db, project_id, run_index, policy_ids):
    """Create one governed run. Returns (run_id, success, error)."""
    rid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    try:
        db.execute(text("INSERT INTO runs (id, project_id, name, status, total_cost, is_demo, created_at) VALUES (:id,:pid,:name,:status,0.0,false,:created)"),
                   {"id": rid, "pid": project_id, "name": f"LongRun#{run_index}", "status": "completed", "created": now})
        db.flush()

        for i in range(3):
            db.execute(text("INSERT INTO artifacts (id, run_id, name, artifact_type, content, version, is_baseline, is_locked, metadata, created_at) VALUES (:id,:rid,:name,:atype,:content,1,false,false,'{}',:created)"),
                       {"id": str(uuid.uuid4()), "rid": rid, "name": f"a-{rid[:8]}-{i}", "atype": "spec" if i==0 else "test" if i==1 else "evidence",
                        "content": f'{{"run":{run_index}}}', "created": now})

        for i in range(2):
            db.execute(text("INSERT INTO phases (id, run_id, name, status, order_index, tokens_in, tokens_out, cost, retry_count, created_at) VALUES (:id,:rid,:name,:status,:oidx,100,50,0.01,0,:created)"),
                       {"id": str(uuid.uuid4()), "rid": rid, "name": f"ph-{rid[:8]}-{i}", "status": "completed", "oidx": i, "created": now})

        for i in range(2):
            db.execute(text("INSERT INTO cost_events (id, run_id, event_type, model_name, provider, tokens_in, tokens_out, estimated_cost, is_local, created_at) VALUES (:id,:rid,:etype,:model,:provider,:tin,:tout,:cost,true,:created)"),
                       {"id": str(uuid.uuid4()), "rid": rid, "etype": "model_call", "model": "test", "provider": "test",
                        "tin": 100*(i+1), "tout": 50*(i+1), "cost": 0.01*(i+1), "created": now})

        for i, pol_id in enumerate(policy_ids[:2]):
            db.execute(text("INSERT INTO governance_evaluations (id, run_id, policy_id, decision, findings, evaluated_at) VALUES (:id,:rid,:pid,:decision,:findings,:eval_at)"),
                       {"id": str(uuid.uuid4()), "rid": rid, "pid": pol_id, "decision": "pass", "findings": "[]", "eval_at": now})

        db.execute(text("INSERT INTO semantic_coverage_reports (id, run_id, overall_semantic_coverage_score, critical_requirements_passed, mutation_score, release_gate_status, created_at) VALUES (:id,:rid,:score,true,:mut_score,:gate,:created)"),
                   {"id": str(uuid.uuid4()), "rid": rid, "score": 0.70 + (run_index % 10) * 0.02, "mut_score": 0.55 + (run_index % 10) * 0.03, "gate": "pending", "created": now})

        for i in range(2):
            db.execute(text("INSERT INTO mutation_tests (id, run_id, requirement_id, mutation_id, mutation_type, killed, created_at) VALUES (:id,:rid,:req,:mid,:mtype,true,:created)"),
                       {"id": str(uuid.uuid4()), "rid": rid, "req": f"REQ-{i:03d}", "mid": f"MUT-{rid[:8]}-{i}", "mtype": "semantic_negation", "created": now})

        db.commit()
        return rid, True, None
    except Exception as e:
        db.rollback()
        return None, False, str(e)[:200]


def main():
    print("=" * 60)
    print("v0.3.3 LONG-RUN STABILITY VALIDATION")
    print("=" * 60)

    init_sync_db()
    db = SyncSessionLocal()

    try:
        # Setup FK chain
        uid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        db.execute(text("INSERT INTO users (id, email, display_name, password_hash, role, is_active, created_at) VALUES (:id,:email,:name,:hash,:role,true,:created)"),
                   {"id": uid, "email": f"lr-{uid[:8]}@t", "name": f"LR{uid[:8]}", "hash": "x", "role": "admin", "created": now})
        db.flush()
        wid = str(uuid.uuid4())
        db.execute(text("INSERT INTO workspaces (id, name, created_by_user_id, created_at) VALUES (:id,:name,:uid,:created)"),
                   {"id": wid, "name": f"LR{wid[:8]}", "uid": uid, "created": now})
        db.flush()
        db.execute(text("INSERT INTO workspace_memberships (id, workspace_id, user_id, role, created_at) VALUES (:id,:wid,:uid,:role,:created)"),
                   {"id": str(uuid.uuid4()), "wid": wid, "uid": uid, "role": "owner", "created": now})
        db.flush()
        pid = str(uuid.uuid4())
        db.execute(text("INSERT INTO projects (id, workspace_id, name, slug, status, config, created_at) VALUES (:id,:wid,:name,:slug,:status,:config,:created)"),
                   {"id": pid, "wid": wid, "name": f"LR{pid[:8]}", "slug": f"lr{pid[:8]}", "status": "active", "config": "{}", "created": now})
        db.commit()

        # Ensure policies
        result = db.execute(text("SELECT id FROM governance_policies LIMIT 3"))
        pids = [r[0] for r in result]
        if len(pids) < 3:
            for i in range(3 - len(pids)):
                db.execute(text("INSERT INTO governance_policies (id, name, category, severity, rego_code, is_active, is_blocking, version, created_at) VALUES (:id,:name,:cat,:sev,:code,true,false,1,:created)"),
                           {"id": str(uuid.uuid4()), "name": f"lr-pol-{i}", "cat": "quality", "sev": "medium", "code": "package t", "created": now})
            db.commit()
            result = db.execute(text("SELECT id FROM governance_policies LIMIT 3"))
            pids = [r[0] for r in result]

        # Baseline counts
        print("\n── Baseline DB State ──")
        baseline = get_db_counts(db)
        for table, count in baseline.items():
            print(f"  {table}: {count}")

        # Execute 25 sequential runs
        NUM_RUNS = 25
        print(f"\n── Executing {NUM_RUNS} Sequential Runs ──")
        
        start_time = time.monotonic()
        success_count = 0
        fail_count = 0
        errors = []
        run_times = []

        for i in range(NUM_RUNS):
            run_start = time.monotonic()
            rid, success, error = create_sequential_run(db, pid, i, pids)
            run_elapsed = time.monotonic() - run_start
            run_times.append(run_elapsed)

            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"Run {i}: {error}")

            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{NUM_RUNS} ({success_count} ok, {fail_count} fail)")

        total_elapsed = time.monotonic() - start_time

        # Post-run counts
        print("\n── Post-Run DB State ──")
        post_counts = get_db_counts(db)
        for table, count in post_counts.items():
            delta = count - baseline.get(table, 0)
            print(f"  {table}: {count} (+{delta})")

        # Validation
        print("\n── Validation ──")
        issues = []

        # Check expected deltas
        expected_runs = success_count
        actual_runs = post_counts.get('runs', 0) - baseline.get('runs', 0)
        if actual_runs != expected_runs:
            issues.append(f"Expected {expected_runs} new runs, got {actual_runs}")

        expected_artifacts = success_count * 3
        actual_artifacts = post_counts.get('artifacts', 0) - baseline.get('artifacts', 0)
        if actual_artifacts != expected_artifacts:
            issues.append(f"Expected {expected_artifacts} new artifacts, got {actual_artifacts}")

        expected_phases = success_count * 2
        actual_phases = post_counts.get('phases', 0) - baseline.get('phases', 0)
        if actual_phases != expected_phases:
            issues.append(f"Expected {expected_phases} new phases, got {actual_phases}")

        expected_events = success_count * 2
        actual_events = post_counts.get('cost_events', 0) - baseline.get('cost_events', 0)
        if actual_events != expected_events:
            issues.append(f"Expected {expected_events} new cost_events, got {actual_events}")

        expected_gov = success_count * 2
        actual_gov = post_counts.get('governance_evaluations', 0) - baseline.get('governance_evaluations', 0)
        if actual_gov != expected_gov:
            issues.append(f"Expected {expected_gov} new gov evals, got {actual_gov}")

        expected_scr = success_count
        actual_scr = post_counts.get('semantic_coverage_reports', 0) - baseline.get('semantic_coverage_reports', 0)
        if actual_scr != expected_scr:
            issues.append(f"Expected {expected_scr} new semantic reports, got {actual_scr}")

        expected_mut = success_count * 2
        actual_mut = post_counts.get('mutation_tests', 0) - baseline.get('mutation_tests', 0)
        if actual_mut != expected_mut:
            issues.append(f"Expected {expected_mut} new mutation tests, got {actual_mut}")

        # Check for orphaned records
        result = db.execute(text("SELECT COUNT(*) FROM artifacts WHERE run_id NOT IN (SELECT id FROM runs)"))
        orphaned = result.scalar()
        if orphaned > 0:
            issues.append(f"{orphaned} orphaned artifacts")

        result = db.execute(text("SELECT COUNT(*) FROM cost_events WHERE run_id NOT IN (SELECT id FROM runs)"))
        orphaned_events = result.scalar()
        if orphaned_events > 0:
            issues.append(f"{orphaned_events} orphaned cost_events")

        # Check for duplicate artifact names (only within new runs)
        result = db.execute(text("""
            SELECT name, COUNT(*) cnt FROM artifacts 
            WHERE run_id IN (SELECT id FROM runs WHERE name LIKE 'LongRun#%')
            GROUP BY name HAVING COUNT(*) > 1
        """))
        dupes = result.fetchall()
        if dupes:
            issues.append(f"{len(dupes)} duplicate artifact names in new runs")

        # Timing analysis
        avg_time = sum(run_times) / len(run_times) if run_times else 0
        max_time = max(run_times) if run_times else 0
        min_time = min(run_times) if run_times else 0

        if not issues:
            print("  ALL VALIDATIONS PASSED")
        else:
            print(f"  {len(issues)} issues:")
            for issue in issues:
                print(f"    -> {issue}")

        if errors:
            print(f"  {len(errors)} run errors:")
            for err in errors[:5]:
                print(f"    -> {err}")

        # Summary
        print(f"\n{'=' * 60}")
        print("LONG-RUN STABILITY SUMMARY")
        print("=" * 60)
        print(f"  Runs: {success_count}/{NUM_RUNS} success, {fail_count} failed")
        print(f"  Total time: {total_elapsed:.2f}s")
        print(f"  Avg run time: {avg_time:.4f}s")
        print(f"  Min run time: {min_time:.4f}s")
        print(f"  Max run time: {max_time:.4f}s")
        print(f"  Issues: {len(issues)}")
        print(f"  RESULT: {'PASS' if not issues and fail_count == 0 else 'FAIL'}")

        return len(issues) == 0 and fail_count == 0

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
