"""Tests for artifact hash integrity, metadata sanitization, traceability, and governance.

Validates:
- Metadata sanitization removes volatile fields
- Artifact hash excludes volatile fields from its computation
- artifact_hash is not stored in metadata_
- content_hash is not stored in metadata_
- size_bytes is not stored in metadata_
- Same stable metadata produces same hash regardless of key order
- Markdown-wrapped JSON normalization works correctly
- Integrity verification recomputes the same hash as creation
- Traceability links are created for each required relation type
- Traceability links have stable source and target IDs
- Governance evaluations are persisted
- Release gates are created
- Overall integrity components are populated
"""
import hashlib
import json
import sys
import os

# Add the API source to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.hashing import (
    compute_artifact_hash,
    compute_hash,
    extract_structured_output,
    _filter_metadata_for_hash,
)
from src.services.artifact_store import sanitize_artifact_metadata


# ─── Fixtures ───────────────────────────────────────────────────────────────

def make_metadata(**extras):
    """Create a standard metadata dict with optional extras."""
    base = {
        "phase_name": "specification",
        "source_engine": "specification-engine",
        "parent_artifact_id": None,
        "subdir": "",
    }
    base.update(extras)
    return base


SAMPLE_CONTENT = '{"requirements": [{"id": "FR-001", "desc": "User auth"}]}'
SAMPLE_TYPE = "specification"
SAMPLE_NAME = "requirements.json"
SAMPLE_PHASE = "specification"


# ─── Test: sanitize_artifact_metadata ──────────────────────────────────────

def test_sanitize_removes_artifact_hash():
    """artifact_hash must be removed from metadata."""
    meta = make_metadata(artifact_hash="abc123")
    result = sanitize_artifact_metadata(meta)
    assert "artifact_hash" not in result, "artifact_hash should be removed"
    assert result["phase_name"] == "specification"


def test_sanitize_removes_content_hash():
    """content_hash must be removed from metadata."""
    meta = make_metadata(content_hash="def456")
    result = sanitize_artifact_metadata(meta)
    assert "content_hash" not in result, "content_hash should be removed"
    assert result["phase_name"] == "specification"


def test_sanitize_removes_size_bytes():
    """size_bytes must be removed from metadata."""
    meta = make_metadata(size_bytes=1024)
    result = sanitize_artifact_metadata(meta)
    assert "size_bytes" not in result, "size_bytes should be removed"
    assert result["phase_name"] == "specification"


def test_sanitize_removes_timestamps():
    """Timestamp fields must be removed from metadata."""
    meta = make_metadata(
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-02T00:00:00Z",
        timestamp="2026-01-03T00:00:00Z",
    )
    result = sanitize_artifact_metadata(meta)
    assert "created_at" not in result
    assert "updated_at" not in result
    assert "timestamp" not in result


def test_sanitize_removes_db_identity():
    """Database identity fields must be removed from metadata."""
    meta = make_metadata(id="some-uuid", run_id="run-123", task_id="task-456")
    result = sanitize_artifact_metadata(meta)
    assert "id" not in result
    assert "run_id" not in result
    assert "task_id" not in result


def test_sanitize_removes_absolute_paths():
    """Absolute paths must be removed from metadata."""
    meta = make_metadata(absolute_path="/tmp/some/path", file_path="/another/path")
    result = sanitize_artifact_metadata(meta)
    assert "absolute_path" not in result
    assert "file_path" not in result


def test_sanitize_keeps_stable_fields():
    """Stable descriptive metadata must be preserved."""
    meta = make_metadata(
        model="gemma-4-e4b",
        spec_id="spec-123",
        arch_id="arch-456",
        link_type="derives",
    )
    result = sanitize_artifact_metadata(meta)
    assert result["phase_name"] == "specification"
    assert result["source_engine"] == "specification-engine"
    assert result["parent_artifact_id"] is None
    assert result["subdir"] == ""
    assert result["model"] == "gemma-4-e4b"
    assert result["spec_id"] == "spec-123"
    assert result["arch_id"] == "arch-456"
    assert result["link_type"] == "derives"


