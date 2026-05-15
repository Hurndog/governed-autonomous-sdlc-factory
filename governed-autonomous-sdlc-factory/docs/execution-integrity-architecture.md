# Execution Integrity Architecture — Hashing & Signatures

## 1. Purpose

This specification defines the hashing and execution signature architecture for the Cognitive Cortex. This infrastructure ensures tamper detection, replay integrity, and forensic verifiability.

**Current phase:** Architecture definition and preparation. Full cryptographic signing is deferred.

---

## 2. Hashing Strategy

### 2.1 Hashing Boundaries

Every artifact that crosses a persistence boundary gets hashed:

```
┌─────────────────────────────────────────────────────────────┐
│                    HASHING BOUNDARIES                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Artifact Content ──→ SHA-256(content) ──→ content_hash     │
│                                                             │
│  Artifact Metadata ─→ SHA-256(metadata) ──→ metadata_hash   │
│                                                             │
│  Lineage Edge ──────→ SHA-256(src+dst+type) ──→ edge_hash   │
│                                                             │
│  Snapshot State ────→ SHA-256(state_json) ──→ state_hash    │
│                                                             │
│  Governance Report ─→ SHA-256(report_json) ──→ report_hash  │
│                                                             │
│  Event Payload ─────→ SHA-256(payload) ──→ event_hash       │
│                                                             │
│  Execution Package ─→ SHA-256(manifest) ──→ execution_hash  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Hash Computation Rules

```python
import hashlib
import json

def compute_artifact_hash(content: str, metadata: dict) -> str:
    """Compute deterministic hash for an artifact.
    
    Hash = SHA-256(content + sorted_metadata_json)
    
    The metadata is sorted by key to ensure deterministic serialization.
    """
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    metadata_json = json.dumps(metadata, sort_keys=True, default=str)
    metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
    combined = f"{content_hash}:{metadata_hash}"
    return hashlib.sha256(combined.encode()).hexdigest()


def compute_lineage_hash(source_type: str, source_id: str,
                          target_type: str, target_id: str,
                          link_type: str) -> str:
    """Compute deterministic hash for a lineage edge."""
    edge_str = f"{source_type}:{source_id}:{target_type}:{target_id}:{link_type}"
    return hashlib.sha256(edge_str.encode()).hexdigest()


def compute_snapshot_hash(state_data: dict) -> str:
    """Compute deterministic hash for a snapshot."""
    state_json = json.dumps(state_data, sort_keys=True, default=str)
    return hashlib.sha256(state_json.encode()).hexdigest()


def compute_execution_hash(manifest: dict) -> str:
    """Compute deterministic hash for an execution package."""
    manifest_json = json.dumps(manifest, sort_keys=True, default=str)
    return hashlib.sha256(manifest_json.encode()).hexdigest()
```

### 2.3 Hash Storage

Hashes are stored alongside the data they protect:

```sql
-- Artifact hash (already in metadata)
UPDATE artifacts SET metadata_ = metadata_ || '{"content_hash": "..."}' WHERE id = '...';

-- Lineage edge hash
ALTER TABLE traceability_links ADD COLUMN edge_hash VARCHAR(64);

-- Snapshot hash
ALTER TABLE run_snapshots ADD COLUMN state_hash VARCHAR(64);

