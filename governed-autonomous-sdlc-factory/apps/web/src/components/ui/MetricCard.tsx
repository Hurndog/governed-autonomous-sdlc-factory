// apps/web/src/components/ui/MetricCard.tsx
import { cn } from '@/lib/utils';
import { Badge } from './Badge';

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral' | 'warning';
  icon?: React.ReactNode;
  className?: string;
  badge?: { label: string; variant: 'green' | 'blue' | 'amber' | 'red' | 'violet' | 'zinc' | 'cyan' };
}

export function MetricCard({ label, value, change, changeType = 'neutral', icon, className, badge }: MetricCardProps) {
  const changeColor = changeType === 'positive' ? 'text-emerald-400' : changeType === 'negative' ? 'text-red-400' : changeType === 'warning' ? 'text-amber-400' : 'text-zinc-500';
  return (
    <div className={cn('card p-4 flex flex-col gap-2', className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">{label}</span>
        {icon && <span className="text-zinc-600">{icon}</span>}
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-semibold tracking-tight text-zinc-100">{value}</span>
        {change && <span className={cn('text-xs font-medium mb-0.5', changeColor)}>{change}</span>}
      </div>
      {badge && <Badge variant={badge.variant} dot>{badge.label}</Badge>}
    </div>
  );
}
