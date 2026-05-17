export interface RuntimeHealth {
  status: string;
  uptime_seconds: number;
  version: string;
  database: string;
  redis: string;
}

export interface RunItem {
  id: string;
  project_id?: string;
  status: string;
  intent?: string;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  model_provider?: string;
  model_name?: string;
  budget_limit?: number;
  cost_usd?: number;
  event_count?: number;
  artifact_count?: number;
  integrity_score?: number;
}

export interface RunDetail {
  id: string;
  project_id?: string;
  status: string;
  intent?: string;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  model_provider?: string;
  model_name?: string;
  budget_limit?: number;
  cost_usd?: number;
  metadata?: Record<string, unknown>;
}

export interface RunStatus {
  id: string;
  status: string;
  phase?: string;
  progress?: number;
  event_count?: number;
  artifact_count?: number;
  cost_usd?: number;
  started_at?: string;
  updated_at?: string;
}

export interface TimelineEvent {
  id: string;
  sequence: number;
  type: string;
  timestamp: string;
  phase?: string;
  agent_id?: string;
  data?: Record<string, unknown>;
  hash?: string;
  previous_hash?: string;
}

export interface IntegrityResponse {
  run_id: string;
  integrity_score: number;
  status: 'pass' | 'warn' | 'fail';
  checks: number;
  passed: number;
  failed: number;
  warnings: number;
  report: {
    run_id: string;
    overall_score: number;
    total_checks: number;
    passed_checks: number;
    failed_checks: number;
    warning_checks: number;
    generated_at: string;
    results: Record<string, IntegrityComponent>;
    duration_ms?: number;
  };
  duration_ms?: number;
}

export interface IntegrityComponent {
  status: 'pass' | 'warn' | 'fail';
  score: number;
  details: Record<string, unknown>;
}

export interface TraceabilityLink {
  id: string;
  run_id: string;
  source_type: string;
  source_id: string;
  target_type: string;
  target_id: string;
  link_type: string;
  confidence?: number;
  rationale?: string;
  edge_hash?: string;
  created_at?: string;
}

export interface GovernanceEvaluation {
  id: string;
  run_id: string;
  policy_id: string;
  policy_name?: string;
  status: 'pass' | 'warn' | 'fail';
  severity: 'critical' | 'warning' | 'info';
  findings: Array<{ type: string; message: string; requirement_id?: string; artifact_id?: string }>;
  input_data?: Record<string, unknown>;
  integrity_hash?: string;
  created_at?: string;
}

export interface GovernancePolicy {
  id: string;
  name: string;
  description?: string;
  category: string;
  severity: string;
  active: boolean;
  created_at?: string;
}

export interface ReleaseGate {
  gate_id?: string;
  run_id: string;
  name?: string;
  status: 'open' | 'passed' | 'failed' | 'waived';
  decision?: string;
  blocking_findings?: string[];
  waiver_reason?: string;
  created_at?: string;
  evaluated_at?: string;
}

export interface ArtifactItem {
  id: string;
  run_id: string;
  type: string;
  name: string;
  phase?: string;
  hash?: string;
  size_bytes?: number;
  metadata?: Record<string, unknown>;
  created_at?: string;
  locked?: boolean;
}

export interface ArtifactDetail extends ArtifactItem {
  content?: string;
}

export interface ReplaySession {
  id: string;
  run_id: string;
  status: string;
  event_count?: number;
  divergence_count?: number;
  integrity_preserved?: boolean;
  integrity_score?: number;
  events?: ReplayEvent[];
  created_at?: string;
}

export interface ReplayEvent {
  id: string;
  sequence: number;
  type: string;
  timestamp: string;
  data: Record<string, unknown>;
  hash: string;
  semantic_transition?: string;
  divergence?: boolean;
}

export interface ModelInfo {
  name: string;
  available: boolean;
  size?: string;
}

export interface ProviderStatus {
  name: string;
  base_url: string;
  models: ModelInfo[];
  default_model?: string;
  is_local: boolean;
  status: 'online' | 'offline' | 'error';
}

export interface ModelStatusResponse {
  providers: ProviderStatus[];
  routing_policy: Record<string, string>;
  default_provider: string;
  default_model: string;
}

