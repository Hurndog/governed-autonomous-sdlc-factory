# PASS Baseline Backup & Restore Report

**Date:** 2026-05-14
**Time:** 08:25 CET

## Backup Information

- **Backup Path:** `/Users/marcovanhurne/governed-autonomous-sdlc-factory/backups/pass-baseline-20260517-120948`
- **Backup Size:** 9.8 MB
- **Backup Type:** git bundle + evidence + manifest + checksums

## Files Included

| File/Dir | Description |
|---|---|
| `repo.bundle` | Full git bundle (all branches, all history) |
| `evidence/` | 52 evidence markdown files |
| `head.txt` | Current HEAD commit hash |
| `tags.txt` | All tags in the repository |
| `checksums.sha256` | SHA256 checksums for all backup files |

## Checksum

- `repo.bundle`: `b014a49f24c8b81e194a9307b71f82030b392a392ee04b22d93ae1223e5b62a8`

## Restore Test

- **Restore Path:** `/var/folders/lz/5qd6j0j960sg7gsqf8dr48v80000gn/T/tmp.LpRNeTHbIG`
- **Restored HEAD:** `e2fc3860095f672feeec22b11153e4c279bc05e7`
- **Local HEAD:** `e2fc3860095f672feeec22b11153e4c279bc05e7`
- **HEAD Match:** ✅ Yes

## Restored Content Verification

| Check | Result |
|---|---|
| Restored tag `v0.2.0-evidence-backed-runtime-pass` | ✅ |
| Restored tag `v0.1.0-golden-integrity-runtime` | ✅ |
| Evidence files (52 .md files) | ✅ |
| Frontend files (`apps/web/`) | ✅ (Next.js, TypeScript, Tailwind) |
| Backend files (`apps/api/src/`) | ✅ (FastAPI, LangGraph, engines) |
| `docs/` directory | ✅ |
| `scripts/` directory | ✅ |
| `alembic/` migrations | ✅ |
| `docker-compose.yml` | ✅ |

## Result

✅ **PASS** — Backup is complete, restorable, and verified. Restored HEAD matches local HEAD. All critical files present. Both tags intact.
