# Frontend Existing Endpoint Reuse Audit

**Date:** 2026-05-17
**Phase:** 1 — Existing Endpoint Reuse Audit

## Backend Endpoint Inventory

### Cost Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/costs/report/{run_id}` | GET | total_cost, budget_limit, by_phase, by_agent, by_model, local/paid split |
| `/costs/events/{run_id}` | GET | individual cost events with model, provider, tokens, cost, latency |

### Agent Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/agents/` | GET | agent list with name, role, model_preference, is_active |
| `/agents/{agent_id}` | GET | single agent detail |

### Phase Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/phases/by-run/{run_id}` | GET | phases with name, status, order_index, agent_id, model_used, tokens, cost |
| `/phases/{phase_id}` | GET | single phase detail |
| `/phases/{phase_id}/complete` | POST | mark phase complete |
| `/phases/{phase_id}/fail` | POST | mark phase failed |

### Task Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/tasks/by-phase/{phase_id}` | GET | tasks with name, description, requirement_ids, acceptance_criteria_ids, test_ids, governance_check_ids |

### Engine Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/engines/specification/{run_id}` | GET | spec versions list |
| `/engines/specification/{run_id}/latest` | GET | requirements_yaml, functional_spec, acceptance_criteria, non_functional_requirements, assumptions |
| `/engines/architecture/{run_id}` | GET | architecture versions list |
| `/engines/architecture/{run_id}/latest` | GET | architecture_yaml, architecture_md, mermaid_diagrams, adrs, constraints, fitness_functions |
| `/engines/test-plan/{run_id}` | GET | test plan versions |
| `/engines/test-plan/{run_id}/latest` | GET | unit_test_strategy, integration_test_strategy, api_contract_tests, edge_cases, smoke_tests, governance_tests, traceability_map |
| `/engines/governance/evaluations/{run_id}` | GET | governance evaluations with decision, findings |
| `/engines/governance/policies` | GET | governance policies |

### Semantic Coverage Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/semantic-coverage/runs/{run_id}/summary` | GET | overall scores, release_gate_status |
| `/semantic-coverage/runs/{run_id}/requirements` | GET | normalized requirements with criticality, testability |
| `/semantic-coverage/runs/{run_id}/acceptance-criteria` | GET | acceptance criteria contracts |
| `/semantic-coverage/runs/{run_id}/test-obligations` | GET | test obligations with status |
| `/semantic-coverage/runs/{run_id}/alignment` | GET | semantic alignment evaluations |
| `/semantic-coverage/runs/{run_id}/verifier-critiques` | GET | verifier critiques with verdict, confidence |
| `/semantic-coverage/runs/{run_id}/mutations` | GET | mutation tests: killed, survived, mutation_type |
| `/semantic-coverage/runs/{run_id}/negative-coverage` | GET | negative test requirements with status |
| `/semantic-coverage/runs/{run_id}/runtime-evidence` | GET | runtime evidence bindings |
| `/semantic-coverage/runs/{run_id}/report` | GET | full report with all scores |

### Pipeline Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/pipeline/runs/{run_id}/timeline` | GET | chronological events with timestamp, severity, message, phase |
| `/pipeline/runs/{run_id}/snapshot` | GET | latest snapshot with phase_states, artifact_states, cost_summary, governance_summary |
| `/pipeline/runs/{run_id}/semantic-graph` | GET | nodes and edges for semantic execution graph |
| `/pipeline/runs/{run_id}/integrity` | GET | integrity verification |
| `/pipeline/runs/{run_id}/divergence` | GET | divergence records |

### Memory Endpoints
| Endpoint | Method | Data |
|---|---|---|
| `/memory/search` | GET | memory items by query |
| `/memory/by-project/{project_id}` | GET | memory items by project |

## Screen Upgrade Analysis

### Spec Room (currently PARTIAL → LIVE)
- **Endpoints:** `/engines/specification/{run_id}/latest`, `/semantic-coverage/runs/{run_id}/requirements`, `/semantic-coverage/runs/{run_id}/acceptance-criteria`, `/artifacts/by-run/{run_id}`
- **Can show:** functional requirements, non-functional requirements, acceptance criteria, governance areas, requirement IDs, linked semantic coverage, linked artifacts
- **Status after pass:** LIVE — all primary data available from backend

