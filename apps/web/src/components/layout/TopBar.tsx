'use client';

import { useStore } from '@/store';
import { clsx } from 'clsx';

export function TopBar() {
  const { selectedProject, selectedRun, phases, costReport } = useStore();

  const currentPhase = selectedRun?.current_phase
    ? phases.find((p) => p.name === selectedRun.current_phase)
    : null;

  return (
    <header className="h-12 bg-[var(--bg-secondary)] border-b border-[var(--border-primary)] flex items-center px-4 gap-6">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded bg-[var(--accent-blue)] flex items-center justify-center text-xs font-bold">F</div>
        <span className="font-semibold text-sm">Forge Control Tower</span>
      </div>

      {/* Project */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Project:</span>
        <span className="text-sm font-medium">{selectedProject?.name || '—'}</span>
      </div>

      {/* Run */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Run:</span>
        <span className="text-sm font-medium text-[var(--accent-cyan)]">{selectedRun?.name || '—'}</span>
      </div>

      {/* Phase */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Phase:</span>
        <span className="text-sm">
          {currentPhase ? (
            <span className="flex items-center gap-1.5">
              <span className={clsx('status-dot', `status-${currentPhase.status}`)} />
              {currentPhase.name}
            </span>
          ) : '—'}
        </span>
      </div>

      {/* Branch */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Branch:</span>
        <span className="text-sm font-mono text-[var(--text-secondary)]">{selectedRun?.branch_name || '—'}</span>
      </div>

      {/* Cost */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Cost:</span>
        <span className={clsx('text-sm font-mono', costReport?.is_near_limit ? 'text-[var(--accent-amber)]' : '')}>
          ${selectedRun?.total_cost?.toFixed(2) || '0.00'}
          {selectedRun?.budget_limit ? ` / $${selectedRun.budget_limit.toFixed(2)}` : ''}
        </span>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Deployment Status */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Deploy:</span>
        <span className="text-sm">—</span>
      </div>

      {/* Model */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--text-muted)]">Model:</span>
        <span className="text-sm text-[var(--text-secondary)]">local</span>
      </div>
    </header>
  );
}
