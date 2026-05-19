# v03 Semantic Coverage Honesty Test

**Date**: 2026-05-19
**Phase**: 6 — Semantic Coverage Honesty Test

## Approach

Code-level audit of the semantic coverage engine to determine if it genuinely validates requirements or can be fooled by weak tests.

## Semantic Coverage Engine Architecture

**File**: `src/engines/semantic_coverage_engine.py`

The engine computes coverage using a weighted formula:
```
overall = 0.30*obligation + 0.25*alignment + 0.20*mutation + 0.10*negative + 0.10*evidence + 0.05*verifier
```

### Component Scores

| Component | Weight | What it measures |
|-----------|--------|------------------|
| obligation_coverage | 30% | % of requirements with test obligations |
| semantic_alignment | 25% | Average alignment score from LLM evaluations |
| mutation_score | 20% | Mutation test survival rate (planned, not executed) |
| negative_coverage | 10% | Coverage of negative requirements |
| runtime_evidence | 10% | Evidence bindings per requirement |
| verifier_confidence | 5% | LLM verifier critique confidence |

## Can It Be Fooled?

### By tautological tests?
**PARTIALLY** — The engine has a `_is_tautological_test()` heuristic (line 990-998):
```python
name_words = set(name_lower.split())
expected_words = set(expected_lower.split())
if len(overlap) / max(len(name_words), 1) > 0.7:
    return True
```
This catches tests where the expected result is too similar to the test name. But it's a simple word-overlap heuristic — sophisticated tautologies could bypass it.

### By weak assertions?
**PARTIALLY** — The `_can_broken_code_pass()` heuristic (line 1000-1005) checks for assertion keywords:
```python
assertion_keywords = ["assert", "verify", "check", "validate", "expect", "return", "status", "error", "reject", "throw", "raise"]
```
Tests without these keywords are flagged as weak. But this is keyword-based, not semantic.

### By fake happy-path tests?
**YES** — The mutation score is always 0.0 because mutations are "planned but not executed" (line 804):
```python
"note": "mutations are planned but not executed — score is 0.0 for mutation component"
```
This means the mutation testing component doesn't actually run mutations — it just plans them. A test suite with only happy-path tests would get a 0.0 on mutation but could still pass if other components score high.

### By duplicate tests?
**NO** — The engine evaluates per-requirement coverage, not per-test. Duplicate tests for the same requirement don't inflate scores.

## Gate Thresholds

```python
gate_status = "pass" if (overall >= 0.5 and critical_passed) else "fail"
if overall < 0.3:
    gate_status = "fail"
elif not critical_passed:
    gate_status = "fail"
```

- Overall score must be >= 0.5 AND all critical requirements must pass
- Overall score < 0.3 is an automatic fail
- Critical requirements must have semantic_alignment >= 0.5

## Verdict

**Semantic Coverage Honesty**: ⚠️ **PARTIALLY SOUND**

### Strengths:
- Real weighted formula with multiple components
- Critical requirements must individually pass
- Tautological test detection heuristic
- Weak test detection heuristic
- Gate threshold is meaningful (0.5 + critical pass)

### Weaknesses:
- Mutation score is always 0.0 (mutations planned but not executed)
- Tautological detection is simple word-overlap
- Weak test detection is keyword-based
- No actual mutation execution means weak tests can't be caught by mutation killing

### Can it discriminate between good and weak tests?
**PARTIALLY** — It can catch obvious tautologies and weak tests, but sophisticated weak tests could bypass the heuristics. The mutation component would be the strongest discriminator but it's not actually executed.

## Recommendation

Execute mutations in a future phase. This would make the mutation score meaningful and catch weak tests that pass by coincidence.
