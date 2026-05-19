# v0.3 Verified Backup + Restore Test

**Date**: 2026-05-19
**Phase**: 9 — Verified Backup + Restore Test

## Backup Details

| Property | Value |
|----------|-------|
| **Backup Path** | `backups/v03-baseline-20260519_103757/` |
| **Bundle File** | `repo.bundle` (24 MB) |
| **Checksum (MD5)** | `883d7f0e325acb316b11facedf3e06c0` |
| **Evidence Dir** | `evidence/` (8 documents) |
| **Total Size** | 24 MB |

## Bundle Contents

| Ref | Hash |
|-----|------|
| HEAD | `c417982ed4013d065bc4df6c8d14ac28ab94da4a` |
| refs/heads/main | `c417982ed4013d065bc4df6c8d14ac28ab94da4a` |
| refs/tags/v0.1.0-golden-integrity-runtime | `8e58c4ff7fe562061b0b2810e976a0979e2d867a` |
| refs/tags/v0.2.0-evidence-backed-runtime-pass | `5088ab53960a234254b963575d22afb372fa1f35` |

## Restore Test

| Step | Result |
|------|--------|
| Clone from bundle | ✅ Success |
| HEAD after restore | `c417982` |
| Expected HEAD | `c417982` |
| Match | ✅ VERIFIED |
| Complete history | ✅ Yes (full clone) |

## Conclusion

Backup created, verified, and restore-tested successfully. The bundle contains complete history including all previous baseline tags.
