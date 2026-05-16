#!/bin/bash
# Hardened GitHub Setup Script for Governed Autonomous SDLC Factory
# Usage: export GITHUB_TOKEN="ghp_..." && bash scripts/github-setup.sh

set -euo pipefail

REPO_NAME="governed-autonomous-sdlc-factory"
REPO_PATH="/Users/marcovanhurne/governed-autonomous-sdlc-factory"
GITHUB_USER="Hurndog"
REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
REMOTE_URL_WITH_TOKEN="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
EVIDENCE_DIR="${REPO_PATH}/evidence"

echo "=== GitHub Setup ==="

# ─── 1. Token Validation ───────────────────────────────────────────────
if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable not set"
    echo ""
    echo "Create a PAT at: https://github.com/settings/tokens/new"
    echo "Required scopes: repo"
    echo ""
    echo "Then run:"
    echo "  export GITHUB_TOKEN=\"ghp_xxxxxxxxxxxxxxxxxxxx\""
    echo "  bash scripts/github-setup.sh"
    exit 1
fi

TOKEN_LEN=${#GITHUB_TOKEN}
echo "Token present: true"
echo "Token length: ${TOKEN_LEN}"

# Test token with GitHub API
echo "Testing token with GitHub API..."
HTTP_CODE=$(curl -s -o /tmp/github_user.json -w "%{http_code}" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user 2>/dev/null)

echo "API response: HTTP ${HTTP_CODE}"

if [ "$HTTP_CODE" = "401" ]; then
    echo "ERROR: Token is invalid or expired (401 Unauthorized)"
    echo "Create a new PAT at: https://github.com/settings/tokens/new"
    rm -f /tmp/github_user.json
    exit 1
elif [ "$HTTP_CODE" = "403" ]; then
    echo "ERROR: Token is blocked or lacks permission (403 Forbidden)"
    rm -f /tmp/github_user.json
    exit 1
elif [ "$HTTP_CODE" != "200" ]; then
    echo "ERROR: Unexpected API response (HTTP ${HTTP_CODE})"
    rm -f /tmp/github_user.json
    exit 1
fi

GITHUB_LOGIN=$(python3 -c "import json; d=json.load(open('/tmp/github_user.json')); print(d.get('login','?'))" 2>/dev/null || echo "?")
echo "Authenticated as: ${GITHUB_LOGIN}"
rm -f /tmp/github_user.json

# ─── 2. Check if repo exists ───────────────────────────────────────────
echo "Checking if repository exists..."
REPO_HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}" 2>/dev/null)

if [ "$REPO_HTTP" = "404" ]; then
    echo "Repository does not exist. Creating..."
    CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"${REPO_NAME}\",\"description\":\"Governed Autonomous SDLC Factory - Cognitive Execution Runtime\",\"private\":false,\"auto_init\":false}" 2>/dev/null)
    CREATE_CODE=$(echo "$CREATE_RESPONSE" | tail -1)
    if [ "$CREATE_CODE" != "201" ]; then
        echo "ERROR: Failed to create repository (HTTP ${CREATE_CODE})"
        echo "$CREATE_RESPONSE" | head -1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('message','unknown error'))" 2>/dev/null
        exit 1
    fi
    echo "Repository created: ${REMOTE_URL}"
elif [ "$REPO_HTTP" = "200" ]; then
    echo "Repository exists: ${REMOTE_URL}"
else
    echo "WARNING: Could not check repository status (HTTP ${REPO_HTTP})"
fi

# ─── 3. Configure remote ───────────────────────────────────────────────
cd "${REPO_PATH}"
git remote remove origin 2>/dev/null || true
git remote add origin "${REMOTE_URL}"
echo "Remote configured: ${REMOTE_URL}"

# ─── 4. Push branch ────────────────────────────────────────────────────
LOCAL_HEAD=$(git rev-parse HEAD)
echo "Local HEAD: ${LOCAL_HEAD}"

echo "Pushing main branch..."
# Use token-embedded URL for push (avoids credential helper issues)
if ! git push -u "${REMOTE_URL_WITH_TOKEN}" main 2>&1; then
    echo "ERROR: Push failed"
    echo "Check: token has 'repo' scope, repo exists, no branch protection"
    exit 1
fi

# ─── 5. Push tags ──────────────────────────────────────────────────────
echo "Pushing tags..."
git push --tags "${REMOTE_URL_WITH_TOKEN}" 2>&1 || echo "WARNING: Tag push failed (non-fatal)"

# ─── 6. Verify remote parity ───────────────────────────────────────────
echo "Verifying remote parity..."
REMOTE_HEAD=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

echo "Local HEAD:  ${LOCAL_HEAD}"
echo "Remote HEAD: ${REMOTE_HEAD}"

if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
    echo "✅ Remote parity verified"
else
    echo "⚠️  Remote parity mismatch — push may have been partial"
fi

# Verify tags
LOCAL_TAG=$(git rev-parse v0.1.0-golden-integrity-runtime 2>/dev/null || echo "none")
REMOTE_TAG=$(git rev-parse origin/v0.1.0-golden-integrity-runtime 2>/dev/null || echo "none")
echo "Local tag:  ${LOCAL_TAG}"
echo "Remote tag: ${REMOTE_TAG}"

# ─── 7. Generate evidence report ───────────────────────────────────────
mkdir -p "${EVIDENCE_DIR}"
cat > "${EVIDENCE_DIR}/github-remote-parity-report.md" << EOF
# GitHub Remote Parity Report

**Date:** $(date -u +"%Y-%m-%dT%H:%M:%S+00:00")
**Status:** ✅ PUSHED

## Remote

| Field | Value |
|-------|-------|
| URL | ${REMOTE_URL} |
| User | ${GITHUB_LOGIN} |
| Repo | ${REPO_NAME} |

## Parity

| | Hash | Match? |
|-|------|--------|
| Local HEAD | ${LOCAL_HEAD} | — |
| Remote HEAD | ${REMOTE_HEAD} | $([ "$LOCAL_HEAD" = "$REMOTE_HEAD" ] && echo "✅" || echo "⚠️") |
| Local Tag | ${LOCAL_TAG} | — |
| Remote Tag | ${REMOTE_TAG} | $([ "$LOCAL_TAG" = "$REMOTE_TAG" ] && echo "✅" || echo "⚠️") |

## Commits Pushed

$(git log --oneline -15)

## Tags Pushed

$(git tag --list)
EOF

echo "Evidence report: ${EVIDENCE_DIR}/github-remote-parity-report.md"

# ─── 8. Summary ────────────────────────────────────────────────────────
echo ""
echo "=== GitHub Setup Complete ==="
echo "Repository: ${REMOTE_URL}"
echo "Local HEAD: ${LOCAL_HEAD}"
echo "Remote HEAD: ${REMOTE_HEAD}"
echo "Parity: $([ "$LOCAL_HEAD" = "$REMOTE_HEAD" ] && echo "✅ VERIFIED" || echo "⚠️ MISMATCH")"
echo ""
echo "View at: https://github.com/${GITHUB_USER}/${REPO_NAME}"
