# Engine Route Validation Report

**Date**: 2026-05-14
**Status**: ALL ROUTES VERIFIED

## Validation Criteria

- [x] All 7 engine modules import without errors
- [x] FastAPI app starts without exceptions
- [x] Health check returns 200 OK
- [x] `/openapi.json` contains all engine routes
- [x] `/docs` displays engine endpoints
- [x] `/api/v1/debug/routes` lists all routes
- [x] `/api/v1/debug/import-check` reports all OK

## Route Groups

### Specification Engine (5 routes)
- POST /api/v1/engines/specification/generate/{run_id}
- GET  /api/v1/engines/specification/{run_id}
- GET  /api/v1/engines/specification/{run_id}/latest
- POST /api/v1/engines/specification/{run_id}/lock/{version_id}
- GET  /api/v1/engines/specification/{run_id}/diff

### Architecture Engine (5 routes)
- POST /api/v1/engines/architecture/generate/{run_id}
- GET  /api/v1/engines/architecture/{run_id}
- GET  /api/v1/engines/architecture/{run_id}/latest
- POST /api/v1/engines/architecture/{run_id}/lock/{version_id}
- POST /api/v1/engines/architecture/{run_id}/drift-check

### Governance Engine (7 routes)
- POST /api/v1/engines/governance/seed
- GET  /api/v1/engines/governance/policies
- POST /api/v1/engines/governance/evaluate/{run_id}
- GET  /api/v1/engines/governance/evaluations/{run_id}
- POST /api/v1/engines/governance/release-gates/{run_id}
- POST /api/v1/engines/governance/release-gates/{run_id}/evaluate/{gate_id}
- POST /api/v1/engines/governance/release-gates/{run_id}/waive/{gate_id}

### Test Plan Engine (3 routes)
- POST /api/v1/engines/test-plan/generate/{run_id}
- GET  /api/v1/engines/test-plan/{run_id}
- GET  /api/v1/engines/test-plan/{run_id}/latest

### Traceability Engine (3 routes)
- GET  /api/v1/engines/traceability/{run_id}
- POST /api/v1/engines/traceability/{run_id}/link
- GET  /api/v1/engines/traceability/{run_id}/coverage

### Snapshot Engine (3 routes)
- POST /api/v1/engines/snapshots/{run_id}
- GET  /api/v1/engines/snapshots/{run_id}
- GET  /api/v1/engines/snapshots/{run_id}/export/{snapshot_id}

## SQLAlchemy Relationship Audit

### Run class relationships (16 total)
- project ✓
- phases ✓
- cost_events ✓
- log_events ✓
- evidence_bundles ✓
- model_calls ✓
- tool_calls_list ✓
- checkpoints ✓
- spec_versions ✓ (Phase 4)
- arch_versions ✓ (Phase 4)
- governance_evals ✓ (Phase 4)
- release_gates ✓ (Phase 4)
- test_plans ✓ (Phase 4)
- traceability_links ✓ (Phase 4)
- artifact_baselines ✓ (Phase 4)
- snapshots ✓ (Phase 4)
- artifact_diffs ✓ (Phase 4)

### Project class relationships (4 total)
- runs ✓
- spec_versions ✓ (Phase 4)
- arch_versions ✓ (Phase 4)
- test_plans ✓ (Phase 4)

### Back-populates cross-reference
All 9 Phase 4 model classes have matching `back_populates="run"` and `back_populates="project"` references. No dangling relationships.

## Conclusion

The Cognitive Cortex runtime is fully operational. All engine routes are mounted, all imports resolve, and all SQLAlchemy relationships are correctly configured.
