'use client';

import React from 'react';
import { useStore } from '@/lib/store';
import { StatusDot } from '@/components/ui/Card';
import { Activity, Clock, GitBranch, Zap } from 'lucide-react';

const roomLabels: Record<string, string> = {
  'command-center': 'Command Center',
  'spec-room': 'Specification Room',
  'architecture-room': 'Architecture Room',
  'governance-room': 'Governance Room',
  'replay-chamber': 'Replay Chamber',
};

export function TopBar() {
  const activeRoom = useStore((s) => s.activeRoom);
  const health = useStore((s) => s.health);
  const wsConnected = useStore((s) => s.wsConnected);

  return (
    <header className="h-12 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-sm flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-[11px] font-mono text-zinc-400">
          {roomLabels[activeRoom] || 'Unknown'}
        </span>
        <span className="text-zinc-700">/</span>
        <span className="text-[10px] font-mono text-zinc-600">COGNITIVE CORTEX v1.0</span>
      </div>

      <div className="flex items-center gap-6">
        {/* Runtime Health */}
        <div className="flex items-center gap-2">
          <StatusDot status={health?.status || 'inactive'} size="sm" pulse={health?.status === 'healthy'} />
          <span className="text-[10px] font-mono text-zinc-500 uppercase">
            {health?.status || 'Unknown'}
          </span>
        </div>

        {/* WS */}
        <div className="flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-zinc-600" />
          <span className="text-[10px] font-mono text-zinc-600">
            {wsConnected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>

        {/* Uptime */}
        {health?.uptime && (
          <div className="flex items-center gap-1.5">
            <Clock className="w-3 h-3 text-zinc-600" />
            <span className="text-[10px] font-mono text-zinc-600">
              {Math.floor(health.uptime / 60)}m
            </span>
          </div>
        )}

        {/* Version */}
        <div className="flex items-center gap-1.5">
          <GitBranch className="w-3 h-3 text-zinc-600" />
          <span className="text-[10px] font-mono text-zinc-600">{health?.version || '—'}</span>
        </div>
      </div>
    </header>
  );
}
