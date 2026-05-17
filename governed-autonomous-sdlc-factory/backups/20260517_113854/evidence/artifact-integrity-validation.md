# Artifact Integrity Validation Report

**Date:** 2026-05-16  
**Run ID:** `789c0b53-fc47-49d7-8c1c-354f7a7395f3`  
**Status:** ✅ PASSED — Artifact Integrity = 1.0

---

## Integrity Scores

| Check | Before Fix | After Fix |
|-------|-----------|-----------|
| Event Chain | 1.0 | 1.0 |
| Snapshot | 1.0 | 1.0 |
| **Artifact** | **0.0** | **1.0** |
| Timeline | 1.0 | 1.0 |
| Traceability | 0.0 | 0.0* |
| Governance | 0.0 | 0.0* |
| **Overall** | **0.33** | **0.67** |

*Traceability and governance warnings are expected — the pipeline does not populate traceability links or governance evaluations via the engine endpoints. This is a separate issue from artifact hashing.

---

## Artifact Hash Table (12/12 Verified)

| # | Artifact ID | Type | Name | Stored Hash | Match | Meta Clean |
|---|-------------|------|------|-------------|-------|------------|
| 1 | 66ec530e... | specification | intent.md | 5f9b37f1eb0d6407... | ✅ | ✅ |
| 2 | f2492c8a... | specification | requirements.json | 5b73df804c030afa... | ✅ | ✅ |
| 3 | a9459103... | specification | acceptance_criteria.json | 311427b819e0f800... | ✅ | ✅ |
| 4 | 29db01ef... | specification | governance_areas.json | a1cc6f8f8d02b990... | ✅ | ✅ |
| 5 | 98784724... | architecture | architecture.md | 9480d1d977ea4ddc... | ✅ | ✅ |
| 6 | 5bbe05d1... | architecture | components.json | 68652ab9f8d96db3... | ✅ | ✅ |
| 7 | 23fc3b71... | architecture | adrs.json | 60884262497c7cd3... | ✅ | ✅ |
| 8 | c99e7e58... | architecture | diagram_*.mmd | fcc8d5b9126f03bb... | ✅ | ✅ |
| 9 | 4f653e73... | governance | governance_concerns.json | 542a9ea211d9c261... | ✅ | ✅ |
| 10 | 3a5e0a6a... | governance | security_findings.json | bcf11ee3c1a220ec... | ✅ | ✅ |
| 11 | c524afa8... | governance | compliance_gaps.json | b7f56ad2fefc2187... | ✅ | ✅ |
| 12 | b07c4133... | test_plan | test_plan.json | 06d9b4d76177be5e... | ✅ | ✅ |

**Result: 12/12 hashes match, 12/12 metadata clean**

---

## Event Chain Integrity

- Total events: 24
- Events with hashes: 24
- Broken chain links: 0
- Missing hashes: 0
- Status: ✅ PASS

## Snapshot Integrity

- Total snapshots: 1
- Verified: 1
- Mismatched: 0
- Status: ✅ PASS

## Timeline Chain Integrity

- Total events: 24
- Ordering violations: 0
- Status: ✅ PASS

---

## Conclusion

The artifact integrity repair is **complete and validated**. All 12 artifacts in the golden run pass hash verification. The metadata_ column contains only stable descriptive fields with no volatile derived values.
