# Active Repository Verification

**Date:** 2026-05-16T17:50:00+00:00
**Status:** ✅ VERIFIED

## Repository

| Field | Value |
|-------|-------|
| Path | `/Users/marcovanhurne/governed-autonomous-sdlc-factory` |
| Git Toplevel | `/Users/marcovanhurne/governed-autonomous-sdlc-factory` |
| Branch | `main` |
| HEAD | `819a2ae` |
| Working Tree | Clean (only `backups/20260516_175019/` untracked) |

## Commit History (latest 15)

```
819a2ae Build cognitive command center control plane
0f14ce6 Fix Pydantic v2 Config deprecation in Settings
f6dd264 Harden integrity verification API with sync runtime
6888ef9 Add traceability and governance persistence to golden pipeline
98299bb Fix artifact metadata sanitization and validate integrity repair
62635da docs: GitHub sync status — token invalid
63e3b64 feat(gemma4): Gemma 4 E4B primary model + golden pipeline + routing policy v2
6355969 feat(runtime): Full autonomous pipeline validation + model benchmarks + backup
fd462fc docs: SESSION_RECOVERY_MANIFEST — full runtime state + recovery instructions
24ef63a feat(ops): GitHub setup script + environment reports
21648a0 feat(frontend): Cognitive Command Center — 5 rooms + WebSocket + dark ops UI
8a86dc1 feat(operationalization): Ollama integration + startup diagnostics + golden baseline
3852c47 feat(cognitive): model router + real AI execution engines
8b82c1a feat(forensic): sync replay runtime + transaction manager + completeness audit
2016f4b docs(architecture): operational hardening documentation suite
```

## Tags

- `v0.1.0-golden-integrity-runtime` ✅

## Remotes

None configured.

## Key Files

| File | Status |
|------|--------|
| `apps/web/src/components/rooms/` | ✅ 12 rooms (6 existing + 6 new) |
| `evidence/` | ✅ 18+ reports |
| `SESSION_RECOVERY_MANIFEST.md` | ✅ Updated |
| `runtime/runtime-state.json` | ✅ Present |
| `apps/web/src/lib/api.ts` | ✅ Updated with all endpoints |
| `apps/web/src/lib/store.ts` | ✅ Updated with all state |
| `apps/web/src/lib/types.ts` | ✅ Updated with all types |
| `apps/api/src/` | ✅ Backend intact |
| `apps/api/tests/` | ✅ 44 tests |

## Verification Results

| Check | Result |
|-------|--------|
| Active repo path correct | ✅ |
| HEAD is 819a2ae | ✅ |
| Tag v0.1.0 exists | ✅ |
| No unexpected uncommitted changes | ✅ (only backup dir) |
| Frontend files exist | ✅ |
| Evidence files exist | ✅ |
| Runtime state exists | ✅ |
| Recovery manifest exists | ✅ |
