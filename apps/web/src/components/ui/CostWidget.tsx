'use client';

import type { CostReport } from '@/types';

interface CostWidgetProps {
  report: CostReport | null;
}

export function CostWidget({ report }: CostWidgetProps) {
  if (!report) {
    return (
      <div className="panel p-3">
        <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Cost Control</div>
        <div className="text-xs text-[var(--text-muted)]">No cost data yet</div>
      </div>
    );
  }

  const pct = report.budget_limit
    ? Math.min((report.total_cost / report.budget_limit) * 100, 100)
    : 0;

  return (
    <div className="panel p-3">
      <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Cost Control</div>

      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-mono font-bold">${report.total_cost.toFixed(2)}</span>
        {report.budget_limit && (
          <span className="text-xs text-[var(--text-muted)]">/ ${report.budget_limit.toFixed(2)}</span>
        )}
      </div>

      {report.budget_limit && (
        <div className="w-full h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden mb-2">
          <div
            className={`h-full rounded-full transition-all ${
              report.is_hard_limit_reached
                ? 'bg-[var(--accent-red)]'
                : report.is_near_limit
                ? 'bg-[var(--accent-amber)]'
                : 'bg-[var(--accent-green)]'
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-[var(--text-muted)]">Local:</span>
          <span className="ml-1 text-[var(--accent-green)]">${report.local_cost.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Paid:</span>
          <span className="ml-1 text-[var(--accent-amber)]">${report.paid_cost.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Saved:</span>
          <span className="ml-1 text-[var(--accent-cyan)]">${report.estimated_savings.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Remaining:</span>
          <span className="ml-1">
            {report.remaining_budget !== null ? `$${report.remaining_budget.toFixed(2)}` : '∞'}
          </span>
        </div>
      </div>
    </div>
  );
}
