import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export function formatCost(cents: number): string {
  return `$${(cents / 100).toFixed(4)}`;
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

export function formatTimestamp(ts: string): string {
  return new Date(ts).toLocaleTimeString('nl-NL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    running: 'text-emerald-400',
    completed: 'text-emerald-400',
    failed: 'text-red-400',
    pending: 'text-amber-400',
    warning: 'text-amber-400',
    error: 'text-red-400',
    active: 'text-emerald-400',
    inactive: 'text-zinc-500',
    healthy: 'text-emerald-400',
    degraded: 'text-amber-400',
    critical: 'text-red-400',
  };
  return map[status.toLowerCase()] || 'text-zinc-400';
}

export function statusBgColor(status: string): string {
  const map: Record<string, string> = {
    running: 'bg-emerald-400/10 border-emerald-400/20',
    completed: 'bg-emerald-400/10 border-emerald-400/20',
    failed: 'bg-red-400/10 border-red-400/20',
    pending: 'bg-amber-400/10 border-amber-400/20',
    warning: 'bg-amber-400/10 border-amber-400/20',
    error: 'bg-red-400/10 border-red-400/20',
    active: 'bg-emerald-400/10 border-emerald-400/20',
    inactive: 'bg-zinc-500/10 border-zinc-500/20',
  };
  return map[status.toLowerCase()] || 'bg-zinc-400/10 border-zinc-400/20';
}
