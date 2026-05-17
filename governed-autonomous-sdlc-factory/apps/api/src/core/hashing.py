"""Cryptographic hashing substrate for the Cognitive Cortex.

Provides deterministic, replay-safe hashing for all runtime entities:
- Events, snapshots, artifacts, traceability links
- Governance evaluations, replay manifests
- Timeline chains, state transitions

Hashing rules:
1. Deterministic: same input → same hash, always
2. Stable across replay: replay produces identical hashes
3. Canonical serialization: sorted keys, normalized values
4. Chain integrity: parent_hash links form verifiable chains
5. SHA256 initially, architecture ready for future signatures
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum


def _canonical_json(data: Any) -> str:
    """Serialize data to canonical JSON string for hashing.
    
    Rules:
    - Dict keys sorted alphabetically
    - Enum values → their .value
    - datetime → ISO format string
    - None values included (structural integrity)
    - No whitespace variation
    """
    return json.dumps(data, sort_keys=True, default=_json_default, separators=(",", ":"))


def _json_default(obj: Any) -> Any:
    """JSON serializer for non-standard types."""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def compute_hash(data: Any) -> str:
    """Compute SHA256 hash of canonical JSON serialization."""
    canonical = _canonical_json(data)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_hash_from_parts(*parts: str) -> str:
    """Compute SHA256 hash from concatenated string parts."""
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_chain_hash(parent_hash: Optional[str], current_hash: str) -> str:
    """Compute chain hash linking parent to current.
    
    Creates hash chain: H(parent_hash || current_hash)
    Genesis blocks use "GENESIS" as parent.
    """
    parent = parent_hash or "GENESIS"
    return compute_hash_from_parts(parent, current_hash)


def _filter_metadata_for_hash(metadata: Optional[dict]) -> dict:
    """Filter metadata to only include hash-stable fields.

    Excludes volatile/circular fields:
    - artifact_hash: circular reference (hash of metadata includes hash)
    - content_hash: derived from content, already included via content field
    - size_bytes: derived from content
    """
    if not metadata:
        return {}
    EXCLUDED_FIELDS = {"artifact_hash", "content_hash", "size_bytes"}
    safe = {}
    for k, v in metadata.items():
        if k in EXCLUDED_FIELDS:
            continue
        if isinstance(v, (str, int, float, bool, type(None))):
            safe[k] = v
        elif isinstance(v, (list, dict)):
            safe[k] = v
        else:
            safe[k] = str(v)
    return safe


def compute_artifact_hash(artifact_type: str, name: str, content: Optional[str],
                           phase_name: Optional[str], metadata: Optional[dict]) -> str:
    """Compute deterministic hash for an artifact.

    The hash is computed over a canonical representation that excludes
    volatile/circular fields (artifact_hash, content_hash, size_bytes)
    to ensure the hash can be recomputed from stored data.
    """
    safe_metadata = _filter_metadata_for_hash(metadata)
    return compute_hash({
        "artifact_type": artifact_type,
        "name": name,
        "content": content or "",
        "phase_name": phase_name or "",
        "metadata": safe_metadata,
    })


def compute_event_hash(run_id: str, event_type: str, message: str,
                        timestamp: str, severity: str = "info",
                        source_file: Optional[str] = None,
                        phase_id: Optional[str] = None,
                        trace_id: Optional[str] = None) -> str:
    """Compute deterministic hash for an event."""
    return compute_hash({
        "run_id": run_id,
        "event_type": event_type,
        "message": message,
        "timestamp": timestamp,
        "severity": severity,
        "source_file": source_file or "",
        "phase_id": phase_id or "",
        "trace_id": trace_id or "",
    })


def compute_snapshot_hash(run_id: str, snapshot_type: str, state_data: dict,
                           phase_states: dict, artifact_states: dict,
                           cost_summary: dict, governance_summary: dict) -> str:
    """Compute deterministic hash for a snapshot."""
    return compute_hash({
        "run_id": run_id,
        "snapshot_type": snapshot_type,
        "state_data": state_data,
        "phase_states": phase_states or {},
        "artifact_states": artifact_states or {},
        "cost_summary": cost_summary or {},
        "governance_summary": governance_summary or {},
    })


def compute_traceability_hash(source_type: str, source_id: str,
                               target_type: str, target_id: str,
                               link_type: str, run_id: str) -> str:
    """Compute deterministic hash for a traceability link."""
    return compute_hash({
        "source_type": source_type,
        "source_id": source_id,
        "target_type": target_type,
        "target_id": target_id,
        "link_type": link_type,
        "run_id": run_id,
    })


def compute_governance_hash(policy_name: str, decision: str, input_data: dict,
                             output_data: dict, run_id: str,
                             artifact_id: Optional[str] = None) -> str:
    """Compute deterministic hash for a governance evaluation."""
    return compute_hash({
        "policy_name": policy_name,
        "decision": decision,
        "input_data": input_data or {},
        "output_data": output_data or {},
        "run_id": run_id,
        "artifact_id": artifact_id or "",
    })


def compute_replay_hash(run_id: str, event_count: int, artifact_count: int,
                         snapshot_count: int, traceability_count: int,
                         governance_count: int, replay_timestamp: str) -> str:
    """Compute deterministic hash for a replay manifest."""
    return compute_hash({
        "run_id": run_id,
        "event_count": event_count,
        "artifact_count": artifact_count,
        "snapshot_count": snapshot_count,
        "traceability_count": traceability_count,
        "governance_count": governance_count,
        "replay_timestamp": replay_timestamp,
    })


def compute_timeline_chain_hash(events: list[dict]) -> str:
    """Compute cumulative chain hash for a timeline.
    
    Each event's hash is chained to the previous, creating
    a verifiable sequence. Any modification breaks the chain.
    """
    chain_hash = "GENESIS"
    for event in events:
        event_hash = compute_hash(event)
        chain_hash = compute_chain_hash(chain_hash, event_hash)
    return chain_hash


def verify_hash(data: Any, expected_hash: str) -> bool:
    """Verify that data matches expected hash."""
    return compute_hash(data) == expected_hash


def verify_chain(hashes: list[str]) -> bool:
    """Verify a chain of hashes is unbroken.
    
    Each hash after genesis must equal H(previous_hash || current_content_hash).
    The final computed chain hash must match the last stored hash.
    """
    if not hashes:
        return True
    chain_hash = "GENESIS"
    for h in hashes:
        chain_hash = compute_chain_hash(chain_hash, h)
    # The final chain hash should match the last element if stored
    return chain_hash == hashes[-1]


# ---------------------------------------------------------------------------
# Structured output normalization
# ---------------------------------------------------------------------------

import re as _re

# Matches fenced JSON blocks: ```json ... ``` or ``` ... ```
_FENCED_JSON_RE = _re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?```",
    _re.DOTALL,
)


def extract_structured_output(raw: str) -> tuple[str, str]:
    """Extract structured content from a model response.

    Returns:
        (normalized_content, raw_response)
        - normalized_content: extracted JSON or cleaned text
        - raw_response: the original raw response (for audit)

    Handles:
    - Plain JSON: {"key": "value"}
    - Markdown-wrapped JSON: ```json\n{...}\n```
    - Text with embedded JSON fences
    """
    if not raw:
        return "", raw

    stripped = raw.strip()

    # Try direct JSON parse first
    try:
        parsed = json.loads(stripped)
        return json.dumps(parsed, sort_keys=True, separators=(",", ":")), raw
    except (json.JSONDecodeError, ValueError):
        pass

    # Try extracting from markdown fences
    match = _FENCED_JSON_RE.search(stripped)
    if match:
        inner = match.group(1).strip()
        try:
            parsed = json.loads(inner)
            return json.dumps(parsed, sort_keys=True, separators=(",", ":")), raw
        except (json.JSONDecodeError, ValueError):
            # Fence found but content isn't valid JSON — return inner text
            return inner, raw

    # Not JSON — return as-is
    return stripped, raw


def compute_raw_response_hash(raw_response: str) -> str:
    """Compute hash over the exact raw model response (for audit)."""
    return hashlib.sha256(raw_response.encode("utf-8")).hexdigest()


def compute_normalized_content_hash(normalized_content: str) -> str:
    """Compute hash over normalized content (for artifact integrity)."""
    return hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()
