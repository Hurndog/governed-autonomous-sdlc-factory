import type {
  SemanticCoverageSummary,
  SemanticRequirement,
  SemanticAcceptanceCriterion,
  SemanticTestObligation,
  SemanticAlignmentEvaluation,
  SemanticVerifierCritique,
  SemanticMutationTest,
  SemanticNegativeRequirement,
  SemanticRuntimeEvidence,
  SemanticCoverageReport,
  SemanticWaiver,
} from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${res.statusText}${body ? ` — ${body}` : ''}`);
  }
  return res.json();
}

export async function fetchText(path: string, init?: RequestInit): Promise<string> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${res.statusText}${body ? ` — ${body}` : ''}`);
  }
  return res.text();
}

// ─── Health & Status ────────────────────────────────────────────────

export const api = {
  getHealth: () => fetchJSON<HealthResponse>('/health'),
  getModelStatus: () => fetchJSON<ModelStatusResponse>('/cognitive/model-status'),
  getGithubStatus: () => fetchJSON<GithubStatusResponse>('/github/status'),
  getSettings: () => fetchJSON<SettingsResponse>('/settings'),

  // ─── Runs ─────────────────────────────────────────────────────────
  listRuns: (params?: { project_id?: string; status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.project_id) q.set('project_id', params.project_id);
    if (params?.status) q.set('status', params.status);
    if (params?.page) q.set('page', String(params.page));
    if (params?.page_size) q.set('page_size', String(params.page_size));
    return fetchJSON<ListRunsResponse>(`/runs?${q}`);
  },
  getRun: (runId: string) => fetchJSON<RunDetail>(`/runs/${runId}`),
  getRunStatus: (runId: string) => fetchJSON<RunStatus>(`/runs/${runId}/status`),
  createRun: (data: CreateRunRequest) => fetchJSON<RunDetail>('/runs', { method: 'POST', body: JSON.stringify(data) }),
  startRun: (runId: string) => fetchJSON<RunDetail>(`/runs/${runId}/start`, { method: 'POST' }),
  pauseRun: (runId: string) => fetchJSON<RunDetail>(`/runs/${runId}/pause`, { method: 'POST' }),
  resumeRun: (runId: string) => fetchJSON<RunDetail>(`/runs/${runId}/resume`, { method: 'POST' }),
  cancelRun: (runId: string) => fetchJSON<RunDetail>(`/runs/${runId}/cancel`, { method: 'POST' }),

  // ─── Pipeline ─────────────────────────────────────────────────────
  runFullPipeline: (params: { intent: string; project_name?: string; project_id?: string; budget_limit?: number }) => {
    const q = new URLSearchParams({ intent: params.intent });
    if (params.project_name) q.set('project_name', params.project_name);
    if (params.project_id) q.set('project_id', params.project_id);
    if (params.budget_limit) q.set('budget_limit', String(params.budget_limit));
    return fetchJSON<PipelineRunResponse>(`/pipeline/run-full-pipeline?${q}`, { method: 'POST' });
  },
  getRunTimeline: (runId: string) => fetchJSON<TimelineResponse>(`/pipeline/runs/${runId}/timeline`),
  getRunSnapshot: (runId: string) => fetchJSON<SnapshotResponse>(`/pipeline/runs/${runId}/snapshot`),
  getDivergence: (runId: string) => fetchJSON<DivergenceResponse>(`/pipeline/runs/${runId}/divergence`),
  compareRunReplay: (runId: string, replaySessionId?: string) => {
    const q = new URLSearchParams();
    if (replaySessionId) q.set('replay_session_id', replaySessionId);
    return fetchJSON<CompareResponse>(`/pipeline/runs/${runId}/compare?${q}`, { method: 'POST' });
  },
  getSemanticGraph: (runId: string) => fetchJSON<SemanticGraphResponse>(`/pipeline/runs/${runId}/semantic-graph`),

  // ─── Integrity ────────────────────────────────────────────────────
  verifyIntegrity: (runId: string) => fetchJSON<IntegrityResponse>(`/pipeline/runs/${runId}/verify-integrity`, { method: 'POST' }),
  getRunIntegrity: (runId: string) => fetchJSON<IntegrityResponse>(`/pipeline/runs/${runId}/integrity`),

  // ─── Replay ───────────────────────────────────────────────────────
  replayRun: (runId: string, params?: { replay_mode?: string; from_timestamp?: string; phase_name?: string }) => {
    const q = new URLSearchParams();
    if (params?.replay_mode) q.set('replay_mode', params.replay_mode);
    if (params?.from_timestamp) q.set('from_timestamp', params.from_timestamp);
    if (params?.phase_name) q.set('phase_name', params.phase_name);
    return fetchJSON<ReplayResponse>(`/pipeline/runs/${runId}/replay?${q}`, { method: 'POST' });
  },
  getReplaySessions: (runId: string) => fetchJSON<ReplaySessionsResponse>(`/pipeline/runs/${runId}/replay`),

  // ─── Traceability ─────────────────────────────────────────────────
  getTraceability: (runId: string) => fetchJSON<TraceabilityResponse>(`/engines/traceability/${runId}`),
  getTraceabilityCoverage: (runId: string) => fetchJSON<CoverageResponse>(`/engines/traceability/${runId}/coverage`),
  getArtifactLineage: (artifactId: string) => fetchJSON<LineageResponse>(`/pipeline/traceability/lineage/${artifactId}`),

  // ─── Governance ───────────────────────────────────────────────────
  getGovernanceEvaluations: (runId: string) => fetchJSON<GovernanceEvaluationsResponse>(`/engines/governance/evaluations/${runId}`),
  getGovernancePolicies: (activeOnly?: boolean) => {
    const q = new URLSearchParams();
    if (activeOnly !== undefined) q.set('active_only', String(activeOnly));
    return fetchJSON<PoliciesResponse>(`/engines/governance/policies?${q}`);
  },
  evaluateGovernance: (runId: string, data?: Record<string, unknown>) => fetchJSON<GovernanceEvaluationsResponse>(`/engines/governance/evaluate/${runId}`, { method: 'POST', body: JSON.stringify(data || {}) }),
  createReleaseGate: (runId: string, params: { gate_name: string; required_policy_ids?: string[] }) => {
    const q = new URLSearchParams({ gate_name: params.gate_name });
    if (params.required_policy_ids) q.set('required_policy_ids', params.required_policy_ids.join(','));
    return fetchJSON<ReleaseGateResponse>(`/engines/governance/release-gates/${runId}?${q}`, { method: 'POST' });
  },
  evaluateReleaseGate: (runId: string, gateId: string) => fetchJSON<ReleaseGateResponse>(`/engines/governance/release-gates/${runId}/evaluate/${gateId}`, { method: 'POST' }),

  // ─── Artifacts ────────────────────────────────────────────────────
  listArtifacts: (runId: string, artifactType?: string) => {
    const q = new URLSearchParams();
    if (artifactType) q.set('artifact_type', artifactType);
    return fetchJSON<ArtifactsResponse>(`/artifacts/by-run/${runId}?${q}`);
  },
  getArtifact: (artifactId: string) => fetchJSON<ArtifactDetail>(`/artifacts/${artifactId}`),
  lockArtifact: (artifactId: string) => fetchJSON<ArtifactDetail>(`/artifacts/${artifactId}/lock`, { method: 'POST' }),

  // ─── Engines: Spec & Arch ─────────────────────────────────────────
  getSpecifications: (runId: string) => fetchJSON<SpecificationsResponse>(`/engines/specification/${runId}`),
  getLatestSpec: (runId: string) => fetchJSON<SpecificationDetail>(`/engines/specification/${runId}/latest`),
  getArchitectures: (runId: string) => fetchJSON<ArchitecturesResponse>(`/engines/architecture/${runId}`),
  getLatestArch: (runId: string) => fetchJSON<ArchitectureDetail>(`/engines/architecture/${runId}/latest`),
  getTestPlans: (runId: string) => fetchJSON<TestPlansResponse>(`/engines/test-plan/${runId}`),
  getLatestTestPlan: (runId: string) => fetchJSON<TestPlanDetail>(`/engines/test-plan/${runId}/latest`),

  // ─── Evidence ─────────────────────────────────────────────────────
  getEvidenceByRun: (runId: string) => fetchJSON<EvidenceResponse>(`/evidence/by-run/${runId}`),
  createEvidence: (runId: string) => fetchJSON<EvidenceBundleResponse>(`/evidence/create/${runId}`, { method: 'POST' }),
  downloadEvidence: (bundleId: string) => fetchText(`/evidence/download/${bundleId}`),

  // ─── Logs ─────────────────────────────────────────────────────────
  getLogs: (params?: { run_id?: string; phase_id?: string; agent_id?: string; severity?: string; error_only?: boolean; limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.run_id) q.set('run_id', params.run_id);
    if (params?.phase_id) q.set('phase_id', params.phase_id);
    if (params?.agent_id) q.set('agent_id', params.agent_id);
    if (params?.severity) q.set('severity', params.severity);
    if (params?.error_only !== undefined) q.set('error_only', String(params.error_only));
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.offset) q.set('offset', String(params.offset));
    return fetchJSON<LogsResponse>(`/logs?${q}`);
  },

  // ─── Costs ────────────────────────────────────────────────────────
  getCostEvents: (runId: string) => fetchJSON<CostEventsResponse>(`/costs/events/${runId}`),
  getCostReport: (runId: string) => fetchJSON<CostReportResponse>(`/costs/report/${runId}`),

  // ─── Agents ───────────────────────────────────────────────────────
  listAgents: (params?: { is_active?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.is_active !== undefined) q.set('is_active', String(params.is_active));
    return fetchJSON<AgentsResponse>(`/agents?${q}`);
  },
  getAgent: (agentId: string) => fetchJSON<AgentDetail>(`/agents/${agentId}`),

  // ─── Phases ───────────────────────────────────────────────────────
  listPhasesByRun: (runId: string) => fetchJSON<PhasesResponse>(`/phases/by-run/${runId}`),
  getPhase: (phaseId: string) => fetchJSON<PhaseDetail>(`/phases/${phaseId}`),

  // ─── Tasks ────────────────────────────────────────────────────────
  listTasksByPhase: (phaseId: string) => fetchJSON<TasksResponse>(`/tasks/by-phase/${phaseId}`),

  // ─── Snapshots ────────────────────────────────────────────────────
  getSnapshots: (runId: string) => fetchJSON<SnapshotsResponse>(`/engines/snapshots/${runId}`),
  createSnapshot: (runId: string, snapshotType?: string) => {
    const q = new URLSearchParams();
    if (snapshotType) q.set('snapshot_type', snapshotType);
    return fetchJSON<SnapshotDetail>(`/engines/snapshots/${runId}?${q}`, { method: 'POST' });
  },

  // ─── Projects ─────────────────────────────────────────────────────
  listProjects: () => fetchJSON<ProjectsResponse>('/projects'),
  getProject: (projectId: string) => fetchJSON<ProjectDetail>(`/projects/${projectId}`),
  createProject: (data: { name: string; description?: string }) => fetchJSON<ProjectDetail>('/projects', { method: 'POST', body: JSON.stringify(data) }),

  // ─── Semantic Coverage ──────────────────────────────────────────────
  getSemanticCoverageSummary: (runId: string) =>
    fetchJSON<SemanticCoverageSummary>(`/semantic-coverage/runs/${runId}/summary`),
  getSemanticRequirements: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; requirements: SemanticRequirement[] }>(`/semantic-coverage/runs/${runId}/requirements`),
  getSemanticAcceptanceCriteria: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; acceptance_criteria: SemanticAcceptanceCriterion[] }>(`/semantic-coverage/runs/${runId}/acceptance-criteria`),
  getSemanticTestObligations: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; obligations: SemanticTestObligation[] }>(`/semantic-coverage/runs/${runId}/test-obligations`),
  getSemanticAlignment: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; evaluations: SemanticAlignmentEvaluation[] }>(`/semantic-coverage/runs/${runId}/alignment`),
  getSemanticVerifierCritiques: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; critiques: SemanticVerifierCritique[] }>(`/semantic-coverage/runs/${runId}/verifier-critiques`),
  getSemanticMutations: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; killed: number; survived: number; mutations: SemanticMutationTest[] }>(`/semantic-coverage/runs/${runId}/mutations`),
  getSemanticNegativeCoverage: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; pending: number; generated: number; requirements: SemanticNegativeRequirement[] }>(`/semantic-coverage/runs/${runId}/negative-coverage`),
  getSemanticRuntimeEvidence: (runId: string) =>
    fetchJSON<{ run_id: string; total: number; bound: number; failed: number; bindings: SemanticRuntimeEvidence[] }>(`/semantic-coverage/runs/${runId}/runtime-evidence`),
  getSemanticCoverageReport: (runId: string) =>
    fetchJSON<SemanticCoverageReport>(`/semantic-coverage/runs/${runId}/report`),
  evaluateSemanticCoverage: (runId: string) =>
    fetchJSON<{ run_id: string; status: string; overall_semantic_coverage_score: number; critical_requirements_passed: boolean; release_gate_status: string }>(`/semantic-coverage/runs/${runId}/evaluate`, { method: 'POST' }),
  createSemanticWaiver: (runId: string, params: { requirement_id: string; waiver_reason: string; waiver_scope?: string; approved_by?: string }) => {
    const q = new URLSearchParams({ requirement_id: params.requirement_id, waiver_reason: params.waiver_reason });
    if (params.waiver_scope) q.set('waiver_scope', params.waiver_scope);
    if (params.approved_by) q.set('approved_by', params.approved_by);
    return fetchJSON<SemanticWaiver>(`/semantic-coverage/runs/${runId}/waivers?${q}`, { method: 'POST' });
  },
};

