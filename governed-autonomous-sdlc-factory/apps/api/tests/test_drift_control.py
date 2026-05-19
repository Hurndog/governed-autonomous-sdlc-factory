"""Integration test for v0.3.4 — drift detection, metacognitive control, replay integrity."""
import sys, os, uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import text
from src.core.sync_database import SyncSessionLocal, sync_engine
from src.core.database import init_sync_db
from src.engines.drift_control_engine import (
    DriftDetectionEngine, MetacognitiveController,
    ReplayIntegrityVerifier, RuntimeTrustScorer
)


def setup_project(db):
    uid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    db.execute(text("INSERT INTO users (id, email, display_name, password_hash, role, is_active, created_at) VALUES (:id,:email,:name,:hash,:role,true,:created)"),
               {"id": uid, "email": f"drift-{uid[:8]}@t", "name": f"Drift{uid[:8]}", "hash": "x", "role": "admin", "created": now})
    db.flush()
    wid = str(uuid.uuid4())
    db.execute(text("INSERT INTO workspaces (id, name, created_by_user_id, created_at) VALUES (:id,:ws_name,:user_id,:created)"),
               {"id": wid, "ws_name": f"Drift{wid[:8]}", "user_id": uid, "created": now})
    db.flush()
    db.execute(text("INSERT INTO workspace_memberships (id, workspace_id, user_id, role, created_at) VALUES (:id,:ws_id,:user_id,:role,:created)"),
               {"id": str(uuid.uuid4()), "ws_id": wid, "user_id": uid, "role": "owner", "created": now})
    db.flush()
    pid = str(uuid.uuid4())
    db.execute(text("INSERT INTO projects (id, workspace_id, name, slug, status, config, created_at) VALUES (:id,:ws_id,:proj_name,:slug,:status,:config,:created)"),
               {"id": pid, "ws_id": wid, "proj_name": f"Drift{pid[:8]}", "slug": f"drift{pid[:8]}", "status": "active", "config": "{}", "created": now})
    db.commit()
    return uid, wid, pid


def seed_test_data(db, project_id, workspace_id):
    now = datetime.now(timezone.utc)
    rid = str(uuid.uuid4())
    db.execute(text("INSERT INTO runs (id, project_id, name, status, total_cost, is_demo, created_at) VALUES (:id,:pid,:run_name,:status,0.0,false,:created)"),
               {"id": rid, "pid": project_id, "run_name": "DriftTestRun", "status": "completed", "created": now})
    db.flush()

    sid = str(uuid.uuid4())
    db.execute(text("INSERT INTO replay_sessions (id, source_run_id, replay_mode, status, integrity_score, created_at) VALUES (:id,:rid,:mode,:status,:score,:created)"),
               {"id": sid, "rid": rid, "mode": "full", "status": "completed", "score": 1.0, "created": now})
    db.flush()

    prev_hash = "genesis"
    for i in range(3):
        eid = str(uuid.uuid4())
        ehash = f"ehash_{rid[:8]}_{i}"
        db.execute(text("INSERT INTO replay_events (id, replay_session_id, event_type, message, event_hash, parent_hash, created_at) VALUES (:id,:sid,:etype,:msg,:ehash,:phash,:created)"),
                   {"id": eid, "sid": sid, "etype": f"step_{i}", "msg": f"Step {i}", "ehash": ehash, "phash": prev_hash, "created": now})
        prev_hash = ehash

    for i in range(2):
        db.execute(text("INSERT INTO evidence_bundles (id, run_id, bundle_path, bundle_hash, size_bytes, artifact_count, chain_hash, created_at) VALUES (:id,:rid,:path,:hash,:size,:ac,:chain,:created)"),
                   {"id": str(uuid.uuid4()), "rid": rid, "path": f"/ev/bundle_{i}.json", "hash": f"bhash_{i}", "size": 1024, "ac": 2, "chain": f"chain_{i}", "created": now})

    db.execute(text("INSERT INTO semantic_coverage_reports (id, run_id, overall_semantic_coverage_score, critical_requirements_passed, mutation_score, release_gate_status, created_at) VALUES (:id,:rid,:score,true,:mut,:gate,:created)"),
               {"id": str(uuid.uuid4()), "rid": rid, "score": 0.85, "mut": 0.70, "gate": "pending", "created": now})

    # Ensure policies exist FIRST (before governance evaluations)
    for i in range(2):
        existing = db.execute(text("SELECT COUNT(*) FROM governance_policies WHERE id = :pid"), {"pid": f"policy-{i}"}).scalar()
        if existing == 0:
            db.execute(text("INSERT INTO governance_policies (id, name, category, severity, rego_code, is_active, is_blocking, version, created_at) VALUES (:id,:name,:cat,:sev,:code,true,false,1,:created)"),
                       {"id": f"policy-{i}", "name": f"policy-{i}", "cat": "quality", "sev": "medium", "code": "package t", "created": now})

    for i in range(2):
        db.execute(text("INSERT INTO governance_evaluations (id, run_id, policy_id, decision, findings, evaluated_at) VALUES (:id,:rid,:pol_id,:decision,:findings,:eval_at)"),
                   {"id": str(uuid.uuid4()), "rid": rid, "pol_id": f"policy-{i}", "decision": "pass", "findings": "[]", "eval_at": now})

    for i in range(3):
        db.execute(text("INSERT INTO memory_items (id, project_id, memory_type, key, content, source, created_at) VALUES (:id,:pid,:mtype,:key,:content,:source,:created)"),
                   {"id": str(uuid.uuid4()), "pid": project_id, "mtype": "requirement", "key": f"req-{i}", "content": f'{{"req": {i}}}', "source": "test", "created": now})

    db.execute(text("INSERT INTO memory_items (id, project_id, memory_type, key, content, source, created_at) VALUES (:id,:pid,:mtype,:key,:content,:source,:created)"),
               {"id": str(uuid.uuid4()), "pid": project_id, "mtype": "requirement", "key": "req-0", "content": '{"req": "CONTRADICTORY"}', "source": "test", "created": now})

    db.commit()
    return rid, sid


