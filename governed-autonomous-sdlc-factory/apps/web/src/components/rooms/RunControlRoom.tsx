'use client';
import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useStore } from '@/lib/store';
import { Play, Square, RotateCcw, Clock, Bot, Coins, AlertTriangle } from 'lucide-react';

export function RunControlRoom() {
  const runs = useStore((s) => s.runs);

  const mockRuns = [
    { id: 'run-7ff8a2fd', status: 'active', phase: 'Semantic Coverage', progress: 0.72, tokens: 174100, cost: 1.847, startedAt: '2026-05-14T06:00:00Z' },
    { id: 'run-3a1b2c3d', status: 'completed', phase: 'Release', progress: 1.0, tokens: 89200, cost: 0.945, startedAt: '2026-05-13T10:00:00Z' },
    { id: 'run-5e6f7g8h', status: 'failed', phase: 'Implementation', progress: 0.45, tokens: 124000, cost: 2.124, startedAt: '2026-05-12T14:00:00Z' },
  ];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Run Control" subtitle="Manage build runs" />

      <div className="grid grid-cols-3 gap-4">
        {mockRuns.map(run => (
          <div key={run.id} className={`card p-4 border ${
            run.status === 'active' ? 'border-blue-400/20 glow-blue' :
            run.status === 'completed' ? 'border-emerald-400/20' :
            'border-red-400/20'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-zinc-400">{run.id.slice(0, 12)}</span>
                <StatusChip status={run.status === 'active' ? 'active' : run.status === 'completed' ? 'verified' : 'failed'} size="sm" />
              </div>
              {run.status === 'active' && (
                <div className="flex items-center gap-1">
                  <button className="p-1 rounded hover:bg-zinc-800/50 text-amber-400"><Square className="w-3 h-3" /></button>
                  <button className="p-1 rounded hover:bg-zinc-800/50 text-red-400"><RotateCcw className="w-3 h-3" /></button>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Phase</span>
                <span className="text-zinc-400">{run.phase}</span>
              </div>
              <ProgressBar value={run.progress} size="sm" color={run.status === 'active' ? 'blue' : run.status === 'completed' ? 'green' : 'red'} showLabel />
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Tokens</span>
                <span className="text-zinc-400">{(run.tokens / 1000).toFixed(1)}k</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Cost</span>
                <span className="text-zinc-400">${run.cost.toFixed(3)}</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Started</span>
                <span className="text-zinc-400">{run.startedAt.slice(0, 16).replace('T', ' ')}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
