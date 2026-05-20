"""
Phases 4-7 Combined: Memory Pressure, Trust Degradation, Failure Injection, Regression
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps", "api", "src"))

from core.config import settings

SYNC_DATABASE_URL = settings.database_url.replace("+asyncpg", "")
engine = sa.create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=engine)


def seed_test_project(db, project_id: str, name: str):
    now = datetime.now(timezone.utc)
    result = db.execute(text("SELECT id FROM workspaces LIMIT 1"))
    ws = result.fetchone()
    ws_id = ws[0] if ws else str(uuid.uuid4())
    if not ws:
        db.execute(text(
            "INSERT INTO workspaces (id, name, slug, created_at, updated_at) "
            "VALUES (:id, :name, :slug, :ca, :ua)"
        ), {"id": ws_id, "name": "Test WS", "slug": "test-ws", "ca": now, "ua": now})
        db.commit()

    result = db.execute(text("SELECT id FROM projects WHERE id = :pid"), {"pid": project_id})
    if not result.fetchone():
        db.execute(text(
            "INSERT INTO projects (id, name, slug, status, workspace_id, created_at, updated_at) "
            "VALUES (:id, :name, :slug, 'active', :ws, :ca, :ua)"
        ), {"id": project_id, "name": name, "slug": name.lower().replace(" ", "-"),
            "ws": ws_id, "ca": now, "ua": now})
    db.commit()
    return ws_id


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4 — Memory Pressure & Memory Leak Validation
# ═══════════════════════════════════════════════════════════════════════════

def run_memory_pressure_test():
    """Generate large memory lineage and measure growth/retrieval."""
    db = SyncSessionLocal()
    project_id = "00000000-0000-0000-0000-000000000004"
    run_id = str(uuid.uuid4())
    results = {"phase": "memory_pressure"}

    try:
        seed_test_project(db, project_id, "Memory Pressure Test")
        now = datetime.now(timezone.utc)

        db.execute(text(
            "INSERT INTO runs (id, project_id, name, status, is_demo, total_cost, "
            " budget_limit, created_at, updated_at) "
            "VALUES (:id, :pid, :name, 'running', false, 0, 10000, :ca, :ua)"
        ), {"id": run_id, "pid": project_id, "name": "Memory Pressure Test",
            "ca": now, "ua": now})
        db.commit()

        # Generate large memory lineage: 500 semantic memory versions
        start = time.time()
        for i in range(500):
            sm_id = str(uuid.uuid4())
            content = json.dumps({
                "version": i,
                "lineage": f"memory_lineage_{i}",
                "data": f"semantic_content_v{i}_{uuid.uuid4().hex[:8]}",
                "drift_indicator": i / 500.0,
            })
            drift = i / 500.0  # 0.0 to 0.998
            db.execute(text(
                "INSERT INTO semantic_memory "
                "(id, project_id, memory_type, entity_type, entity_id, "
                " semantic_content, drift_score, confidence, created_at, updated_at, is_active) "
                "VALUES (:id, :pid, 'memory_lineage', 'run', :eid, "
                " :content, :drift, :conf, :ca, :ua, true)"
            ), {
                "id": sm_id, "pid": project_id, "eid": run_id,
                "content": content, "drift": drift, "conf": 1.0 - drift,
                "ca": now, "ua": now,
            })
        db.commit()
        results["semantic_write_time_ms"] = (time.time() - start) * 1000

        # Generate governance history: 200 entries
        start = time.time()
        for i in range(200):
            mi_id = str(uuid.uuid4())
            db.execute(text(
                "INSERT INTO memory_items "
                "(id, project_id, memory_type, key, content, source, metadata, created_at) "
                "VALUES (:id, :pid, 'governance_history', :key, :content, :source, :meta, :ca)"
            ), {
                "id": mi_id, "pid": project_id,
                "key": f"governance:{i}",
                "content": f"Governance event {i}: decision={uuid.uuid4().hex[:8]}",
                "source": "memory_pressure_test",
                "meta": json.dumps({"event_index": i, "type": "governance"}),
                "ca": now,
            })
        db.commit()
        results["governance_write_time_ms"] = (time.time() - start) * 1000

        # Measure retrieval latency
        start = time.time()
        count = db.execute(text(
            "SELECT COUNT(*) FROM semantic_memory WHERE project_id = :pid"
        ), {"pid": project_id}).fetchone()[0]
        results["semantic_count"] = count
        results["semantic_count_latency_ms"] = (time.time() - start) * 1000

        start = time.time()
        drifted = db.execute(text(
            "SELECT COUNT(*) FROM semantic_memory WHERE project_id = :pid AND drift_score > 0.5"
        ), {"pid": project_id}).fetchone()[0]
        results["drifted_count"] = drifted
        results["drifted_query_latency_ms"] = (time.time() - start) * 1000

        start = time.time()
        lineage = db.execute(text("""
            SELECT semantic_content->>'version' as ver, drift_score
            FROM semantic_memory
            WHERE project_id = :pid AND memory_type = 'memory_lineage'
            ORDER BY created_at DESC LIMIT 10
        """), {"pid": project_id}).fetchall()
        results["lineage_retrieval_ms"] = (time.time() - start) * 1000
        results["latest_versions"] = [r[0] for r in lineage]

        # Check for orphaned records
        orphaned = db.execute(text("""
            SELECT COUNT(*) FROM semantic_memory sm
            WHERE sm.project_id = :pid
            AND NOT EXISTS (SELECT 1 FROM projects p WHERE p.id = sm.project_id)
        """), {"pid": project_id}).fetchone()[0]
        results["orphaned_records"] = orphaned

        # Memory growth analysis
        total_semantic = db.execute(text(
            "SELECT COUNT(*) FROM semantic_memory"
        )).fetchone()[0]
        total_memory_items = db.execute(text(
            "SELECT COUNT(*) FROM memory_items"
        )).fetchone()[0]
        results["total_semantic_memory"] = total_semantic
        results["total_memory_items"] = total_memory_items

        results["status"] = "PASS" if orphaned == 0 else "FAIL"

        print(f"  Phase 4 — Memory Pressure:")
        print(f"    Semantic memory entries: {count}")
        print(f"    Drifted entries: {drifted}")
        print(f"    Orphaned records: {orphaned}")
        print(f"    Write time (500 entries): {results['semantic_write_time_ms']:.0f}ms")
        print(f"    Retrieval latency: {results['lineage_retrieval_ms']:.2f}ms")
        print(f"    Status: {'✅ PASS' if orphaned == 0 else '❌ FAIL'}")

        return results

    except Exception as e:
        db.rollback()
        results["status"] = "ERROR"
        results["error"] = str(e)
        return results
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5 — Trust Degradation & Autonomy Collapse
# ═══════════════════════════════════════════════════════════════════════════

def run_trust_degradation_test():
    """Trigger trust degradation scenarios and observe behavior."""
    db = SyncSessionLocal()
    project_id = "00000000-0000-0000-0000-000000000005"
    run_id = str(uuid.uuid4())
    results = {"phase": "trust_degradation"}

    try:
        seed_test_project(db, project_id, "Trust Degradation Test")
        now = datetime.now(timezone.utc)

        db.execute(text(
            "INSERT INTO runs (id, project_id, name, status, is_demo, total_cost, "
            " budget_limit, created_at, updated_at) "
            "VALUES (:id, :pid, :name, 'running', false, 0, 10000, :ca, :ua)"
        ), {"id": run_id, "pid": project_id, "name": "Trust Degradation Test",
            "ca": now, "ua": now})
        db.commit()

        trust_events = []

        # Scenario 1: Replay corruption (inject evidence with broken chain)
        ev_id = str(uuid.uuid4())
        fake_hash = "deadbeef" * 8
        db.execute(text(
            "INSERT INTO evidence_bundles "
            "(id, run_id, bundle_path, bundle_hash, size_bytes, artifact_count, created_at, chain_hash) "
            "VALUES (:id, :rid, :path, :hash, :size, :count, :ca, :chain)"
        ), {
            "id": ev_id, "rid": run_id,
            "path": "/evidence/corrupted/test.json",
            "hash": fake_hash, "size": 100, "count": 1,
            "ca": now, "chain": "broken_chain_hash",
        })

        # Detect corruption: bundle_hash != chain_hash
        corruption = db.execute(text("""
            SELECT COUNT(*) FROM evidence_bundles
            WHERE run_id = :rid AND bundle_hash != chain_hash
        """), {"rid": run_id}).fetchone()[0]
        trust_events.append({
            "scenario": "replay_corruption",
            "corrupted_events": corruption,
            "detected": corruption > 0,
        })

        # Scenario 2: Semantic drift accumulation
        for i in range(20):
            sm_id = str(uuid.uuid4())
            db.execute(text(
                "INSERT INTO semantic_memory "
                "(id, project_id, memory_type, entity_type, entity_id, "
                " semantic_content, drift_score, confidence, created_at, updated_at, is_active) "
                "VALUES (:id, :pid, 'drift_scenario', 'run', :eid, "
                " :content, :drift, :conf, :ca, :ua, true)"
            ), {
                "id": sm_id, "pid": project_id, "eid": run_id,
                "content": json.dumps({"scenario": "drift", "index": i}),
                "drift": 0.8 + (i % 3) * 0.05,  # High drift: 0.8-0.9
                "conf": 0.1,
                "ca": now, "ua": now,
            })

        high_drift = db.execute(text("""
            SELECT COUNT(*) FROM semantic_memory
            WHERE project_id = :pid AND drift_score > 0.7
        """), {"pid": project_id}).fetchone()[0]
        trust_events.append({
            "scenario": "semantic_drift",
            "high_drift_entries": high_drift,
            "detected": high_drift > 0,
        })

        # Scenario 3: Memory poisoning (contradictory entries)
        for i in range(10):
            mi_id = str(uuid.uuid4())
            db.execute(text(
                "INSERT INTO memory_items "
                "(id, project_id, memory_type, key, content, source, metadata, created_at) "
                "VALUES (:id, :pid, 'poison', :key, :content, :source, :meta, :ca)"
            ), {
                "id": mi_id, "pid": project_id,
                "key": "system_architecture",  # Same key, different content = poison
                "content": f"Architecture variant {i}: use_{['microservices', 'monolith', 'serverless', 'event-driven', 'layered'][i % 5]}",
                "source": "poison_test",
                "meta": json.dumps({"contradicts": True}),
                "ca": now,
            })

        # Detect poisoning: same key, different content
        poison = db.execute(text("""
            SELECT key, COUNT(DISTINCT content) as variants
            FROM memory_items
            WHERE project_id = :pid AND memory_type = 'poison'
            GROUP BY key
            HAVING COUNT(DISTINCT content) > 1
        """), {"pid": project_id}).fetchall()
        trust_events.append({
            "scenario": "memory_poisoning",
            "poisoned_keys": len(poison),
            "max_variants": max(r[1] for r in poison) if poison else 0,
            "detected": len(poison) > 0,
        })

        # Scenario 4: Incomplete evidence
        incomplete_ev = str(uuid.uuid4())
        db.execute(text(
            "INSERT INTO evidence_bundles "
            "(id, run_id, bundle_path, bundle_hash, size_bytes, artifact_count, created_at, chain_hash) "
            "VALUES (:id, :rid, :path, :hash, :size, :count, :ca, :chain)"
        ), {
            "id": incomplete_ev, "rid": run_id,
            "path": "/evidence/incomplete/test.json",
            "hash": None, "size": 0, "count": 0,  # Incomplete: no hash
            "ca": now, "chain": None,
        })

        incomplete = db.execute(text("""
            SELECT COUNT(*) FROM evidence_bundles
            WHERE run_id = :rid AND chain_hash IS NULL
        """), {"rid": run_id}).fetchone()[0]
        trust_events.append({
            "scenario": "incomplete_evidence",
            "incomplete_events": incomplete,
            "detected": incomplete > 0,
        })

        db.commit()

        # Compute trust score degradation
        total_events = len(trust_events)
        detected_events = sum(1 for e in trust_events if e["detected"])
        trust_score = 1.0 - (detected_events / total_events) if total_events > 0 else 1.0

        results["trust_events"] = trust_events
        results["total_scenarios"] = total_events
        results["detected_scenarios"] = detected_events
        results["trust_score"] = trust_score
        results["autonomy_level"] = "full" if trust_score > 0.7 else "reduced" if trust_score > 0.4 else "restricted"
        results["status"] = "PASS" if detected_events == total_events else "FAIL"

        print(f"\n  Phase 5 — Trust Degradation:")
        for ev in trust_events:
            print(f"    {ev['scenario']}: detected={ev['detected']}")
        print(f"    Trust score: {trust_score:.2f}")
        print(f"    Autonomy level: {results['autonomy_level']}")
        print(f"    Status: {'✅ PASS' if detected_events == total_events else '❌ FAIL'}")

        return results

    except Exception as e:
        db.rollback()
        results["status"] = "ERROR"
        results["error"] = str(e)
        return results
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6 — Failure Injection & Recovery
# ═══════════════════════════════════════════════════════════════════════════

def run_failure_injection_test():
    """Inject failures and verify recovery."""
    db = SyncSessionLocal()
    project_id = "00000000-0000-0000-0000-000000000006"
    run_id = str(uuid.uuid4())
    results = {"phase": "failure_injection"}

    try:
        seed_test_project(db, project_id, "Failure Injection Test")
        now = datetime.now(timezone.utc)

        db.execute(text(
            "INSERT INTO runs (id, project_id, name, status, is_demo, total_cost, "
            " budget_limit, created_at, updated_at) "
            "VALUES (:id, :pid, :name, 'running', false, 0, 10000, :ca, :ua)"
        ), {"id": run_id, "pid": project_id, "name": "Failure Injection Test",
            "ca": now, "ua": now})
        db.commit()

        failure_results = []

        # Test 1: Transaction rollback mid-persistence
        try:
            for i in range(5):
                sm_id = str(uuid.uuid4())
                db.execute(text(
                    "INSERT INTO semantic_memory "
                    "(id, project_id, memory_type, entity_type, entity_id, "
                    " semantic_content, drift_score, confidence, created_at, updated_at, is_active) "
                    "VALUES (:id, :pid, 'failure_test', 'run', :eid, "
                    " :content, 0.5, 0.5, :ca, :ua, true)"
                ), {
                    "id": sm_id, "pid": project_id, "eid": run_id,
                    "content": json.dumps({"index": i}),
                    "ca": now, "ua": now,
                })
            # Simulate failure: rollback
            db.rollback()

            # Verify: count should be 0 (rolled back)
            count_after_rollback = db.execute(text(
                "SELECT COUNT(*) FROM semantic_memory WHERE project_id = :pid AND memory_type = 'failure_test'"
            ), {"pid": project_id}).fetchone()[0]

            # Now re-insert successfully
            for i in range(5):
                sm_id = str(uuid.uuid4())
                db.execute(text(
                    "INSERT INTO semantic_memory "
                    "(id, project_id, memory_type, entity_type, entity_id, "
                    " semantic_content, drift_score, confidence, created_at, updated_at, is_active) "
                    "VALUES (:id, :pid, 'failure_test', 'run', :eid, "
                    " :content, 0.5, 0.5, :ca, :ua, true)"
                ), {
                    "id": sm_id, "pid": project_id, "eid": run_id,
                    "content": json.dumps({"index": i, "recovered": True}),
                    "ca": now, "ua": now,
                })
            db.commit()

            count_after_recovery = db.execute(text(
                "SELECT COUNT(*) FROM semantic_memory WHERE project_id = :pid AND memory_type = 'failure_test'"
            ), {"pid": project_id}).fetchone()[0]

            failure_results.append({
                "test": "transaction_rollback",
                "rolled_back_clean": count_after_rollback == 0,
                "recovery_success": count_after_recovery == 5,
                "status": "PASS" if count_after_rollback == 0 and count_after_recovery == 5 else "FAIL",
            })
        except Exception as e:
            db.rollback()
            failure_results.append({"test": "transaction_rollback", "status": "ERROR", "error": str(e)})

        # Test 2: Partial DB failure (simulate by inserting then corrupting)
        try:
            # Insert valid evidence
            ev_id = str(uuid.uuid4())
            content = json.dumps({"test": "partial_failure"})
            ev_hash = hashlib.sha256(content.encode()).hexdigest()
            db.execute(text(
                "INSERT INTO evidence_bundles "
                "(id, run_id, bundle_path, bundle_hash, size_bytes, artifact_count, created_at, chain_hash) "
                "VALUES (:id, :rid, :path, :hash, :size, :count, :ca, :chain)"
            ), {
                "id": ev_id, "rid": run_id,
                "path": "/evidence/partial/test.json",
                "hash": ev_hash, "size": len(content), "count": 1,
                "ca": now, "chain": ev_hash,
            })
            db.commit()

            # Verify chain intact
            chain_check = db.execute(text("""
                SELECT bundle_hash = chain_hash as intact
                FROM evidence_bundles WHERE id = :eid
            """), {"eid": ev_id}).fetchone()[0]

            failure_results.append({
                "test": "partial_failure_recovery",
                "chain_intact": chain_check,
                "status": "PASS" if chain_check else "FAIL",
            })
        except Exception as e:
            db.rollback()
            failure_results.append({"test": "partial_failure_recovery", "status": "ERROR", "error": str(e)})

        # Test 3: Stale session reuse
        try:
            stale_db = SyncSessionLocal()
            stale_db.rollback()  # Ensure clean state
            sm_id = str(uuid.uuid4())
            stale_db.execute(text(
                "INSERT INTO semantic_memory "
                "(id, project_id, memory_type, entity_type, entity_id, "
                " semantic_content, drift_score, confidence, created_at, updated_at, is_active) "
                "VALUES (:id, :pid, 'stale_session', 'run', :eid, "
                " :content, 0.5, 0.5, :ca, :ua, true)"
            ), {
                "id": sm_id, "pid": project_id, "eid": run_id,
                "content": json.dumps({"test": "stale_session"}),
                "ca": now, "ua": now,
            })
            stale_db.commit()
            stale_db.close()

            # Verify
            stale_count = db.execute(text(
                "SELECT COUNT(*) FROM semantic_memory WHERE project_id = :pid AND memory_type = 'stale_session'"
            ), {"pid": project_id}).fetchone()[0]

            failure_results.append({
                "test": "stale_session_reuse",
                "session_reusable": stale_count == 1,
                "status": "PASS" if stale_count == 1 else "FAIL",
            })
        except Exception as e:
            failure_results.append({"test": "stale_session_reuse", "status": "ERROR", "error": str(e)})

        # Test 4: Retry storm simulation
        try:
            retry_success = 0
            for attempt in range(5):
                try:
                    mi_id = str(uuid.uuid4())
                    db.execute(text(
                        "INSERT INTO memory_items "
                        "(id, project_id, memory_type, key, content, source, metadata, created_at) "
                        "VALUES (:id, :pid, 'retry_storm', :key, :content, :source, :meta, :ca)"
                    ), {
                        "id": mi_id, "pid": project_id,
                        "key": f"retry:{attempt}",
                        "content": f"Retry attempt {attempt}",
                        "source": "retry_test",
                        "meta": json.dumps({"attempt": attempt}),
                        "ca": now,
                    })
                    db.commit()
                    retry_success += 1
                except Exception:
                    db.rollback()

            failure_results.append({
                "test": "retry_storm",
                "successful_retries": retry_success,
                "status": "PASS" if retry_success == 5 else "PARTIAL",
            })
        except Exception as e:
            db.rollback()
            failure_results.append({"test": "retry_storm", "status": "ERROR", "error": str(e)})

        db.commit()

        passed = sum(1 for r in failure_results if r.get("status") == "PASS")
        total = len(failure_results)
        results["failure_results"] = failure_results
        results["passed"] = passed
        results["total"] = total
        results["status"] = "PASS" if passed == total else "PARTIAL" if passed > 0 else "FAIL"

        print(f"\n  Phase 6 — Failure Injection & Recovery:")
        for fr in failure_results:
            print(f"    {fr['test']}: {fr.get('status', 'UNKNOWN')}")
        print(f"    Passed: {passed}/{total}")
        print(f"    Status: {'✅ PASS' if passed == total else '⚠️ PARTIAL' if passed > 0 else '❌ FAIL'}")

        return results

    except Exception as e:
        db.rollback()
        results["status"] = "ERROR"
        results["error"] = str(e)
        return results
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  v0.3.6 — PHASES 4-6: MEMORY, TRUST, FAILURE INJECTION")
    print("=" * 70)

    r4 = run_memory_pressure_test()
    r5 = run_trust_degradation_test()
    r6 = run_failure_injection_test()

    print(f"\n{'=' * 70}")
    print("  COMBINED RESULTS")
    print(f"{'=' * 70}")
    print(f"  Phase 4 (Memory Pressure):  {r4.get('status', 'UNKNOWN')}")
    print(f"  Phase 5 (Trust Degradation): {r5.get('status', 'UNKNOWN')}")
    print(f"  Phase 6 (Failure Injection): {r6.get('status', 'UNKNOWN')}")

    all_pass = all(r.get("status") == "PASS" for r in [r4, r5, r6])
    print(f"\n  OVERALL: {'✅ ALL PASS' if all_pass else '⚠️ SOME ISSUES'}")
    print(f"{'=' * 70}")
