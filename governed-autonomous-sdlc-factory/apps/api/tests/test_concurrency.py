"""Concurrency validation for v0.3.3 — hardened."""
import sys, os, time, uuid, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import text
from src.core.sync_database import SyncSessionLocal, sync_engine
from src.core.database import init_sync_db


def setup_fk_chain(db):
    uid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    db.execute(text("INSERT INTO users (id, email, display_name, password_hash, role, is_active, created_at) VALUES (:id,:email,:name,:hash,:role,true,:created)"),
               {"id": uid, "email": f"ct-{uid[:8]}@t", "name": f"T{uid[:8]}", "hash": "x", "role": "admin", "created": now})
    db.flush()
    wid = str(uuid.uuid4())
    db.execute(text("INSERT INTO workspaces (id, name, created_by_user_id, created_at) VALUES (:id,:name,:user_id,:created)"),
               {"id": wid, "name": f"WS{wid[:8]}", "user_id": uid, "created": now})
    db.flush()
    db.execute(text("INSERT INTO workspace_memberships (id, workspace_id, user_id, role, created_at) VALUES (:id,:ws_id,:user_id,:role,:created)"),
               {"id": str(uuid.uuid4()), "ws_id": wid, "user_id": uid, "role": "owner", "created": now})
    db.flush()
    pid = str(uuid.uuid4())
    db.execute(text("INSERT INTO projects (id, workspace_id, name, slug, status, config, created_at) VALUES (:id,:ws_id,:name,:slug,:status,:config,:created)"),
               {"id": pid, "ws_id": wid, "name": f"P{pid[:8]}", "slug": f"p{pid[:8]}", "status": "active", "config": "{}", "created": now})
    db.commit()
    return uid, wid, pid


def ensure_policies(db):
    result = db.execute(text("SELECT id FROM governance_policies LIMIT 3"))
    ids = [r[0] for r in result]
    if len(ids) < 3:
        now = datetime.now(timezone.utc)
        for i in range(3 - len(ids)):
            pid = str(uuid.uuid4())
            db.execute(text("INSERT INTO governance_policies (id, name, category, severity, rego_code, is_active, is_blocking, version, created_at) VALUES (:id,:name,:cat,:sev,:code,true,false,1,:created)"),
                       {"id": pid, "name": f"pol-{i}", "cat": "quality", "sev": "medium", "code": "package t", "created": now})
        db.commit()
        result = db.execute(text("SELECT id FROM governance_policies LIMIT 3"))
        ids = [r[0] for r in result]
    return ids


def create_run(db, project_id, run_index, policy_ids):
    rid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    db.execute(text("INSERT INTO runs (id, project_id, name, status, total_cost, is_demo, created_at) VALUES (:id,:project_id,:name,:status,0.0,false,:created)"),
               {"id": rid, "project_id": project_id, "name": f"Run#{run_index}", "status": "completed", "created": now})
    db.flush()

    for i in range(3):
        db.execute(text("INSERT INTO artifacts (id, run_id, name, artifact_type, content, version, is_baseline, is_locked, metadata, created_at) VALUES (:id,:run_id,:name,:atype,:content,1,false,false,'{}',:created)"),
                   {"id": str(uuid.uuid4()), "run_id": rid, "name": f"a-{rid[:8]}-{i}", "atype": "spec" if i==0 else "test" if i==1 else "evidence",
                    "content": f'{{"idx":{run_index}}}', "created": now})

    for i in range(2):
        db.execute(text("INSERT INTO phases (id, run_id, name, status, order_index, tokens_in, tokens_out, cost, retry_count, created_at) VALUES (:id,:run_id,:name,:status,:oidx,100,50,0.01,0,:created)"),
                   {"id": str(uuid.uuid4()), "run_id": rid, "name": f"ph-{rid[:8]}-{i}", "status": "completed", "oidx": i, "created": now})

    for i in range(2):
        db.execute(text("INSERT INTO cost_events (id, run_id, event_type, model_name, provider, tokens_in, tokens_out, estimated_cost, is_local, created_at) VALUES (:id,:run_id,:etype,:model,:provider,:tin,:tout,:cost,true,:created)"),
                   {"id": str(uuid.uuid4()), "run_id": rid, "etype": "model_call", "model": "test", "provider": "test",
                    "tin": 100*(i+1), "tout": 50*(i+1), "cost": 0.01*(i+1), "created": now})

    for i, pol_id in enumerate(policy_ids[:2]):
        db.execute(text("INSERT INTO governance_evaluations (id, run_id, policy_id, decision, findings, evaluated_at) VALUES (:id,:run_id,:pol_id,:decision,:findings,:eval_at)"),
                   {"id": str(uuid.uuid4()), "run_id": rid, "pol_id": pol_id, "decision": "pass", "findings": "[]", "eval_at": now})

    db.execute(text("INSERT INTO semantic_coverage_reports (id, run_id, overall_semantic_coverage_score, critical_requirements_passed, mutation_score, release_gate_status, created_at) VALUES (:id,:run_id,:score,true,:mut_score,:gate,:created)"),
               {"id": str(uuid.uuid4()), "run_id": rid, "score": 0.75+run_index*0.01, "mut_score": 0.60+run_index*0.02, "gate": "pending", "created": now})

    for i in range(2):
        db.execute(text("INSERT INTO mutation_tests (id, run_id, requirement_id, mutation_id, mutation_type, killed, created_at) VALUES (:id,:run_id,:req_id,:mid,:mtype,true,:created)"),
                   {"id": str(uuid.uuid4()), "run_id": rid, "req_id": f"REQ-{i:03d}", "mid": f"MUT-{rid[:8]}-{i}", "mtype": "semantic_negation", "created": now})

    db.commit()
    return rid


