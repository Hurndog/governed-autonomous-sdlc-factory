# GitHub Recovery Instructions

**Date:** 2026-05-16
**Status:** ✅ COMPLETE — No further action needed

## What Was Done

1. ✅ Token validated (HTTP 200, authenticated as Hurndog)
2. ✅ Repository created: `governed-autonomous-sdlc-factory`
3. ✅ Remote configured: `https://github.com/Hurndog/governed-autonomous-sdlc-factory.git`
4. ✅ Branch `main` pushed (15 commits)
5. ✅ Tag `v0.1.0-golden-integrity-runtime` pushed
6. ✅ Remote parity verified (local HEAD == remote HEAD)

## Repository

https://github.com/Hurndog/governed-autonomous-sdlc-factory

## Future Pushes

For future pushes, either:

### Option A: Use the script
```bash
export GITHUB_TOKEN="ghp_..."
bash scripts/github-setup.sh
```

### Option B: Manual push
```bash
git push origin main
git push --tags
```

### Option C: Set credential helper permanently
```bash
git config --global credential.helper store
# First push will prompt for credentials, then cache them
```

## Token Management

- Token name: `Hermes SDLC Factory Push Token`
- Token type: Classic PAT with `repo` scope
- Token location: User's environment (NOT stored in repo)
- To revoke: https://github.com/settings/tokens
