'use client';

import { useStore } from '@/store';

export function AgentMonitor() {
  const { agents, phases } = useStore();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Agent Monitor</h1>

      <div className="grid grid-cols-2 gap-4">
        {agents.map((agent) => {
          const agentPhases = phases.filter(p => p.agent_id === agent.id);
          const activePhase = agentPhases.find(p => p.status === 'running');

          return (
            <div key={agent.id} className="panel p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className={`status-dot ${agent.is_active ? 'status-completed' : 'status-pending'}`} />
                  <span className="font-semibold">{agent.name}</span>
                </div>
                <span className="text-xs text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-2 py-0.5 rounded">
                  {agent.role}
                </span>
              </div>

              <div className="text-xs text-[var(--text-muted)] mb-2">
                Model: {agent.model_preference || 'default'} · Retries: {agent.max_retries}
              </div>

              {activePhase ? (
                <div className="bg-[var(--accent-blue)]/10 border border-[var(--accent-blue)]/30 rounded p-2 mt-2">
                  <div className="text-xs text-[var(--accent-blue)] font-medium">Active: {activePhase.name}</div>
                  <div className="text-xs text-[var(--text-muted)] mt-1">
                    Tokens: {activePhase.tokens_in + activePhase.tokens_out} · Cost: ${activePhase.cost.toFixed(4)}
                  </div>
                </div>
              ) : (
                <div className="text-xs text-[var(--text-muted)] mt-2">Idle</div>
              )}

              {agentPhases.length > 0 && (
                <div className="mt-3 space-y-1">
                  <div className="text-xs text-[var(--text-muted)]">Recent phases:</div>
                  {agentPhases.slice(-3).map(p => (
                    <div key={p.id} className="text-xs flex items-center gap-2">
                      <span className={`status-dot status-${p.status}`} />
                      <span>{p.name}</span>
                      <span className="text-[var(--text-muted)]">${p.cost.toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
