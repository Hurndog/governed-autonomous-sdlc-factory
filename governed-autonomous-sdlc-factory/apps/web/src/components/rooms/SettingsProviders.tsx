'use client';
import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { useStore } from '@/lib/store';
import { Server, Cpu, HardDrive, Wifi, CheckCircle2, XCircle } from 'lucide-react';

export function SettingsProviders() {
  const modelStatus = useStore((s) => s.modelStatus);

  const mockProviders = [
    { name: 'OpenAI', model: 'gpt-4o', status: 'online', latency: '142ms', requests: 1247 },
    { name: 'Anthropic', model: 'claude-sonnet-4', status: 'online', latency: '198ms', requests: 892 },
    { name: 'Local LM Studio', model: 'llama-3.1-70b', status: 'online', latency: '45ms', requests: 2103 },
    { name: 'Ollama', model: 'codellama-34b', status: 'offline', latency: '—', requests: 0 },
  ];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Settings & Providers" subtitle="Model provider configuration" />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <SectionHeader title="Model Providers" />
          <div className="space-y-2 mt-2">
            {mockProviders.map(p => (
              <div key={p.name} className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <Server className="w-4 h-4 text-zinc-500" />
                <div className="flex-1">
                  <div className="text-[11px] font-medium text-zinc-300">{p.name}</div>
                  <div className="text-[9px] text-zinc-600">{p.model}</div>
                </div>
                <StatusChip status={p.status === 'online' ? 'verified' : 'failed'} size="sm" />
                <span className="text-[10px] font-mono text-zinc-600 w-16 text-right">{p.latency}</span>
                <span className="text-[10px] font-mono text-zinc-600 w-12 text-right">{p.requests}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-4 card p-4">
          <SectionHeader title="System Resources" />
          <div className="space-y-3 mt-2">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-zinc-500 flex items-center gap-1"><Cpu className="w-3 h-3" /> CPU</span>
                <span className="text-[10px] font-mono text-zinc-400">34%</span>
              </div>
              <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-400/60 rounded-full" style={{ width: '34%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-zinc-500 flex items-center gap-1"><HardDrive className="w-3 h-3" /> Memory</span>
                <span className="text-[10px] font-mono text-zinc-400">8.2 / 32 GB</span>
              </div>
              <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-violet-400/60 rounded-full" style={{ width: '26%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-zinc-500 flex items-center gap-1"><Wifi className="w-3 h-3" /> Network</span>
                <span className="text-[10px] font-mono text-zinc-400">12 MB/s</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