// ─── Type Definitions ──────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  redis: string;
  uptime_seconds: number;
}

export interface ModelStatusResponse {
  providers: Array<{
    name: string;
    base_url: string;
    models: Array<{ name: string; available: boolean; size?: string }>;
    default_model?: string;
    is_local: boolean;
    status: 'online' | 'offline' | 'error';
  }>;
  routing_policy: Record<string, string>;
  default_provider: string;
  default_model: string;
}

export interface GithubStatusResponse {
  configured: boolean;
  token_valid: boolean;
  owner?: string;
  repo?: string;
  last_sync?: string;
  error?: string;
}

export interface SettingsResponse {
  settings: Array<{ key: string; value: string; value_type: string }>;
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

export interface ListRunsResponse {
  items: RunItem[];
  total: number;
  page: number;
  page_size: number;
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

export interface CreateRunRequest {
  project_id?: string;
  intent: string;
  project_name?: string;
  budget_limit?: number;
}

export interface PipelineRunResponse {
  run_id: string;
  status: string;
  message?: string;
}

export interface TimelineResponse {
  run_id: string;
  events: TimelineEvent[];
  total: number;
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

export interface SnapshotResponse {
  run_id: string;
  snapshots: SnapshotItem[];
}

export interface SnapshotItem {
  id: string;
  run_id: string;
  snapshot_type: string;
  created_at: string;
  hash?: string;
  data?: Record<string, unknown>;
}

export interface SnapshotDetail {
  id: string;
  run_id: string;
  snapshot_type: string;
  created_at: string;
  hash?: string;
  data?: Record<string, unknown>;
}

export interface DivergenceResponse {
  run_id: string;
  divergences: DivergenceItem[];
  total: number;
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

export interface CompareResponse {
  run_id: string;
  replay_session_id?: string;
  match: boolean;
  differences: Array<{
    field: string;
    original: unknown;
    replay: unknown;
  }>;
}

export interface SemanticGraphResponse {
  run_id: string;
  nodes: Array<{ id: string; label: string; type: string }>;
  edges: Array<{ source: string; target: string; label?: string }>;
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

export interface ReplayResponse {
  replay_session_id?: string;
  run_id: string;
  status: string;
  event_count?: number;
  integrity_preserved?: boolean;
  message?: string;
}

export interface ReplaySessionsResponse {
  run_id: string;
  sessions: ReplaySessionItem[];
}

export interface ReplaySessionItem {
  id: string;
  run_id: string;
  status: string;
  event_count?: number;
  divergence_count?: number;
  integrity_preserved?: boolean;
  created_at?: string;
}

export interface TraceabilityResponse {
  run_id: string;
  links: TraceabilityLink[];
  total: number;
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

export interface CoverageResponse {
  run_id: string;
  total_requirements: number;
  covered_requirements: number;
  coverage_pct: number;
  by_phase: Record<string, number>;
}

export interface LineageResponse {
  artifact_id: string;
  upstream: TraceabilityLink[];
  downstream: TraceabilityLink[];
}

export interface GovernanceEvaluationsResponse {
  run_id: string;
  evaluations: GovernanceEvaluation[];
  total: number;
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

export interface PoliciesResponse {
  policies: GovernancePolicy[];
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

export interface ReleaseGateResponse {
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

export interface ArtifactsResponse {
  run_id: string;
  artifacts: ArtifactItem[];
  total: number;
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

export interface ArtifactDetail {
  id: string;
  run_id: string;
  type: string;
  name: string;
  phase?: string;
  hash?: string;
  size_bytes?: number;
  content?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  locked?: boolean;
}

export interface SpecificationsResponse {
  run_id: string;
  specifications: SpecificationItem[];
}

export interface SpecificationItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface SpecificationDetail {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  content?: string;
  functional_requirements?: string[];
  non_functional_requirements?: string[];
  acceptance_criteria?: string[];
  created_at?: string;
}

export interface ArchitecturesResponse {
  run_id: string;
  architectures: ArchitectureItem[];
}

export interface ArchitectureItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface ArchitectureDetail {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  content?: string;
  components?: Array<{ id: string; name: string; type: string; dependencies?: string[] }>;
  decisions?: Array<{ id: string; title: string; context: string; decision: string; status: string }>;
  mermaid_diagram?: string;
  created_at?: string;
}

export interface TestPlansResponse {
  run_id: string;
  test_plans: TestPlanItem[];
}

export interface TestPlanItem {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  created_at?: string;
}

export interface TestPlanDetail {
  id: string;
  run_id: string;
  version?: number;
  title?: string;
  content?: string;
  test_cases?: Array<{ id: string; name: string; type: string; requirement_id?: string }>;
  created_at?: string;
}

export interface EvidenceResponse {
  run_id: string;
  bundles: EvidenceBundle[];
}

export interface EvidenceBundle {
  id: string;
  run_id: string;
  file_count?: number;
  size_bytes?: number;
  created_at?: string;
}

export interface EvidenceBundleResponse {
  bundle_id: string;
  run_id: string;
  file_count?: number;
  size_bytes?: number;
  message?: string;
}

export interface LogsResponse {
  logs: LogEntry[];
  total: number;
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

export interface CostEventsResponse {
  run_id: string;
  events: CostEvent[];
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

export interface CostAggregationItem {
  key: string;
  label: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
  call_count: number;
  error_count: number;
  retry_count: number;
  percentage_of_total: number;
  is_estimated: boolean;
}

export interface CostWasteSummary {
  retry_tokens: number;
  failed_call_tokens: number;
  oversized_prompt_tokens: number | null;
  unused_context_tokens: number | null;
  unknown_waste_tokens: number | null;
  notes: string;
}

export interface CostReportResponse {
  run_id: string;
  generated_at: string;
  aggregation_confidence: string;
  total_cost: number;
  total_tokens: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_calls: number;
  total_errors: number;
  total_retries: number;
  budget_limit: number | null;
  remaining_budget: number | null;
  warning_threshold: number;
  is_near_limit: boolean;
  is_hard_limit_reached: boolean;
  local_cost: number;
  paid_cost: number;
  estimated_savings: number;
  by_phase: Record<string, CostAggregationItem>;
  by_model: Record<string, CostAggregationItem>;
  by_provider: Record<string, CostAggregationItem>;
  by_agent: Record<string, CostAggregationItem>;
  waste_summary: CostWasteSummary;
  missing_fields: string[];
  data_quality_warnings: string[];
}

export interface SnapshotsResponse {
  run_id: string;
  snapshots: SnapshotItem[];
}

// ─── Agents ───────────────────────────────────────────────────────

export interface AgentsResponse {
  agents: AgentItem[];
}

export interface AgentItem {
  id: string;
  name: string;
  role: string;
  description?: string;
  model_preference?: string;
  max_retries: number;
  is_active: boolean;
  allowed_tools?: string[];
  disallowed_tools?: string[];
}

export interface AgentDetail extends AgentItem {}

// ─── Phases ───────────────────────────────────────────────────────

export interface PhasesResponse {
  phases: PhaseItem[];
}

export interface PhaseItem {
  id: string;
  run_id: string;
  name: string;
  order_index: number;
  status: string;
  agent_id?: string;
  model_used?: string;
  tokens_in?: number;
  tokens_out?: number;
  cost?: number;
  error_message?: string;
  created_at?: string;
  completed_at?: string;
}

export interface PhaseDetail extends PhaseItem {}

// ─── Tasks ────────────────────────────────────────────────────────

export interface TasksResponse {
  tasks: TaskItem[];
}

export interface TaskItem {
  id: string;
  phase_id: string;
  name: string;
  description?: string;
  status?: string;
  requirement_ids?: string[];
  acceptance_criteria_ids?: string[];
  expected_artifacts?: string[];
  test_ids?: string[];
  governance_check_ids?: string[];
  created_at?: string;
}

export interface ProjectsResponse {
  projects: ProjectItem[];
}

export interface ProjectItem {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectDetail {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  run_count?: number;
}

// Re-export semantic coverage types for convenience
export type { SemanticCoverageSummary, SemanticCoverageReport } from '@/lib/types';
