"""v0.3.5 Integration Integrity Test — hardened with per-test sessions."""
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


def fresh_db():
    return SyncSessionLocal()


def setup_project(db):
    uid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    db.execute(text("INSERT INTO users (id, email, display_name, password_hash, role, is_active, created_at) VALUES (:id,:email,:name,:hash,:role,true,:created)"),
               {"id": uid, "email": f"v5-{uid[:8]}@t", "name": f"V5{uid[:8]}", "hash": "x", "role": "admin", "created": now})
    db.flush()
    wid = str(uuid.uuid4())
    db.execute(text("INSERT INTO workspaces (id, name, created_by_user_id, created_at) VALUES (:id,:ws_name,:user_id,:created)"),
               {"id": wid, "ws_name": f"V5{wid[:8]}", "user_id": uid, "created": now})
    db.flush()
    db.execute(text("INSERT INTO workspace_memberships (id, workspace_id, user_id, role, created_at) VALUES (:id,:ws_id,:user_id,:role,:created)"),
               {"id": str(uuid.uuid4()), "ws_id": wid, "user_id": uid, "role": "owner", "created": now})
    db.flush()
    pid = str(uuid.uuid4())
    db.execute(text("INSERT INTO projects (id, workspace_id, name, slug, status, config, created_at) VALUES (:id,:ws_id,:proj_name,:slug,:status,:config,:created)"),
               {"id": pid, "ws_id": wid, "proj_name": f"V5{pid[:8]}", "slug": f"v5{pid[:8]}", "status": "active", "config": "{}", "created": now})
    db.commit()
    return uid, wid, pid


def seed_and_test(db, project_id):
    """Seed data and run all tests in one session."""
    now = datetime.now(timezone.utc)
    rid = str(uuid.uuid4())

    # Run
    db.execute(text("INSERT INTO runs (id, project_id, name, status, total_cost, is_demo, created_at) VALUES (:id,:pid,:run_name,:status,0.0,false,:created)"),
               {"id": rid, "pid": project_id, "run_name": "V5TestRun", "status": "completed", "created": now})
    db.flush()

    # Replay session
    sid = str(uuid.uuid4())
    db.execute(text("INSERT INTO replay_sessions (id, source_run_id, replay_mode, status, integrity_score, created_at) VALUES (:id,:rid,:mode,:status,:score,:created)"),
               {"id": sid, "rid": rid, "mode": "full", "status": "completed", "score": 1.0, "created": now})
    db.flush()

    # Replay events
    prev_hash = "genesis"
    for i in range(3):
        eid = str(uuid.uuid4())
        ehash = f"ehash_{rid[:8]}_{i}"
        db.execute(text("INSERT INTO replay_events (id, replay_session_id, event_type, message, event_hash, parent_hash, created_at) VALUES (:id,:sid,:etype,:msg,:ehash,:phash,:created)"),
                   {"id": eid, "sid": sid, "etype": f"step_{i}", "msg": f"Step {i}", "ehash": ehash, "phash": prev_hash, "created": now})
        prev_hash = ehash

    # Evidence bundles
    for i in range(2):
        db.execute(text("INSERT INTO evidence_bundles (id, run_id, bundle_path, bundle_hash, size_bytes, artifact_count, chain_hash, created_at) VALUES (:id,:rid,:path,:hash,:size,:ac,:chain,:created)"),
                   {"id": str(uuid.uuid4()), "rid": rid, "path": f"/ev/bundle_{i}.json", "hash": f"bhash_{i}", "size": 1024, "ac": 2, "chain": f"chain_{i}", "created": now})

    # Semantic coverage
    db.execute(text("INSERT INTO semantic_coverage_reports (id, run_id, overall_semantic_coverage_score, critical_requirements_passed, mutation_score, release_gate_status, created_at) VALUES (:id,:rid,:score,true,:mut,:gate,:created)"),
               {"id": str(uuid.uuid4()), "rid": rid, "score": 0.85, "mut": 0.70, "gate": "pending", "created": now})

    # Policies FIRST
    for i in range(2):
        existing = db.execute(text("SELECT COUNT(*) FROM governance_policies WHERE id = :pid"), {"pid": f"v5p-{i}"}).scalar()
        if existing == 0:
            db.execute(text("INSERT INTO governance_policies (id, name, category, severity, rego_code, is_active, is_blocking, version, created_at) VALUES (:id,:name,:cat,:sev,:code,true,false,1,:created)"),
                       {"id": f"v5p-{i}", "name": f"v5p-{i}", "cat": "quality", "sev": "medium", "code": "package t", "created": now})

    # Evaluations
    for i in range(2):
        db.execute(text("INSERT INTO governance_evaluations (id, run_id, policy_id, decision, findings, evaluated_at) VALUES (:id,:rid,:pol_id,:decision,:findings,:eval_at)"),
                   {"id": str(uuid.uuid4()), "rid": rid, "pol_id": f"v5p-{i}", "decision": "pass", "findings": "[]", "eval_at": now})

    # Memory items + contradiction
    for i in range(3):
        db.execute(text("INSERT INTO memory_items (id, project_id, memory_type, key, content, source, created_at) VALUES (:id,:pid,:mtype,:key,:content,:source,:created)"),
                   {"id": str(uuid.uuid4()), "pid": project_id, "mtype": "requirement", "key": f"req-{i}", "content": f'{{"req": {i}}}', "source": "test", "created": now})
    db.execute(text("INSERT INTO memory_items (id, project_id, memory_type, key, content, source, created_at) VALUES (:id,:pid,:mtype,:key,:content,:source,:created)"),
               {"id": str(uuid.uuid4()), "pid": project_id, "mtype": "requirement", "key": "req-0", "content": '{"req": "CONTRADICTORY"}', "source": "test", "created": now})

    db.commit()
    return rid, sid


