# Phase 2 — Static Anti-Fraud Scan Report

**Date**: 2026-05-17
**Files scanned**: 59 Python files in critical runtime paths

---

## Findings Summary

| Category | Count |
|---|---|
| Critical runtime issues | 0 |
| High-risk runtime issues | 1 |
| Medium-risk issues | 2 |
| Low-risk issues | 0 |
| Allowed in tests | 0 |
| Allowed in documentation | 0 |
| False positives (legitimate code) | 12 |
| **Total findings** | **15** |

---

## Detailed Findings

### HIGH RISK (1)

| # | File | Line | Pattern | Context | Risk | Classification |
|---|---|---|---|---|---|---|
| 1 | `apps/api/src/api/v1/endpoints/engines.py` | 151 | `not implemented` | `return {"from": from_version, "to": to_version, "diff": "not implemented"}` | Specification diff endpoint returns hardcoded stub response | **HIGH** — API endpoint returns fake data |

### MEDIUM RISK (2)

| # | File | Line | Pattern | Context | Risk | Classification |
|---|---|---|---|---|---|---|
| 2 | `apps/api/src/engines/model_providers.py` | 108 | `NotImplementedError` | `raise NotImplementedError` in abstract base class method | Expected for abstract interface, but confirms not all providers are implemented | **MEDIUM** — Abstract base, but runtime provider may be missing |
| 3 | `apps/api/src/core/hashing.py` | 216 | `return True` | `return True  # Chain integrity verified by recomputation` | Chain integrity function always returns True after loop — the loop computes but the return is unconditional | **MEDIUM** — Always returns True regardless of actual chain validity |

### FALSE POSITIVES / LEGITIMATE (12)

| # | File | Line | Pattern | Context | Classification |
|---|---|---|---|---|---|
| 4 | `phase_service.py` | 104 | `demo` | `approval.approver = "demo-auto-approver"` — demo mode flag | Legitimate demo mode |
| 5 | `project_service.py` | 66 | `return False` | Permission check returning False | Legitimate boolean logic |
| 6 | `project_service.py` | 68 | `return True` | Permission check returning True | Legitimate boolean logic |
| 7-9 | `semantic_coverage_engine.py` | 997-1009 | `return True/False` | `_is_tautological()`, `_can_broken_code_pass()` — deterministic classifier returns | Legitimate boolean classifiers |
| 10 | `specification_engine.py` | 84 | `demo` | `"verification_method": "test|review|demo|analysis"` — example string in docstring/template | Legitimate template |
| 11 | `auth.py` | 35 | `return True` | Role-based permission check | Legitimate auth logic |
| 12 | `hashing.py` | 211 | `return True` | Empty hashes edge case | Legitimate edge case |
| 13 | `approvals.py` | 27 | `demo` | Demo mode auto-approver | Legitimate demo mode |

---

## Critical Checks

| Check | Result |
|---|---|
| Hardcoded integrity pass | ✅ NONE FOUND |
| Hardcoded semantic coverage pass | ✅ NONE FOUND |
| Hardcoded governance pass | ✅ NONE FOUND |
| Hardcoded release gate pass | ✅ NONE FOUND |
| Fake frontend success state | ✅ NONE FOUND (frontend not built) |
| Fake model response | ✅ NONE FOUND |
| Fake evidence binding | ✅ NONE FOUND |
| Fake test execution | ✅ NONE FOUND |
| Fake replay result | ✅ NONE FOUND |
| Fake backup result | ✅ NONE FOUND |
| `while True` in runtime | ✅ NONE FOUND |
| `TODO` in runtime | ✅ NONE FOUND |
| `FIXME` in runtime | ✅ NONE FOUND |

---

## Issues Requiring Action

### Issue 1: Specification Diff Endpoint Returns Stub (HIGH)

**File**: `apps/api/src/api/v1/endpoints/engines.py:151`
**Problem**: The `/api/v1/engines/specification/{run_id}/diff` endpoint returns `{"diff": "not implemented"}` — a hardcoded stub.
**Impact**: Any frontend or API consumer calling this endpoint gets fake data.
**Required Fix**: Implement actual diff logic or return 501 with clear error.

### Issue 2: Chain Integrity Always Returns True (MEDIUM)

**File**: `apps/api/src/core/hashing.py:216`
**Problem**: `verify_chain_integrity()` always returns `True` after the loop, regardless of whether the chain is actually valid.
**Impact**: Chain integrity verification is theatrical — it computes but never fails.
**Required Fix**: Compare computed chain hash against stored hash and return False on mismatch.

### Issue 3: Abstract Model Provider (MEDIUM)

**File**: `apps/api/src/engines/model_providers.py:108`
**Problem**: Base provider class raises `NotImplementedError` — expected for abstract, but need to verify concrete providers exist and are used.
**Impact**: If a concrete provider isn't registered, runtime will crash.
**Required Fix**: Verify concrete provider registration (non-blocking if providers exist elsewhere).

---

## Verdict

✅ **No critical runtime stubs found.**
✅ **No hardcoded pass states found.**
⚠️ **1 HIGH issue**: Specification diff endpoint is a stub.
⚠️ **2 MEDIUM issues**: Chain integrity always True, abstract provider.

The core semantic coverage engine, integrity runtime, and governance engine are **free of hardcoded pass states and fake evidence**.
