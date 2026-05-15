#!/bin/bash
# GitHub Operationalization Script
# Run this after setting GITHUB_TOKEN environment variable

set -e

REPO_NAME="governed-autonomous-sdlc-factory"
REPO_PATH="/Users/marcovanhurne/governed-autonomous-sdlc-factory"
GITHUB_USER="Hurndog"

echo "=== GitHub Operationalization ==="

# Check for token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable not set"
    echo "Set it with: export GITHUB_TOKEN=ghp_xxxxxxxxxxxx"
    exit 1
fi

# Configure git credentials
git config --global credential.helper store
echo "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials

# Create GitHub repository (if it doesn't exist)
echo "Creating GitHub repository..."
curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\": \"${REPO_NAME}\", \"description\": \"Governed Autonomous SDLC Factory - Cognitive Execution Runtime\", \"private\": false, \"auto_init\": false}" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('full_name', d.get('message', 'unknown')))" 2>/dev/null || echo "Repo may already exist"

# Add remote
cd "${REPO_PATH}"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

# Push all branches
echo "Push main branch..."
git push -u origin main --force

# Push tags
echo "Push tags..."
git push --tags 2>/dev/null || echo "No tags to push"

# Verify
echo "Verifying remote..."
git remote -v
git log --oneline -3

echo "=== GitHub Operationalization Complete ==="
echo "Repository: https://github.com/${GITHUB_USER}/${REPO_NAME}"
