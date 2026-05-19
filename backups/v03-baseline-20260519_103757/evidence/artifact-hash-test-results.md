# Artifact Hash Test Results

**Date:** 2026-05-16  
**Test File:** `apps/api/tests/test_artifact_hash_integrity.py`  
**Status:** ✅ ALL 30 TESTS PASSED

---

## Test Categories

### Metadata Sanitization (9 tests)

| Test | Result |
|------|--------|
| `test_sanitize_removes_artifact_hash` | ✅ |
| `test_sanitize_removes_content_hash` | ✅ |
| `test_sanitize_removes_size_bytes` | ✅ |
| `test_sanitize_removes_timestamps` | ✅ |
| `test_sanitize_removes_db_identity` | ✅ |
| `test_sanitize_removes_absolute_paths` | ✅ |
| `test_sanitize_keeps_stable_fields` | ✅ |
| `test_sanitize_none_input` | ✅ |
| `test_sanitize_empty_dict` | ✅ |

### Hash Computation (10 tests)

| Test | Result |
|------|--------|
| `test_hash_excludes_artifact_hash_from_metadata` | ✅ |
| `test_hash_excludes_content_hash_from_metadata` | ✅ |
| `test_hash_excludes_size_bytes_from_metadata` | ✅ |
| `test_hash_same_metadata_different_key_order` | ✅ |
| `test_hash_different_content_produces_different_hash` | ✅ |
| `test_hash_different_name_produces_different_hash` | ✅ |
| `test_hash_different_type_produces_different_hash` | ✅ |
| `test_hash_is_deterministic` | ✅ |
| `test_hash_64_char_hex` | ✅ |
| `test_artifact_hash_not_in_own_hash` | ✅ |

### Structured Output Normalization (7 tests)

| Test | Result |
|------|--------|
| `test_extract_plain_json` | ✅ |
| `test_extract_markdown_wrapped_json` | ✅ |
| `test_extract_markdown_wrapped_json_no_lang` | ✅ |
| `test_extract_plain_text` | ✅ |
| `test_extract_empty_string` | ✅ |
| `test_extract_preserves_raw` | ✅ |
| `test_extract_json_keys_sorted` | ✅ |

### Hash Contract (4 tests)

| Test | Result |
|------|--------|
| `test_filter_excludes_volatile` | ✅ |
| `test_filter_none_input` | ✅ |
| `test_mutation_after_hashing_creates_mismatch` | ✅ |
| `test_raw_vs_normalized_different_when_markdown` | ✅ |

---

## Summary

- **Total:** 30 tests
- **Passed:** 30
- **Failed:** 0
- **Duration:** 0.35s
- **Command:** `python -m pytest tests/test_artifact_hash_integrity.py -v`
