'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockPhases, mockAgents } from '@/lib/mock-data';
import { CheckCircle2, Clock, AlertTriangle, Bot, ChevronRight, RefreshCw } from 'lucide-react';

type PhaseStatus = 'completed' | 'active' | 'pending' | 'blocked' | 'failed';

interface PhaseData {
  id: string; run_id: string; name: string; order_index: number; status: PhaseStatus;
  agent_id?: string; model_used?: string; tokens_in?: number; tokens_out?: number;
  cost?: number; error_message?: string; created_at?: string; completed_at?: string;
}

export function SDLCNavigator() {
  const [phases, setPhases] = useState<PhaseData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);

  const fetchPhases = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      try {
        const res = await api.listPhasesByRun(latestRun.id);
        const phaseList = Array.isArray(res) ? res : (res as { phases: PhaseData[] }).phases || [];
        if (phaseList.length > 0) {
          setPhases(phaseList as PhaseData[]);
          setDataSource('PARTIAL');
          const active = (phaseList as PhaseData[]).find(p => p.status === 'active');
          if (active) setExpandedPhase(active.id);
        } else { setDataSource('MOCK'); }
      } catch { setDataSource('MOCK'); }
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchPhases(); }, []);

  const displayPhases: PhaseData[] = phases.length > 0 ? phases : mockPhases.map(p => ({
    id: p.id, run_id: '', name: p.name, order_index: p.order, status: p.status as PhaseStatus,
    tokens_in: p.tokenUsage, tokens_out: 0, cost: 0, model_used: undefined, error_message: undefined,
  }));

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="SDLC Phase Navigator" subtitle={`${displayPhases.length} phases from intake to retrospective`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchPhases} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="card p-4">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-thin pb-2">
          {displayPhases.map((phase, i) => (
            <React.Fragment key={phase.id}>
              <button onClick={() => setExpandedPhase(expandedPhase === phase.id ? null : phase.id)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[10px] font-medium transition-all ${phase.status === 'completed' ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20' : phase.status === 'active' ? 'bg-blue-400/10 text-blue-400 border border-blue-400/20 ring-1 ring-blue-400/30' : phase.status === 'blocked' || phase.status === 'failed' ? 'bg-red-400/10 text-red-400 border border-red-400/20' : 'bg-zinc-800/30 text-zinc-600 border border-zinc-700/30'}`}>
                {phase.status === 'completed' ? <CheckCircle2 className="w-3 h-3" /> : phase.status === 'active' ? <Clock className="w-3 h-3 animate-pulse" /> : phase.status === 'blocked' || phase.status === 'failed' ? <AlertTriangle className="w-3 h-3" /> : <div className="w-3 h-3 rounded-full border border-zinc-600" />}
                {phase.name}
              </button>
              {i < displayPhases.length - 1 && (
                <ChevronRight className={`w-3 h-3 flex-shrink-0 ${phase.status === 'completed' ? 'text-emerald-400/40' : 'text-zinc-800'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          {expandedPhase && (
            <div className="card p-4">
              {(() => {
                const phase = displayPhases.find(p => p.id === expandedPhase);
                if (!phase) return null;
                return (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-zinc-200">{phase.name}</h3>
                        <p className="text-[10px] text-zinc-600">Status: {phase.status}{phase.model_used ? ` • Model: ${phase.model_used}` : ''}{phase.tokens_in !== undefined ? ` • Tokens: ${(phase.tokens_in / 1000).toFixed(1)}k` : ''}</p>
                      </div>
                      <StatusChip status={phase.status === 'completed' ? 'verified' : phase.status === 'active' ? 'active' : 'pending'} />
                    </div>
                    {phase.error_message && (
                      <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
                        <div className="text-[10px] text-red-400">{phase.error_message}</div>
                      </div>
                    )}
                    <div className="grid grid-cols-4 gap-3">
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Status</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.status}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Tokens</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.tokens_in ? `${(phase.tokens_in / 1000).toFixed(1)}k` : '—'}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Model</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.model_used || '—'}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Cost</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.cost ? `$${phase.cost.toFixed(3)}` : '—'}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-[9px] text-zinc-600">
                      <DataSourceBadge state={dataSource} />
                      {dataSource === 'MOCK' && <span>Showing mock phase data</span>}
                      {dataSource === 'PARTIAL' && <span>Phase data from backend</span>}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        <div className="col-span-4 card p-4">
          <SectionHeader title="Phase Agents" subtitle="Active and completed" />
          <div className="space-y-2">
            {mockAgents.filter(a => a.tokenUsage > 0).slice(0, 6).map(agent => (
              <div key={agent.id} className="flex items-center gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: agent.color }} />
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-medium text-zinc-400 truncate">{agent.name}</div>
                  <div className="text-[9px] text-zinc-700">{(agent.tokenUsage / 1000).toFixed(1)}k tokens</div>
                </div>
                <StatusChip status={agent.status === 'working' ? 'active' : 'idle'} size="sm" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
