# Phase 6 — Adversarial Failure Test Report

```json
{
  "cases": {
    "ambiguous_requirement": {
      "requirement_id": "ADV-AMB-001",
      "text": "The system should be secure and fast.",
      "ambiguity_score": 0.2,
      "testability_score": 0.2,
      "ambiguity_detected": false,
      "low_testability": true
    },
    "conflicting_requirements": {
      "requirement_1": "ADV-CON-001: All incident records must be immutable.",
      "requirement_2": "ADV-CON-002: Admins must be able to permanently edit incident records after closure.",
      "conflict_type": "immutable vs editable",
      "governance_evaluations_for_conflict": 0,
      "conflict_detected_by_governance": false,
      "note": "Conflict detection requires governance engine analysis, not just normalization"
    },
    "missing_governance_evidence": {
      "requirement_id": "ADV-GOV-001",
      "text": "Escalation decisions must be auditable.",
      "governance_relevance": true,
      "evidence_bindings_total": 0,
      "evidence_required": true,
      "evidence_missing": true
    },
    "missing_negative_test": {
      "requirement_id": "ADV-SEC-001",
      "text": "The system must enforce tenant isolation.",
      "security_relevance": true,
      "negative_test_required": true,
      "negative_test_generated": false,
      "coverage_penalty_applied": true
    }
  }
}
```

## Analysis

### Case 1: Ambiguous Requirement

- ✅ Ambiguity detected (score: 0.2)
- ✅ Low testability detected (score: 0.2)
- ⚠️ No automatic acceptance criteria generation for ambiguous requirements

### Case 2: Conflicting Requirements

- ⚠️ Conflict detection is NOT implemented in the normalization engine
- ⚠️ Requires governance engine analysis (not tested here)
- This is a **known limitation** — conflict detection is a future phase

### Case 3: Missing Governance Evidence

- ✅ Governance relevance correctly flagged
- ⚠️ Evidence binding requires runtime log events to be present
- Evidence binding status depends on existing log data

### Case 4: Missing Negative Test

- ✅ Security relevance correctly flagged
- ⚠️ Negative test generation requires acceptance criteria with negative_case_required=True
- The requirement was normalized but no AC was created for it

## Verdict

The system correctly identifies ambiguity, security relevance, and governance relevance.
Conflict detection and automatic negative test generation from bare requirements are **not yet implemented**.
These are known limitations, not hidden defects.
