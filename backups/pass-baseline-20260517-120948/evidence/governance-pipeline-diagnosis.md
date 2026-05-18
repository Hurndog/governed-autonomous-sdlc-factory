# Governance Pipeline Diagnosis

**Date:** 2026-05-16  
**Status:** ❌ NOT PERSISTED

---

## Current State

### What Exists
- `GovernanceEngine` class — fully implemented, generates rich governance analysis
- `GovernanceEvaluation` model — complete with `run_id`, `policy_id`, `artifact_id`, `decision`, `findings`, `evidence`, `integrity_hash`
- `GovernanceReleaseGate` model — complete with `run_id`, `gate_name`, `status`, `evaluation_ids`
- `GovernancePolicy` model — complete with `name`, `category`, `rego_code`, `is_blocking`
- `governance_evaluations` and `governance_release_gates` tables in database
- API endpoints for governance evaluation and release gates

### What's Missing
1. **GovernanceEngine generates data but only returns it as a dataclass** — never persists to DB
2. **No GovernanceEvaluation records are created** during pipeline execution
3. **No GovernanceReleaseGate records are created**
4. **No GovernancePolicy records exist** in the database (no seed data)
5. **Governance findings are not linked** to requirements, artifacts, or policies
6. **No integrity_hash is computed** for governance evaluations

### Governance Engine Output
The engine generates:
- `runtime_governance_concerns` (RGC-001, RGC-002, ...)
- `security_sensitive_findings` (SSF-001, SSF-002, ...)
- `compliance_gaps` (CG-001, CG-002, ...)
- `architecture_governance_findings` (AGF-001, ...)
- `deployment_governance_findings` (DGF-001, ...)
- `evidence_requirements` (EVR-001, ...)
- `audit_requirements` (AUD-001, ...)
- `risk_assessment`

All of this is written as artifact files but NEVER as structured DB records.

### Integrity Verification Gap
- `IntegrityManager.verify_governance_integrity()` queries `GovernanceEvaluation` table
- Table is empty → score = 0.0

### Policy Infrastructure
- `GovernancePolicy` model requires `rego_code` (OPA Rego policy)
- No policies are seeded in the database
- The governance engine does NOT use policies — it uses LLM inference directly
- **Mismatch:** The engine generates findings but there are no policies to evaluate against

### Conclusion
The governance infrastructure is partially built but disconnected. The engine generates rich analysis but doesn't persist it. The integrity manager expects `GovernanceEvaluation` records but none are created. Policies need to be seeded (or the engine needs to create them dynamically), and the pipeline needs to persist evaluations.
