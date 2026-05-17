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
