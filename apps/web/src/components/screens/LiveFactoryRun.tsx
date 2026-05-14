'use client';

import { useStore } from '@/store';
import { LangGraphVisualization } from '@/components/ui/LangGraphViz';
import { LogViewer } from '@/components/ui/LogViewer';
import { CostWidget } from '@/components/ui/CostWidget';
import { PhaseCard } from '@/components/ui/PhaseCard';
import { clsx } from 'clsx';

export function LiveFactoryRun() {
  const { selectedRun, phases, logs, costReport, liveEvents } = useStore();

  if (!selectedRun) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-5xl mb-4">🏭</div>
          <h2 className="text-xl font-semibold mb-2">Live Factory Run</h2>
          <p className="text-sm text-[var(--text-muted)]">Select a run from Command Center to view the pipeline</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Run Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-primary)] bg-[var(--bg-secondary)]">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold">{selectedRun.name}</h1>
          <span className={clsx('status-dot', `status-${selectedRun.status}`)} />
          <span className="text-sm text-[var(--text-muted)]">{selectedRun.status}</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-[var(--text-muted)]">
            Branch: <span className="font-mono text-[var(--text-secondary)]">{selectedRun.branch_name || '—'}</span>
          </span>
          <span className="text-[var(--text-muted)]">
            Cost: <span className="font-mono">${selectedRun.total_cost.toFixed(2)}</span>
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* LangGraph Visualization */}
        <div className="border-b border-[var(--border-primary)]" style={{ minHeight: '320px' }}>
          <LangGraphVisualization />
        </div>

        {/* Bottom Panels */}
        <div className="grid grid-cols-3 gap-0 divide-x divide-[var(--border-primary)]">
          {/* Active Phases */}
          <div className="p-3">
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Active Phases</div>
            <div className="space-y-2">
              {phases.filter(p => p.status === 'running').map(phase => (
                <PhaseCard key={phase.id} phase={phase} expanded />
              ))}
              {phases.filter(p => p.status === 'running').length === 0 && (
                <div className="text-xs text-[var(--text-muted)]">No active phases</div>
              )}
            </div>
          </div>

          {/* Live Logs */}
          <div className="p-3">
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
              Live Logs ({logs.length})
            </div>
            <LogViewer logs={logs.slice(-30)} />
          </div>

          {/* Live Events + Cost */}
          <div className="p-3 space-y-3">
            <CostWidget report={costReport} />
            <div>
              <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                Live Events ({liveEvents.length})
              </div>
              <div className="max-h-32 overflow-auto space-y-1">
                {liveEvents.slice(-15).reverse().map((evt, i) => (
                  <div key={i} className="text-xs font-mono flex gap-2 py-0.5">
                    <span className="text-[var(--text-muted)] shrink-0">
                      {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '—'}
                    </span>
                    <span className={clsx(
                      'shrink-0',
                      (evt as any).severity === 'error' ? 'text-[var(--accent-red)]' :
                      (evt as any).severity === 'warning' ? 'text-[var(--accent-amber)]' :
                      (evt as any).severity === 'critical' ? 'text-[var(--accent-red)]' :
                      'text-[var(--accent-cyan)]'
                    )}>
                      {evt.type}
                    </span>
                    <span className="text-[var(--text-secondary)] truncate">
                      {(evt.data as any)?.message || ''}
                    </span>
                  </div>
                ))}
                {liveEvents.length === 0 && (
                  <div className="text-xs text-[var(--text-muted)]">Waiting for events...</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
