# Normalization Layer Specification

## Purpose

The normalization layer provides deterministic, replay-safe serialization of all values crossing serialization boundaries in the Cognitive Cortex.

## Problem

The runtime contains mixed value types:
- SQLAlchemy string columns (e.g., `Run.status`, `Artifact.artifact_type`)
- Python Enum types (e.g., `RunStatus`, `ArtifactType`, `Severity`)
- Datetime objects
- Nested dicts/lists
- ORM objects with `.value` attributes

Serializing these inconsistently causes:
- Replay drift
- API response inconsistency
- Snapshot corruption
- Event payload mismatch

## Solution

All values MUST pass through `normalize_value()` before serialization.

### Core Functions

```python
from core.normalization import normalize_value, normalize_status, normalize_artifact_type, safe_isoformat
```

### Usage Rules

1. **Snapshots**: All ORM field values MUST be normalized
2. **API responses**: All status/type fields MUST be normalized
3. **Event payloads**: All values MUST be normalized
4. **Evidence exports**: All values MUST be normalized
5. **Replay data**: All values MUST be normalized

### Examples

```python
# Before (broken):
"status": run.status.value if hasattr(run.status, 'value') else str(run.status)

# After (correct):
"status": normalize_status(run.status)

# Before (broken):
"type": a.type.value if hasattr(a.type, 'value') else str(a.type)

# After (correct):
"type": normalize_artifact_type(a.artifact_type)
```

## Files Updated

- `core/normalization.py` — New shared module
- `engines/snapshots.py` — Line 66, 102
- `api/v1/endpoints/pipeline.py` — Line 140, 224
