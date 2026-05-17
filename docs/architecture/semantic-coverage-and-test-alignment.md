# Semantic Coverage and Test Alignment Contract

**Date:** 2026-05-16
**Version:** 1.0
**Status:** DRAFT — Defines the formal contract for Phase 2+

---

## 1. Semantic Coverage — Definition

**Semantic Coverage** is a measured degree to which tests prove the intended behavior of requirements and acceptance criteria.

Unlike code coverage (which measures which lines are executed), semantic coverage measures:
- Whether tests actually validate what requirements **mean**
- Whether acceptance criteria are **proven**, not just referenced
- Whether tests can detect **broken behavior**, not just happy paths
- Whether runtime evidence **binds** to test results
- Whether mutations are **killed** by tests
- Whether an independent verifier **confirms** the alignment

**Semantic Coverage = 0.0** when tests exist as JSON definitions but are never executed.
**Semantic Coverage = 1.0** when every critical requirement has proven, executed, verified, mutation-tested, evidence-bound tests.

---

## 2. Requirement Normalization

Every requirement must be normalized into a testable structure.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `requirement_id` | string | Unique identifier (e.g., AUTH-001) |
| `title` | string | Short human-readable title |
| `normalized_statement` | string | Single testable statement in "Actor SHALL Action Object WHEN Constraint" format |
| `actor` | string | Who performs the action |
| `action` | string | What is done |
| `object` | string | What is acted upon |
| `constraints` | JSON | Conditions, limits, boundaries |
| `expected_behavior` | string | Observable correct behavior |
| `failure_behavior` | string | Observable failure behavior |
| `governance_relevance` | boolean | Whether this requirement has governance implications |
| `security_relevance` | boolean | Whether this requirement has security implications |
| `evidence_required` | JSON | List of required evidence types |
| `criticality` | enum | `critical`, `high`, `medium`, `low` |
| `ambiguity_score` | float | 0.0 (clear) to 1.0 (ambiguous) |
| `testability_score` | float | 0.0 (untestable) to 1.0 (fully testable) |

### Normalization Rules

1. Each requirement MUST have exactly one `normalized_statement`
2. The statement MUST be testable (can be verified by observation)
3. Ambiguous requirements MUST be split or clarified
4. Criticality MUST be assigned based on impact analysis
5. Security-relevant requirements MUST be flagged
6. Governance-relevant requirements MUST be flagged

---

## 3. Acceptance Criteria Contract

Every requirement must have at least one acceptance criterion.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `acceptance_criterion_id` | string | Unique identifier |
| `requirement_id` | string | Parent requirement |
| `given` | string | Precondition/context |
| `when` | string | Action/trigger |
| `then` | string | Expected outcome |
| `and_conditions` | JSON | Additional conditions |
| `evidence_required` | JSON | Required evidence types |
| `negative_case_required` | boolean | Whether negative test is required |
| `governance_case_required` | boolean | Whether governance test is required |
| `security_case_required` | boolean | Whether security test is required |

### Validation Rules

1. Every requirement MUST have at least one acceptance criterion
2. Acceptance criteria MUST follow Given/When/Then format
3. Critical requirements MUST have at least 3 acceptance criteria
4. Security requirements MUST have negative case criteria
5. Missing acceptance criteria FAIL the release gate

---

## 4. Test Obligation

A test obligation is a formal statement of what must be proven before executable tests are considered adequate.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `obligation_id` | string | Unique identifier |
| `requirement_id` | string | Parent requirement |
| `acceptance_criterion_id` | string | Parent acceptance criterion |
| `obligation_type` | enum | See types below |
| `proof_statement` | string | What must be proven |
| `required_test_type` | enum | `unit`, `integration`, `contract`, `e2e`, `mutation`, `negative` |
| `required_evidence_type` | enum | `api_response`, `database_state`, `log_event`, `audit_event`, `governance_eval`, `artifact_hash`, `event_chain`, `snapshot` |
| `criticality` | enum | Inherited from requirement |
| `status` | enum | `pending`, `satisfied`, `waived`, `failed` |

