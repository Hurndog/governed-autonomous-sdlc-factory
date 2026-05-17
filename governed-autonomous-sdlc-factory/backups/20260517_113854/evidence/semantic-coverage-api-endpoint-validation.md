# Semantic Coverage API Endpoint Validation

**Date:** 2026-05-16
**Phase:** J — API Endpoint Validation

## All 12 Endpoints Validated ✅

| # | Method | Path | Status | Response |
|---|---|---|---|---|
| 1 | GET | /summary | 200 | score=0.6772 |
| 2 | GET | /requirements | 200 | total=6 |
| 3 | GET | /acceptance-criteria | 200 | total=6 |
| 4 | GET | /test-obligations | 200 | total=10 |
| 5 | GET | /alignment | 200 | total=13 |
| 6 | GET | /verifier-critiques | 200 | total=13 |
| 7 | GET | /mutations | 200 | total=25, killed=0, survived=0 |
| 8 | GET | /negative-coverage | 200 | total=6 |
| 9 | GET | /runtime-evidence | 200 | total=1, bound=1 |
| 10 | GET | /report | 200 | overall=0.6772, gate=fail |
| 11 | POST | /evaluate | 200 | status=evaluated, score=0.6772 |
| 12 | POST | /waivers | 200 | waiver creation works |

## Legacy Run Behavior

For a non-existent run (00000000-...):
- GET /summary returns: `{"status": "pre_semantic_coverage", "message": "..."}`
- Never returns fake pass

## OpenAPI

All 12 endpoints visible in `/openapi.json` under tag `semantic-coverage`.

## Status: COMPLETE ✅
