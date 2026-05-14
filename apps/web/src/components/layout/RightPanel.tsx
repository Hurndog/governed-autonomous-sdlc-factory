'use client';

import { useStore } from '@/store';
import { PhaseCard } from '../ui/PhaseCard';
import { LogViewer } from '../ui/LogViewer';
import { CostWidget } from '../ui/CostWidget';

export function RightPanel() {
  const { inspectorOpen, selectedRun, phases, logs, costReport } = useStore();

  if (!inspectorOpen) return null;

  return (
    <aside className="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-primary)] flex flex-col overflow-hidden">
      {/* Inspector Header */}
      <div className="panel-header flex items-center justify-between">
        <span>Inspector</span>
        <span className="text-xs text-[var(--text-muted)]">
          {selectedRun?.name || 'No run'}
        </span>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-4">
        {/* Current Phase Detail */}
        {phases.length > 0 && (
          <div>
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Current Phase</div>
            {phases.filter(p => p.status === 'running').map(phase => (
              <PhaseCard key={phase.id} phase={phase} expanded />
            ))}
          </div>
        )}

        {/* Cost Widget */}
        <CostWidget report={costReport} />

        {/* Recent Logs */}
        <div>
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Recent Logs</div>
          <LogViewer logs={logs.slice(-20)} compact />
        </div>
      </div>
    </aside>
  );
}
