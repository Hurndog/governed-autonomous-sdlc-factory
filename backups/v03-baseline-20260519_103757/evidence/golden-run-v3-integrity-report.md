# Golden Run v3 Integrity Report

**Date:** 2026-05-16  
**Run ID:** `6a7f7ea0-297f-435e-9bb2-899368c7d332`  
**Pipeline:** Traceability+Governance+Validation  
**Model:** gpt-oss:20b (Ollama fallback)  
**Overall Integrity:** 1.0 ✅

---

## Integrity Scores

| Component | Score | Status |
|-----------|-------|--------|
| Event Chain | 1.0 | ✅ PASS |
| Snapshot | 1.0 | ✅ PASS |
| Artifact | 1.0 | ✅ PASS |
| Timeline | 1.0 | ✅ PASS |
| Traceability | 1.0 | ✅ PASS |
| Governance | 1.0 | ✅ PASS |
| **Overall** | **1.0** | ✅ **PASS** |

---

## Event Chain
- Total events: 239
- Events with hashes: 239
- Broken chain links: 0
- Missing hashes: 0

## Snapshot
- Total snapshots: 1
- Verified: 1
- Mismatched: 0

## Artifacts
- Total: 12
- Verified: 12
- Mismatched: 0
- All metadata_ clean (no volatile fields)

## Timeline
- Total events: 239
- Ordering violations: 0

## Traceability
- Total links: 215
- Links with edge hashes: 215
- Missing hashes: 0
- Relation types covered: 9/9 required

## Governance
- Total evaluations: 10
- Pass: 9
- Fail: 1 (no-critical-vulnerabilities — legitimate security finding)
- Release gates: 1 (status: failed due to blocking policy)
- All evaluations have integrity_hash

---

## Conclusion

The golden run achieves **overall integrity = 1.0**, exceeding the target of >= 0.95. All six integrity components score 1.0. The pipeline now produces complete traceability links and governance evaluations, fulfilling the traceability and governance contracts.
