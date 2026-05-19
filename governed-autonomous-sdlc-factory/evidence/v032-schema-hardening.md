# v0.3.2 Structural Integrity — Schema Hardening Report

**Date:** 2026-05-19
**Commit:** ff265b7

## Schema Drift Audit Results

### Tables
- 61 SQLAlchemy ORM models → all 61 tables exist in DB ✅
- 73 total DB tables (12 extra are semantic coverage tables from separate Base) ✅
- No missing tables ✅

### Column-Level Drift
- **1 issue found:** `projects.workspace_id` — in ORM but NOT in database
- All other key tables (runs, artifacts, phases, cost_events) — perfect match ✅

### Fix Applied
```sql
ALTER TABLE projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36) REFERENCES workspaces(id)
```
- Executed via sync engine migration
- Verified: column now exists in database ✅

### Migration Infrastructure
- Added `init_sync_db()` function in `database.py` for idempotent sync engine migrations
- Added `workspace_id` migration for both `projects` and `runs` tables (defensive)

## JWT Security Hardening

### Issue
- Test suite used `JWT_SECRET_KEY=test-secret-key-for-tests` (25 bytes)
- Minimum required: 32 bytes per RFC 7518 Section 3.2

### Fix
- Added `__init__` validation in `Settings` class: raises `ValueError` if secret < 32 bytes
- Updated test secrets to `test-secret-key-for-tests-32bytes!` (32 bytes)
- Result: 0 JWT warnings (down from 8)

## Verification
- Backend tests: 122/122 PASS ✅
- JWT warnings: 0 ✅
- Schema drift: 0 critical issues ✅
- GitHub parity: commit ff265b7 pushed ✅
