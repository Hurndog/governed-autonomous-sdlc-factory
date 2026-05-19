'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type TimelineEvent } from '@/lib/api';
import { mockProcessEvents } from '@/lib/mock-data';
import { Clock, AlertTriangle, User, RefreshCw, CheckCircle2, XCircle, Shield, Activity } from 'lucide-react';

interface DisplayEvent {
  id: string;
  timestamp: string;
  label: string;
  source: string;
  phase: string;
  type: string;
  severity: string;
  isSuccess: boolean;
  isFailure: boolean;
  isGovernance: boolean;
  duration?: number; // ms since previous event
}

function buildDisplayEvents(
  timelineEvents: TimelineEvent[],
  governanceEvents: Array<{ created_at: string; policy_name: string; policy_id: string; status: string }>,
  hasReal: boolean,
): DisplayEvent[] {
  const events: DisplayEvent[] = [];

  if (hasReal && timelineEvents.length > 0) {
    timelineEvents.forEach((evt, i) => {
      const prev = i > 0 ? timelineEvents[i - 1] : null;
      const duration = prev ? new Date(evt.timestamp).getTime() - new Date(prev.timestamp).getTime() : undefined;
      events.push({
        id: evt.id || `evt-${i}`,
        timestamp: evt.timestamp,
        label: evt.type || 'unknown',
        source: evt.agent_id || evt.phase || 'system',
        phase: evt.phase || '',
        type: evt.type || '',
        severity: (evt.type || '').includes('error') || (evt.type || '').includes('fail') ? 'critical' : (evt.type || '').includes('warn') ? 'warning' : 'info',
        isSuccess: (evt.type || '').includes('success') || (evt.type || '').includes('complete'),
        isFailure: (evt.type || '').includes('error') || (evt.type || '').includes('fail'),
        isGovernance: false,
        duration,
      });
    });
  }

  // Merge governance events
  governanceEvents.forEach((gov, i) => {
    events.push({
      id: `gov-${i}`,
      timestamp: gov.created_at,
      label: `Governance: ${gov.policy_name || gov.policy_id} — ${gov.status}`,
      source: 'governance',
      phase: '',
      type: 'governance_evaluation',
      severity: gov.status === 'fail' ? 'critical' : gov.status === 'warn' ? 'warning' : 'info',
      isSuccess: gov.status === 'pass',
      isFailure: gov.status === 'fail',
      isGovernance: true,
    });
  });

  // Sort by timestamp
  events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  // Calculate durations
  events.forEach((evt, i) => {
    if (i > 0 && !evt.duration) {
      evt.duration = new Date(evt.timestamp).getTime() - new Date(events[i - 1].timestamp).getTime();
    }
  });

  return events;
}

type FilterType = 'all' | 'success' | 'failure' | 'governance' | 'bottleneck';

