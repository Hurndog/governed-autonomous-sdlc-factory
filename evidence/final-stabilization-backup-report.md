# Final Stabilization Backup Report

**Date:** 2026-05-16T18:20:00+00:00
**Status:** ✅ VERIFIED

## Backup

| Field | Value |
|-------|-------|
| Location | `backups/20260516_182041/` |
| Size | 6.6MB |
| Files | 36 |
| Bundle SHA256 | `9647b6fc4f73c3c20d1ae5cf04bfaa14d4654d5129112097798e753d1dd530da` |
| Bundle verified | ✅ `git bundle verify` passed |
| HEAD | `cbb52b9` |
| Tag | `v0.1.0-golden-integrity-runtime` |

## Restore Test

| Check | Result |
|-------|--------|
| Clone from bundle | ✅ Success |
| HEAD matches | ✅ `cbb52b9` |
| Tag present | ✅ `v0.1.0-golden-integrity-runtime` |
| Commit `819a2ae` present | ✅ |
| Commit `cbb52b9` present | ✅ |
| Frontend rooms (12) | ✅ All present |
| Evidence files (26) | ✅ All present |
| Runtime state (3) | ✅ All present |
| Recovery manifest | ✅ Present |

## Checksum Verification

- **Fresh checksum:** `9647b6fc4f73c3c20d1ae5cf04bfaa14d4654d5129112097798e753d1dd530da`
- **Previous backup checksum:** `f3cf28204dd73c327a22a7d049d0ece00fb10bbfe8589281fac7f4f8887c962c`
- **Different:** ✅ Yes — fresh checksums are generated correctly

## Conclusion

Backup is trustworthy. The hardened backup script correctly generates fresh checksums, verifies the bundle, and includes all necessary files.
