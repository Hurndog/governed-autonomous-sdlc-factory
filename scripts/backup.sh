#!/bin/bash
# Hardened Backup Script for Governed Autonomous SDLC Factory
# Usage: bash scripts/backup.sh

set -euo pipefail

REPO_PATH="/Users/marcovanhurne/governed-autonomous-sdlc-factory"
BACKUP_DIR="${REPO_PATH}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"

echo "=== Backup: ${TIMESTAMP} ==="

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# 1. Git bundle (full repo backup)
echo "Creating git bundle..."
cd "${REPO_PATH}"
if ! git bundle create "${BACKUP_PATH}/repo.bundle" --all 2>&1; then
    echo "ERROR: git bundle creation failed"
    exit 1
fi

# Verify bundle immediately
echo "Verifying git bundle..."
if ! git bundle verify "${BACKUP_PATH}/repo.bundle" 2>&1; then
    echo "ERROR: git bundle verification failed"
    exit 1
fi

# 2. Database dump (if pg_dump available)
echo "Creating database dump..."
if command -v pg_dump &>/dev/null; then
    PGPASSWORD=forge pg_dump -h localhost -p 5432 -U governance -d sdlc_factory --no-owner --no-privileges > "${BACKUP_PATH}/database.sql" 2>/dev/null || echo "WARNING: DB dump failed (non-fatal)"
else
    echo "WARNING: pg_dump not found, skipping DB dump"
fi

# 3. Evidence directory
echo "Backing up evidence..."
if [ -d "${REPO_PATH}/evidence" ]; then
    cp -r "${REPO_PATH}/evidence" "${BACKUP_PATH}/evidence"
fi

# 4. Runtime manifests
echo "Backing up runtime manifests..."
cp "${REPO_PATH}/runtime/"*.json "${BACKUP_PATH}/" 2>/dev/null || true
cp "${REPO_PATH}/SESSION_RECOVERY_MANIFEST.md" "${BACKUP_PATH}/" 2>/dev/null || true
cp "${REPO_PATH}/EXECUTIVE_RUNTIME_STATUS.md" "${BACKUP_PATH}/" 2>/dev/null || true

# 5. Config files (never include secrets)
echo "Backing up config..."
cp "${REPO_PATH}/docker-compose.yml" "${BACKUP_PATH}/" 2>/dev/null || true

# 6. Checksums (always fresh)
echo "Generating fresh checksums..."
cd "${BACKUP_PATH}"
rm -f checksums.sha256
find . -type f ! -name "checksums.sha256" -exec shasum -a 256 {} \; > checksums.sha256

# 7. Backup manifest
cat > "${BACKUP_PATH}/manifest.json" << EOF
{
  "timestamp": "${TIMESTAMP}",
  "repo_path": "${REPO_PATH}",
  "git_commit": "$(cd ${REPO_PATH} && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(cd ${REPO_PATH} && git branch --show-current 2>/dev/null || echo 'unknown')",
  "git_tags": "$(cd ${REPO_PATH} && git tag --points-at HEAD 2>/dev/null || echo 'none')",
  "bundle_verified": true,
  "files": $(find . -type f | wc -l),
  "size_bytes": $(du -sk . | awk '{print $1 * 1024}')
}
EOF

# 8. Restore instructions
cat > "${BACKUP_PATH}/RESTORE.md" << 'RESTORE_EOF'
# Restore Instructions

## From Git Bundle
```bash
git clone /path/to/backup/repo.bundle restored-repo
cd restored-repo
git checkout main
```

## From Database Dump
```bash
PGPASSWORD=forge psql -h localhost -p 5432 -U governance -d sdlc_factory < database.sql
```

## Verify Integrity
```bash
cd restored-repo
git log --oneline -5
git tag --list
git bundle verify repo.bundle
shasum -a 256 repo.bundle  # compare with checksums.sha256
```
RESTORE_EOF

# 9. Cleanup old backups (keep last 10)
echo "Cleaning old backups..."
cd "${BACKUP_DIR}"
ls -1d */ 2>/dev/null | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true

# 10. Final verification
echo "=== Backup Verification ==="
echo "Bundle: $(shasum -a 256 ${BACKUP_PATH}/repo.bundle | awk '{print $1}')"
echo "Files: $(find ${BACKUP_PATH} -type f | wc -l)"
echo "Size: $(du -sh ${BACKUP_PATH} | awk '{print $1}')"
echo "HEAD: $(cd ${REPO_PATH} && git rev-parse HEAD)"
echo "Tags: $(cd ${REPO_PATH} && git tag --points-at HEAD)"

echo "=== Backup Complete: ${BACKUP_PATH} ==="
