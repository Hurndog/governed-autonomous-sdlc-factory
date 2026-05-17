'use client';

import React from 'react';
import { useStore } from '@/lib/store';
import { mockApplication, mockBuildRun, mockScores } from '@/lib/mock-data';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Wifi, WifiOff, Bell } from 'lucide-react';

export function TopBar() {
  const wsConnected = useStore((s) => s.wsConnected);

  return (
    <header className="h-11 border-b border-[#1e2230] bg-[#0a0b0f]/80 backdrop-blur-sm flex items-center justify-between px-4 flex-shrink-0">
      {/* Left: App info */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          <span className="text-xs font-semibold text-zinc-200">{mockApplication.name}</span>
          <Badge variant="violet" size="sm">v1.0</Badge>
        </div>
        <div className="h-3 w-px bg-zinc-800" />
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-600">Run</span>
          <span className="text-[10px] font-mono text-zinc-400">{mockBuildRun.id.slice(0, 12)}</span>
        </div>
        <div className="h-3 w-px bg-zinc-800" />
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-zinc-600">Progress</span>
          <div className="w-20">
            <ProgressBar value={mockScores.overloadProgress} size="sm" color="violet" />
          </div>
          <span className="text-[10px] font-mono text-zinc-500">{Math.round(mockScores.overallProgress * 100)}%</span>
        </div>
      </div>

      {/* Right: Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          {wsConnected ? (
            <Wifi className="w-3 h-3 text-emerald-400" />
          ) : (
            <WifiOff className="w-3 h-3 text-red-400" />
          )}
          <span className="text-[9px] text-zinc-600 uppercase tracking-wider">
            {wsConnected ? 'Live' : 'Offline'}
          </span>
        </div>
        <div className="h-3 w-px bg-zinc-800" />
        <div className="flex items-center gap-1.5">
          <Bell className="w-3 h-3 text-zinc-600" />
          <span className="text-[9px] text-zinc-600">2</span>
        </div>
        <div className="h-3 w-px bg-zinc-800" />
        <div className="flex items-center gap-1.5">
          <div className="w-5 h-5 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
            <span className="text-[8px] font-bold text-violet-400">M</span>
          </div>
        </div>
      </div>
    </header>
  );
}