### Tokenomics (currently MOCK → PARTIAL)
- **Endpoints:** `/costs/report/{run_id}`, `/costs/events/{run_id}`
- **Can show:** total tokens per run, tokens by phase, tokens by model, tokens by provider, cost events, budget status
- **Missing:** per-agent token breakdown (agent_id in cost events exists but may be null), retry waste inference
- **Status after pass:** PARTIAL — real cost/token data available, some aggregation done frontend-side

### Build Map (currently MOCK → PARTIAL)
- **Endpoints:** `/engines/architecture/{run_id}/latest`, `/pipeline/runs/{run_id}/semantic-graph`, `/artifacts/by-run/{run_id}`
- **Can show:** components from architecture_yaml, ADRs, Mermaid diagrams, architecture constraints, semantic graph nodes/edges
- **Missing:** structured component topology (YAML needs parsing), infrastructure nodes
- **Status after pass:** PARTIAL — real architecture artifacts available, parsing needed

### SDLC Navigator (currently MOCK → PARTIAL)
- **Endpoints:** `/phases/by-run/{run_id}`, `/pipeline/runs/{run_id}/timeline`, `/tasks/by-phase/{phase_id}`
- **Can show:** phase names, status, order, model_used, artifacts per phase, events per phase
- **Missing:** structured swimlane visualization data
- **Status after pass:** PARTIAL — real phase and event data available

### Process Timeline (currently MOCK → PARTIAL)
- **Endpoints:** `/pipeline/runs/{run_id}/timeline`, `/phases/by-run/{run_id}`, `/costs/events/{run_id}`
- **Can show:** chronological events, phase transitions, cost events, governance moments
- **Missing:** structured swimlane layout
- **Status after pass:** PARTIAL — real timeline events available

### Agent Command (currently MOCK → PARTIAL)
- **Endpoints:** `/agents/`, `/phases/by-run/{run_id}`, `/costs/events/{run_id}`, `/logs/`
- **Can show:** agent list, model/provider per phase, latency, errors from logs, cost per agent
- **Missing:** real-time agent activity stream, explicit agent state
- **Status after pass:** PARTIAL — agent list + phase/agent cost data available

### Backlog Checklist (currently MOCK → PARTIAL)
- **Endpoints:** `/semantic-coverage/runs/{run_id}/requirements`, `/semantic-coverage/runs/{run_id}/test-obligations`, `/engines/test-plan/{run_id}/latest`, `/tasks/by-phase/{phase_id}`
- **Can show:** requirements, test obligations, test plan items, task links
- **Missing:** product-management fields (priority, story points)
- **Status after pass:** PARTIAL — real requirement/obligation data available

### Executive Cockpit (currently MOCK → PARTIAL)
- **Endpoints:** `/pipeline/runs/{run_id}/snapshot`, `/semantic-coverage/runs/{run_id}/summary`, `/engines/governance/evaluations/{run_id}`, `/costs/report/{run_id}`, `/artifacts/by-run/{run_id}`, `/evidence/by-run/{run_id}`
- **Can show:** latest run status, integrity score, semantic coverage score, release gate status, artifact count, evidence count, governance findings, token usage
- **Missing:** dedicated aggregate endpoint (all computed frontend-side)
- **Status after pass:** PARTIAL — all data available from multiple endpoints, aggregated in frontend

### Mutation Testing (currently not integrated → PARTIAL)
- **Endpoints:** `/semantic-coverage/runs/{run_id}/mutations`, `/semantic-coverage/runs/{run_id}/verifier-critiques`, `/semantic-coverage/runs/{run_id}/negative-coverage`, `/semantic-coverage/runs/{run_id}/runtime-evidence`
- **Can show:** mutation test count, survived/killed, verifier critique summary, negative test status, runtime evidence binding
- **Status after pass:** PARTIAL — integrate into Semantic Coverage screen
