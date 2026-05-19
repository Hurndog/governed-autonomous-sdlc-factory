# Semantic Coverage Integrity API Validation

**Date:** 2026-05-16
**Phase:** G — Integrity API Expansion Verification

## Results

### Integrity API: 7 Components ✅

| Component | Status | Score |
|---|---|---|
| event_chain | pass | 1.0 |
| snapshot | pass | 1.0 |
| artifact | pass | 1.0 |
| timeline | pass | 1.0 |
| traceability | pass | 1.0 |
| governance | pass | 1.0 |
| semantic_coverage | warning | 0.6772 |

- **Overall integrity**: 0.9539 (95.39%)
- **Status**: pass
- **Checks**: 7 (6 passed, 0 failed, 1 warning)

### Semantic Coverage Component Details

The semantic_coverage component is the 7th integrity check:
- **Status**: warning (score 0.6772, threshold: ≥ 0.90 = pass, ≥ 0.50 = warning, < 0.50 = fail)
- **Score breakdown**:
  - obligation_coverage: 1.0
  - semantic_alignment: 0.6111
  - mutation_score: 0.0 (planned but not executed — honest)
  - negative_coverage: 0.8
  - runtime_evidence: 1.0
  - verifier_confidence: 0.8885
  - critical_requirements_passed: false
  - release_gate_status: fail

### Legacy Run Behavior ✅

For runs without semantic coverage evaluation:
- Status: warning
- Score: 0.0
- Message: "No semantic coverage report for this run"
- semantic_coverage_status: "pre_semantic_coverage"

### Existing 6 Components Unchanged ✅

All existing integrity components remain unchanged:
- event_chain: 1.0 (239 events, all hashed)
- snapshot: 1.0 (1 snapshot, verified)
- artifact: 1.0 (12 artifacts, all verified)
- timeline: 1.0 (239 events, no violations)
- traceability: 1.0 (215 links, all verified)
- governance: 1.0 (10 evaluations, all verified)

## Status: COMPLETE ✅
