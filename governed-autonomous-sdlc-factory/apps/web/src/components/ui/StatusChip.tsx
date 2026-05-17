import { cn } from '@/lib/utils';

type StatusType = 'verified' | 'accepted' | 'tested' | 'active' | 'working' | 'warning' | 'blocked' | 'failed' | 'pending' | 'idle' | 'partial' | 'missing' | 'covered' | 'rejected' | 'approved' | 'escalated' | 'waived' | 'generated' | 'implemented' | 'in-progress' | 'waiting' | 'error' | 'paused';

interface StatusChipProps {
  status: StatusType;
  className?: string;
  size?: 'sm' | 'md';
}

const statusConfig: Record<string, { label: string; classes: string; dot: string }> = {
  verified: { label: 'Verified', classes: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', dot: 'bg-emerald-400' },
  accepted: { label: 'Accepted', classes: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', dot: 'bg-emerald-400' },
  tested: { label: 'Tested', classes: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', dot: 'bg-emerald-400' },
  active: { label: 'Active', classes: 'bg-blue-400/10 text-blue-400 border-blue-400/20', dot: 'bg-blue-400' },
  working: { label: 'Working', classes: 'bg-blue-400/10 text-blue-400 border-blue-400/20', dot: 'bg-blue-400' },
  warning: { label: 'Warning', classes: 'bg-amber-400/10 text-amber-400 border-amber-400/20', dot: 'bg-amber-400' },
  blocked: { label: 'Blocked', classes: 'bg-red-400/10 text-red-400 border-red-400/20', dot: 'bg-red-400' },
  failed: { label: 'Failed', classes: 'bg-red-400/10 text-red-400 border-red-400/20', dot: 'bg-red-400' },
  generated: { label: 'Generated', classes: 'bg-amber-400/10 text-amber-400 border-amber-400/20', dot: 'bg-amber-400' },
  pending: { label: 'Pending', classes: 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30', dot: 'bg-zinc-500' },
  implemented: { label: 'Implemented', classes: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20', dot: 'bg-cyan-400' },
  'in-progress': { label: 'In Progress', classes: 'bg-blue-400/10 text-blue-400 border-blue-400/20', dot: 'bg-blue-400' },
  idle: { label: 'Idle', classes: 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30', dot: 'bg-zinc-500' },
  waiting: { label: 'Waiting', classes: 'bg-amber-400/10 text-amber-400 border-amber-400/20', dot: 'bg-amber-400' },
  error: { label: 'Error', classes: 'bg-red-400/10 text-red-400 border-red-400/20', dot: 'bg-red-400' },
  paused: { label: 'Paused', classes: 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30', dot: 'bg-zinc-500' },
  partial: { label: 'Partial', classes: 'bg-amber-400/10 text-amber-400 border-amber-400/20', dot: 'bg-amber-400' },
  missing: { label: 'Missing', classes: 'bg-red-400/10 text-red-400 border-red-400/20', dot: 'bg-red-400' },
  covered: { label: 'Covered', classes: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', dot: 'bg-emerald-400' },
  rejected: { label: 'Rejected', classes: 'bg-red-400/10 text-red-400 border-red-400/20', dot: 'bg-red-400' },
  approved: { label: 'Approved', classes: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20', dot: 'bg-emerald-400' },
  escalated: { label: 'Escalated', classes: 'bg-violet-400/10 text-violet-400 border-violet-400/20', dot: 'bg-violet-400' },
  waived: { label: 'Waived', classes: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20', dot: 'bg-cyan-400' },
};

export function StatusChip({ status, className, size = 'sm' }: StatusChipProps) {
  const config = statusConfig[status] || statusConfig.pending;
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 border rounded font-medium',
      config.classes,
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs',
      className
    )}>
      <span className={cn('rounded-full', config.dot, size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2')} />
      {config.label}
    </span>
  );
}
