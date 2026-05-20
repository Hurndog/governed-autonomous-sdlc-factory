# Governance Documentation

## Governance Framework

The governance framework enforces policies across all runtime operations. It is built on three pillars:

1. **Policy Definition** — OPA Rego policies define what is allowed
2. **Policy Evaluation** — Every action is evaluated against policies
3. **Policy Enforcement** — Violations are blocked with reasoning

## Policy Structure

Policies are defined in OPA Rego format:

```rego
package governance

# Deny actions that violate sovereignty constraints
deny[msg] {
    input.sovereignty_requirement == "local_only"
    input.selected_provider != "ollama"
    msg := sprintf("Local-only sovereignty requires Ollama, got %s", [input.selected_provider])
}

# Deny actions when trust is below threshold
deny[msg] {
    input.trust_score < input.trust_threshold
    msg := sprintf("Trust score %f below threshold %f", [input.trust_score, input.trust_threshold])
}

# Deny actions that exceed cost budget
deny[msg] {
    input.estimated_cost > input.cost_budget
    msg := sprintf("Cost %f exceeds budget %f", [input.estimated_cost, input.cost_budget])
}

# Deny actions with high hallucination risk for sensitive tasks
deny[msg] {
    input.task_type == "governance_analysis"
    input.hallucination_risk > 0.1
    msg := sprintf("Hallucination risk %f too high for governance analysis", [input.hallucination_risk])
}
```

## Governance Dimensions

### Trust Governance

Trust scores govern autonomy levels. The system automatically adjusts autonomy based on trust:

- **High trust (0.9+)**: Full autonomy, minimal oversight
- **Medium trust (0.5-0.9)**: Moderate autonomy, approval for significant decisions
- **Low trust (0.3-0.5)**: Low autonomy, approval for all decisions
- **Critical trust (0.0-0.3)**: Minimal autonomy, human-in-the-loop

### Sovereignty Governance

Sovereignty constraints govern where cognition happens:

- **local_only**: All processing on-premises, no external APIs
- **sovereign_preferred**: Prefer local, use frontier when necessary
- **sovereign_required**: Require local, fallback with approval
- **hybrid**: Arbitrate between local and frontier
- **frontier_only**: Use most capable models regardless of location

### Cost Governance

Cost controls prevent budget overruns:

- **Warning threshold**: Alert at 80% of budget
- **Hard limit**: Block at 100% of budget
- **Per-run limits**: Maximum cost per run
- **Per-phase limits**: Maximum cost per phase
- **Daily limits**: Maximum cost per day

### Quality Governance

Quality gates ensure output meets standards:

- **Semantic coverage threshold**: Minimum semantic completeness score
- **Integrity score threshold**: Minimum seven-component integrity score
- **Hallucination tolerance**: Maximum acceptable hallucination rate
- **Replay stability threshold**: Minimum replay verification score

## Governance Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Action Requested                           │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  1. RBAC Check                                                │
│     Does the actor have permission?                           │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Trust Check                                               │
│     Is the trust score sufficient for this action?            │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Policy Evaluation (OPA Rego)                              │
│     Does the action comply with all policies?                 │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Sovereignty Check                                         │
│     Does the selected model comply with sovereignty?          │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Cost Check                                                │
│     Is the estimated cost within budget?                      │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Execute (if all checks pass)                              │
│     Capture evidence, update trust, record audit trail        │
└──────────────────────────────────────────────────────────────┘
```

## Audit Trail

Every governance decision is recorded in the immutable audit trail:

```json
{
  "timestamp": "2026-05-19T12:00:00.000Z",
  "actor": "user-uuid",
  "action": "governance.evaluate",
  "target": "run-uuid",
  "decision": "allow",
  "reasoning": "All governance checks passed",
  "checks": {
    "rbac": "pass",
    "trust": "pass (0.85)",
    "policy": "pass (0 violations)",
    "sovereignty": "pass (local)",
    "cost": "pass ($2.30 of $50.00)"
  },
  "hash_chain": "sha256"
}
```
