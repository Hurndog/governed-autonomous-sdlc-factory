# Semantic Coverage Contract Test Results

**Date:** 2026-05-16
**Phase:** F — Contract Test Suite

## Results: 70/70 PASSED ✅

- 44 existing tests (test_artifact_hash_integrity.py): ALL PASS
- 26 new semantic coverage tests (test_semantic_coverage.py): ALL PASS

## Test Coverage

### 1. Requirement Normalization (4 tests)
- ✅ Creates stable, idempotent records
- ✅ Extracts all 6 requirements from golden run
- ✅ Security relevance detection (FR-001 = JWT auth)
- ✅ Governance relevance detection (FR-004 = audit logging)

### 2. Acceptance Criteria (2 tests)
- ✅ Extraction from artifacts
- ✅ Security case detection

### 3. Test Obligations (2 tests)
- ✅ Generated per acceptance criterion
- ✅ Security obligations for security-relevant ACs

### 4. Test Alignment (2 tests)
- ✅ Semantic alignment evaluation
- ✅ Tautological tests get low alignment

### 5. Verifier Critique (2 tests)
- ✅ Detects missing assertions
- ✅ can_broken_code_pass flag for weak tests

### 6. Mutation Tests (2 tests)
- ✅ Planned but NOT executed (honest)
- ✅ Mutation score = 0.0 when not executed

### 7. Negative Test Coverage (1 test)
- ✅ Security requirements generate negative test requirements

### 8. Runtime Evidence (1 test)
- ✅ Governance obligations get evidence bindings

### 9. Score Computation (3 tests)
- ✅ Formula is deterministic
- ✅ Critical requirements without coverage fail gate
- ✅ No hardcoded pass states

### 10. Report (2 tests)
- ✅ Report persisted to database
- ✅ Report JSON contains required fields

### 11. Waivers (1 test)
- ✅ Waiver creation and persistence

### 12. Legacy Behavior (1 test)
- ✅ Legacy runs return pre_semantic_coverage

### 13. Integrity Integration (1 test)
- ✅ Integrity API includes semantic coverage

### 14. Full Pipeline (2 tests)
- ✅ Idempotent pipeline
- ✅ All record types produced

## Key Validations

- **No hardcoded pass states**: Scores are computed from actual data
- **No fake semantic coverage**: Mutations are planned but not executed (score = 0.0)
- **Idempotent**: Re-running produces same results
- **Deterministic formula**: Same input → same output
- **Release gate honesty**: Fails when critical requirements aren't covered