### Obligation Types

| Type | Description |
|------|-------------|
| `happy_path` | Proves correct behavior under normal conditions |
| `negative_path` | Proves correct failure behavior |
| `boundary` | Proves behavior at limits |
| `security` | Proves security properties |
| `governance` | Proves governance compliance |
| `audit` | Proves audit trail |
| `data_integrity` | Proves data correctness |
| `error_handling` | Proves error behavior |
| `authorization` | Proves access control |
| `rate_limit` | Proves rate limiting |
| `persistence` | Proves data persistence |
| `observability` | Proves logging/metrics |

---

## 5. Semantic Alignment Evaluation

Each test must be evaluated against the obligation it claims to satisfy.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `evaluation_id` | string | Unique identifier |
| `run_id` | string | Pipeline run |
| `test_case_id` | string | Test case being evaluated |
| `requirement_id` | string | Parent requirement |
| `acceptance_criterion_id` | string | Parent acceptance criterion |
| `obligation_id` | string | Parent obligation |
| `semantic_alignment_score` | float | 0.0 to 1.0 |
| `coverage_score` | float | 0.0 to 1.0 |
| `evidence_score` | float | 0.0 to 1.0 |
| `verifier_verdict` | enum | `pass`, `fail`, `partial` |
| `critique` | text | Verifier's critique |
| `missing_assertions` | JSON | List of missing assertions |
| `missing_edge_cases` | JSON | List of missing edge cases |
| `can_broken_code_pass` | boolean | Whether broken code could still pass |
| `status` | enum | `evaluated`, `pending`, `waived` |

---

## 6. Independent Verifier Critique

A separate verifier (LLM or deterministic evaluator) must judge whether a test proves the obligation.

### Verifier Questions

1. Does this test prove the acceptance criterion?
2. Could broken code still pass this test?
3. Does it assert the right observable behavior?
4. Does it check failure behavior?
5. Does it check security behavior when required?
6. Does it check governance behavior when required?
7. Does it check audit evidence when required?
8. Does it inspect runtime evidence?
9. Are assertions specific enough?
10. Are edge cases missing?

### Verifier Output

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | enum | `pass`, `fail`, `partial` |
| `confidence` | float | 0.0 to 1.0 |
| `critique` | text | Detailed critique |
| `recommendations` | JSON | List of improvements |

---

## 7. Mutation Testing Contract

The system must inject controlled faults and verify that tests fail.

### Mutation Categories

| Category | Description |
|----------|-------------|
| `remove_authorization` | Remove authorization check |
| `remove_tenant_isolation` | Remove tenant isolation |
| `remove_rate_limit` | Remove rate limiting |
| `change_boundary_operator` | Change `<` to `<=` etc. |
| `skip_audit_event` | Skip audit event emission |
| `return_wrong_status` | Return 200 instead of 403 etc. |
| `skip_persistence` | Skip database write |
| `corrupt_response_field` | Return wrong field value |
| `disable_validation` | Disable input validation |
| `bypass_governance_gate` | Bypass governance gate |

### Mutation Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `mutation_id` | string | Unique identifier |
| `requirement_id` | string | Target requirement |
| `obligation_id` | string | Target obligation |
| `mutation_type` | enum | Category |
| `mutated_component` | string | What was mutated |
| `expected_test_failure` | boolean | Whether test should fail |
| `actual_test_result` | enum | `pass`, `fail`, `error` |
| `killed` | boolean | Whether mutation was detected |
| `survived` | boolean | Whether mutation escaped detection |
| `mutation_score_impact` | float | Impact on score |

---

## 8. Negative Test Contract

Critical and security-relevant requirements MUST have negative tests.

Negative tests must:
1. Verify that invalid input is rejected
2. Verify that unauthorized access is denied
3. Verify that boundary violations are caught
4. Verify that error messages don't leak information
5. Verify that audit events are emitted for failures

