// apps/web/src/components/ui/ProgressBar.tsx
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number; // 0-1
  className?: string;
  color?: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'cyan';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
}

const colorMap = {
  blue: 'bg-blue-400',
  green: 'bg-emerald-400',
  amber: 'bg-amber-400',
  red: 'bg-red-400',
  violet: 'bg-violet-400',
  cyan: 'bg-cyan-400',
};

const glowMap = {
  blue: 'shadow-[0_0_8px_rgba(96,165,250,0.4)]',
  green: 'shadow-[0_0_8px_rgba(52,211,153,0.4)]',
  amber: 'shadow-[0_0_8px_rgba(251,191,36,0.4)]',
  red: 'shadow-[0_0_8px_rgba(248,113,113,0.4)]',
  violet: 'shadow-[0_0_8px_rgba(167,139,250,0.4)]',
  cyan: 'shadow-[0_0_8px_rgba(34,211,238,0.4)]',
};

const sizeMap = { sm: 'h-1', md: 'h-1.5', lg: 'h-2.5' };

export function ProgressBar({ value, className, color = 'blue', size = 'md', showLabel, animated }: ProgressBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className={cn('flex-1 bg-zinc-800/60 rounded-full overflow-hidden', sizeMap[size])}>
        <div
          className={cn(
            'h-full rounded-full transition-all duration-700 ease-out',
            colorMap[color],
            animated && value > 0 && glowMap[color]
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && <span className="text-xs text-zinc-500 font-mono w-8 text-right">{pct}%</span>}
    </div>
  );
}
