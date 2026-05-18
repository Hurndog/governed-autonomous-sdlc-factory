# Traceability Pipeline Diagnosis

**Date:** 2026-05-16  
**Status:** ❌ NOT PERSISTED

---

## Current State

### What Exists
- `TraceabilityManager` class in `apps/api/src/engines/traceability.py` — fully implemented with `link()`, `get_chain()`, `get_full_chain()`, `validate_coverage()` methods
- `TraceabilityLink` model in `apps/api/src/models.py` — complete with `run_id`, `source_type`, `source_id`, `target_type`, `target_id`, `link_type`, `edge_hash`
- `traceability_links` table in database
- API endpoints for traceability in `apps/api/src/api/v1/endpoints/engines.py`

### What's Missing
1. **TraceabilityManager is imported but NEVER called** in `full_pipeline_orchestrator.py`
2. **No TraceabilityLink records are created** during pipeline execution
3. **No links between requirements, architecture, tests, or governance** are persisted
4. **Requirement IDs from spec are not propagated** to architecture, test, or governance engines
5. **No phase-to-artifact links** are created

### Engine-by-Engine Analysis

#### Specification Engine
- Generates `functional_requirements` with stable IDs (FR-001, FR-002, ...)
- Generates `acceptance_criteria` with `requirement_id` references
- Generates `governance_sensitive_areas`
- **Does NOT create TraceabilityLink records**

#### Architecture Engine
- Generates `component_breakdown` with component names
- Generates `adrs` (architecture decision records)
- **Does NOT link components back to requirements**
- **Does NOT create TraceabilityLink records**

#### Test Plan Engine
- Generates `test_cases` with test case data
- **Does NOT link test cases back to requirements**
- **Does NOT create TraceabilityLink records**

#### Governance Engine
- Generates `runtime_governance_concerns`, `security_sensitive_findings`, `compliance_gaps`
- **Does NOT link findings back to requirements**
- **Does NOT create TraceabilityLink records**
- **Does NOT create GovernanceEvaluation records**

### Integrity Verification Gap
- `IntegrityManager.verify_traceability_integrity()` queries `TraceabilityLink` table
- Table is empty → score = 0.0

### Stable ID Analysis
- Requirement IDs: ✅ Stable (FR-001, FR-002, ... from LLM)
- Acceptance Criteria IDs: ✅ Stable (AC-001, AC-002, ... with `requirement_id` reference)
- Architecture Component IDs: ⚠️ Names only, no stable IDs
- Test Case IDs: ⚠️ Names only, no stable requirement references
- Governance Concern IDs: ✅ Stable (RGC-001, SSF-001, CG-001, ...)

### Conclusion
The traceability infrastructure (manager, model, table, endpoints) exists but is completely disconnected from the pipeline. The pipeline needs to be extended to create traceability links after each generation phase.
