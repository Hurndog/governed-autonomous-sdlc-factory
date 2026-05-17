# Phase 3 — Runtime Anti-Stub Validation Report

**Date**: 2026-05-17
**Run ID**: 6a7f7ea0-297f-435e-9bb2-899368c7d332

## Results

```json
{
  "run_id": "6a7f7ea0-297f-435e-9bb2-899368c7d332",
  "phases": {
    "requirement_normalization": {
      "status": "ok",
      "count": 6,
      "records": [
        {
          "id": "9b88752c-cb05-4515-8c41-dd5f43855231",
          "requirement_id": "FR-001",
          "normalized_statement": "User SHALL process jwt"
        },
        {
          "id": "79f6d04a-acd6-43aa-bfd5-d4478d560652",
          "requirement_id": "FR-002",
          "normalized_statement": "The system SHALL enforce task"
        },
        {
          "id": "7bdfe8d4-3c3b-4d29-8876-9fd8fbdff422",
          "requirement_id": "FR-003",
          "normalized_statement": "User SHALL limit user"
        }
      ]
    },
    "acceptance_criteria": {
      "status": "ok",
      "count": 6,
      "records": [
        {
          "id": "d2cd7742-6848-47df-a85c-70fc90170b7e",
          "ac_id": "AC-001",
          "then": "A new user can register with a valid email and password, receives a JWT that exp"
        },
        {
          "id": "3a78efb9-1baf-4eee-bdfc-d6cc4c4d78b9",
          "ac_id": "AC-002",
          "then": "A user can create a task with title, description, and due date; retrieve only th"
        },
        {
          "id": "806a2a97-0ebf-44ce-82c9-4ac89f237446",
          "ac_id": "AC-003",
          "then": "The system enforces a limit of 100 requests per minute per user/IP. After exceed"
        }
      ]
    },
    "test_obligations": {
      "status": "ok",
      "count": 10,
      "records": [
        {
          "id": "a7c2fad5-1aa3-4f5a-bc3f-ea0aac525170",
          "obl_id": "OBL-FR-001-AC-001-FUNC",
          "type": "functional"
        },
        {
          "id": "511b859e-42fa-46cf-af41-976f2bbb083d",
          "obl_id": "OBL-FR-001-AC-001-SEC",
          "type": "security"
        },
        {
          "id": "076d3f27-6658-4fad-9110-1e72e12fc3ec",
          "obl_id": "OBL-FR-002-AC-002-FUNC",
          "type": "functional"
        }
      ]
    },
    "semantic_alignment": {
      "status": "ok",
      "count": 13,
      "records": [
        {
          "id": "1567259e-efbf-4270-9760-21110265053b",
          "tc_id": "TC-001",
          "score": 0.7000000000000001,
          "verdict": "pass"
        },
        {
          "id": "9a2ab562-fe32-4376-a6e8-8ac6892c02fb",
          "tc_id": "TC-001",
          "score": 0.7000000000000001,
          "verdict": "pass"
        },
        {
          "id": "d1c2cf08-bb8b-46fc-8e2d-76f5dab9fe14",
          "tc_id": "TC-002",
          "score": 0.5,
          "verdict": "fail"
        }
      ]
    },
    "verifier_critique": {
      "status": "ok",
      "count": 13,
      "records": [
        {
          "id": "1f103194-3d03-4100-b2e3-df2666a48a6b",
          "verdict": "fail",
          "confidence": 0.9
        },
        {
          "id": "0793029d-6d30-4cef-b6d9-2ff0dcc83794",
          "verdict": "fail",
          "confidence": 0.9
        },
        {
          "id": "be959325-6033-454a-9639-d5a8135b713c",
          "verdict": "partial",
          "confidence": 0.9
        }
      ]
    },
    "mutation_tests": {
      "status": "ok",
      "count": 25,
      "records": [
        {
          "id": "4ddb817e-5a46-4dad-adf8-932407f8d239",
          "mut_id": "MUT-FR-001-boundary_shift",
          "type": "boundary_shift"
        },
        {
          "id": "d713e0f0-a33d-4cb3-9424-54d0feaec158",
          "mut_id": "MUT-FR-001-null_injection",
          "type": "null_injection"
        },
        {
          "id": "a162c3df-441d-4b6f-bb77-97511063654e",
          "mut_id": "MUT-FR-001-type_confusion",
          "type": "type_confusion"
        }
      ]
    },
    "negative_coverage": {
      "status": "ok",
      "count": 6,
      "records": [
        {
          "id": "d90ee1e9-d768-48ab-aa0f-a5db0e9e1738",
          "req_id": "FR-001",
          "status": "pending"
        },
        {
          "id": "1ddca520-8a55-4fad-ac4c-e4c59d7cb438",
          "req_id": "FR-003",
          "status": "pending"
        },
        {
          "id": "f9fe1a8b-435d-4146-90c2-7d26eb9d1400",
          "req_id": "FR-002",
          "status": "pending"
        }
      ]
    },
    "runtime_evidence": {
      "status": "ok",
      "count": 1,
      "records": [
        {
          "id": "94f3ea25-6a77-4363-b991-214cefe219d9",
          "type": "audit_log",
          "status": "bound"
        }
      ]
    },
    "score_computation": {
      "status": "ok",
      "score": 0.6772,
      "gate": "fail",
      "critical_passed": false,
      "id": "bf62aeec-ab08-4e34-bb4d-9277807f9fd5"
    }
  },
  "errors": [],
  "idempotency": {
    "status": "ok",
    "score": 0.6772,
    "gate": "fail"
  },
  "db_count_requirement_normalizations": 6,
  "db_count_acceptance_criteria_contracts": 6,
  "db_count_test_obligations": 10,
  "db_count_semantic_alignment_evaluations": 13,
  "db_count_verifier_critiques": 13,
  "db_count_mutation_tests": 25,
  "db_count_negative_test_requirements": 4,
  "db_count_runtime_evidence_bindings": 1,
  "db_count_semantic_coverage_reports": 1,
  "score_source": {
    "requirements_in_db": 6,
    "obligations_in_db": 10,
    "evaluations_in_db": 13,
    "score_computed_from_records": true
  }
}
```

## Errors

None — all phases executed successfully.

## Verdict

✅ All phases executed with real inputs and real outputs.
✅ Scores are computed from persisted records, not hardcoded.
✅ Pipeline is idempotent — re-run produces same results.
