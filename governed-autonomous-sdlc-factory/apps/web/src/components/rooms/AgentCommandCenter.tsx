'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockAgents, mockProcessEvents } from '@/lib/mock-data';
import { Bot, Clock, Coins, AlertTriangle, CheckCircle2, ArrowRight, Filter } from 'lucide-react';

export function AgentCommandCenter() {
  const [filter, setFilter] = useState<string>('all');
  const workingAgents = mockAgents.filter(a => a.status === 'working');
  const waitingAgents = mockAgents.filter(a => a.status === 'waiting');
  const idleAgents = mockAgents.filter(a => a.status === 'idle');

  const filteredEvents = filter === 'all'
    ? mockProcessEvents
    : mockProcessEvents.filter(e => e.result === filter);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Agent Command Center" subtitle={`${workingAgents.length} active • ${waitingAgents.length} waiting • ${idleAgents.length} idle`} />

      {/* Agent Grid */}
      <div className="grid grid-cols-4 gap-3">
        {mockAgents.map(agent => (
          <div key={agent.id} className={`card p-3 border ${
            agent.status === 'working' ? 'border-blue-400/20 glow-blue' :
            agent.status === 'waiting' ? 'border-amber-400/20' :
            agent.status === 'error' ? 'border-red-400/20' :
            'border-[#1e2230]'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: agent.color, boxShadow: agent.status === 'working' ? `0 0 8px ${agent.color}60` : 'none' }} />
              <span className="text-[11px] font-medium text-zinc-300 flex-1">{agent.name}</span>
              <StatusChip status={agent.status === 'working' ? 'active' : agent.status} size="sm" />
            </div>

            <div className="text-[9px] text-zinc-600 mb-2 truncate">{agent.currentTask}</div>

            <div className="grid grid-cols-2 gap-1.5 mb-2">
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Tokens</div>
                <div className="text-[10px] font-mono text-zinc-400">{(agent.tokenUsage / 1000).toFixed(1)}k</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Latency</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.latencyMs}ms</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Retries</div>
                <div className="text-[10px] font-mono text-zinc-400">{agent.retryCount}</div>
              </div>
              <div>
                <div className="text-[8px] text-zinc-700 uppercase">Errors</div>
                <div className={`text-[10px] font-mono ${agent.errorCount > 0 ? 'text-red-400' : 'text-zinc-400'}`}>{agent.errorCount}</div>
              </div>
            </div>

            {/* Confidence bar */}
            <div>
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-[8px] text-zinc-700 uppercase">Confidence</span>
                <span className="text-[9px] font-mono text-zinc-500">{Math.round(agent.confidence * 100)}%</span>
              </div>
              <ProgressBar value={agent.confidence} size="sm" color={agent.confidence >= 0.8 ? 'green' : agent.confidence >= 0.5 ? 'amber' : 'red'} />
            </div>

            {/* Policy constraints */}
            {agent.policyConstraints.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {agent.policyConstraints.map(pc => (
                  <Badge key={pc} variant="violet" size="sm">{pc}</Badge>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Event Stream */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <SectionHeader title="Live Event Stream" subtitle={`${mockProcessEvents.length} events`} />
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