export interface LogEntry {
  id: string;
  run_id?: string;
  phase_id?: string;
  agent_id?: string;
  severity: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

export interface CostEvent {
  id: string;
  run_id: string;
  provider: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  timestamp: string;
}

export interface CostReport {
  run_id: string;
  total_tokens: number;
  total_cost_usd: number;
  by_provider: Record<string, { tokens: number; cost_usd: number }>;
  by_model: Record<string, { tokens: number; cost_usd: number }>;
}

export interface EvidenceBundle {
  id: string;
  run_id: string;
  file_count?: number;
  size_bytes?: number;
  created_at?: string;
}

export interface ProjectItem {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectDetail extends ProjectItem {
  run_count?: number;
}

export interface SnapshotItem {
  id: string;
  run_id: string;
  snapshot_type: string;
  created_at: string;
  hash?: string;
  data?: Record<string, unknown>;
}

export interface DivergenceItem {
  id: string;
  replay_session_id: string;
  event_id: string;
  type: string;
  description: string;
  severity: string;
  original_data?: Record<string, unknown>;
  replay_data?: Record<string, unknown>;
  created_at: string;
}

export interface SpecificationItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface SpecificationDetail extends SpecificationItem {
  content?: string;
  functional_requirements?: string[];
  non_functional_requirements?: string[];
  acceptance_criteria?: string[];
  governance_areas?: string[];
  inference_trace_id?: string;
}

export interface ArchitectureItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface ArchitectureDetail extends ArchitectureItem {
  content?: string;
  components?: Array<{ id: string; name: string; type: string; dependencies?: string[] }>;
  decisions?: Array<{ id: string; title: string; context: string; decision: string; status: string }>;
  mermaid_diagram?: string;
}

export interface TestPlanItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface TestPlanDetail extends TestPlanItem {
  content?: string;
  test_cases?: Array<{ id: string; name: string; type: string; requirement_id?: string }>;
}

// ─── Semantic Coverage ─────────────────────────────────────────────────

export interface SemanticCoverageSummary {
  run_id: string;
  status?: string;
  message?: string;
  overall_semantic_coverage_score: number;
  obligation_coverage_score: number;
  semantic_alignment_score: number;
  mutation_score: number;
  negative_coverage_score: number;
  runtime_evidence_score: number;
  verifier_confidence_score: number;
  critical_requirements_passed: boolean;
  release_gate_status: string;
  report: Record<string, unknown> | null;
}

export interface SemanticRequirement {
  requirement_id: string;
  normalized_statement: string;
  actor: string;
  action: string;
  object: string;
  criticality: string;
  security_relevance: boolean;
  governance_relevance: boolean;
  ambiguity_score: number;
  testability_score: number;
}

export interface SemanticAcceptanceCriterion {
  acceptance_criterion_id: string;
  requirement_id: string;
  given: string;
  when: string;
  then: string;
  negative_case_required: boolean;
  security_case_required: boolean;
  governance_case_required: boolean;
}

export interface SemanticTestObligation {
  obligation_id: string;
  requirement_id: string;
  obligation_type: string;
  proof_statement: string;
  required_test_type: string;
  criticality: string;
  status: string;
}

export interface SemanticAlignmentEvaluation {
  evaluation_id: string;
  test_case_id: string;
  requirement_id: string;
  obligation_id: string;
  semantic_alignment_score: number;
  verifier_verdict: string;
  can_broken_code_pass: boolean;
  critique: string;
}

export interface SemanticVerifierCritique {
  test_case_id: string;
  obligation_id: string;
  verifier_model: string;
  verdict: string;
  confidence: number;
  critique: string;
  recommendations: string[] | null;
}

export interface SemanticMutationTest {
  mutation_id: string;
  requirement_id: string;
  mutation_type: string;
  mutated_component: string;
  expected_test_failure: boolean;
  actual_test_result: string | null;
  killed: boolean;
  survived: boolean;
}

export interface SemanticNegativeRequirement {
  requirement_id: string;
  required_negative_case: string;
  status: string;
}

export interface SemanticRuntimeEvidence {
  test_case_id: string;
  obligation_id: string;
  evidence_type: string;
  binding_status: string;
}

export interface SemanticCoverageReport {
  run_id: string;
  scores: {
    obligation_coverage: number;
    semantic_alignment: number;
    mutation: number;
    negative_coverage: number;
    runtime_evidence: number;
    verifier_confidence: number;
    overall: number;
  };
  critical_requirements_passed: boolean;
  release_gate_status: string;
  report: Record<string, unknown> | null;
}

export interface SemanticWaiver {
  waiver_id: string;
  status: string;
}
