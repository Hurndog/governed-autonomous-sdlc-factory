import { cn } from '@/lib/utils';

type BadgeVariant = 'green' | 'blue' | 'amber' | 'red' | 'violet' | 'zinc' | 'cyan';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
  dot?: boolean;
  size?: 'sm' | 'md';
}

const variantClasses: Record<BadgeVariant, string> = {
  green: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  blue: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
  amber: 'bg-amber-400/10 text-amber-400 border-amber-400/20',
  red: 'bg-red-400/10 text-red-400 border-red-400/20',
  violet: 'bg-violet-400/10 text-violet-400 border-violet-400/20',
  zinc: 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30',
  cyan: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20',
};

const dotClasses: Record<BadgeVariant, string> = {
  green: 'bg-emerald-400',
  blue: 'bg-blue-400',
  amber: 'bg-amber-400',
  red: 'bg-red-400',
  violet: 'bg-violet-400',
  zinc: 'bg-zinc-500',
  cyan: 'bg-cyan-400',
};

export function Badge({ variant = 'zinc', children, className, dot, size = 'md' }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 rounded font-medium border',
      variantClasses[variant],
      size === 'sm' ? 'px-1.5 py-0.5 text-[9px]' : 'px-2 py-0.5 text-xs',
      className
    )}>
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dotClasses[variant])} />}
      {children}
    </span>
  );
}
