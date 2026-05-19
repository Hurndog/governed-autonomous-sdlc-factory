# v0.3.1 Runtime Truth — Phase 0 Baseline Verification

**Date:** 2026-05-19
**Commit:** c417982ed4013d065bc4df6c8d14ac28ab94da4a
**Branch:** main

## Verification Results

| Check | Status | Details |
|-------|--------|---------|
| Branch | ✅ | `main` |
| Local HEAD | ✅ | `c417982` |
| Remote HEAD | ✅ | `c417982` — parity confirmed |
| GitHub parity | ✅ | 0 ahead, 0 behind |
| Frontend build | ✅ | Next.js build SUCCESS |
| TypeScript | ✅ | 0 errors (`tsc --noEmit`) |
| Backend tests | ✅ | 122/122 PASS |
| Replay operational | ✅ | Evidence chain tests pass |
| Mutation execution | ✅ | `execute_mutation` in SemanticCoverageEngine |
| Governance operational | ✅ | Release gate enforcement active |
| Semantic coverage | ✅ | Engine + endpoint operational |

## Baseline Fixes Applied

1. **CostReportResponse schema** — Added `missing_fields: List[str]` and `data_quality_warnings: List[str]` fields. Tests were checking for these fields but they didn't exist in the schema. This was a regression from the tautological test replacement.

## Test Count Evolution

- v0.3 baseline: 114 tests
- After release gate tests: 122 tests
- After schema fix: 122 tests (all pass)

## Epistemic Status

- Release gates: genuinely enforce (not stubbed)
- Mutation execution: genuinely runs (not hardcoded 0.0)
- Tests: no tautological assertions remain
- Schema: response models match what tests expect

## Known Issues

- Pyright warnings on SQLAlchemy models (pre-existing, non-blocking)
- JWT key length warning (25 bytes < 32 recommended) — functional but should be hardened
