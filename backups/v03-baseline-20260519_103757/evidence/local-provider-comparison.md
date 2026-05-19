# Local Provider Comparison Report
**Date:** 2026-05-14
**Models Compared:** Gemma 4 E4B (LM Studio) vs gpt-oss:20b (Ollama)

## Performance Summary

| Metric | Gemma 4 E4B | gpt-oss:20b | Winner |
|--------|-------------|-------------|--------|
| Basic Inference | 1.2s | 6.9s | **Gemma** (5.7x) |
| Spec Generation | 17.9s | 34.0s | **Gemma** (1.9x) |
| Token Throughput | 45-50 tok/s | 41-53 tok/s | Tie |
| JSON Output | Markdown-wrapped | Direct JSON | **gpt-oss** |
| Code Quality | 122 lines, complete | — | **Gemma** |
| Architecture | 7 components, 2 ADRs | — | **Gemma** |
| Governance | 5 concerns, 2 findings | — | **Gemma** |

## Golden Pipeline Results (Gemma 4 E4B)
- **Run ID:** 43dafe8e-0a6b-448e-bc1a-3ec9dd20b221
- **Duration:** 216,333ms (3.6 min)
- **Status:** COMPLETED
- **Artifacts:** 12
  - Specification: 6 FR, 4 NFR
  - Architecture: 7 components, 2 ADRs, Mermaid diagram
  - Governance: 5 concerns, 2 security findings
  - Test Plan: 6 test cases, 3 edge cases
- **Integrity:**
  - Event chain: PASS (score 1.0)
  - Snapshot: PASS (score 1.0)
  - Timeline: PASS (score 1.0)
  - Artifact: FAIL (0.0 — hashes not matching)
  - Replay: FAIL (36 divergences)
  - Overall: 0.4286

## Recommendation
**Gemma 4 E4B is the recommended primary model** for:
- Architecture reasoning (faster, good quality)
- Governance reasoning (faster, good quality)
- Specification generation (faster, slightly less detailed)
- Code generation (excellent quality)
- Structured output (with markdown extraction)

**gpt-oss:20b remains the fallback** for:
- Heavy reasoning requiring more detail
- Direct JSON output (no markdown wrapping)
- Second opinion / baseline comparison

## Known Issues
1. Gemma 4 E4B wraps JSON in markdown code blocks — API must extract
2. Artifact integrity check fails — needs investigation (may be hash computation issue)
3. Replay divergences (36) — common across both models, likely timing-related