def main():
    print("=" * 60)
    print("v0.3.4 MEMORY, DRIFT, METACOGNITIVE, REPLAY INTEGRITY TEST")
    print("=" * 60)

    init_sync_db()
    db = SyncSessionLocal()

    try:
        print("\n── Setup ──")
        uid, wid, pid = setup_project(db)
        rid, sid = seed_test_data(db, pid, wid)
        print(f"  Project: {pid[:8]}... Session: {sid[:8]}...")

        # Test 1: Drift Detection
        print("\n── Test 1: Drift Detection ──")
        drift_engine = DriftDetectionEngine(db)
        drift_report = drift_engine.run_full_drift_scan(pid)
        print(f"  Overall drift: {drift_report['overall_drift_score']:.4f}")
        print(f"  Categories with drift: {drift_report['categories_with_drift']}")
        for cat, result in drift_report["category_results"].items():
            print(f"    {cat:20s}: {'DRIFT' if result.get('drift_detected') else 'OK'} ({result.get('score', 0):.4f})")

        # Test 2: Metacognitive Control
        print("\n── Test 2: Metacognitive Control ──")
        controller = MetacognitiveController(db)
        evaluation = controller.evaluate_runtime_state(pid, drift_report)
        print(f"  Autonomy: {evaluation['recommended_autonomy']}")
        print(f"  Escalation: {evaluation['recommended_escalation']}")
        state_id = controller.apply_metacognitive_state(pid, wid, evaluation)
        print(f"  State persisted: {state_id[:8]}...")

        # Test 3: Replay Integrity
        print("\n── Test 3: Replay Integrity ──")
        verifier = ReplayIntegrityVerifier(db)
        integrity = verifier.verify_replay_integrity(sid)
        print(f"  Clean chain valid: {integrity['integrity_valid']}")
        print(f"  Events checked: {integrity['events_checked']}")

        # Test 4: Tamper detection
        print("\n── Test 4: Tamper Detection ──")
        db.execute(text("UPDATE replay_events SET parent_hash = 'tampered' WHERE replay_session_id = :sid AND event_type = 'step_2'"), {"sid": sid})
        db.commit()
        integrity_after = verifier.verify_replay_integrity(sid)
        print(f"  After tampering: valid={integrity_after['integrity_valid']}, breaks={integrity_after['chain_breaks']}")
        tamper_detected = not integrity_after["integrity_valid"]

        # Test 5: Trust Scoring
        print("\n── Test 5: Trust Scoring ──")
        scorer = RuntimeTrustScorer(db)
        trust = scorer.compute_trust_scores(pid)
        print(f"  Overall trust: {trust['overall_trust']:.4f}")
        for dim, data in trust.get("dimensions", {}).items():
            print(f"    {dim:30s}: {data['score']:.4f}")
        score_ids = scorer.persist_trust_scores(pid, wid, trust)
        print(f"  Scores persisted: {len(score_ids)}")

        # Test 6: Operator Intervention
        print("\n── Test 6: Operator Intervention ──")
        int_id = controller.record_operator_intervention(pid, wid, uid, "correction", "Fixed threshold", {"t": 0.5}, {"t": 0.3})
        print(f"  Intervention: {int_id[:8]}...")

        # Summary
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print("=" * 60)
        tests = [
            ("Drift detection (8 categories)", drift_report["categories_scanned"] == 8),
            ("Metacognitive control", evaluation["recommended_autonomy"] in ["full", "reduced", "supervised", "paused"]),
            ("Replay integrity (clean)", integrity["integrity_valid"]),
            ("Replay integrity (tampered)", tamper_detected),
            ("Trust scoring", trust["overall_trust"] > 0),
            ("Operator intervention", int_id is not None),
        ]
        all_pass = True
        for name, passed in tests:
            status = "PASS" if passed else "FAIL"
            print(f"  {status}: {name}")
            if not passed:
                all_pass = False

        print(f"\n  RESULT: {'PASS' if all_pass else 'FAIL'}")
        return all_pass

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
