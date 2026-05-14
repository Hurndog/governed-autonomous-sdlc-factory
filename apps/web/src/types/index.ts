// Core domain types for Forge Control Tower

export interface Project {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  idea_text: string | null;
  status: string;
  github_repo_url: string | null;
  local_path: string | null;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Run {
  id: string;
  project_id: string;
  name: string;
  status: RunStatus;
  branch_name: string | null;
  current_phase: string | null;
  total_cost: number;
  budget_limit: number | null;
  is_demo: boolean;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export type RunStatus = 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';

export interface Phase {
  id: string;
  run_id: string;
  name: string;
  status: PhaseStatus;
  order_index: number;
  agent_id: string | null;
  model_used: string | null;
  tokens_in: number;
  tokens_out: number;
  cost: number;
  retry_count: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export type PhaseStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string | null;
  allowed_tools: string[];
  disallowed_tools: string[];
  model_preference: string | null;
  max_retries: number;
  is_active: boolean;
  created_at: string;
}

export interface Task {
  id: string;
  phase_id: string;
  name: string;
  description: string | null;
  status: string;
  requirement_ids: string[];
  acceptance_criteria_ids: string[];
  expected_artifacts: string[];
  test_ids: string[];
  governance_check_ids: string[];
  created_at: string;
}

export interface Artifact {
  id: string;
  task_id: string;
  run_id: string;
  name: string;
  artifact_type: string;
  content: string | null;
  file_path: string | null;
  version: number;
  is_baseline: boolean;
  is_locked: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Approval {
  id: string;
  run_id: string;
  artifact_id: string | null;
  approval_type: string;
  status: ApprovalStatus;
  approver: string | null;
  approved_at: string | null;
  artifact_version: number | null;
  is_demo: boolean;
  notes: string | null;
  created_at: string;
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'auto_approved';

export interface LogEvent {
  id: string;
  run_id: string;
  phase_id: string | null;
  agent_id: string | null;
  task_id: string | null;
  trace_id: string | null;
  severity: 'critical' | 'error' | 'warning' | 'info' | 'debug';
  message: string;
  source_file: string | null;
  commit_hash: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface CostEvent {
  id: string;
  run_id: string;
  phase_id: string | null;
  agent_id: string | null;
  event_type: string;
  model_name: string | null;
  provider: string | null;
  tokens_in: number;
  tokens_out: number;
  estimated_cost: number;
  actual_cost: number | null;
  is_local: boolean;
  latency_ms: number | null;
  created_at: string;
}

export interface CostReport {
  run_id: string;
  total_cost: number;
  budget_limit: number | null;
  remaining_budget: number | null;
  warning_threshold: number;
  is_near_limit: boolean;
  is_hard_limit_reached: boolean;
  local_cost: number;
  paid_cost: number;
  estimated_savings: number;
  by_phase: Record<string, number>;
  by_agent: Record<string, number>;
  by_model: Record<string, number>;
}

export interface EvidenceBundle {
  id: string;
  run_id: string;
  bundle_path: string | null;
  bundle_hash: string | null;
  size_bytes: number | null;
  artifact_count: number;
  created_at: string;
}

export interface Deployment {
  id: string;
  run_id: string;
  project_id: string;
  status: string;
  localhost_url: string | null;
  port: number | null;
  container_id: string | null;
  health_status: string;
  deployment_log: string | null;
  evidence_bundle_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Pattern {
  id: string;
  name: string;
  pattern_type: string;
  problem_solved: string | null;
  applicability: string | null;
  implementation_notes: string | null;
  source_project: string | null;
  related_files: string[];
  evidence_reference: string | null;
  cost_profile: Record<string, unknown>;
  success_notes: string | null;
  created_at: string;
}

export interface MemoryItem {
  id: string;
  key: string;
  content: string;
  memory_type: string;
  project_id: string | null;
  source: string;
  created_at: string;
}

export interface SystemSetting {
  key: string;
  value: string;
  value_type: string;
  description: string | null;
}

// WebSocket event types
export type WSEventType =
  | 'run.started'
  | 'run.status_changed'
  | 'run.completed'
  | 'run.failed'
  | 'run.cancelled'
  | 'run.pause_requested'
  | 'phase.transition'
  | 'artifact.created'
  | 'log.entry'
  | 'cost.recorded'
  | 'deployment.state_changed'
  | 'governance.finding'
  | 'security.finding'
  | 'agent.activity'
  | 'project.created'
  | 'intent.captured'
  | 'context.enriched'
  | 'spec.validated'
  | 'approval.baseline_created'
  | 'approval.auto_approved'
  | 'approval.pending'
  | 'approval.required'
  | 'approval.decision'
  | 'git.branch_created'
  | 'test.completed'
  | 'refactor.started'
  | 'refactor.skipped'
  | 'evidence.updated'
  | 'memory.updated'
  | 'gates.evaluated'
  | 'custom'
  | 'connected'
  | 'replay'
  | 'subscribed'
  | 'ping'
  | 'pong';

export interface WSEvent {
  type: WSEventType;
  run_id?: string;
  timestamp?: string;
  severity?: string;
  data?: Record<string, unknown>;
}

// Slash command types
export type SlashCommand =
  | '/project.create'
  | '/spec.generate'
  | '/spec.revise'
  | '/spec.approve'
  | '/fd.generate'
  | '/architecture.generate'
  | '/architecture.review'
  | '/design.generate'
  | '/governance.generate'
  | '/tests.generate'
  | '/build.prepare'
  | '/build.run'
  | '/build.pause'
  | '/build.resume'
  | '/build.cancel'
  | '/refactor.run'
  | '/security.scan'
  | '/governance.check'
  | '/evidence.export'
  | '/logs.download'
  | '/cost.report'
  | '/deploy.localhost'
  | '/patterns.extract'
  | '/memory.search'
  | '/github.sync';

export interface ParsedCommand {
  command: SlashCommand;
  args: string;
  raw: string;
}

// API response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  redis: string;
  uptime_seconds: number;
}
