'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type TimelineEvent } from '@/lib/api';
import { mockProcessEvents } from '@/lib/mock-data';
import { Clock, AlertTriangle, User, RefreshCw } from 'lucide-react';

type DisplayEvent = {
  timestamp: string;
  label: string;
  source: string;
  phase: string;
  isSuccess: boolean;
  isFailure: boolean;
};

function toDisplayEvents(events: TimelineEvent[], hasReal: boolean): DisplayEvent[] {
  if (hasReal) {
    return events.map(evt => ({
      timestamp: evt.timestamp,
      label: (evt.type || '').slice(0, 20),
      source: evt.agent_id || 'system',
      phase: evt.phase || '',
      isSuccess: (evt.type || '').includes('success') || (evt.type || '').includes('complete'),
      isFailure: (evt.type || '').includes('error') || (evt.type || '').includes('fail'),
    }));
  }
  return mockProcessEvents.map(evt => ({
    timestamp: evt.timestamp,
    label: evt.action?.slice(0, 20) || '',
    source: evt.agent,
    phase: '',
    isSuccess: evt.result === 'success',
    isFailure: evt.result === 'failure',
  }));
}

export function ProcessTimeline() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchTimeline = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      try {
        const res = await api.getRunTimeline(latestRun.id) as { events: TimelineEvent[]; total: number };
        if (res.events && res.events.length > 0) { setEvents(res.events); setDataSource('PARTIAL'); }
        else { setDataSource('MOCK'); }
      } catch { setDataSource('MOCK'); }
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchTimeline(); }, []);

  const hasRealEvents = events.length > 0;
  const displayEvents = toDisplayEvents(events, hasRealEvents);

  const lanes = [
    { id: 'user', label: 'User', icon: User, color: '#e8eaed' },
    { id: 'product', label: 'Product', icon: Clock, color: '#60a5fa' },
    { id: 'arch', label: 'Arch', icon: Clock, color: '#fbbf24' },
    { id: 'governance', label: 'Gov', icon: Clock, color: '#a78bfa' },
    { id: 'coding', label: 'Code', icon: Clock, color: '#22d3ee' },
    { id: 'testing', label: 'Test', icon: Clock, color: '#c084fc' },
    { id: 'verifier', label: 'Verify', icon: Clock, color: '#f87171' },
  ];

  const laneAgentMap: Record<string, string[]> = {
    'user': ['Marco'], 'product': ['Product Analyst', 'Requirement Normalizer'],
    'arch': ['Architecture Agent'], 'governance': ['Governance Agent'],
    'coding': ['Code Generation'], 'testing': ['Test Generation', 'Semantic Coverage', 'Evidence Agent'],
    'verifier': ['Verifier'],
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Process Timeline" subtitle="SDLC workflow visualization with swimlanes" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchTimeline} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="card p-4">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-[9px] text-zinc-700">06:00</span>
          <div className="flex-1 relative h-2 bg-zinc-800 rounded-full">
            <div className="absolute inset-y-0 left-0 w-[72%] bg-gradient-to-r from-violet-500/40 to-blue-500/40 rounded-full" />
            <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-violet-400 rounded-full shadow-[0_0_8px_rgba(167,139,250,0.5)]" style={{ left: '72%' }} />
          </div>
          <span className="text-[9px] text-zinc-700">08:15</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600"><Clock className="w-3 h-3" /> Elapsed: 2h 14m</div>
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600"><AlertTriangle className="w-3 h-3 text-amber-400" /> 3 rework loops</div>
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600"><User className="w-3 h-3" /> 4 human interventions</div>
        </div>
      </div>

      <div className="card p-4">
        <div className="space-y-1">
          {lanes.map(lane => {
            const Icon = lane.icon;
            const laneEvents = displayEvents.filter(evt => laneAgentMap[lane.id]?.includes(evt.source));
            return (
              <div key={lane.id} className="flex items-center gap-3 py-1.5">
                <div className="w-20 flex-shrink-0 flex items-center gap-1.5">
                  <Icon className="w-3 h-3" style={{ color: lane.color }} />
                  <span className="text-[9px] text-zinc-500">{lane.label}</span>
                </div>
                <div className="flex-1 relative h-6 bg-zinc-800/20 rounded">
                  {laneEvents.map((evt, i) => {
                    const startHour = 6;
                    const evtHour = parseInt(evt.timestamp.slice(11, 13));
                    const evtMin = parseInt(evt.timestamp.slice(14, 16));
                    const pos = ((evtHour - startHour) * 60 + evtMin) / 135 * 100;
                    return (
                      <div key={i}
                        className={`absolute top-0.5 h-5 rounded text-[7px] flex items-center px-1.5 truncate ${evt.isSuccess ? 'bg-emerald-400/20 text-emerald-400 border border-emerald-400/30' : evt.isFailure ? 'bg-red-400/20 text-red-400 border border-red-400/30' : 'bg-amber-400/20 text-amber-400 border border-amber-400/30'}`}
                        style={{ left: `${Math.min(pos, 90)}%`, width: '120px' }} title={evt.label}>
                        {evt.label}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card p-4">
        <SectionHeader title="Timeline Events" subtitle={`${displayEvents.length} events ${!hasRealEvents ? '(mock)' : '(live)'}`} />
        <div className="space-y-1 mt-2 max-h-64 overflow-y-auto scrollbar-thin">
          {displayEvents.slice(0, 20).map((evt, i) => (
            <div key={i} className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-zinc-800/30">
              <span className="text-[9px] font-mono text-zinc-700 w-12 flex-shrink-0">{evt.timestamp.slice(11, 16)}</span>
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${evt.isSuccess ? 'bg-emerald-400' : evt.isFailure ? 'bg-red-400' : 'bg-amber-400'}`} />
              <span className="text-[10px] text-zinc-500 w-24 flex-shrink-0">{evt.source}</span>
              <span className="text-[10px] text-zinc-400 flex-1 truncate">{evt.label}</span>
              <span className="text-[9px] text-zinc-600">{evt.phase}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
