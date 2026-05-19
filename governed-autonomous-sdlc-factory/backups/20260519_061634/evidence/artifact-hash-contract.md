# Artifact Hash Contract

**Date:** 2026-05-16  
**Status:** ✅ ENFORCED  
**Version:** 2.0 (post-fix)

---

## Canonical Hash Computation

The artifact hash is the SHA-256 of a canonical JSON payload:

```python
import hashlib, json

payload = {
    "artifact_type": artifact_type,     # e.g. "specification"
    "name": name,                       # e.g. "requirements.json"
    "content": content or "",           # full artifact content
    "phase_name": phase_name or "",     # e.g. "specification"
    "metadata": safe_metadata,          # ONLY stable descriptive fields
}

canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
artifact_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

## Serialization Rules

1. **Sorted keys:** `sort_keys=True` — order-independent
2. **No whitespace:** `separators=(",", ":")` — compact
3. **Default handler:** `default=str` — handles datetime, enum, bytes
4. **None values:** Included as `null` (structural integrity)

## Volatile Fields (EXCLUDED from hash and metadata_)

| Field | Reason |
|-------|--------|
| `artifact_hash` | Circular reference |
| `content_hash` | Derived from content |
| `size_bytes` | Derived from content |
| `id` | Database identity |
| `created_at` | Database timestamp |
| `updated_at` | Database timestamp |
| `timestamp` | Runtime timestamp |
| `started_at` | Runtime timestamp |
| `completed_at` | Runtime timestamp |
| `evaluated_at` | Runtime timestamp |
| `verified_at` | Runtime timestamp |
| `captured_at` | Runtime timestamp |
| `absolute_path` | Environment-specific |
| `file_path` | Environment-specific |
| `duration_ms` | Execution metadata |
| `duration` | Execution metadata |
| `retry_count` | Execution metadata |
| `retries` | Execution metadata |
| `attempt` | Execution metadata |
| `run_id` | Runtime reference |
| `project_id` | Runtime reference |
| `task_id` | Runtime reference |
| `agent_id` | Runtime reference |
| `trace_id` | Runtime reference |
| `session_id` | Runtime reference |
| `replay_session_id` | Runtime reference |

## Stable Fields (INCLUDED in hash and metadata_)

| Field | Description |
|-------|-------------|
| `phase_name` | Pipeline phase (e.g. "specification") |
| `source_engine` | Engine that created the artifact |
| `parent_artifact_id` | Parent artifact reference |
| `subdir` | Storage subdirectory |
| `model` | LLM model used |
| `spec_id` | Specification version ID |
| `arch_id` | Architecture version ID |
| `test_plan_id` | Test plan ID |
| `link_type` | Traceability link type |
| Any other user-provided stable string/int/bool values |

## Metadata Storage Contract

The `metadata_` column in the database MUST contain ONLY stable descriptive fields.

```python
# CORRECT
metadata_ = {
    "phase_name": phase_name,
    "source_engine": source_engine,
    "parent_artifact_id": parent_artifact_id,
    "subdir": subdir,
    **(sanitize_artifact_metadata(extra_metadata)),
}

# WRONG — never do this
metadata_ = {
    "phase_name": phase_name,
    "content_hash": content_hash,      # ← VOLATILE
    "artifact_hash": artifact_hash,    # ← VOLATILE
    "size_bytes": len(content),        # ← VOLATILE
    ...
}
```

## Hash Stability Guarantee

Given the same `(artifact_type, name, content, phase_name, stable_metadata)`, the hash MUST be identical regardless of:
- Database ID or timestamps
- Runtime environment (paths, hostnames)
- Execution order or retry count
- Key order in metadata dict
- Number of times the computation is performed
