# GitHub Recovery Instructions

**Date:** 2026-05-16
**Status:** 🔴 BLOCKED — Awaiting valid PAT

## Exact Steps for User

### Step 1: Create GitHub PAT

1. Go to https://github.com/settings/tokens/new
2. Set:
   - **Note:** `governed-sdlc-factory`
   - **Expiration:** 90 days
   - **Scopes:** ✅ `repo` (full control)
3. Click **Generate token**
4. **Copy the token immediately** (starts with `ghp_`)

### Step 2: Export Token (in terminal)

```bash
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
```

### Step 3: Run Setup Script

```bash
cd /Users/marcovanhurne/governed-autonomous-sdlc-factory
bash scripts/github-setup.sh
```

### Step 4: Verify

```bash
git remote -v
git log --oneline -3
git tag --list
```

## What the Script Does

1. ✅ Validates `GITHUB_TOKEN` is present
2. ✅ Tests token with GitHub API (prints only HTTP status, never token)
3. ✅ Checks if remote exists
4. ✅ Checks if repo exists (creates if needed)
5. ✅ Configures remote
6. ✅ Pushes `main` branch
7. ✅ Pushes all tags
8. ✅ Verifies remote parity (local HEAD == remote HEAD)
9. ✅ Generates evidence report

## After Push

The repository will be available at:
https://github.com/Hurndog/governed-autonomous-sdlc-factory

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `GITHUB_TOKEN not set` | Token not exported | Run `export GITHUB_TOKEN="..."` |
| `401 Unauthorized` | Token invalid/expired | Create new PAT |
| `403 Forbidden` | Token lacks `repo` scope | Recreate with `repo` scope |
| `remote already exists` | Old remote configured | Script handles this |
| `push rejected` | Branch protection | Push to new repo or adjust settings |
