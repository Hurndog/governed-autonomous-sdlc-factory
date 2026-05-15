export interface RuntimeHealth {
  status: 'healthy' | 'degraded' | 'critical';
  uptime: number;
  version: string;
  checks: {
    database: 'pass' | 'fail' | 'warn';
    ollama: 'pass' | 'fail' | 'warn';
    lm_studio: 'pass' | 'fail' | 'warn';
    model_router: 'pass' | 'fail' | 'warn';
    replay_runtime: 'pass' | 'fail' | 'warn';
    evidence_dir: 'pass' | 'fail' | 'warn';
    backup: 'pass' | 'fail' | 'warn';
    github: 'pass' | 'fail' | 'warn';
    api_keys: 'pass' | 'fail' | 'warn';
    docker: 'pass' | 'fail' | 'warn';
    routes: 'pass' | 'fail' | 'warn';
  };
}

export interface Pipeline {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  stage: string;
  progress: number;
  started_at: string;
  updated_at: string;
  stages: PipelineStage[];
}

export interface PipelineStage {
  name: string;
  status: 'completed' | 'running' | 'pending' | 'failed';
  duration_ms?: number;
  tokens?: number;
}

export interface ReplaySession {
  id: string;
  pipeline_id: string;
  status: 'completed' | 'running' | 'failed';
  integrity_score: number;
  event_count: number;
  divergence_count: number;
  created_at: string;
  events: ReplayEvent[];
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

export interface GovernanceFinding {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  category: string;
  title: string;
  description: string;
  replay_session_id?: string;
  created_at: string;
}

export interface ModelStatus {
  provider: string;
  model: string;
  available: boolean;
  latency_ms?: number;
  tokens_used: number;
  cost: number;
  role: string;
}

export interface TokenUsage {
  total_tokens: number;
  total_cost: number;
  by_provider: Record<string, { tokens: number; cost: number }>;
  by_model: Record<string, { tokens: number; cost: number }>;
}

export interface Artifact {
  id: string;
  type: string;
  name: string;
  pipeline_id: string;
  hash: string;
  size: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface Specification {
  id: string;
  pipeline_id: string;
  title: string;
  functional_requirements: Requirement[];
  non_functional_requirements: Requirement[];
  acceptance_criteria: string[];
  governance_areas: string[];
  inference_trace_id?: string;
  created_at: string;
}

export interface Requirement {
  id: string;
  text: string;
  priority: 'must' | 'should' | 'could';
  governance_sensitive: boolean;
}

export interface Architecture {
  id: string;
  pipeline_id: string;
  components: ArchComponent[];
  decisions: ArchitectureDecision[];
  mermaid_diagram: string;
  created_at: string;
}

export interface ArchComponent {
  id: string;
  name: string;
  type: string;
  dependencies: string[];
  governance_relevant: boolean;
}

export interface ArchitectureDecision {
  id: string;
  title: string;
  context: string;
  decision: string;
  consequences: string[];
  status: 'proposed' | 'accepted' | 'deprecated';
}
