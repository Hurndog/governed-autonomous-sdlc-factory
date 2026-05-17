import { cn } from '@/lib/utils';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
}

export function SectionHeader({ title, subtitle, action, className, icon }: SectionHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between mb-4', className)}>
      <div className="flex items-center gap-2">
        {icon && <span className="text-zinc-600">{icon}</span>}
        <div>
          <h2 className="text-sm font-semibold text-zinc-100 uppercase tracking-widest">{title}</h2>
          {subtitle && <p className="text-xs text-zinc-500 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
