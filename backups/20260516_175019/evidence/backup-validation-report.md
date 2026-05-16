# Backup Validation Report

**Backup ID:** 20260516_154820
**Date:** 2026-05-16T15:48:20
**Status:** ✅ VALIDATED

---

## Backup Contents

| File | Size | SHA256 |
|------|------|--------|
| `repo.bundle` | 2.1MB | `494bbce34840f91dd7b3f874882855e25983bddd7c040f0269f5f5b1e119058a` |
| `database_dump.json` | 1.5MB | `b96b6ca58e2fc363eaf2b5f7817ca2a3ff77115808f944b229c27499370c73d0` |
| `database.sql` | 195KB | `195886726ad911e0a8bdf5611fed0e213302319c29aa390884ce41ae532b5e7b` |
| `evidence/` | 16 files | (see checksums.sha256) |
| `SESSION_RECOVERY_MANIFEST.md` | 4.1KB | `610ddd07d413f9c533237d2dc6c2c27cfe3a654554e4d8f38abd8f994d0dc1a9` |
| `EXECUTIVE_RUNTIME_STATUS.md` | 13.6KB | `75248f9d1cc93cbd761f328132db7651e001274ff63f3fef3da23005d019ce85` |
| `environment-discovery.json` | 3.7KB | `f9af0336e81ee2232b96f9a68e9497991317ee4524a052e0f31a52b63e0e7791` |
| `model-registry.json` | 2.4KB | `d7d627f4c2d2f640179e97a5e84acb59267d969eb83bb805fe3ad0cf9ce7fa28` |
| `checksums.sha256` | 1.4KB | `06dd2d21acc5d3a5d0828330ecbcc49fa79b511774bc12663fc57cda2b943e27` |

## Database Dump Summary

| Table | Rows |
|-------|------|
| agents | 18 |
| artifacts | 365 |
| governance_evaluations | 80 |
| governance_policies | 10 |
| governance_release_gates | 1 |
| integrity_verifications | 86 |
| log_events | 957 |
| replay_events | 1059 |
| replay_manifests | 3 |
| replay_sessions | 9 |
| runs | 23 |
| run_snapshots | 10 |
| traceability_links | 367 |
| projects | 5 |
| system_settings | 8 |
| test_plans | 2 |
| architecture_versions | 7 |
| artifact_baselines | 7 |
| specification_versions | 7 |

## Validation Checks

| Check | Status |
|-------|--------|
| Git bundle created | ✅ |
| Git bundle valid (`git bundle verify`) | ✅ |
| Database dump created | ✅ |
| Evidence reports included | ✅ (16 files) |
| Recovery manifest included | ✅ |
| Runtime state included | ✅ |
| Config files included | ✅ |
| Checksums generated | ✅ |
| Total backup size | 5.7MB |
| Total files | 22 |

## Restore Instructions

### From Git Bundle
```bash
git clone /path/to/backups/20260516_154820/repo.bundle restored-repo
cd restored-repo
git checkout main
```

### From Database Dump (JSON)
```bash
cd restored-repo/governed-autonomous-sdlc-factory
python3 -c "
import asyncio, json, asyncpg
async def restore():
    conn = await asyncpg.connect('postgresql://governance:forge@localhost:5432/sdlc_factory')
    with open('/path/to/backups/20260516_154820/database_dump.json') as f:
        dump = json.load(f)
    for table, rows in dump.items():
        if rows:
            cols = list(rows[0].keys())
            values = [tuple(r.get(c) for c in cols) for r in rows]
            await conn.execute(f'TRUNCATE {table} CASCADE')
            await conn.copy_records_to_table(table, records=values, columns=cols)
            print(f'Restored {len(rows)} rows to {table}')
    await conn.close()
asyncio.run(restore())
"
```

---

**Validated by:** OWL (Hermes Agent)
**Validated at:** 2026-05-16T15:48:20
