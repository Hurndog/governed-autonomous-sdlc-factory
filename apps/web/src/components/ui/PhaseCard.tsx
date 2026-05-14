'use client';

import type { Phase } from '@/types';
import { clsx } from 'clsx';

interface PhaseCardProps {
  phase: Phase;
  expanded?: boolean;
}

export function PhaseCard({ phase, expanded = false }: PhaseCardProps) {
  return (
    <div className={clsx('panel p-3', expanded && 'ring-1 ring-[var(--accent-blue)]')}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={clsx('status-dot', `status-${phase.status}`)} />
          <span className="text-sm font-medium">{phase.name}</span>
        </div>
        <span className="text-xs text-[var(--text-muted)]">#{phase.order_index}</span>
      </div>

      {expanded && (
        <div className="space-y-2 mt-3">
          <div className="grid grid-cols-2 gap-2 text-xs">
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
              <span className="text-[var(--text-muted)]">Duration:</span>
              <span className="ml-1">
                {phase.started_at && phase.completed_at
                  ? `${Math.round((new Date(phase.completed_at).getTime() - new Date(phase.started_at).getTime()) / 1000)}s`
                  : '—'}
              </span>
            </div>
          </div>

          {phase.error_message && (
            <div className="text-xs text-[var(--accent-red)] bg-[var(--accent-red)]/10 rounded p-2 mt-2">
              {phase.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
