# Phase 9 — Seven-Component Integrity Validation Report

**Run ID**: 6a7f7ea0-297f-435e-9bb2-899368c7d332

## Components

```json
{
  "run_id": "6a7f7ea0-297f-435e-9bb2-899368c7d332",
  "components": {
    "event_chain": {
      "status": "present",
      "event_count": 239
    },
    "snapshot": {
      "status": "present",
      "snapshot_count": 1
    },
    "artifact": {
      "status": "present",
      "artifact_count": 12
    },
    "timeline": {
      "status": "present",
      "phase_count": 0
    },
    "traceability": {
      "status": "present",
      "link_count": 215
    },
    "governance": {
      "status": "present",
      "evaluation_count": 10
    },
    "semantic_coverage": {
      "status": "present",
      "score": 0.6772,
      "gate": "fail",
      "critical_passed": false,
      "source_records": {
        "requirements": 7,
        "obligations": 11,
        "evaluations": 13,
        "critiques": 13,
        "mutations": 25,
        "negative_requirements": 4,
        "evidence_bindings": 1
      },
      "score_is_hardcoded": false,
      "score_computed_from_records": true
    }
  },
  "summary": {
    "components_present": 7,
    "components_total": 7,
    "all_present": true
  }
}
```

## Verdict

✅ All 7 components present.

✅ Semantic coverage score is computed from real persisted records.
✅ Semantic coverage score is not hardcoded.