def main():
    print("=" * 60)
    print("v0.3.5 INTEGRATION INTEGRITY TEST")
    print("=" * 60)

    init_sync_db()
    results = []

    # Setup
    db = fresh_db()
    uid, wid, pid = setup_project(db)
    rid, sid = seed_and_test(db, pid)
    print(f"Setup: Project={pid[:8]} Session={sid[:8]}")

    # Test 1: Drift Detection
    print("\n── Test 1: Drift Detection ──")
    try:
        engine = DriftDetectionEngine(db)
        report = engine.run_full_drift_scan(pid)
        print(f"  Drift: {report['overall_drift_score']:.4f}, Categories: {report['categories_scanned']}")
        results.append(("Drift detection", True))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Drift detection", False))

    # Test 2: Metacognitive Control
    print("\n── Test 2: Metacognitive Control ──")
    try:
        controller = MetacognitiveController(db)
        evaluation = controller.evaluate_runtime_state(pid, report)
        state_id = controller.apply_metacognitive_state(pid, wid, evaluation)
        print(f"  Autonomy: {evaluation['recommended_autonomy']}, State: {state_id[:8]}...")
        results.append(("Metacognitive control", True))
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        results.append(("Metacognitive control", False))

    # Test 3: Replay Integrity
    print("\n── Test 3: Replay Integrity ──")
    try:
        verifier = ReplayIntegrityVerifier(db)
        integrity = verifier.verify_replay_integrity(sid)
        print(f"  Valid: {integrity['integrity_valid']}, Events: {integrity['events_checked']}")
        results.append(("Replay integrity", integrity["integrity_valid"]))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Replay integrity", False))

    # Test 4: Tamper Detection
    print("\n── Test 4: Tamper Detection ──")
    try:
        db.execute(text("UPDATE replay_events SET parent_hash = 'tampered' WHERE replay_session_id = :sid AND event_type = 'step_2'"), {"sid": sid})
        db.commit()
        after = verifier.verify_replay_integrity(sid)
        print(f"  After tamper: valid={after['integrity_valid']}, breaks={after['chain_breaks']}")
        results.append(("Tamper detection", not after["integrity_valid"]))
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        results.append(("Tamper detection", False))

    # Test 5: Trust Scoring
    print("\n── Test 5: Trust Scoring ──")
    try:
        scorer = RuntimeTrustScorer(db)
        trust = scorer.compute_trust_scores(pid)
        ids = scorer.persist_trust_scores(pid, wid, trust)
        print(f"  Trust: {trust['overall_trust']:.4f}, Dimensions: {len(ids)}")
        results.append(("Trust scoring", len(ids) == 7))
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        results.append(("Trust scoring", False))

    # Test 6: Operator Intervention
    print("\n── Test 6: Operator Intervention ──")
    try:
        int_id = controller.record_operator_intervention(pid, wid, uid, "correction", "Fix", {"t": 0.5}, {"t": 0.3})
        print(f"  Intervention: {int_id[:8]}...")
        results.append(("Operator intervention", True))
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        results.append(("Operator intervention", False))

    # Test 7: Drift Event Persistence
    print("\n── Test 7: Drift Event Persistence ──")
    try:
        eid = str(uuid.uuid4())
        db.execute(text("INSERT INTO drift_events (id, project_id, workspace_id, drift_type, drift_category, severity, drift_score, threshold, evidence, recommended_action, detected_at) VALUES (:id,:pid,:wid,:dtype,:dcat,:sev,:score,:thresh,:ev,:act,:det)"),
                   {"id": eid, "pid": pid, "wid": wid, "dtype": "cognitive", "dcat": "cognitive", "sev": "low", "score": 0.15, "thresh": 0.4, "ev": "{}", "act": "Monitor", "det": datetime.now(timezone.utc)})
        db.commit()
        cnt = db.execute(text("SELECT COUNT(*) FROM drift_events WHERE id = :eid"), {"eid": eid}).scalar()
        print(f"  Drift event persisted: {cnt == 1}")
        results.append(("Drift event persistence", cnt == 1))
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        results.append(("Drift event persistence", False))

    # Test 8: Memory Poisoning
    print("\n── Test 8: Memory Poisoning Detection ──")
    try:
        poisoning = engine.detect_memory_poisoning(pid)
        print(f"  Poisoning: {poisoning['drift_detected']}, Contradictions: {poisoning.get('contradictory_keys', 0)}")
        results.append(("Memory poisoning", poisoning["drift_detected"]))
    except Exception as e:
        print(f"  Error: {e}")
        results.append(("Memory poisoning", False))

    db.close()

    # Summary
    print(f"\n{'=' * 60}")
    print("v0.3.5 INTEGRATION INTEGRITY SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False
    print(f"\n  RESULT: {'PASS' if all_pass else 'FAIL'} ({sum(1 for _, p in results if p)}/{len(results)})")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