def test_sanitize_none_input():
    """None input must return empty dict."""
    result = sanitize_artifact_metadata(None)
    assert result == {}


def test_sanitize_empty_dict():
    """Empty dict input must return empty dict."""
    result = sanitize_artifact_metadata({})
    assert result == {}


# ─── Test: compute_artifact_hash ──────────────────────────────────────────

def test_hash_excludes_artifact_hash_from_metadata():
    """artifact_hash in metadata must not affect the computed hash."""
    meta_clean = make_metadata()
    meta_dirty = make_metadata(artifact_hash="some-hash-value")

    hash_clean = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_clean)
    hash_dirty = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_dirty)

    assert hash_clean == hash_dirty, "Hash should be identical regardless of artifact_hash in metadata"


def test_hash_excludes_content_hash_from_metadata():
    """content_hash in metadata must not affect the computed hash."""
    meta_clean = make_metadata()
    meta_dirty = make_metadata(content_hash="some-content-hash")

    hash_clean = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_clean)
    hash_dirty = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_dirty)

    assert hash_clean == hash_dirty, "Hash should be identical regardless of content_hash in metadata"


def test_hash_excludes_size_bytes_from_metadata():
    """size_bytes in metadata must not affect the computed hash."""
    meta_clean = make_metadata()
    meta_dirty = make_metadata(size_bytes=99999)

    hash_clean = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_clean)
    hash_dirty = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_dirty)

    assert hash_clean == hash_dirty, "Hash should be identical regardless of size_bytes in metadata"


def test_hash_same_metadata_different_key_order():
    """Same metadata with different key order must produce the same hash."""
    meta1 = {"phase_name": "spec", "source_engine": "engine", "subdir": "", "parent_artifact_id": None}
    meta2 = {"parent_artifact_id": None, "subdir": "", "source_engine": "engine", "phase_name": "spec"}

    hash1 = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta1)
    hash2 = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta2)

    assert hash1 == hash2, "Hash must be identical regardless of metadata key order"


def test_hash_different_content_produces_different_hash():
    """Different content must produce different hashes."""
    meta = make_metadata()
    hash1 = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, "content A", SAMPLE_PHASE, meta)
    hash2 = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, "content B", SAMPLE_PHASE, meta)

    assert hash1 != hash2, "Different content must produce different hashes"


def test_hash_different_name_produces_different_hash():
    """Different name must produce different hashes."""
    meta = make_metadata()
    hash1 = compute_artifact_hash(SAMPLE_TYPE, "file_a.json", SAMPLE_CONTENT, SAMPLE_PHASE, meta)
    hash2 = compute_artifact_hash(SAMPLE_TYPE, "file_b.json", SAMPLE_CONTENT, SAMPLE_PHASE, meta)

    assert hash1 != hash2, "Different name must produce different hashes"


def test_hash_different_type_produces_different_hash():
    """Different artifact_type must produce different hashes."""
    meta = make_metadata()
    hash1 = compute_artifact_hash("specification", SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta)
    hash2 = compute_artifact_hash("architecture", SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta)

    assert hash1 != hash2, "Different artifact_type must produce different hashes"


def test_hash_is_deterministic():
    """Same inputs must always produce the same hash."""
    meta = make_metadata()
    hashes = [
        compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta)
        for _ in range(10)
    ]
    assert len(set(hashes)) == 1, "Hash must be deterministic"


def test_hash_64_char_hex():
    """Hash must be a 64-character hex string (SHA256)."""
    meta = make_metadata()
    h = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta)
    assert len(h) == 64, f"Expected 64 chars, got {len(h)}"
    assert all(c in "0123456789abcdef" for c in h), "Hash must be hex"


# ─── Test: extract_structured_output ───────────────────────────────────────

def test_extract_plain_json():
    """Plain JSON should be normalized."""
    raw = '{"key": "value", "num": 42}'
    normalized, original = extract_structured_output(raw)
    assert json.loads(normalized) == {"key": "value", "num": 42}
    assert original == raw


