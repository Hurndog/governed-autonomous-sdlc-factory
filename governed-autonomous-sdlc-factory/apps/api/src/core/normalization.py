"""Normalization layer for the Cognitive Cortex.

Provides deterministic serialization of ORM values, enums, and complex types
across all serialization boundaries: snapshots, events, replay, evidence, APIs.

Every value that crosses a serialization boundary MUST pass through these helpers.
This ensures replay-safe, JSON-safe, deterministic output.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Any, Optional


def normalize_value(value: Any) -> Any:
    """Normalize any value to a JSON-safe, replay-safe primitive.
    
    Handles:
    - Enum values → their .value
    - datetime → ISO format string
    - None → None
    - str, int, float, bool → as-is
    - dict → recursively normalized
    - list → recursively normalized
    - objects with .value attribute → .value
    - anything else → str()
    """
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_value(v) for v in value]
    if hasattr(value, "value"):
        return normalize_value(value.value)
    return str(value)


def normalize_status(status: Any) -> str:
    """Normalize a status field to string.
    
    Handles both string columns and Enum columns.
    """
    if status is None:
        return "unknown"
    if isinstance(status, Enum):
        return str(status.value)
    return str(status)


def normalize_artifact_type(artifact_type: Any) -> str:
    """Normalize an artifact_type field to string."""
    if artifact_type is None:
        return "unknown"
    if isinstance(artifact_type, Enum):
        return str(artifact_type.value)
    return str(artifact_type)


def normalize_dict(data: dict) -> dict:
    """Recursively normalize all values in a dict."""
    return {k: normalize_value(v) for k, v in data.items()}


def safe_isoformat(dt: Optional[datetime]) -> Optional[str]:
    """Safely convert datetime to ISO format string."""
    if dt is None:
        return None
    return dt.isoformat()
