'use client';

import { useStore } from '@/store';
import { PhaseCard } from '@/components/ui/PhaseCard';
import { LogViewer } from '@/components/ui/LogViewer';
import { CostWidget } from '@/components/ui/CostWidget';
import { clsx } from 'clsx';

const PIPELINE_PHASES = [
  'intake', 'context_injection', 'spec_generation', 'cross_domain_validation',
  'functional_design', 'technical_architecture', 'governance_design', 'test_design',
  'approval', 'backlog_creation', 'branch_creation', 'build_execution',
  'code_documentation', 'commit', 'test_execution', 'security_scan',
  'governance_scan', 'refactor_loop', 'evidence_bundle', 'pattern_extraction',
  'cost_report', 'localhost_deployment',
];

export function LiveFactoryRun() {
  const { selectedRun, phases, logs, costReport, liveEvents } = useStore();

  if (!selectedRun) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-4xl mb-4">🏭</div>
          <h2 className="text-xl font-semibold mb-2">Live Factory Run</h2>
          <p className="text-sm text-[var(--text-muted)]">Select a run from Command Center to view the pipeline</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Run Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold">{selectedRun.name}</h1>
          <div className="flex items-center gap-3 text-sm text-[var(--text-muted)]">
            <span className={clsx('status-dot', `status-${selectedRun.status}`)} />
            <span>{selectedRun.status}</span>
            <span>·</span>
            <span>{selectedRun.branch_name || 'no branch'}</span>
            <span>·</span>
            <span>${selectedRun.total_cost.toFixed(2)}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--text-muted)]">
            {phases.filter(p => p.status === 'completed').length}/{PIPELINE_PHASES.length} phases
          </span>
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-11 gap-1 mb-4">
          {PIPELINE_PHASES.map((phaseName, i) => {
            const phase = phases.find(p => p.name === phaseName);
            const status = phase?.status || 'pending';
            return (
              <div
                key={phaseName}
                className={clsx(
                  'text-center py-2 px-1 rounded text-xs font-mono',
                  status === 'completed' && 'bg-[var(--accent-green)]/20 text-[var(--accent-green)]',
                  status === 'running' && 'bg-[var(--accent-blue)]/20 text-[var(--accent-blue)] animate-pulse',
                  status === 'failed' && 'bg-[var(--accent-red)]/20 text-[var(--accent-red)]',
                  status === 'pending' && 'bg-[var(--bg-tertiary)] text-[var(--text-muted)]',
                )}
                title={phaseName}
              >
                <div className="truncate">{i + 1}. {phaseName.replace(/_/g, ' ')}</div>
              </div>
            );
          })}
        </div>

        {/* Phase Cards */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {phases.filter(p => p.status === 'running').map(phase => (
            <PhaseCard key={phase.id} phase={phase} expanded />
          ))}
        </div>

        {/* Bottom Panels */}
        <div className="grid grid-cols-3 gap-4">
          {/* Logs */}
          <div className="panel p-3">
            <div className="panel-header -mx-3 -mt-3 mb-3">Live Logs</div>
            <LogViewer logs={logs} />
          </div>

          {/* Cost */}
          <div>
            <CostWidget report={costReport} />
          </div>

          {/* Live Events */}
          <div className="panel p-3">
            <div className="panel-header -mx-3 -mt-3 mb-3">Live Events ({liveEvents.length})</div>
            <div className="max-h-48 overflow-auto space-y-1">
              {liveEvents.slice(-20).reverse().map((evt, i) => (
                <div key={i} className="text-xs font-mono flex gap-2">
                  <span className="text-[var(--text-muted)] shrink-0">
                    {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '—'}
                  </span>
                  <span className="text-[var(--accent-cyan)]">{evt.type}</span>
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
  );
}
