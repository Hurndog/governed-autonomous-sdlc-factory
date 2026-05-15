'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: 'none' | 'emerald' | 'amber' | 'red' | 'blue';
  onClick?: () => void;
}

export function Card({ children, className, glow = 'none', onClick }: CardProps) {
  const glowMap = {
    none: '',
    emerald: 'shadow-emerald-500/5 shadow-lg',
    amber: 'shadow-amber-500/5 shadow-lg',
    red: 'shadow-red-500/5 shadow-lg',
    blue: 'shadow-blue-500/5 shadow-lg',
  };

  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-zinc-900/80 border border-zinc-800 rounded-lg p-4 backdrop-blur-sm',
        glowMap[glow],
        onClick && 'cursor-pointer hover:border-zinc-700 transition-colors',
        className
      )}
    >
      {children}
    </div>
  );
}

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'emerald' | 'amber' | 'red' | 'blue' | 'zinc';
  size?: 'sm' | 'md';
}

export function Badge({ children, variant = 'default', size = 'sm' }: BadgeProps) {
  const variantMap = {
    default: 'bg-zinc-800 text-zinc-300 border-zinc-700',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    red: 'bg-red-500/10 text-red-400 border-red-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    zinc: 'bg-zinc-700/50 text-zinc-400 border-zinc-600',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center border rounded font-mono font-medium',
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs',
        variantMap[variant]
      )}
    >
      {children}
    </span>
  );
}

interface MetricProps {
  label: string;
  value: string | number;
  sub?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

export function Metric({ label, value, sub, trend, color }: MetricProps) {
  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
  const trendColor =
    trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-red-400' : 'text-zinc-500';

  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">{label}</span>
      <div className="flex items-baseline gap-2">
        <span className={cn('text-2xl font-mono font-bold', color || 'text-zinc-100')}>
          {value}
        </span>
        {trend && <span className={cn('text-xs font-mono', trendColor)}>{trendIcon}</span>}
      </div>
      {sub && <span className="text-[10px] text-zinc-600 font-mono">{sub}</span>}
    </div>
  );
}

interface StatusDotProps {
  status: 'healthy' | 'degraded' | 'critical' | 'running' | 'completed' | 'failed' | 'pending' | 'active' | 'inactive';
  size?: 'sm' | 'md' | 'lg';
  pulse?: boolean;
}

export function StatusDot({ status, size = 'md', pulse = false }: StatusDotProps) {
  const colorMap: Record<string, string> = {
    healthy: 'bg-emerald-400',
    completed: 'bg-emerald-400',
    running: 'bg-emerald-400',
    active: 'bg-emerald-400',
    degraded: 'bg-amber-400',
    pending: 'bg-amber-400',
    critical: 'bg-red-400',
    failed: 'bg-red-400',
    inactive: 'bg-zinc-600',
  };

  const sizeMap = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-3 h-3',
  };

  return (
    <span className="relative flex items-center justify-center">
      <span
        className={cn(
          'rounded-full',
          sizeMap[size],
          colorMap[status] || 'bg-zinc-500',
          pulse && 'animate-pulse'
        )}
      />
    </span>
  );
}

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: 'emerald' | 'amber' | 'red' | 'blue' | 'zinc';
  size?: 'sm' | 'md';
  showLabel?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  color = 'emerald',
  size = 'md',
  showLabel = false,
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const colorMap = {
    emerald: 'bg-emerald-400',
    amber: 'bg-amber-400',
    red: 'bg-red-400',
    blue: 'bg-blue-400',
    zinc: 'bg-zinc-500',
  };

  return (
    <div className="flex items-center gap-2 w-full">
      <div
        className={cn(
          'flex-1 bg-zinc-800 rounded-full overflow-hidden',
          size === 'sm' ? 'h-1' : 'h-2'
        )}
      >
        <div
          className={cn('h-full rounded-full transition-all duration-500', colorMap[color])}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-[10px] font-mono text-zinc-500 w-8 text-right">
          {Math.round(pct)}%
        </span>
      )}
    </div>
  );
}

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export function SectionHeader({ title, subtitle, icon, action }: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        {icon && <span className="text-zinc-500">{icon}</span>}
        <div>
          <h2 className="text-sm font-semibold text-zinc-200 uppercase tracking-wider font-mono">
            {title}
          </h2>
          {subtitle && <p className="text-[10px] text-zinc-600 font-mono mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}
