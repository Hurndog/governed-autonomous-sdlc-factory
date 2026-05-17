// apps/web/src/components/ui/GaugeChart.tsx
import { cn } from '@/lib/utils';

interface GaugeChartProps {
  value: number; // 0-1
  label: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  color?: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'cyan';
  showValue?: boolean;
}

const colorConfig = {
  blue: { stroke: '#60a5fa', glow: 'rgba(96,165,250,0.3)' },
  green: { stroke: '#34d399', glow: 'rgba(52,211,153,0.3)' },
  amber: { stroke: '#fbbf24', glow: 'rgba(251,191,36,0.3)' },
  red: { stroke: '#f87171', glow: 'rgba(248,113,113,0.3)' },
  violet: { stroke: '#a78bfa', glow: 'rgba(167,139,250,0.3)' },
  cyan: { stroke: '#22d3ee', glow: 'rgba(34,211,238,0.3)' },
};

const sizes = {
  sm: { width: 80, stroke: 5, fontSize: 14, labelSize: 9 },
  md: { width: 120, stroke: 6, fontSize: 20, labelSize: 10 },
  lg: { width: 160, stroke: 8, fontSize: 28, labelSize: 11 },
};

export function GaugeChart({ value, label, size = 'md', className, color = 'blue', showValue = true }: GaugeChartProps) {
  const s = sizes[size];
  const c = colorConfig[color];
  const radius = (s.width - s.stroke) / 2;
  const circumference = Math.PI * radius; // half circle
  const filled = circumference * Math.min(Math.max(value, 0), 1);
  const pct = Math.round(value * 100);

  return (
    <div className={cn('flex flex-col items-center gap-1', className)}>
      <svg width={s.width} height={s.width / 2 + 10} viewBox={`0 0 ${s.width} ${s.width / 2 + 10}`}>
        {/* Background arc */}
        <path
          d={`M ${s.stroke / 2} ${s.width / 2} A ${radius} ${radius} 0 0 1 ${s.width - s.stroke / 2} ${s.width / 2}`}
          fill="none"
          stroke="#1e2230"
          strokeWidth={s.stroke}
          strokeLinecap="round"
        />
        {/* Filled arc */}
        {value > 0 && (
          <path
            d={`M ${s.stroke / 2} ${s.width / 2} A ${radius} ${radius} 0 0 1 ${s.width - s.stroke / 2} ${s.width / 2}`}
            fill="none"
            stroke={c.stroke}
            strokeWidth={s.stroke}
            strokeLinecap="round"
            strokeDasharray={`${filled} ${circumference}`}
            style={{ filter: `drop-shadow(0 0 4px ${c.glow})` }}
          />
        )}
        {/* Value text */}
        {showValue && (
          <text
            x={s.width / 2}
            y={s.width / 2 - 4}
            textAnchor="middle"
            fill="#e8eaed"
            fontSize={s.fontSize}
            fontWeight="600"
            fontFamily="monospace"
          >
            {pct}
          </text>
        )}
      </svg>
      <span className="text-zinc-500 uppercase tracking-wider font-medium" style={{ fontSize: s.labelSize }}>
        {label}
      </span>
    </div>
  );
}
