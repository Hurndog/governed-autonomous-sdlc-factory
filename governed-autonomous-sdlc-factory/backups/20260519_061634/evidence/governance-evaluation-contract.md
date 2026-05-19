# Governance Evaluation Contract

**Date:** 2026-05-16  
**Status:** DEFINED  
**Version:** 1.0

---

## Required Records Per Golden Run

### 1. Governance Policies Used
- All active `GovernancePolicy` records are evaluated
- Policies are seeded in the database (10 default policies)
- Each policy has: `name`, `category`, `severity`, `is_blocking`, `rego_code`

### 2. Governance Concerns Found
- From `GovernanceEngine.generate_governance()`:
  - `runtime_governance_concerns` (RGC-001, RGC-002, ...)
  - `security_sensitive_findings` (SSF-001, SSF-002, ...)
  - `compliance_gaps` (CG-001, CG-002, ...)

### 3. Governance Evaluations
- One `GovernanceEvaluation` per active policy
- Fields: `run_id`, `policy_id`, `decision`, `findings`, `evidence`, `integrity_hash`
- Decision: `pass`, `fail`, or `warn`

### 4. Severity
- From policy: `info`, `warning`, `error`, `critical`
- From findings: `critical`, `high`, `medium`, `low`

### 5. Pass/Fail/Warn Status
- `pass`: No blocking issues found
- `fail`: Blocking policy violated
- `warn`: Non-blocking policy violated

### 6. Evidence References
- `evidence` field links to governance artifact ID
- `artifact_id` links to affected artifact

### 7. Affected Artifacts
- Governance artifacts: `governance_concerns.json`, `security_findings.json`, `compliance_gaps.json`

### 8. Affected Requirements
- Traceability links connect requirements to governance concerns

### 9. Release Gate Decision
- One `GovernanceReleaseGate` per run
- Status: `passed` (no blocking failures), `failed` (blocking failure), or `waived`
- Links to all evaluation IDs

### 10. Integrity Hash
- Each evaluation has `integrity_hash` = SHA256 of canonical evaluation representation
- Computed via `compute_governance_hash()`

---

## Evaluation Logic

For each active policy:
1. Check if the policy category matches any governance findings
2. If findings exist and policy is blocking → `fail`
3. If findings exist and policy is non-blocking → `warn`
4. If no findings → `pass`
5. Compute integrity hash
6. Create traceability links: concern → policy → evaluation → release gate
