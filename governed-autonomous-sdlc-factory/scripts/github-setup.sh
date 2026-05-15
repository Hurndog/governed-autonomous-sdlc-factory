#!/bin/bash
# GitHub Operationalization Script
# Run: GITHUB_TOKEN=ghp_xxx bash scripts/github-setup.sh

set -e

REPO_NAME="governed-autonomous-sdlc-factory"
REPO_DESC="Governed Autonomous SDLC Factory — Cognitive Execution Layer with Replay, Integrity, Governance"
VISIBILITY="${1:-private}"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "ERROR: GITHUB_TOKEN not set"
  echo "Usage: GITHUB_TOKEN=ghp_xxx bash scripts/github-setup.sh [private|public]"
  exit 1
fi

echo "=== GitHub Operationalization ==="
echo "Token: ${GITHUB_TOKEN:0:8}..."
echo "Repo: $REPO_NAME"
echo "Visibility: $VISIBILITY"

# Create repo via API
echo "→ Creating repository..."
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESC\",\"private\":$VISIBILITY == \"private\",\"auto_init\":false}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Created: {d.get(\"html_url\",\"ERROR\")}')" 2>/dev/null || echo "  May already exist, continuing..."

# Configure remote
echo "→ Configuring remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://Hurndog:${GITHUB_TOKEN}@github.com/Hurndog/${REPO_NAME}.git"

# Push all branches
echo "→ Pushing main..."
git push -u origin main --force

# Create branches
echo "→ Creating branches..."
git checkout -b develop 2>/dev/null || git checkout develop
git push -u origin develop --force

git checkout -b recovery/baseline 2>/dev/null || git checkout recovery/baseline
git push -u origin recovery/baseline --force

git checkout -b replay/hardening 2>/dev/null || git checkout replay/hardening
git push -u origin replay/hardening --force

# Back to main
git checkout main

# Create tags
echo "→ Creating tags..."
git tag -f first-operational-slice -m "First operational vertical slice — Ollama integration + golden baseline"
git tag -f replay-runtime-stable -m "Replay runtime — deterministic, integrity score 1.0"
git tag -f cognitive-execution-enabled -m "Cognitive execution — ModelRouter + real AI engines"
git tag -f first-real-spec-generation -m "First real AI-generated specification via Ollama gpt-oss:20b"
git tag -f frontend-command-center -m "Cognitive Command Center — 5 rooms + WebSocket + dark ops UI"
git push origin --tags --force

echo ""
echo "=== GitHub Operationalization Complete ==="
echo "Repository: https://github.com/Hurndog/$REPO_NAME"
echo "Branches: main, develop, recovery/baseline, replay/hardening"
echo "Tags: first-operational-slice, replay-runtime-stable, cognitive-execution-enabled, first-real-spec-generation, frontend-command-center"
