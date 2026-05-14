'use client';

import type { LogEvent } from '@/types';
import { clsx } from 'clsx';

interface LogViewerProps {
  logs: LogEvent[];
  compact?: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'text-[var(--accent-red)]',
  error: 'text-[var(--accent-red)]',
  warning: 'text-[var(--accent-amber)]',
  info: 'text-[var(--accent-blue)]',
  debug: 'text-[var(--text-muted)]',
};

export function LogViewer({ logs, compact = false }: LogViewerProps) {
  if (logs.length === 0) {
    return <div className="text-xs text-[var(--text-muted)] py-2">No logs yet</div>;
  }

  return (
    <div className={clsx('space-y-1', compact ? 'max-h-48' : 'max-h-96', 'overflow-auto')}>
      {logs.map((log) => (
        <div key={log.id} className="text-xs font-mono flex gap-2 py-0.5">
          <span className="text-[var(--text-muted)] shrink-0">
            {new Date(log.created_at).toLocaleTimeString()}
          </span>
          <span className={clsx('shrink-0 w-12', SEVERITY_COLORS[log.severity])}>
            {log.severity.toUpperCase().slice(0, 5)}
          </span>
          <span className="text-[var(--text-secondary)] truncate">{log.message}</span>
        </div>
      ))}
    </div>
  );
}
