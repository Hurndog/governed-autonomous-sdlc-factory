#!/bin/bash
# Automated Backup Script
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$REPO_DIR/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=== Cognitive Cortex Backup ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Backup dir: $BACKUP_DIR"

# Git bundle
echo "→ Creating git bundle..."
cd "$REPO_DIR"
git bundle create "$BACKUP_DIR/repo.bundle" --all 2>/dev/null || echo "  Warning: git bundle failed"

# Database dump
echo "→ Dumping database..."
docker exec governed-autonomous-sdlc-factory-postgres-1 pg_dump -U governance sdlc_factory 2>/dev/null | gzip > "$BACKUP_DIR/db.sql.gz" || echo "  Warning: DB dump failed"

# Evidence
echo "→ Copying evidence..."
cp -r "$REPO_DIR/evidence" "$BACKUP_DIR/evidence" 2>/dev/null || true

# Runtime manifests
echo "→ Copying runtime manifests..."
cp -r "$REPO_DIR/runtime" "$BACKUP_DIR/runtime" 2>/dev/null || true
cp "$REPO_DIR/SESSION_RECOVERY_MANIFEST.md" "$BACKUP_DIR/" 2>/dev/null || true

# Checksums
echo "→ Generating checksums..."
cd "$BACKUP_DIR"
find . -type f -exec sha256sum {} \; > checksums.sha256 2>/dev/null || true

# Size
SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo "=== Backup Complete ==="
echo "Size: $SIZE"
echo "Location: $BACKUP_DIR"
