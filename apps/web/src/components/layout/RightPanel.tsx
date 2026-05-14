'use client';

import { useState } from 'react';
import { useStore } from '@/store';
import { LogViewer } from '@/components/ui/LogViewer';
import { CostWidget } from '@/components/ui/CostWidget';
import { clsx } from 'clsx';
import type { Phase } from '@/types';

type InspectorTab = 'overview' | 'logs' | 'artifacts' | 'json' | 'traces';

export function RightPanel() {
  const { inspectorOpen, selectedRun, phases, logs, costReport, selectedPhaseId, setSelectedPhaseId } = useStore();
  const [activeTab, setActiveTab] = useState<InspectorTab>('overview');

  if (!inspectorOpen) return null;

  const selectedPhase = phases.find(p => p.id === selectedPhaseId);
  const phaseLogs = selectedPhase
    ? logs.filter(l => l.phase_id === selectedPhase.id)
    : logs.slice(-20);

  const tabs: { id: InspectorTab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'logs', label: 'Logs' },
    { id: 'artifacts', label: 'Artifacts' },
    { id: 'json', label: 'JSON' },
    { id: 'traces', label: 'Traces' },
  ];

  return (
    <aside className="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-primary)] flex flex-col overflow-hidden">
      {/* Inspector Header */}
      <div className="panel-header flex items-center justify-between shrink-0">
        <span>Inspector</span>
        <span className="text-xs text-[var(--text-muted)]">
          {selectedRun?.name || 'No run'}
        </span>
      </div>

      {/* Phase Selector */}
      {phases.length > 0 && (
        <div className="px-3 py-2 border-b border-[var(--border-primary)] shrink-0">
          <select
            value={selectedPhaseId || ''}
            onChange={(e) => setSelectedPhaseId(e.target.value || null)}
            className="w-full bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded px-2 py-1 text-xs focus:outline-none"
          >
            <option value="">All Phases</option>
            {phases.map(p => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.status})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-[var(--border-primary)] shrink-0">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={clsx(
              'flex-1 px-2 py-2 text-xs font-medium transition-colors',
              activeTab === tab.id
                ? 'text-[var(--accent-blue)] border-b-2 border-[var(--accent-blue)]'
                : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-3">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {selectedPhase ? (
              <PhaseDetail phase={selectedPhase} />
            ) : (
              <>
                <CostWidget report={costReport} />
                <div>
                  <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Recent Logs</div>
                  <LogViewer logs={logs.slice(-20)} compact />
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <LogViewer logs={phaseLogs} />
        )}

        {activeTab === 'artifacts' && (
          <div className="text-xs text-[var(--text-muted)]">
            Artifacts for selected phase will appear here.
          </div>
        )}

        {activeTab === 'json' && (
          <div className="text-xs font-mono">
            <pre className="whitespace-pre-wrap break-all text-[var(--text-secondary)]">
              {JSON.stringify(selectedPhase || selectedRun || {}, null, 2)}
            </pre>
          </div>
        )}

        {activeTab === 'traces' && (
          <div className="text-xs text-[var(--text-muted)]">
            Trace data for selected phase will appear here.
          </div>
        )}
      </div>
    </aside>
  );
}

function PhaseDetail({ phase }: { phase: Phase }) {
  return (
    <div className="space-y-3">
      <div className="panel p-3">
        <div className="flex items-center gap-2 mb-2">
          <span className={clsx('status-dot', `status-${phase.status}`)} />
          <span className="font-semibold text-sm">{phase.name}</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-[var(--text-muted)]">Status:</span>
            <span className="ml-1">{phase.status}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Agent:</span>
            <span className="ml-1">{phase.agent_id || '—'}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Model:</span>
            <span className="ml-1">{phase.model_used || '—'}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Tokens:</span>
            <span className="ml-1">{phase.tokens_in + phase.tokens_out}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Cost:</span>
            <span className="ml-1">${phase.cost.toFixed(4)}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Retries:</span>
            <span className="ml-1">{phase.retry_count}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Started:</span>
            <span className="ml-1">{phase.started_at ? new Date(phase.started_at).toLocaleTimeString() : '—'}</span>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Completed:</span>
            <span className="ml-1">{phase.completed_at ? new Date(phase.completed_at).toLocaleTimeString() : '—'}</span>
          </div>
        </div>
        {phase.error_message && (
          <div className="text-xs text-[var(--accent-red)] bg-[var(--accent-red)]/10 rounded p-2 mt-2">
            {phase.error_message}
          </div>
        )}
      </div>
    </div>
  );
}
