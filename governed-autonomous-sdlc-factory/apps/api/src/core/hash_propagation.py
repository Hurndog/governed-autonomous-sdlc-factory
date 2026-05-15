"""Hash Propagation Layer for the Cognitive Cortex.

Centralized hash generation for all runtime entities.
Every artifact, event, snapshot, traceability link, and governance evaluation
MUST pass through this layer to receive its hashes.

This ensures deterministic, replay-safe hashing across all engines.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

from src.core.hashing import (
    compute_artifact_hash, compute_event_hash, compute_snapshot_hash,
    compute_traceability_hash, compute_governance_hash, compute_chain_hash,
)


def _safe_metadata(metadata: Optional[dict]) -> dict:
    """Normalize metadata to JSON-safe dict."""
    if not metadata:
        return {}
    safe = {}
    for k, v in metadata.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            safe[k] = v
        elif isinstance(v, (list, dict)):
            safe[k] = v
        else:
            safe[k] = str(v)
    return safe


def hash_artifact(artifact, content: Optional[str] = None):
    """Compute and assign hash to an artifact."""
    artifact.artifact_hash = compute_artifact_hash(
        artifact_type=artifact.artifact_type,
        name=artifact.name,
        content=content or artifact.content,
        phase_name=artifact.phase_name,
        metadata=_safe_metadata(artifact.metadata_),
    )
    return artifact.artifact_hash


def hash_event(event, run_id: str, parent_hash: Optional[str] = None):
    """Compute and assign hash to a log event."""
    event.event_hash = compute_event_hash(
        run_id=run_id,
        event_type="log",
        message=event.message,
        timestamp=event.created_at.isoformat() if event.created_at else "",
        severity=event.severity,
        source_file=event.source_file,
        phase_id=event.phase_id,
        trace_id=event.trace_id,
    )
    if parent_hash:
        event.chain_hash = compute_chain_hash(parent_hash, event.event_hash)
    return event.event_hash


def hash_snapshot(snapshot):
    """Compute and assign hash to a snapshot."""
    snapshot.snapshot_hash = compute_snapshot_hash(
        run_id=snapshot.run_id,
        snapshot_type=snapshot.snapshot_type,
        state_data=snapshot.state_data or {},
        phase_states=snapshot.phase_states or {},
        artifact_states=snapshot.artifact_states or {},
        cost_summary=snapshot.cost_summary or {},
        governance_summary=snapshot.governance_summary or {},
    )
    return snapshot.snapshot_hash


def hash_traceability_link(link):
    """Compute and assign hash to a traceability link."""
    link.edge_hash = compute_traceability_hash(
        source_type=link.source_type,
        source_id=link.source_id,
        target_type=link.target_type,
        target_id=link.target_id,
        link_type=link.link_type,
        run_id=link.run_id,
    )
    return link.edge_hash


def hash_governance_eval(eval_obj, policy_name: str):
    """Compute and assign hash to a governance evaluation."""
    eval_obj.integrity_hash = compute_governance_hash(
        policy_name=policy_name,
        decision=eval_obj.decision,
        input_data=eval_obj.findings if isinstance(eval_obj.findings, dict) else {},
        output_data=eval_obj.evidence if isinstance(eval_obj.evidence, dict) else {},
        run_id=eval_obj.run_id,
        artifact_id=eval_obj.artifact_id,
    )
    return eval_obj.integrity_hash


def hash_checkpoint(checkpoint):
    """Compute and assign state hash to a checkpoint."""
    from src.core.hashing import compute_hash
    checkpoint.state_hash = compute_hash({
        "run_id": checkpoint.run_id,
        "phase_name": checkpoint.phase_name,
        "state_data": checkpoint.state_data or {},
    })
    return checkpoint.state_hash


def hash_evidence_bundle(bundle):
    """Compute and assign chain hash to an evidence bundle."""
    from src.core.hashing import compute_hash
    bundle.bundle_hash = compute_hash({
        "run_id": bundle.run_id,
        "bundle_path": bundle.bundle_path or "",
        "artifact_count": bundle.artifact_count,
        "size_bytes": bundle.size_bytes or 0,
    })
    return bundle.bundle_hash
