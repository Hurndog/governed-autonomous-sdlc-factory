# Traceability Contract

**Date:** 2026-05-16  
**Status:** DEFINED  
**Version:** 1.0

---

## Required Links Per Golden Run

### 1. Requirement → Acceptance Criterion
- **source_type:** `requirement`
- **source_id:** `{requirement.id}` (e.g., "FR-001")
- **target_type:** `acceptance_criterion`
- **target_id:** `{acceptance_criterion.id}` (e.g., "AC-001")
- **link_type:** `validated_by`
- **created_by:** `pipeline`

### 2. Requirement → Architecture Component
- **source_type:** `requirement`
- **source_id:** `{requirement.id}`
- **target_type:** `architecture_component`
- **target_id:** `{component.id}` (stable UUID or name-based ID)
- **link_type:** `implemented_by`
- **created_by:** `pipeline`

### 3. Requirement → Test Case
- **source_type:** `requirement`
- **source_id:** `{requirement.id}`
- **target_type:** `test_case`
- **target_id:** `{test_case.id}`
- **link_type:** `tested_by`
- **created_by:** `pipeline`

### 4. Requirement → Governance Concern
- **source_type:** `requirement`
- **source_id:** `{requirement.id}`
- **target_type:** `governance_concern`
- **target_id:** `{concern.id}` (e.g., "RGC-001")
- **link_type:** `governed_by`
- **created_by:** `pipeline`

### 5. Architecture Component → Test Case
- **source_type:** `architecture_component`
- **source_id:** `{component.id}`
- **target_type:** `test_case`
- **target_id:** `{test_case.id}`
- **link_type:** `tested_by`
- **created_by:** `pipeline`

### 6. Governance Concern → Governance Policy
- **source_type:** `governance_concern`
- **source_id:** `{concern.id}`
- **target_type:** `governance_policy`
- **target_id:** `{policy.id}`
- **link_type:** `evaluated_by`
- **created_by:** `pipeline`

### 7. Governance Policy → Governance Evaluation
- **source_type:** `governance_policy`
- **source_id:** `{policy.id}`
- **target_type:** `governance_evaluation`
- **target_id:** `{evaluation.id}`
- **link_type:** `evaluated_as`
- **created_by:** `pipeline`

### 8. Governance Evaluation → Release Gate
- **source_type:** `governance_evaluation`
- **source_id:** `{evaluation.id}`
- **target_type:** `release_gate`
- **target_id:** `{gate.id}`
- **link_type:** `gates`
- **created_by:** `pipeline`

### 9. Phase → Artifact
- **source_type:** `phase`
- **source_id:** `{phase_name}` (e.g., "specification")
- **target_type:** `artifact`
- **target_id:** `{artifact.id}` (UUID)
- **link_type:** `produces`
- **created_by:** `pipeline`

### 10. Artifact → Inference Trace
- **source_type:** `artifact`
- **source_id:** `{artifact.id}`
- **target_type:** `inference_trace`
- **target_id:** `{trace.id}`
- **link_type:** `generated_by`
- **created_by:** `pipeline`

---

## Link Record Schema

```python
TraceabilityLink(
    id: str,                # UUID
    run_id: str,            # Run this link belongs to
    source_type: str,       # Entity type of source
    source_id: str,         # Stable ID of source entity
    target_type: str,       # Entity type of target
    target_id: str,         # Stable ID of target entity
    link_type: str,         # Relationship type
    edge_hash: str,         # SHA256 of canonical link representation
    created_at: datetime,   # When link was created
)
```

## Stable ID Requirements

- **Requirements:** FR-001, FR-002, ... (from specification engine)
- **Acceptance Criteria:** AC-001, AC-002, ... (with requirement_id reference)
- **Architecture Components:** Generated UUID or name-based stable ID
- **Test Cases:** Generated UUID or name-based stable ID
- **Governance Concerns:** RGC-001, SSF-001, CG-001, ... (from governance engine)
- **Artifacts:** UUID from database
- **Phases:** phase_name string (specification, architecture, governance, quality)
