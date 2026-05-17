# Phase 4 — Full Black-Box Run Report

**Run ID**: 7ff8a2fd-5e9f-4d68-8611-ef320da02627

```json
{
  "run_id": "7ff8a2fd-5e9f-4d68-8611-ef320da02627",
  "phases": {
    "full_pipeline": {
      "status": "ok",
      "score": 0.6559,
      "gate": "fail",
      "critical_passed": false
    }
  },
  "count_requirements": 8,
  "count_acceptance_criteria": 8,
  "count_test_obligations": 14,
  "count_alignment_evaluations": 18,
  "count_verifier_critiques": 18,
  "count_mutation_tests": 40,
  "count_negative_requirements": 7,
  "count_evidence_bindings": 3,
  "count_coverage_reports": 1,
  "conflicts": {
    "count": 1,
    "findings": [
      {
        "type": "immutability_vs_editability",
        "severity": "critical",
        "req1": "FR-004",
        "req2": "FR-005"
      }
    ]
  },
  "artifacts": [
    {
      "type": "specification",
      "name": "intent.md"
    },
    {
      "type": "specification",
      "name": "requirements.json"
    },
    {
      "type": "specification",
      "name": "acceptance_criteria.json"
    },
    {
      "type": "specification",
      "name": "governance_areas.json"
    },
    {
      "type": "architecture",
      "name": "adrs.json"
    },
    {
      "type": "governance",
      "name": "security_findings.json"
    },
    {
      "type": "architecture",
      "name": "architecture.md"
    },
    {
      "type": "architecture",
      "name": "components.json"
    },
    {
      "type": "architecture",
      "name": "diagram_Incident Submission Flow.mmd"
    },
    {
      "type": "governance",
      "name": "governance_concerns.json"
    },
    {
      "type": "governance",
      "name": "compliance_gaps.json"
    },
    {
      "type": "test_plan",
      "name": "test_plan.json"
    }
  ],
  "idempotency": {
    "status": "ok",
    "score": 0.6559,
    "gate": "fail"
  }
}
```

## Verdict

✅ Full black-box run completed successfully.
- Semantic coverage score: 0.6559
- Release gate: fail
- Conflicts detected: 1
