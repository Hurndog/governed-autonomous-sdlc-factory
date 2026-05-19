# v03 Fake Data & Hardcoded State Hunt

**Date**: 2026-05-19
**Phase**: 3 — Fake Data & Hardcoded State Hunt

## Methodology

Scanned all 25 room screens + mock-data.ts for:
- Hardcoded success states
- Static progress values
- Fake token counts/costs/timestamps
- Always-true conditions
- Silent error swallowing
- Mock data used as primary (not fallback) data
- Fallback abuse (mock presented as real)

---

## Findings

### 🔴 CRITICAL

#### 1. evaluate_release_gate always returns "passed"
- **File**: `src/api/v1/endpoints/engines.py:392`
- **Code**: `return {"gate_id": gate_id, "status": "passed"}`
- **Severity**: HIGH
- **Impact**: If called, bypasses governance entirely
- **Mitigation**: Not called from any frontend screen
- **Status**: Latent vulnerability — should be fixed or removed

---

### 🟡 MEDIUM

#### 2. BuildMap initial state is mock data
- **File**: `apps/web/src/components/rooms/BuildMap.tsx:109`
- **Code**: `useState<ArchComponent[]>(mockArchComponents)`
- **Severity**: MEDIUM
- **Impact**: On first render (before API response), mock data is displayed
- **Mitigation**: DataSourceBadge shows "LOADING" initially, then updates to LIVE/PARTIAL/MOCK based on API results
- **Status**: Acceptable — standard React pattern for initial state

#### 3. Tautological tests in test_cost_report.py
- **File**: `tests/test_cost_report.py:19,46,52`
- **Code**: `assert True  # Placeholder`
- **Severity**: MEDIUM
- **Impact**: False confidence — tests always pass
- **Mitigation**: Clearly marked as placeholders
- **Status**: Should be replaced with real integration tests

#### 4. Mock data used as initial state in multiple screens
- **Screens**: Dashboard, ExecutiveCockpit, AgentCommandCenter, BacklogChecklist, ProcessTimeline, SDLCNavigator, BuildMap, and others
- **Pattern**: `useState(mockXxx)` for initial values
- **Severity**: LOW
- **Impact**: Brief flash of mock data before API response
- **Mitigation**: All screens use loading states and DataSourceBadge to indicate data provenance
- **Status**: Acceptable — standard React pattern

---

### 🟢 LOW / ACCEPTABLE

#### 5. ArchitectureIntelligence is entirely mock-based
- **File**: `apps/web/src/components/rooms/ArchitectureIntelligence.tsx`
- **Severity**: LOW
- **Impact**: Shows static topology, not runtime state
- **Justification**: Architecture topology is inherently static (design-time, not runtime)
- **Status**: ACCEPTABLE — documented in sealed baseline

#### 6. Static timestamps in mock-data.ts
- **File**: `apps/web/src/lib/mock-data.ts`
- **Count**: 23 static timestamps
- **Severity**: LOW
- **Impact**: Mock data has fixed dates (2026-05-10 to 2026-05-14)
- **Justification**: Mock data is for fallback/demo only
- **Status**: ACCEPTABLE

#### 7. Hardcoded success states in mock GovGate data
- **File**: `apps/web/src/lib/mock-data.ts`
- **Count**: 25 hardcoded `'passed'`/`'verified'` statuses
- **Severity**: LOW
- **Impact**: Mock governance gates show success
- **Justification**: Mock data only used as fallback when API returns no data
- **Status**: ACCEPTABLE — but DataSourceBadge correctly indicates MOCK status

#### 8. UserManagement silent error swallowing
- **File**: `apps/web/src/components/rooms/UserManagement.tsx`
- **Pattern**: `catch(() => ({}))`
- **Severity**: LOW
- **Impact**: API errors silently ignored, empty object returned
- **Justification**: Graceful degradation — UI won't crash on API errors
- **Status**: ACCEPTABLE — but could be improved with error logging

#### 9. ProcessTimeline mock fallback uses `new Date()`
- **File**: `apps/web/src/components/rooms/ProcessTimeline.tsx`
- **Pattern**: `timestamp: new Date().toISOString()` in mock mapping
- **Severity**: LOW
- **Impact**: Mock events get current timestamp
- **Justification**: Only used when no backend data exists
- **Status**: ACCEPTABLE

---

## What Was NOT Found

✅ No `Math.random()` usage in production code
✅ No `if True` or `assert True` in production code (only in tests)
✅ No fake evidence generation in backend
✅ No fake governance outcomes in real evaluation engine
✅ No fabricated token counts in cost tracking
✅ No unreachable failure states in governance engine
✅ No demo-mode code hiding real behavior
✅ No fake telemetry generators

## Differentiation: Legitimate Mock Fallback vs Deceptive Behavior

### Legitimate (ACCEPTABLE)
- Mock data as initial React state (replaced by API data on mount)
- Mock data as fallback when API returns empty/null
- DataSourceBadge clearly indicates MOCK/LIVE/PARTIAL status
- Static architecture topology (inherently design-time, not runtime)

### Deceptive (FOUND)
- `evaluate_release_gate` always returns "passed" — this is a stub that could be called to bypass governance
- 3 tautological tests that always pass — provide false confidence

---

## Severity Summary

| Severity | Count | Items |
|----------|-------|-------|
| CRITICAL | 0 | — |
| HIGH | 1 | evaluate_release_gate stub |
| MEDIUM | 3 | BuildMap initial mock, tautological tests, mock initial state pattern |
| LOW | 5 | ArchitectureIntelligence MOCK, static timestamps, mock GovGate, silent errors, mock timestamps |
| ACCEPTABLE | 4 | All documented and mitigated |

## Conclusion

**No systematic fake runtime behavior found.** The system's core data flow is honest:
- Backend returns real data from DB
- Frontend fetches from real API endpoints
- Mock data is used only as initial state or fallback
- DataSourceBadge clearly indicates data provenance
- One governance stub exists but is not called from UI
- Three tautological tests exist but are clearly marked as placeholders