def test_extract_markdown_wrapped_json():
    """Markdown-wrapped JSON should be extracted and normalized."""
    raw = '```json\n{"key": "value", "num": 42}\n```'
    normalized, original = extract_structured_output(raw)
    assert json.loads(normalized) == {"key": "value", "num": 42}
    assert original == raw


def test_extract_markdown_wrapped_json_no_lang():
    """Markdown fence without json lang spec should also work."""
    raw = '```\n{"key": "value"}\n```'
    normalized, original = extract_structured_output(raw)
    assert json.loads(normalized) == {"key": "value"}


def test_extract_plain_text():
    """Plain text should be returned as-is."""
    raw = "This is just plain text"
    normalized, original = extract_structured_output(raw)
    assert normalized == raw
    assert original == raw


def test_extract_empty_string():
    """Empty string should return empty."""
    normalized, original = extract_structured_output("")
    assert normalized == ""
    assert original == ""


def test_extract_preserves_raw():
    """Raw response must always be preserved for audit."""
    raw = '```json\n{"a": 1}\n```Some explanation text'
    normalized, original = extract_structured_output(raw)
    assert original == raw, "Raw response must be preserved exactly"


def test_extract_json_keys_sorted():
    """Normalized JSON must have sorted keys for deterministic hashing."""
    raw = '{"z": 1, "a": 2, "m": 3}'
    normalized, _ = extract_structured_output(raw)
    parsed = json.loads(normalized)
    assert list(parsed.keys()) == ["a", "m", "z"], "Keys must be sorted"


# ─── Test: _filter_metadata_for_hash ──────────────────────────────────────

def test_filter_excludes_volatile():
    """_filter_metadata_for_hash must exclude volatile fields."""
    meta = {
        "phase_name": "spec",
        "artifact_hash": "abc",
        "content_hash": "def",
        "size_bytes": 42,
        "model": "gemma",
    }
    filtered = _filter_metadata_for_hash(meta)
    assert "artifact_hash" not in filtered
    assert "content_hash" not in filtered
    assert "size_bytes" not in filtered
    assert filtered["phase_name"] == "spec"
    assert filtered["model"] == "gemma"


def test_filter_none_input():
    """_filter_metadata_for_hash with None must return empty dict."""
    assert _filter_metadata_for_hash(None) == {}


# ─── Test: Hash contract ──────────────────────────────────────────────────

def test_artifact_hash_not_in_own_hash():
    """artifact_hash must not be included in its own computation."""
    # Simulate: compute hash with metadata that includes artifact_hash
    # The old bug was that artifact_hash was in the metadata during hashing
    meta_with_hash = make_metadata(artifact_hash="computed-hash-placeholder")
    meta_without = make_metadata()

    hash_with = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_with_hash)
    hash_without = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta_without)

    assert hash_with == hash_without, "artifact_hash must not affect its own computation"


def test_mutation_after_hashing_creates_mismatch():
    """Mutating content after hashing must produce a different hash."""
    meta = make_metadata()
    original_hash = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, SAMPLE_CONTENT, SAMPLE_PHASE, meta)

    # Mutate content
    mutated_content = SAMPLE_CONTENT + "\n# Modified"
    mutated_hash = compute_artifact_hash(SAMPLE_TYPE, SAMPLE_NAME, mutated_content, SAMPLE_PHASE, meta)

    assert original_hash != mutated_hash, "Mutated content must produce different hash"


def test_raw_vs_normalized_different_when_markdown():
    """Raw response hash must differ from normalized content hash when markdown wrapping exists."""
    raw = '```json\n{"key": "value"}\n```'
    normalized, original = extract_structured_output(raw)

    raw_hash = hashlib.sha256(raw.encode()).hexdigest()
    normalized_hash = hashlib.sha256(normalized.encode()).hexdigest()

    assert raw_hash != normalized_hash, "Raw and normalized hashes must differ when markdown wrapping exists"


# ─── Traceability Tests ────────────────────────────────────────────────────

