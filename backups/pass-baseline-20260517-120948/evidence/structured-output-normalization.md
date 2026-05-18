# Structured Output Normalization

**Date:** 2026-05-16  
**Status:** ✅ VALIDATED

---

## Problem

Different LLM providers produce different output formats for structured data:

- **Ollama (gpt-oss:20b):** Returns pure JSON: `{"key": "value"}`
- **LM Studio (Gemma 4 E4B):** Returns markdown-wrapped JSON: `` ```json\n{"key": "value"}\n``` ``

This causes hash mismatches when the same logical content is produced by different providers.

## Solution

The `extract_structured_output()` function in `apps/api/src/core/hashing.py` normalizes both formats:

```python
def extract_structured_output(raw: str) -> tuple[str, str]:
    """Returns (normalized_content, raw_response)"""
    # 1. Try direct JSON parse → return sorted-keys JSON
    # 2. Try extracting from markdown fences → return sorted-keys JSON
    # 3. Return stripped text as-is
```

## Key Properties

1. **Raw response is preserved** — the original LLM output is stored for audit
2. **Normalized content is deterministic** — sorted keys, no whitespace variation
3. **Hash is computed over normalized content** — ensures cross-provider consistency
4. **Raw and normalized are never confused** — separate code paths for audit vs integrity

## Test Results

| Test | Result |
|------|--------|
| Plain JSON normalization | ✅ |
| Markdown-wrapped JSON extraction | ✅ |
| Markdown fence without lang spec | ✅ |
| Plain text passthrough | ✅ |
| Empty string handling | ✅ |
| Raw response preservation | ✅ |
| Key sorting for determinism | ✅ |
| Raw vs normalized hash differs | ✅ |

## Integration

The `LMStudioProvider` in `apps/api/src/engines/model_providers.py` calls `extract_structured_output()` on all responses before they are used for artifact creation. This ensures that Gemma 4 E4B's markdown-wrapped JSON is normalized to pure JSON before hashing.

The `gpt-oss:20b` fallback (Ollama) returns pure JSON which passes through normalization unchanged.
