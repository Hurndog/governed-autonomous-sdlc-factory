# Restore Instructions — Backup 20260517_113854

## Quick Restore

```bash
# 1. Clone from bundle
git clone repo.bundle restored-repo
cd restored-repo

# 2. Verify HEAD
git log --oneline -1
# Expected: 7e1bbd4

# 3. Restore database
gunzip db.sql.gz
psql -U governance -h localhost sdlc_factory < db.sql

# 4. Verify
cd apps/api
python -m pytest tests/ -q
# Expected: 82 passed
```

## Verification Checklist

- [ ] `git log --oneline -1` shows `7e1bbd4`
- [ ] `python -m pytest tests/ -q` shows 82 passed
- [ ] `pnpm build` in apps/web succeeds
- [ ] Evidence files present in evidence/
- [ ] Checksums match checksums.sha256

## Backup Contents

| File | Description |
|---|---|
| repo.bundle | Full git history bundle |
| db.sql.gz | PostgreSQL database dump |
| evidence/ | All evidence reports |
| checksums.sha256 | SHA256 checksums for all files |
| manifest.json | Backup metadata |
| RESTORE.md | This file |
