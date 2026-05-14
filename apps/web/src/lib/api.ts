import type { PaginatedResponse, HealthResponse } from '@/types';

const API_BASE = '/api/v1';

class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

async function requestPaginated<T>(path: string, params?: Record<string, string>): Promise<PaginatedResponse<T>> {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return request<PaginatedResponse<T>>(`${path}${qs}`);
}

// Projects
export const api = {
  health: () => request<HealthResponse>('/health'),

  // Projects
  listProjects: (page = 1, page_size = 50) =>
    requestPaginated<Project>('/projects', { page: String(page), page_size: String(page_size) }),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: { name: string; description?: string; idea_text?: string }) =>
    request<Project>('/projects/', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id: string, data: Partial<{ name: string; description: string; status: string }>) =>
    request<Project>(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<{ message: string }>(`/projects/${id}`, { method: 'DELETE' }),

  // Runs
  listRuns: (project_id?: string, page = 1) =>
    requestPaginated<Run>('/runs', { ...(project_id && { project_id }), page: String(page) }),
  getRun: (id: string) => request<Run>(`/runs/${id}`),
  createRun: (data: { project_id: string; name: string; budget_limit?: number; is_demo?: boolean }) =>
    request<Run>('/runs/', { method: 'POST', body: JSON.stringify(data) }),
  updateRun: (id: string, data: { status?: string; current_phase?: string }) =>
    request<Run>(`/runs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  pauseRun: (id: string) => request<Run>(`/runs/${id}/pause`, { method: 'POST' }),
  resumeRun: (id: string) => request<Run>(`/runs/${id}/resume`, { method: 'POST' }),
  cancelRun: (id: string) => request<Run>(`/runs/${id}/cancel`, { method: 'POST' }),
  getRunStatus: (id: string) => request<Run>(`/runs/${id}/status`),

  // Phases
  listPhasesByRun: (run_id: string) => request<Phase[]>(`/phases/by-run/${run_id}`),
  getPhase: (id: string) => request<Phase>(`/phases/${id}`),
  createPhase: (data: { run_id: string; name: string; order_index?: number; agent_id?: string }) =>
    request<Phase>('/phases/', { method: 'POST', body: JSON.stringify(data) }),
  completePhase: (id: string, tokens_in?: number, tokens_out?: number, cost?: number) =>
    request<Phase>(`/phases/${id}/complete`, { method: 'POST', body: JSON.stringify({ tokens_in, tokens_out, cost }) }),
  failPhase: (id: string, error_message: string) =>
    request<Phase>(`/phases/${id}/fail`, { method: 'POST', body: JSON.stringify({ error_message }) }),

  // Agents
  listAgents: (is_active?: boolean) =>
    request<Agent[]>(`/agents/${is_active !== undefined ? `?is_active=${is_active}` : ''}`),
  getAgent: (id: string) => request<Agent>(`/agents/${id}`),
  createAgent: (data: { name: string; role: string; description?: string; model_preference?: string }) =>
    request<Agent>('/agents/', { method: 'POST', body: JSON.stringify(data) }),

  // Tasks
  listTasksByPhase: (phase_id: string) => request<Task[]>(`/tasks/by-phase/${phase_id}`),
  createTask: (data: { phase_id: string; name: string; description?: string }) =>
    request<Task>('/tasks/', { method: 'POST', body: JSON.stringify(data) }),

  // Artifacts
  listArtifactsByRun: (run_id: string, artifact_type?: string) =>
    request<Artifact[]>(`/artifacts/by-run/${run_id}${artifact_type ? `?artifact_type=${artifact_type}` : ''}`),
  createArtifact: (data: { task_id: string; run_id: string; name: string; artifact_type: string; content?: string; file_path?: string }) =>
    request<Artifact>('/artifacts/', { method: 'POST', body: JSON.stringify(data) }),

  // Approvals
  listApprovalsByRun: (run_id: string) => request<Approval[]>(`/approvals/by-run/${run_id}`),
  createApproval: (data: { run_id: string; approval_type: string; is_demo?: boolean }) =>
    request<Approval>('/approvals/', { method: 'POST', body: JSON.stringify(data) }),
  approve: (id: string) => request<Approval>(`/approvals/${id}/approve`, { method: 'POST' }),
  reject: (id: string) => request<Approval>(`/approvals/${id}/reject`, { method: 'POST' }),

  // Logs
  listLogs: (params?: { run_id?: string; severity?: string; error_only?: boolean; limit?: number; offset?: number }) =>
    requestPaginated<LogEvent>('/logs', params as Record<string, string>),
  exportLogs: (run_id: string) => request<{ content: string; count: number }>(`/logs/export?run_id=${run_id}`),

  // Evidence
  listEvidenceByRun: (run_id: string) => request<{ bundles: EvidenceBundle[] }>(`/evidence/by-run/${run_id}`),
  createEvidenceBundle: (run_id: string) =>
    request<EvidenceBundle>(`/evidence/create/${run_id}`, { method: 'POST' }),

  // Costs
  getCostReport: (run_id: string) => request<CostReport>(`/costs/report/${run_id}`),
  listCostEvents: (run_id: string) => request<{ events: CostEvent[] }>(`/costs/events/${run_id}`),
  recordCostEvent: (data: { run_id: string; event_type: string; model_name?: string; tokens_in?: number; tokens_out?: number; estimated_cost?: number }) =>
    request<{ id: string }>('/costs/', { method: 'POST', body: JSON.stringify(data) }),

  // Patterns
  listPatterns: (pattern_type?: string) =>
    requestPaginated<Pattern>('/patterns', pattern_type ? { pattern_type } : undefined),
  createPattern: (data: { name: string; pattern_type: string; problem_solved?: string }) =>
    request<Pattern>('/patterns/', { method: 'POST', body: JSON.stringify(data) }),

  // Memory
  searchMemory: (q: string, memory_type?: string, project_id?: string) =>
    request<{ items: MemoryItem[] }>(`/memory/search?q=${encodeURIComponent(q)}${memory_type ? `&memory_type=${memory_type}` : ''}${project_id ? `&project_id=${project_id}` : ''}`),

  // GitHub
  getGitHubStatus: () => request<{ configured: boolean; owner: string; repo: string }>('/github/status'),
  syncGitHub: (run_id: string) => request<{ status: string }>(`/github/sync/${run_id}`, { method: 'POST' }),

  // Deployment
  deployRun: (run_id: string) => request<Deployment>(`/deployment/${run_id}`, { method: 'POST' }),
  getDeploymentStatus: (run_id: string) => request<Deployment>(`/deployment/status/${run_id}`),
  shutdownDeployment: (run_id: string) => request<{ status: string }>(`/deployment/shutdown/${run_id}`, { method: 'POST' }),
  restartDeployment: (run_id: string) => request<{ status: string }>(`/deployment/restart/${run_id}`, { method: 'POST' }),

  // Settings
  getSettings: () => request<Record<string, SystemSetting>>('/settings/'),
  updateSetting: (key: string, value: string) =>
    request<{ key: string; value: string }>(`/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value }) }),
};

import type { Project, Run, Phase, Agent, Task, Artifact, Approval, LogEvent, CostEvent, CostReport, EvidenceBundle, Deployment, Pattern, MemoryItem, SystemSetting } from '@/types';