---

## 9. Runtime Evidence Binding

Test results must be connected to runtime evidence.

### Evidence Types

| Type | Description |
|------|-------------|
| `api_response` | HTTP response from API |
| `database_state` | Database row state |
| `log_event` | Log entry |
| `audit_event` | Audit trail entry |
| `governance_evaluation` | Governance evaluation result |
| `traceability_link` | Traceability link |
| `artifact_hash` | Artifact content hash |
| `event_chain_entry` | Event chain entry |
| `snapshot` | System snapshot |
| `replay_event` | Replay event |

### Binding Rules

1. Every test result MUST bind to at least one evidence item
2. Critical tests MUST bind to at least 3 evidence items
3. Security tests MUST bind to audit events
4. Governance tests MUST bind to governance evaluations
5. Missing evidence binding REDUCES the evidence score

---

## 10. Semantic Coverage Score

### Formula

```
semantic_coverage = (
    obligation_coverage * 0.30 +
    semantic_alignment * 0.25 +
    mutation_score * 0.20 +
    negative_coverage * 0.10 +
    runtime_evidence * 0.10 +
    verifier_confidence * 0.05
)
```

### Component Definitions

| Component | Definition |
|-----------|------------|
| `obligation_coverage` | % of obligations with at least one test |
| `semantic_alignment` | Average alignment score across all evaluations |
| `mutation_score` | % of mutations killed |
| `negative_coverage` | % of required negative tests that exist |
| `runtime_evidence` | % of tests with evidence bindings |
| `verifier_confidence` | Average verifier confidence |

### Critical Rules

- Critical requirements require semantic coverage 1.0 or explicit waiver
- Security requirements require negative tests
- Governance requirements require evidence binding
- Surviving critical mutations fail the release gate
- Missing acceptance criteria fail the release gate
- Missing test obligations fail the release gate

---

## 11. New Integrity Component

Add **Semantic Coverage** as the seventh integrity component.

### Existing Components
1. Event Chain
2. Snapshot
3. Artifact
4. Timeline
5. Traceability
6. Governance

### New Component
7. **Semantic Coverage**

### Targets
- Semantic Coverage >= 0.90
- Overall integrity >= 0.95
- Critical semantic coverage = 1.0 (or waived)

---

## 12. Waiver Model

Waivers must be explicit, auditable, scoped, justified, and linked to a user or system decision.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `waiver_id` | string | Unique identifier |
| `requirement_id` | string | Waived requirement |
| `obligation_id` | string | Waived obligation |
| `waiver_reason` | text | Why the waiver is needed |
| `waiver_scope` | enum | `requirement`, `obligation`, `test` |
| `approved_by` | string | Who approved |
| `expires_at` | datetime | When waiver expires |

---

## 13. Release Gate Model

Release gates must include semantic coverage checks.

### Required Gate Checks

1. All critical requirements have acceptance criteria
2. All critical acceptance criteria have test obligations
3. All critical obligations have tests
4. Semantic alignment score meets threshold (>= 0.90)
5. Independent verifier verdict passes
6. Critical mutation tests are killed or waived
7. Negative tests exist for security and failure behavior
8. Runtime evidence is bound
9. Governance requirements have evidence
10. Semantic coverage report exists
11. No unwaived critical semantic gaps

---

## 14. Evidence Reports

Required reports:

1. `semantic-coverage-contract.md` (this document)
2. `requirement-normalization-report.md`
3. `acceptance-criteria-validation-report.md`
4. `test-obligation-report.md`
5. `semantic-alignment-report.md`
6. `verifier-critique-report.md`
7. `mutation-testing-report.md`
8. `negative-test-coverage-report.md`
9. `runtime-evidence-binding-report.md`
10. `semantic-coverage-integrity-report.md`
11. `golden-run-v4-semantic-coverage-report.md`