-- Execution package hash (in baseline manifest)
-- Stored in evidence/FIRST_OPERATIONAL_VERTICAL_SLICE/manifest.json
```

---

## 3. Execution Signature Architecture (Future)

### 3.1 Signature Boundaries

When cryptographic signing is implemented, the following boundaries will be signed:

```
┌─────────────────────────────────────────────────────────────┐
│                  SIGNATURE BOUNDARIES                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Level 1: Artifact Signatures                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Each artifact is signed by its producing engine.     │   │
│  │ Signature = Sign(engine_key, artifact_hash)          │   │
│  │ Stored in artifact metadata.                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 2: Lineage Signatures                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Each lineage edge is signed by the orchestrator.     │   │
│  │ Signature = Sign(orchestrator_key, edge_hash)        │   │
│  │ Stored in traceability_links table.                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 3: Snapshot Signatures                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Each snapshot is signed by the snapshot manager.     │   │
│  │ Sign(snapshot_key, state_hash)                       │   │
│  │ Stored in run_snapshots table.                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 4: Execution Signatures                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Each execution package is signed by the runtime.     │   │
│  │ Sign(runtime_key, execution_hash)                    │   │
│  │ Stored in baseline manifest.                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 5: Governance Signatures                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Each governance evaluation is signed by the engine.  │   │
│  │ Sign(governance_key, evaluation_hash)                │   │
│  │ Stored in governance_evaluations table.              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Key Management (Future)

```
Key Hierarchy:
├── Runtime Master Key (HSM or KMS)
│   ├── Orchestrator Key
│   ├── Engine Keys (per engine)
│   │   ├── Specification Engine Key
│   │   ├── Architecture Engine Key
│   │   ├── Governance Engine Key
│   │   ├── Test Engine Key
│   │   └── Traceability Engine Key
│   ├── Snapshot Key
│   └── Governance Key
```

### 3.3 Tamper Detection

```python
class TamperDetector:
    """Detects evidence tampering through hash verification."""
    
    def verify_artifact(self, artifact: Artifact) -> TamperResult:
        stored_hash = artifact.metadata_.get("content_hash")
        computed_hash = compute_artifact_hash(
            artifact.content, 
            {"name": artifact.name, "type": artifact.artifact_type, ...}
        )
        return TamperResult(
            artifact_id=artifact.id,
            intact=(stored_hash == computed_hash),
            stored_hash=stored_hash,
            computed_hash=computed_hash
        )
    
    def verify_lineage(self, link: TraceabilityLink) -> TamperResult:
        stored_hash = link.edge_hash
        computed_hash = compute_lineage_hash(
            link.source_type, link.source_id,
            link.target_type, link.target_id,
            link.link_type
        )
        return TamperResult(
            link_id=link.id,
            intact=(stored_hash == computed_hash),
            stored_hash=stored_hash,
            computed_hash=computed_hash
        )
    
    def verify_execution(self, manifest: dict) -> TamperResult:
        stored_hash = manifest.get("execution_hash")
        computed_hash = compute_execution_hash(manifest)
        return TamperResult(
            execution_id=manifest["run_id"],
            intact=(stored_hash == computed_hash),
            stored_hash=stored_hash,
            computed_hash=computed_hash
        )
```

---

## 4. Current Implementation Status

### 4.1 Implemented
- ✅ Content hashing in `ArtifactStore.persist()` (SHA-256 of content)
- ✅ Hash stored in `artifact.metadata_["content_hash"]`
- ✅ Normalization layer for deterministic serialization

### 4.2 Prepared (Schema Ready)
- ⬜ `traceability_links.edge_hash` column (schema defined, not yet added)
- ⬜ `run_snapshots.state_hash` column (schema defined, not yet added)
- ⬜ Execution package hash computation

### 4.3 Future (Cryptographic)
- ⬜ Per-engine signing keys
- ⬜ Artifact signatures
- ⬜ Lineage signatures
- ⬜ Snapshot signatures
- ⬜ Execution signatures
- ⬜ Governance signatures
- ⬜ Tamper detection API
- ⬜ Key rotation mechanism

---

## 5. Migration Path

### Phase A (Current): Hash Everything
1. Add `edge_hash` to traceability_links
2. Add `state_hash` to run_snapshots
3. Compute hashes for all existing baseline data
4. Verify baseline integrity

### Phase B (Near Future): Sign Critical Paths
1. Sign all governance evaluations
2. Sign all snapshots
3. Sign execution packages

### Phase C (Future): Full Cryptographic Chain
1. Per-engine signing
2. Artifact signatures
3. Lineage signatures
4. Key management infrastructure
5. Tamper detection API
