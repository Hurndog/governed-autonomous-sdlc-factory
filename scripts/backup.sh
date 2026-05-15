#!/bin/bash
# Automated Backup Script for Governed Autonomous SDLC Factory
# Run via cron: 0 */6 * * * /path/to/backup.sh

set -e

REPO_PATH="/Users/marcovanhurne/governed-autonomous-sdlc-factory"
BACKUP_DIR="${REPO_PATH}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"

echo "=== Backup: ${TIMESTAMP} ==="

mkdir -p "${BACKUP_PATH}"

# 1. Git bundle (full repo backup)
echo "Creating git bundle..."
cd "${REPO_PATH}"
git bundle create "${BACKUP_PATH}/repo.bundle" --all 2>/dev/null || echo "Bundle failed"

# 2. Database dump
echo "Creating database dump..."
docker exec governed-autonomous-sdlc-factory-postgres-1 pg_dump -U governance sdlc_factory > "${BACKUP_PATH}/database.sql" 2>/dev/null || echo "DB dump failed"

# 3. Evidence directory
echo "Backing up evidence..."
if [ -d "${REPO_PATH}/evidence" ]; then
    cp -r "${REPO_PATH}/evidence" "${BACKUP_PATH}/evidence"
fi

# 4. Runtime manifests
echo "Backing up runtime manifests..."
cp "${REPO_PATH}/runtime/"*.json "${BACKUP_PATH}/" 2>/dev/null || true
cp "${REPO_PATH}/EXECUTIVE_RUNTIME_STATUS.md" "${BACKUP_PATH}/" 2>/dev/null || true
cp "${REPO_PATH}/SESSION_RECOVERY_MANIFEST.md" "${BACKUP_PATH}/" 2>/dev/null || true

# 5. Config files
echo "Backing up config..."
cp "${REPO_PATH}/.env" "${BACKUP_PATH}/.env" 2>/dev/null || true
cp "${REPO_PATH}/docker-compose.yml" "${BACKUP_PATH}/" 2>/dev/null || true

# 6. Checksums
echo "Generating checksums..."
cd "${BACKUP_PATH}"
find . -type f -exec sha256sum {} \; > checksums.sha256

# 7. Backup manifest
cat > "${BACKUP_PATH}/manifest.json" << EOF
{
  "timestamp": "${TIMESTAMP}",
  "repo_path": "${REPO_PATH}",
  "git_commit": "$(cd ${REPO_PATH} && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(cd ${REPO_PATH} && git branch --show-current 2>/dev/null || echo 'unknown')",
  "files": $(find . -type f | wc -l),
  "size_bytes": $(du -sk . | awk '{print $1 * 1024}')
}
EOF

# 8. Cleanup old backups (keep last 10)
echo "Cleaning old backups..."
cd "${BACKUP_DIR}"
ls -1d */ | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true

echo "=== Backup Complete: ${BACKUP_PATH} ==="
echo "Size: $(du -sh ${BACKUP_PATH} | awk '{print $1}')"