def run_one(project_id, run_index, policy_ids):
    db = SyncSessionLocal()
    tname = threading.current_thread().name
    start = time.monotonic()
    try:
        rid = create_run(db, project_id, run_index, policy_ids)
        return {"run_id": rid, "thread": tname, "success": True, "error": None, "elapsed": time.monotonic() - start}
    except Exception as e:
        db.rollback()
        return {"run_id": None, "thread": tname, "success": False, "error": str(e)[:300], "elapsed": time.monotonic() - start}
    finally:
        db.close()


def run_scale(project_id, policy_ids, n):
    results = []
    with ThreadPoolExecutor(max_workers=n, thread_name_prefix="c") as ex:
        futs = {ex.submit(run_one, project_id, i, policy_ids): i for i in range(n)}
        for f in as_completed(futs):
            try:
                results.append(f.result(timeout=30))
            except Exception as e:
                results.append({"run_id": None, "thread": f"fut-{futs[f]}", "success": False, "error": str(e)[:300], "elapsed": 0})
    return results


def validate(db, run_ids):
    if not run_ids:
        return ["No successful runs to validate"]
    issues = []

    result = db.execute(text("SELECT id FROM runs WHERE id IN :ids"), {"ids": tuple(run_ids)})
    found = {r[0] for r in result}
    missing = set(run_ids) - found
    if missing:
        issues.append(f"{len(missing)} runs not found in DB")

    result = db.execute(text("SELECT run_id, COUNT(*) FROM artifacts WHERE run_id IN :ids GROUP BY run_id"), {"ids": tuple(run_ids)})
    art_counts = {r[0]: r[1] for r in result}
    for rid in run_ids:
        if rid not in art_counts:
            issues.append(f"Run {rid[:8]}: no artifacts")
        elif art_counts[rid] != 3:
            issues.append(f"Run {rid[:8]}: {art_counts[rid]} artifacts (expected 3)")

    result = db.execute(text("SELECT run_id, COUNT(*) FROM governance_evaluations WHERE run_id IN :ids GROUP BY run_id"), {"ids": tuple(run_ids)})
    gov_counts = {r[0]: r[1] for r in result}
    for rid in run_ids:
        if rid not in gov_counts:
            issues.append(f"Run {rid[:8]}: no governance evaluations")
        elif gov_counts[rid] != 2:
            issues.append(f"Run {rid[:8]}: {gov_counts[rid]} gov evals (expected 2)")

    result = db.execute(text("SELECT name, COUNT(*) cnt FROM artifacts WHERE run_id IN :ids GROUP BY name HAVING COUNT(*) > 1"), {"ids": tuple(run_ids)})
    for r in result:
        issues.append(f"Duplicate artifact name: {r[0]} ({r[1]} occurrences)")

    result = db.execute(text("SELECT COUNT(*) FROM artifacts WHERE run_id IN :ids AND run_id NOT IN (SELECT id FROM runs)"), {"ids": tuple(run_ids)})
    if result.scalar() > 0:
        issues.append(f"{result.scalar()} orphaned artifacts")

    result = db.execute(text("SELECT COUNT(*) FROM cost_events WHERE run_id IN :ids AND run_id NOT IN (SELECT id FROM runs)"), {"ids": tuple(run_ids)})
    if result.scalar() > 0:
        issues.append(f"{result.scalar()} orphaned cost_events")

    return issues


def main():
    print("=" * 60)
    print("v0.3.3 CONCURRENCY VALIDATION")
    print("=" * 60)

    init_sync_db()
    db = SyncSessionLocal()
    try:
        print("\n── Setup ──")
        uid, wid, pid = setup_fk_chain(db)
        pids = ensure_policies(db)
        print(f"  Project: {pid[:8]}... Policies: {len(pids)}")

        all_run_ids = []
        for scale in [2, 5, 10]:
            print(f"\n── Scale: {scale} concurrent ──")
            results = run_scale(pid, pids, scale)
            ok = [r for r in results if r["success"]]
            fail = [r for r in results if not r["success"]]
            print(f"  {len(ok)}/{scale} success, {len(fail)} failed")
            for r in results:
                s = "OK" if r["success"] else "FAIL"
                rid_short = r["run_id"][:8] if r["run_id"] else "NONE"
                print(f"    {s} {r['thread']}: {rid_short}... {r['elapsed']:.2f}s")
                if r["error"]:
                    print(f"      ERR: {r['error'][:120]}")
            all_run_ids.extend([r["run_id"] for r in ok])

        print(f"\n── Validation ({len(all_run_ids)} runs) ──")
        issues = validate(db, all_run_ids)
        if not issues:
            print("  ALL VALIDATIONS PASSED")
        else:
            print(f"  {len(issues)} issues:")
            for i in issues:
                print(f"    -> {i}")

        print(f"\n{'=' * 60}")
        total_expected = 17
        passed = len(issues) == 0 and len(all_run_ids) == total_expected
        print(f"RESULT: {'PASS' if passed else 'FAIL'}")
        print(f"  Successful runs: {len(all_run_ids)}/{total_expected}")
        print(f"  Issues: {len(issues)}")
        return passed
    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
