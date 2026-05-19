# Legacy Hash Contract Runs

**Date:** 2026-05-16  
**Status:** ✅ DOCUMENTED

---

## Affected Runs

These runs were created BEFORE the hash contract fix and have artifact integrity < 1.0:

| Run ID | Created | Artifact Integrity | Overall Score | Reason |
|--------|---------|-------------------|---------------|--------|
| `d6da6253-df9c-4aaf-a9ca-374e394bc52c` | 2026-05-16 | 0.0 (0/12) | ~0.33 | Old hashing code |
| `03a6ba18-13cd-45b1-9c46-099d2ed622c9` | 2026-05-16 | 0.0 (0/12) | ~0.33 | Old hashing code |
| `e384da5b-3522-4cff-93e7-254ded89da5b` | 2026-05-16 | 0.0 (0/12) | ~0.33 | Old hashing code (reload didn't work) |
| `f3069377-b5de-4f29-b2e5-106dc0fc26c9` | 2026-05-16 | 0.0 (0/12) | ~0.33 | Old hashing code (reload didn't work) |
| `64b223fd-7f50-48dd-87a8-12a960fc7dab` | 2026-05-16 | 0.0 (0/12) | ~0.50 | metadata_ still contained volatile fields |

---

## Why They Fail

All these runs were created with the OLD hashing code that:

1. Computed `artifact_hash` via `compute_hash()` over metadata containing `content_hash` and `size_bytes`
2. Stored `artifact_hash`, `content_hash`, `size_bytes` inside `metadata_`
3. During verification, the hash was recomputed over the same metadata (which now contained the stored `artifact_hash`), producing a different result

The root cause was a **circular reference**: the hash was computed over metadata that included derived values, and those derived values were then stored in the same metadata.

---

## Marking as Legacy

These runs are marked as `legacy_hash_contract` in the sense that they were created under the old hashing rules. Their artifacts are NOT modified — the original data is preserved for forensic integrity.

The new run `789c0b53-fc47-49d7-8c1c-354f7a7395f3` is the first run created under the corrected hash contract and achieves artifact integrity = 1.0.

---

## No History Rewritten

Per the integrity policy, old artifacts are NOT modified. The legacy runs retain their original hashes and metadata. The fix only applies to new runs created after the code change.