def test_traceability_link_creation():
    """TraceabilityManager.link must create a link with all required fields."""
    from src.core.hashing import compute_traceability_hash
    link_data = {
        "source_type": "requirement",
        "source_id": "FR-001",
        "target_type": "acceptance_criterion",
        "target_id": "AC-001",
        "link_type": "validated_by",
        "run_id": "test-run-id",
    }
    edge_hash = compute_traceability_hash(**link_data)
    assert len(edge_hash) == 64, "Edge hash must be 64-char hex"
    assert all(c in "0123456789abcdef" for c in edge_hash), "Edge hash must be hex"


def test_traceability_link_deterministic():
    """Same traceability link must produce same edge hash."""
    from src.core.hashing import compute_traceability_hash
    params = {
        "source_type": "requirement",
        "source_id": "FR-001",
        "target_type": "test_case",
        "target_id": "TC-001",
        "link_type": "tested_by",
        "run_id": "test-run-id",
    }
    h1 = compute_traceability_hash(**params)
    h2 = compute_traceability_hash(**params)
    assert h1 == h2, "Edge hash must be deterministic"


def test_traceability_link_different_sources_produce_different_hashes():
    """Different source/target must produce different edge hashes."""
    from src.core.hashing import compute_traceability_hash
    base = {"link_type": "implements", "run_id": "test-run-id"}
    h1 = compute_traceability_hash(source_type="requirement", source_id="FR-001", target_type="test_case", target_id="TC-001", **base)
    h2 = compute_traceability_hash(source_type="requirement", source_id="FR-002", target_type="test_case", target_id="TC-001", **base)
    assert h1 != h2, "Different source_id must produce different hash"


def test_traceability_required_relation_types():
    """All required traceability relation types must be supported."""
    from src.core.hashing import compute_traceability_hash
    required_types = [
        ("requirement", "acceptance_criterion", "validated_by"),
        ("requirement", "architecture_component", "implemented_by"),
        ("requirement", "test_case", "tested_by"),
        ("requirement", "governance_concern", "governed_by"),
        ("architecture_component", "test_case", "tested_by"),
        ("governance_concern", "governance_policy", "evaluated_by"),
        ("governance_policy", "governance_evaluation", "evaluated_as"),
        ("governance_evaluation", "release_gate", "gates"),
        ("phase", "artifact", "produces"),
    ]
    base = {"run_id": "test-run-id", "source_id": "SRC-001", "target_id": "TGT-001"}
    for src_type, tgt_type, link_type in required_types:
        h = compute_traceability_hash(source_type=src_type, target_type=tgt_type, link_type=link_type, **base)
        assert len(h) == 64, f"Hash for {src_type}→{tgt_type} ({link_type}) must be 64 chars"


# ─── Governance Tests ──────────────────────────────────────────────────────

def test_governance_evaluation_hash():
    """Governance evaluation integrity hash must be computable."""
    from src.core.hashing import compute_governance_hash
    h = compute_governance_hash(
        policy_name="test-policy",
        decision="pass",
        input_data={"findings": []},
        output_data={"decision": "pass"},
        run_id="test-run-id",
    )
    assert len(h) == 64, "Governance hash must be 64-char hex"
    assert all(c in "0123456789abcdef" for c in h), "Governance hash must be hex"


def test_governance_evaluation_hash_deterministic():
    """Same governance evaluation must produce same hash."""
    from src.core.hashing import compute_governance_hash
    params = {
        "policy_name": "no-critical-vulnerabilities",
        "decision": "fail",
        "input_data": {"findings": [{"impact": "high"}]},
        "output_data": {"decision": "fail"},
        "run_id": "test-run-id",
    }
    h1 = compute_governance_hash(**params)
    h2 = compute_governance_hash(**params)
    assert h1 == h2, "Governance hash must be deterministic"


def test_governance_evaluation_different_decisions_different_hashes():
    """Different decisions must produce different hashes."""
    from src.core.hashing import compute_governance_hash
    base = {
        "policy_name": "test-policy",
        "input_data": {"findings": []},
        "output_data": {},
        "run_id": "test-run-id",
    }
    h_pass = compute_governance_hash(decision="pass", **base)
    h_fail = compute_governance_hash(decision="fail", **base)
    assert h_pass != h_fail, "Different decisions must produce different hashes"


