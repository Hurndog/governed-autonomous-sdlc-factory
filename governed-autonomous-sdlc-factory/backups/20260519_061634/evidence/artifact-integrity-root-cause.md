# Artifact Integrity Root Cause Analysis

**Date:** 2026-05-16  
**Status:** ✅ RESOLVED  
**Severity:** CRITICAL — All artifact hashes were mismatching (0/12 passing)

---

## Executive Summary

The artifact hash mismatch was caused by **volatile derived fields being stored inside artifact metadata_**, which made it impossible to recompute the same hash from stored data. The fix involved:

1. Removing `artifact_hash`, `content_hash`, and `size_bytes` from `metadata_` storage
2. Adding `sanitize_artifact_metadata()` to strip all volatile/non-deterministic fields
3. Ensuring the same sanitized metadata is used for both hashing and storage
4. Hard-restarting the API to ensure the new code was active

---

## Root Cause Details

### The Three-Layer Problem

#### Layer 1: Circular Hash Reference (Original Bug)

In the OLD `artifact_store.py`, the `artifact_hash` was computed via `compute_hash()` over a payload that included `content_hash` and `size_bytes` inside the metadata:

```python
# OLD CODE (buggy)
artifact_hash_input = {
    "artifact_type": artifact_type,
    "name": name,
    "content": content,
    "phase_name": phase_name or "",
    "metadata": {
        "phase_name": phase_name,
        "content_hash": content_hash,      # ← VOLATILE, derived from content
        "size_bytes": len(content),        # ← VOLATILE, derived from content
        "source_engine": source_engine,
        "parent_artifact_id": parent_artifact_id,
        "subdir": subdir,
        **(metadata or {}),
    },
}
artifact_hash = compute_hash(artifact_hash_input)
```

The hash was computed over metadata containing derived values. When the same computation was attempted during verification, the derived values (computed from the DB-stored content, which may be truncated to 10000 chars) produced a different hash.

#### Layer 2: Volatile Fields in Stored Metadata

Even after introducing `compute_artifact_hash()` (which filters volatile fields), the `metadata_` dict stored in the database still contained:

```python
metadata_={
    "phase_name": phase_name,
    "content_hash": content_hash,      # ← Still stored in DB
    "artifact_hash": artifact_hash,    # ← Still stored in DB
    "size_bytes": len(content),        # ← Still stored in DB
    "source_engine": source_engine,
    "parent_artifact_id": parent_artifact_id,
    "subdir": subdir,
    **(metadata or {}),
}
```

While `compute_artifact_hash()` correctly filters these during hash computation, storing them in `metadata_` is a design violation: derived integrity values should not be mixed with descriptive metadata.

#### Layer 3: API Not Restarted with New Code

The API was running with `--reload` but the old uvicorn process had not picked up the code changes. Multiple pipeline runs were executed with the OLD hashing code:

- `d6da6253` — Created with old code (before fix)
- `03a6ba18` — Created with old code (before fix)
- `e384da5b` — Created with old code (reload didn't pick up changes)
- `f3069377` — Created with old code (reload didn't pick up changes)
- `64b223fd` — Created with old code (metadata_ still contained volatile fields)
- `789c0b53` — ✅ Created with NEW code after hard restart — ALL HASHES MATCH

---

## Canonical Hash Contract

The artifact hash is computed over:

```python
{
    "artifact_type": "<type>",
    "name": "<filename>",
    "content": "<full content>",
    "phase_name": "<phase>",
    "metadata": { <only stable descriptive fields> }
}
```

**Excluded from hash (volatile fields):**
- `artifact_hash` — circular reference
- `content_hash` — derived from content
- `size_bytes` — derived from content
- `id`, `created_at`, `updated_at` — database identity
- `timestamp`, `started_at`, `completed_at` — runtime timestamps
- `absolute_path`, `file_path` — environment-specific paths
- `run_id`, `task_id`, `agent_id`, `trace_id` — runtime references
- `duration_ms`, `retry_count`, `attempt` — execution metadata

**Serialization:** `json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)`  
**Algorithm:** SHA-256

---

## Verification Results

### Run `789c0b53-fc47-49d7-8c1c-354f7a7395f3` (Post-Fix)

| Check | Status | Score |
|-------|--------|-------|
| Event Chain | ✅ PASS | 1.0 |
| Snapshot | ✅ PASS | 1.0 |
| **Artifact** | ✅ **PASS** | **1.0** |
| Timeline | ✅ PASS | 1.0 |
| Traceability | ⚠️ WARNING | 0.0 (not populated by pipeline) |
| Governance | ⚠️ WARNING | 0.0 (not populated by pipeline) |
| **Overall** | | **0.6667** |

**Artifact Integrity: 12/12 verified ✅**

All 12 artifact hashes match their recomputed values. All metadata_ entries are clean (no volatile fields).

---

## Files Changed

1. `apps/api/src/services/artifact_store.py`
   - Added `sanitize_artifact_metadata()` function
   - Added `_VOLATILE_METADATA_FIELDS` constant
   - Removed `artifact_hash`, `content_hash`, `size_bytes` from `metadata_` storage
   - Used `safe_metadata` for both hashing and storage

2. `apps/api/src/core/hashing.py` (previously changed)
   - Added `_filter_metadata_for_hash()`
   - Added `compute_artifact_hash()` with volatile field exclusion
   - Added `extract_structured_output()` for markdown-wrapped JSON normalization

3. `apps/api/src/engines/model_providers.py` (previously changed)
   - LM Studio provider uses `extract_structured_output()` for response normalization

---

## Lessons Learned

1. **Never store derived values in metadata.** Metadata should only contain stable descriptive fields.
2. **Hash the same data you store.** If the hash is computed over field X, the stored data must allow recomputing the same X.
3. **`--reload` is not reliable for critical fixes.** Always hard-restart and verify the new process is running.
4. **Verify code is active.** Check process start time and test the actual code path, don't assume file changes are picked up.
