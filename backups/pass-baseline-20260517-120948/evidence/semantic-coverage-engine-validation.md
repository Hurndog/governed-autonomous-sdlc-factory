# Semantic Coverage Engine Validation

**Date:** 2026-05-16
**Phase:** E — Semantic Coverage Engine Validation

## Engine Rewrite

The semantic_coverage_engine.py was completely rewritten (~860 lines) with:
- Idempotent design: `_clear_existing()` uses raw SQL for reliable deletion
- Honest scoring: mutations are planned but not executed (score = 0.0)
- Proper UUID handling: `_to_uuid()` and `_to_str()` helpers
- Source extraction from JSON blob artifacts
- Deterministic verifier (no LLM dependency)

## Evaluation Results (Run 6a7f7ea0)

### Semantic Coverage Score: 0.6772 (67.72%)

| Component | Score | Weight | Notes |
|---|---|---|---|
| Obligation coverage | 1.0 | 30% | All 6 requirements have obligations |
| Semantic alignment | 0.6111 | 25% | Tests partially align with obligations |
| Mutation | 0.0 | 20% | 25 planned, 0 executed (honest) |
| Negative coverage | 0.8 | 10% | 80% of sec/gov requirements covered |
| Runtime evidence | 1.0 | 10% | Governance obligations have evidence |
| Verifier confidence | 0.8885 | 5% | High confidence in deterministic critiques |

### Data Counts
- Requirements: 6 (from requirements.json artifact)
- Acceptance criteria: 6 (from acceptance_criteria.json artifact)
- Test obligations: 10 (generated from ACs)
- Semantic alignment evaluations: 13
- Verifier critiques: 13
- Mutation tests planned: 25 (5 types × 5 critical/high requirements)
- Negative test requirements: 6
- Runtime evidence bindings: 1

### Release Gate: FAIL
- Critical requirements: 3 (must_have priority)
- Critical requirements passed: false
- Reason: Not all critical requirements have full semantic alignment

### Integrity API Integration
- 7th component (semantic_coverage) added to integrity check
- Overall integrity: 0.9539 (95.39%)
- 6 pass, 0 fail, 1 warning (semantic_coverage = warning)

## Verification

### Endpoints Tested
| Endpoint | Status | Result |
|---|---|---|
| POST /evaluate | 200 | Evaluation completed |
| GET /summary | 200 | Score: 0.6772 |
| GET /requirements | 200 | 6 requirements |
| GET /test-obligations | 200 | 10 obligations |
| GET /alignment | 200 | 13 evaluations |
| GET /verifier-critiques | 200 | 13 critiques |
| GET /mutations | 200 | 25 planned |
| GET /negative-coverage | 200 | 6 requirements |
| GET /runtime-evidence | 200 | 1 binding |
| GET /report | 200 | Full report with scores |

## Status: COMPLETE ✅
