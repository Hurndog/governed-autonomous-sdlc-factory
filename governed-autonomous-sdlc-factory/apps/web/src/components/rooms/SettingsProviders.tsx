'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { Server, Cpu, HardDrive, Wifi, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';
import type { HealthResponse, ModelStatusResponse } from '@/lib/api';

export function SettingsProviders() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, modelsRes] = await Promise.allSettled([
        api.getHealth(),
        api.getModelStatus(),
      ]);
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
      if (modelsRes.status === 'fulfilled') setModelStatus(modelsRes.value);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const providers = (modelStatus?.providers || [
    { name: 'OpenAI', default_model: 'gpt-4o', status: 'online' as const, is_local: false },
    { name: 'Anthropic', default_model: 'claude-sonnet-4', status: 'online' as const, is_local: false },
    { name: 'Local LM Studio', default_model: 'llama-3.1-70b', status: 'online' as const, is_local: true },
    { name: 'Ollama', default_model: 'codellama-34b', status: 'offline' as const, is_local: true },
  ]).map(p => ({
    name: p.name,
    model: p.default_model || '—',
    status: p.status,
    is_local: p.is_local,
    latency: '—',
    requests: 0,
  }));

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Settings & Providers" subtitle="Model provider configuration" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Backend Health */}
      {health && (
        <div className="card p-4">
          <SectionHeader title="Backend Health" />
          <div className="grid grid-cols-4 gap-3 mt-2">
            <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
              <div className="text-[9px] text-zinc-700 uppercase">Status</div>
              <div className="flex items-center gap-1 mt-0.5">
                {health.status === 'healthy' ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <XCircle className="w-3 h-3 text-red-400" />}
                <span className="text-[10px] text-zinc-300">{health.status}</span>
              </div>
            </div>
            <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
              <div className="text-[9px] text-zinc-700 uppercase">Version</div>
              <div className="text-[10px] text-zinc-300 mt-0.5">{health.version || '—'}</div>
            </div>
            <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
              <div className="text-[9px] text-zinc-700 uppercase">Database</div>
              <div className="flex items-center gap-1 mt-0.5">
                {health.database === 'connected' ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <XCircle className="w-3 h-3 text-red-400" />}
                <span className="text-[10px] text-zinc-300">{health.database}</span>
              </div>
            </div>
            <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
              <div className="text-[9px] text-zinc-700 uppercase">Uptime</div>
              <div className="text-[10px] text-zinc-300 mt-0.5">{health.uptime_seconds ? `${Math.round(health.uptime_seconds)}s` : '—'}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <SectionHeader title="Model Providers" subtitle={`${providers.length} providers configured`} />
          <div className="space-y-2 mt-2">
            {providers.map(p => (
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
