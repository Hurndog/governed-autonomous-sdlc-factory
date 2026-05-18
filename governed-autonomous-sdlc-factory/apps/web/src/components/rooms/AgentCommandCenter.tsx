'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip, type StatusType } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockAgents, mockProcessEvents } from '@/lib/mock-data';
import { Bot, Clock, Coins, AlertTriangle, CheckCircle2, ArrowRight, Filter, RefreshCw } from 'lucide-react';

interface AgentData {
  id: string;
  name: string;
  role: string;
  description?: string;
  model_preference?: string;
  is_active: boolean;
}

export function AgentCommandCenter() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [filter, setFilter] = useState<string>('all');

  const fetchAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      try {
        const agentsRes = await api.listAgents() as { agents: AgentData[] } | AgentData[];
        const agentList = Array.isArray(agentsRes) ? agentsRes : (agentsRes.agents || []);
        if (agentList.length > 0) {
          setAgents(agentList);
          setDataSource('PARTIAL');
        } else {
          setDataSource('MOCK');
        }
      } catch {
        setDataSource('MOCK');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agents');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  // Use real agents if available, enrich with mock data for display
  const displayAgents = agents.length > 0
    ? agents.map((a, i) => {
        const mock = mockAgents[i % mockAgents.length];
        return {
          ...a,
          status: a.is_active ? 'working' : 'idle',
          currentTask: a.is_active ? 'Processing' : 'Awaiting next run',
          tokenUsage: mock.tokenUsage,
          latencyMs: mock.latencyMs,
          retryCount: mock.retryCount,
          errorCount: mock.errorCount,
          confidence: mock.confidence,
          color: mock.color,
          policyConstraints: mock.policyConstraints,
        };
      })
    : mockAgents;

const mapAgentStatus = (s: string): StatusType => {
    if (s === 'working' || s === 'active') return 'active';
    if (s === 'waiting') return 'waiting';
    if (s === 'error') return 'error';
    if (s === 'paused') return 'paused';
    return 'idle';
  };

  const workingAgents = displayAgents.filter(a => a.status === 'working' || a.status === 'active');
  const waitingAgents = displayAgents.filter(a => a.status === 'waiting');
  const idleAgents = displayAgents.filter(a => a.status === 'idle');

  const filteredEvents = filter === 'all'
    ? mockProcessEvents
    : mockProcessEvents.filter(e => e.result === filter);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Agent Command Center" subtitle={`${workingAgents.length} active • ${waitingAgents.length} waiting • ${idleAgents.length} idle`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchAgents}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

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
                <div className="text-[10px] font-mono text-zinc-400">{agent.tokenUsage ? `${(agent.tokenUsage / 1000).toFixed(1)}k` : '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Latency</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.latencyMs ? `${agent.latencyMs}ms` : '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Retries</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.retryCount ?? '—'}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Errors</div>
                <div className={`text-[10px] font-mono ${(agent.errorCount ?? 0) > 0 ? 'text-red-400' : 'text-zinc-400'}`}>{agent.errorCount ?? '—'}</div>
              </div>
            </div>

            {/* Confidence bar */}
            {agent.confidence !== undefined && (
              <div>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[8px] text-zinc-700 uppercase">Confidence</span>
                  <span className="text-[9px] font-mono text-zinc-500">{Math.round(agent.confidence * 100)}%</span>
                </div>
                <ProgressBar value={agent.confidence} size="sm" color={agent.confidence >= 0.8 ? 'green' : agent.confidence >= 0.5 ? 'amber' : 'red'} />
              </div>
            )}

            {/* Policy constraints */}
            {agent.policyConstraints && agent.policyConstraints.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {agent.policyConstraints.map(pc => (
                  <Badge key={pc} variant="violet" size="sm">{pc}</Badge>
                ))}
              </div>
            )}

            {/* Role from backend */}
            {'role' in agent && agent.role && (
              <div className="mt-2 text-[8px] text-zinc-700">
                Role: <span className="text-zinc-500">{agent.role}</span>
                {'model_preference' in agent && agent.model_preference && ` • ${agent.model_preference}`}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Event Stream */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <SectionHeader title="Live Event Stream" subtitle={`${mockProcessEvents.length} events (mock)`} />
          <div className="flex items-center gap-1">
            {['all', 'success', 'warning', 'failure'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${
                  filter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1 max-h-64 overflow-y-auto scrollbar-thin">
          {filteredEvents.map(evt => (
            <div key={evt.id} className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-zinc-800/30">
              <span className="text-[9px] font-mono text-zinc-700 w-12 flex-shrink-0">{evt.timestamp.slice(11, 16)}</span>
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                evt.result === 'success' ? 'bg-emerald-400' : evt.result === 'failure' ? 'bg-red-400' : 'bg-amber-400'
              }`} />
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
