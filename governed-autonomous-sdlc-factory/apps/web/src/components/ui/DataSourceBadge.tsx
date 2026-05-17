'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { DataSourceState, getDataSourceConfig } from '@/lib/data-source';

interface DataSourceBadgeProps {
  state: DataSourceState;
  className?: string;
  showLabel?: boolean;
}

export function DataSourceBadge({ state, className, showLabel = true }: DataSourceBadgeProps) {
  const config = getDataSourceConfig(state);
  return (
    <span className={cn(
      'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[8px] font-semibold uppercase tracking-wider border',
      config.color, config.bg, config.border,
      className
    )}>
      <span className={cn('w-1 h-1 rounded-full', config.color.replace('text-', 'bg-'))} />
      {showLabel && config.label}
    </span>
  );
}

export function DataSourceBanner({ state, message }: { state: DataSourceState; message?: string }) {
  if (state === 'LIVE') return null;
  
  const config = getDataSourceConfig(state);
  return (
    <div className={cn(
      'flex items-center gap-2 px-3 py-1.5 rounded-md text-[10px] border mb-3',
      config.color, config.bg, config.border
    )}>
      <span className={cn('w-1.5 h-1.5 rounded-full', config.color.replace('text-', 'bg-'))} />
      <span>
        {state === 'MOCK' && 'Showing mock data — backend endpoint not yet available'}
        {state === 'PARTIAL' && 'Partially connected — some data from backend, some from mock fallback'}
        {state === 'ERROR' && 'Backend connection failed — showing fallback data'}
        {state === 'LOADING' && 'Loading data from backend...'}
        {message && ` — ${message}`}
      </span>
    </div>
  );
}