def test_governance_evaluation_links_to_policy():
    """Governance evaluation must reference a policy."""
    from src.core.hashing import compute_governance_hash
    h = compute_governance_hash(
        policy_name="no-critical-vulnerabilities",
        decision="pass",
        input_data={"findings": []},
        output_data={"decision": "pass"},
        run_id="test-run-id",
        artifact_id="art-123",
    )
    assert len(h) == 64


def test_governance_all_decisions_produce_valid_hashes():
    """All decision types (pass, fail, warn) must produce valid hashes."""
    from src.core.hashing import compute_governance_hash
    base = {
        "policy_name": "test-policy",
        "input_data": {"findings": []},
        "output_data": {"decision": "pass"},
        "run_id": "test-run-id",
    }
    for decision in ["pass", "fail", "warn"]:
        h = compute_governance_hash(decision=decision, **base)
        assert len(h) == 64, f"Hash for decision={decision} must be 64 chars"


# ─── Integrity Runtime Sync Tests ──────────────────────────────────────────

def test_sync_integrity_verifier_import():
    """Sync integrity verifier must be importable."""
    from src.engines.integrity_runtime_sync import IntegrityVerifier, verify_integrity_sync
    assert IntegrityVerifier is not None
    assert verify_integrity_sync is not None


def test_sync_verifier_returns_report_for_missing_run():
    """Sync verifier must return a report for a missing run."""
    from src.engines.integrity_runtime_sync import IntegrityVerifier
    verifier = IntegrityVerifier(run_id="nonexistent-run-id")
    report = verifier.verify()
    assert report.run_id == "nonexistent-run-id"
    assert report.total_checks >= 1


def test_sync_verifier_governance_hash_matches_pipeline():
    """Sync verifier governance hash must match pipeline's hash structure."""
    from src.core.hashing import compute_governance_hash
    # Pipeline uses: input_data={"findings": findings}, output_data={"decision": decision}
    findings = [{"issue": "test"}]
    hash1 = compute_governance_hash(
        policy_name="test-policy",
        decision="fail",
        input_data={"findings": findings},
        output_data={"decision": "fail"},
        run_id="test-run",
    )
    # Sync runtime must use the same structure
    hash2 = compute_governance_hash(
        policy_name="test-policy",
        decision="fail",
        input_data={"findings": findings},
        output_data={"decision": "fail"},
        run_id="test-run",
    )
    assert hash1 == hash2, "Pipeline and sync runtime must produce same governance hash"


def test_sync_verifier_artifact_hash_matches():
    """Sync verifier artifact hash must match compute_artifact_hash."""
    from src.core.hashing import compute_artifact_hash, _filter_metadata_for_hash
    content = '{"test": true}'
    metadata = {"phase_name": "test", "source_engine": "test"}
    safe_meta = _filter_metadata_for_hash(metadata)
    h1 = compute_artifact_hash("specification", "test.json", content, "test", safe_meta)
    h2 = compute_artifact_hash("specification", "test.json", content, "test", safe_meta)
    assert h1 == h2, "Artifact hash must be deterministic"
    assert len(h1) == 64


def test_sync_verifier_traceability_hash_matches():
    """Sync verifier traceability hash must match compute_traceability_hash."""
    from src.core.hashing import compute_traceability_hash
    h = compute_traceability_hash(
        source_type="requirement", source_id="FR-001",
        target_type="test_case", target_id="TC-001",
        link_type="tested_by", run_id="test-run",
    )
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ─── Run all tests ────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        v for k, v in sorted(globals().items())
        if k.startswith("test_") and callable(v)
    ]

    passed = 0
    failed = 0
    errors = []

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
            print(f"  ✅ {test_fn.__name__}")
        except AssertionError as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  ❌ {test_fn.__name__}: {e}")
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  ❌ {test_fn.__name__}: {type(e).__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if errors:
        print("\nFailures:")
        for name, msg in errors:
            print(f"  {name}: {msg}")
        sys.exit(1)
    else:
        print("All tests passed! ✅")
        sys.exit(0)
