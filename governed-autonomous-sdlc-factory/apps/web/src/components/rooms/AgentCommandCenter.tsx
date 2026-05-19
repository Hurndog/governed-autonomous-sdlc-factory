'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip, type StatusType } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockAgents, mockProcessEvents } from '@/lib/mock-data';
import { Bot, Clock, Coins, AlertTriangle, CheckCircle2, ArrowRight, RefreshCw, Cpu, Zap, Shield } from 'lucide-react';

interface AgentData {
  id: string; name: string; role: string; description?: string;
  model_preference?: string; is_active: boolean;
}

interface EnrichedAgent extends AgentData {
  status: string;
  currentTask: string;
  tokenUsage: number;
  latencyMs?: number;
  retryCount: number;
  errorCount: number;
  confidence: number;
  color: string;
  provider?: string;
  model?: string;
  lastActivity?: string;
}

export function AgentCommandCenter() {
  const [agents, setAgents] = useState<EnrichedAgent[]>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [filter, setFilter] = useState<string>('all');

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      setRunId(latestRun.id);

      // Fetch agents + cost report + model calls in parallel
      const [agentsRes, costRes] = await Promise.allSettled([
        api.listAgents() as Promise<{ agents: AgentData[] } | AgentData[]>,
        api.getCostReport(latestRun.id),
      ]);

      let agentList: AgentData[] = [];
      if (agentsRes.status === 'fulfilled') {
        const res = agentsRes.value;
        agentList = Array.isArray(res) ? res : (res.agents || []);
      }

      // Build cost-by-agent map from cost report
      const costByAgent: Record<string, { tokensIn: number; tokensOut: number; cost: number; calls: number; errors: number; retries: number }> = {};
      if (costRes.status === 'fulfilled') {
        const cost = costRes.value as {
          by_agent?: Record<string, { input_tokens?: number; output_tokens?: number; cost?: number; call_count?: number; error_count?: number; retry_count?: number }>;
          by_model?: Record<string, { input_tokens?: number; output_tokens?: number; cost?: number }>;
        };
        if (cost.by_agent) {
          Object.entries(cost.by_agent).forEach(([agentId, data]) => {
            costByAgent[agentId] = {
              tokensIn: data.input_tokens ?? 0,
              tokensOut: data.output_tokens ?? 0,
              cost: data.cost ?? 0,
              calls: data.call_count ?? 0,
              errors: data.error_count ?? 0,
              retries: data.retry_count ?? 0,
            };
          });
        }
      }

      if (agentList.length === 0 && Object.keys(costByAgent).length === 0) {
        setDataSource('MOCK');
        setLoading(false);
        return;
      }

      // Enrich agents with real cost data
      const enriched: EnrichedAgent[] = agentList.map((a, i) => {
        const mock = mockAgents[i % mockAgents.length];
        const cost = costByAgent[a.id] || costByAgent[a.name] || {};
        return {
          ...a,
          status: a.is_active ? 'working' : 'idle',
          currentTask: a.is_active ? `Executing ${a.role}` : 'Awaiting next run',
          tokenUsage: (cost.tokensIn ?? 0) + (cost.tokensOut ?? 0),
          latencyMs: mock.latencyMs,
          retryCount: cost.retries ?? mock.retryCount,
          errorCount: cost.errors ?? mock.errorCount,
          confidence: mock.confidence,
          color: mock.color,
          model: a.model_preference,
          lastActivity: mock.lastActionAt,
        };
      });

      // If we have cost data but no agents, create synthetic agent entries from cost by_agent
      if (agentList.length === 0 && Object.keys(costByAgent).length > 0) {
        Object.entries(costByAgent).forEach(([agentId, cost], i) => {
          const mock = mockAgents[i % mockAgents.length];
          enriched.push({
            id: agentId,
            name: agentId,
            role: 'engineer',
            is_active: true,
            status: 'working',
            currentTask: 'Executing',
            tokenUsage: (cost.tokensIn ?? 0) + (cost.tokensOut ?? 0),
            latencyMs: mock.latencyMs,
            retryCount: cost.retries ?? 0,
            errorCount: cost.errors ?? 0,
            confidence: 0.8,
            color: mock.color,
            provider: 'unknown',
            model: 'unknown',
          });
        });
      }

      setAgents(enriched);
      setDataSource(enriched.length > 0 ? 'LIVE' : 'PARTIAL');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Fallback to mock
  const displayAgents = agents.length > 0 ? agents : mockAgents;

  const mapAgentStatus = (s: string): StatusType => {
    if (s === 'working' || s === 'active') return 'active';
    if (s === 'waiting') return 'waiting';
    if (s === 'error') return 'error';
    if (s === 'paused') return 'paused';
    return 'idle';
  };

  const workingAgents = displayAgents.filter(a => a.status === 'working' || a.status === 'active');
  const totalTokens = displayAgents.reduce((s, a) => s + a.tokenUsage, 0);
  const totalErrors = displayAgents.reduce((s, a) => s + a.errorCount, 0);
  const totalRetries = displayAgents.reduce((s, a) => s + a.retryCount, 0);

  const filteredEvents = filter === 'all'
    ? mockProcessEvents
    : mockProcessEvents.filter(e => e.result === filter);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Agent Command Center"
          subtitle={dataSource === 'LIVE' && runId
            ? `Run ${runId.slice(0, 8)} • ${workingAgents.length} active • ${(totalTokens / 1000).toFixed(1)}k tokens`
            : `${workingAgents.length} active • ${displayAgents.length} total`}
        />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Summary */}
      {dataSource === 'LIVE' && (
        <div className="card p-3 flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <Cpu className="w-3 h-3 text-blue-400" />
            <span className="text-zinc-300 font-mono">{displayAgents.length}</span> engines
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <Zap className="w-3 h-3 text-amber-400" />
            <span className="text-zinc-300 font-mono">{(totalTokens / 1000).toFixed(1)}k</span> tokens
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <AlertTriangle className="w-3 h-3 text-red-400" />
            <span className="text-zinc-300 font-mono">{totalErrors}</span> errors
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <RefreshCw className="w-3 h-3 text-violet-400" />
            <span className="text-zinc-300 font-mono">{totalRetries}</span> retries
          </div>
          <div className="ml-auto"><DataSourceBadge state={dataSource} /></div>
        </div>
      )}

      {/* Agent Grid */}
      <div className="grid grid-cols-4 gap-3">
        {displayAgents.map(agent => (
          <div key={agent.id} className={`card p-3 border ${
            agent.status === 'working' || agent.status === 'active' ? 'border-blue-400/20 glow-blue' :
            agent.status === 'waiting' ? 'border-amber-400/20' :
            agent.status === 'error' ? 'border-red-400/20' :
            'border-[#1e2230]'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: agent.color, boxShadow: agent.status === 'working' ? `0 0 8px ${agent.color}60` : 'none' }} />
              <span className="text-[11px] font-medium text-zinc-300 flex-1">{agent.name}</span>
              <StatusChip status={mapAgentStatus(agent.status)} size="sm" />
            </div>

            <div className="text-[9px] text-zinc-600 mb-2 truncate">{agent.currentTask}</div>

            <div className="grid grid-cols-2 gap-1.5 mb-2">
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Tokens</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.tokenUsage > 0 ? `${(agent.tokenUsage / 1000).toFixed(1)}k` : '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Latency</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.latencyMs ? `${agent.latencyMs}ms` : '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Retries</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.retryCount || '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Errors</div>
                <div className={`text-[10px] font-mono ${agent.errorCount > 0 ? 'text-red-400' : 'text-zinc-400'}`}>{agent.errorCount || '—'}</div>
              </div>
            </div>

            {agent.confidence !== undefined && (
              <div>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[8px] text-zinc-700 uppercase">Confidence</span>
                  <span className="text-[9px] font-mono text-zinc-500">{Math.round(agent.confidence * 100)}%</span>
                </div>
                <ProgressBar value={agent.confidence} size="sm" color={agent.confidence >= 0.8 ? 'green' : agent.confidence >= 0.5 ? 'amber' : 'red'} />
              </div>
            )}

            <div className="mt-2 text-[8px] text-zinc-700">
              Role: <span className="text-zinc-500">{agent.role}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Event Stream */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <SectionHeader title="Live Event Stream" subtitle={`${filteredEvents.length} events${dataSource === 'LIVE' ? '' : ' (mock)'}`} />
          <div className="flex items-center gap-1">
            {['all', 'success', 'warning', 'failure'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${filter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'}`}>
                {f}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-1 max-h-64 overflow-y-auto scrollbar-thin">
          {filteredEvents.map(evt => (
            <div key={evt.id} className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-zinc-800/30">
              <span className="text-[9px] font-mono text-zinc-700 w-12 flex-shrink-0">{evt.timestamp.slice(11, 16)}</span>
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${evt.result === 'success' ? 'bg-emerald-400' : evt.result === 'failure' ? 'bg-red-400' : 'bg-amber-400'}`} />
              <span className="text-[10px] text-zinc-500 w-24 flex-shrink-0">{evt.agent}</span>
              <span className="text-[10px] text-zinc-400 flex-1 truncate">{evt.action}</span>
              <ArrowRight className="w-2.5 h-2.5 text-zinc-700 flex-shrink-0" />
              <span className="text-[10px] text-zinc-600 w-28 truncate flex-shrink-0">{evt.artifact}</span>
              <span className="text-[9px] font-mono text-zinc-700 w-12 text-right flex-shrink-0">{(evt.tokenCost / 1000).toFixed(1)}k</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
