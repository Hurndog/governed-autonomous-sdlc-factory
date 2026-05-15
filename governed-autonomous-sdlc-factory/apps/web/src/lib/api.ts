const API_BASE = '/api/v1';

export async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  // Health & Status
  getHealth: () => fetchJSON<Record<string, unknown>>('/health'),
  getModelStatus: () => fetchJSON<Record<string, unknown>>('/cognitive/models/status'),

  // Pipelines
  getPipelines: () => fetchJSON<Record<string, unknown>[]>('/pipelines'),
  getPipeline: (id: string) => fetchJSON<Record<string, unknown>>(`/pipelines/${id}`),
  createPipeline: (data: Record<string, unknown>) =>
    fetchJSON('/pipelines', { method: 'POST', body: JSON.stringify(data) }),

  // Cognitive
  generateSpec: (intent: string) =>
    fetchJSON('/cognitive/specification', {
      method: 'POST',
      body: JSON.stringify({ intent }),
    }),
  generateArchitecture: (specId: string) =>
    fetchJSON('/cognitive/architecture', {
      method: 'POST',
      body: JSON.stringify({ specification_id: specId }),
    }),
  generateGovernance: (specId: string) =>
    fetchJSON('/cognitive/governance', {
      method: 'POST',
      body: JSON.stringify({ specification_id: specId }),
    }),
  generateTests: (specId: string) =>
    fetchJSON('/cognitive/tests', {
      method: 'POST',
      body: JSON.stringify({ specification_id: specId }),
    }),

  // Replay
  getReplaySessions: () => fetchJSON<Record<string, unknown>[]>('/replay/sessions'),
  getReplaySession: (id: string) => fetchJSON<Record<string, unknown>>(`/replay/sessions/${id}`),
  executeReplay: (sessionId: string) =>
    fetchJSON(`/replay/sessions/${sessionId}/execute`, { method: 'POST' }),

  // Governance
  getGovernanceFindings: () => fetchJSON<Record<string, unknown>[]>('/governance/findings'),

  // Artifacts
  getArtifacts: () => fetchJSON<Record<string, unknown>[]>('/artifacts'),
};