export function ProcessTimeline() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [governanceEvents, setGovernanceEvents] = useState<Array<{ created_at: string; policy_name: string; policy_id: string; status: string }>>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [filter, setFilter] = useState<FilterType>('all');

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      setRunId(latestRun.id);

      const [timelineRes, govRes] = await Promise.allSettled([
        api.getRunTimeline(latestRun.id) as Promise<{ events: TimelineEvent[]; total: number }>,
        api.getGovernanceEvaluations(latestRun.id) as Promise<{ evaluations: Array<{ created_at: string; policy_name?: string; policy_id: string; status: string }> }>,
      ]);

      let timelineEvents: TimelineEvent[] = [];
      let govEvents: Array<{ created_at: string; policy_name: string; policy_id: string; status: string }> = [];
      let hasReal = false;

      if (timelineRes.status === 'fulfilled') {
        const res = timelineRes.value;
        if (res.events && res.events.length > 0) {
          timelineEvents = res.events;
          hasReal = true;
        }
      }

      if (govRes.status === 'fulfilled') {
        const res = govRes.value;
        if (res.evaluations && res.evaluations.length > 0) {
          govEvents = res.evaluations.map(e => ({
            created_at: e.created_at || new Date().toISOString(),
            policy_name: e.policy_name || 'Unknown Policy',
            status: e.status,
            policy_id: e.policy_id,
          }));
          hasReal = true;
        }
      }

      if (!hasReal) {
        setDataSource('MOCK');
        setLoading(false);
        return;
      }

      setEvents(timelineEvents);
      setGovernanceEvents(govEvents);
      setDataSource(timelineEvents.length > 0 ? 'LIVE' : 'PARTIAL');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const hasRealEvents = events.length > 0 || governanceEvents.length > 0;
  const allDisplayEvents = buildDisplayEvents(events, governanceEvents, hasRealEvents);
  const displayEvents: DisplayEvent[] = hasRealEvents ? allDisplayEvents : mockProcessEvents.map(evt => ({
    id: `mock-${evt.timestamp}`,
    timestamp: evt.timestamp,
    label: evt.action || '',
    source: evt.agent || 'system',
    phase: '',
    type: 'mock',
    severity: 'info',
    isSuccess: evt.result === 'success',
    isFailure: evt.result === 'failure',
    isGovernance: false,
    duration: undefined,
  }));

  // Apply filter
  const filteredEvents = filter === 'all' ? displayEvents :
    filter === 'success' ? displayEvents.filter(e => e.isSuccess) :
    filter === 'failure' ? displayEvents.filter(e => e.isFailure) :
    filter === 'governance' ? displayEvents.filter(e => e.isGovernance) :
    filter === 'bottleneck' ? displayEvents.filter(e => (e.duration ?? 0) > 60000) : // > 1 min gap = bottleneck
    displayEvents;

  // Compute stats
  const successCount = displayEvents.filter(e => e.isSuccess).length;
  const failureCount = displayEvents.filter(e => e.isFailure).length;
  const govCount = displayEvents.filter(e => e.isGovernance).length;
  const bottleneckCount = displayEvents.filter(e => (e.duration ?? 0) > 60000).length;
  const totalDuration = displayEvents.length >= 2
    ? new Date(displayEvents[displayEvents.length - 1].timestamp).getTime() - new Date(displayEvents[0].timestamp).getTime()
    : 0;

  // Unique sources for swimlanes
  const sources = [...new Set(displayEvents.map(e => e.source))].slice(0, 8);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Process Timeline"
          subtitle={dataSource === 'LIVE' && runId ? `Run ${runId.slice(0, 8)} • ${displayEvents.length} events` : 'SDLC workflow visualization'}
        />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Stats bar */}
      {dataSource === 'LIVE' && (
        <div className="card p-3 flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span className="text-emerald-400 font-mono">{successCount}</span> success
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <XCircle className="w-3 h-3 text-red-400" />
            <span className="text-red-400 font-mono">{failureCount}</span> failures
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <Shield className="w-3 h-3 text-violet-400" />
            <span className="text-violet-400 font-mono">{govCount}</span> governance
          </div>
          {bottleneckCount > 0 && (
            <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
              <AlertTriangle className="w-3 h-3 text-amber-400" />
              <span className="text-amber-400 font-mono">{bottleneckCount}</span> bottlenecks
            </div>
          )}
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-500">
            <Clock className="w-3 h-3" />
            <span className="text-zinc-300 font-mono">{Math.round(totalDuration / 60000)}m</span> total
          </div>
          <div className="ml-auto"><DataSourceBadge state={dataSource} /></div>
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex items-center gap-1">
        {(['all', 'success', 'failure', 'governance', 'bottleneck'] as FilterType[]).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2.5 py-1 rounded text-[9px] font-medium transition-colors ${filter === f ? 'bg-violet-500/15 text-violet-300 border border-violet-500/25' : 'text-zinc-600 hover:text-zinc-400 border border-transparent'}`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'bottleneck' && bottleneckCount > 0 && <span className="ml-1 text-amber-400">({bottleneckCount})</span>}
          </button>
        ))}
      </div>

      {/* Timeline visualization */}
      <div className="card p-4">
        {dataSource === 'LIVE' && displayEvents.length >= 2 ? (
          <div className="space-y-1">
            {sources.map(source => {
              const sourceEvents = displayEvents.filter(e => e.source === source);
              if (sourceEvents.length === 0) return null;
              return (
                <div key={source} className="flex items-center gap-3 py-1">
                  <div className="w-20 flex-shrink-0 text-[9px] text-zinc-500 truncate">{source}</div>
                  <div className="flex-1 relative h-6 bg-zinc-800/20 rounded">
                    {sourceEvents.map((evt, i) => {
                      const startTime = new Date(displayEvents[0].timestamp).getTime();
                      const endTime = new Date(displayEvents[displayEvents.length - 1].timestamp).getTime();
                      const totalSpan = endTime - startTime || 1;
                      const evtTime = new Date(evt.timestamp).getTime();
                      const pos = ((evtTime - startTime) / totalSpan) * 100;
                      return (
                        <div
                          key={i}
                          className={`absolute top-0.5 h-5 rounded text-[7px] flex items-center px-1 truncate cursor-pointer ${evt.isSuccess ? 'bg-emerald-400/20 text-emerald-400 border border-emerald-400/30' : evt.isFailure ? 'bg-red-400/20 text-red-400 border border-red-400/30' : evt.isGovernance ? 'bg-violet-400/20 text-violet-400 border border-violet-400/30' : 'bg-amber-400/20 text-amber-400 border border-amber-400/30'}`}
                          style={{ left: `${Math.min(pos, 92)}%`, width: 'auto', maxWidth: '120px', minWidth: '40px' }}
                          title={`${evt.label} — ${evt.timestamp}${evt.duration ? ` (${Math.round(evt.duration / 1000)}s gap)` : ''}`}
                        >
                          {evt.label.slice(0, 15)}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-[10px] text-zinc-600 p-4">No timeline events available from backend. Showing mock data.</div>
        )}
      </div>

      {/* Event list */}
      <div className="card p-4">
        <SectionHeader title="Timeline Events" subtitle={`${filteredEvents.length} events${filter !== 'all' ? ` (filtered: ${filter})` : ''}`} />
        <div className="space-y-1 mt-2 max-h-64 overflow-y-auto scrollbar-thin">
          {filteredEvents.slice(0, 50).map((evt, i) => (
            <div key={i} className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-zinc-800/30">
              <span className="text-[9px] font-mono text-zinc-700 w-12 flex-shrink-0">
                {evt.timestamp.slice(11, 16)}
              </span>
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${evt.isSuccess ? 'bg-emerald-400' : evt.isFailure ? 'bg-red-400' : evt.isGovernance ? 'bg-violet-400' : 'bg-amber-400'}`} />
              {evt.isGovernance && <Shield className="w-3 h-3 text-violet-400 flex-shrink-0" />}
              {(evt.duration ?? 0) > 60000 && <AlertTriangle className="w-3 h-3 text-amber-400 flex-shrink-0" />}
              <span className="text-[10px] text-zinc-500 w-24 flex-shrink-0 truncate">{evt.source}</span>
              <span className="text-[10px] text-zinc-400 flex-1 truncate">{evt.label}</span>
              {evt.duration !== undefined && (
                <span className="text-[8px] text-zinc-700 w-12 text-right flex-shrink-0">
                  {evt.duration > 1000 ? `${Math.round(evt.duration / 1000)}s` : '—'}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
