'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockProcessEvents } from '@/lib/mock-data';
import { Play, Pause, SkipBack, SkipForward, Clock, Bot, CheckCircle2, AlertTriangle, RotateCcw, RefreshCw } from 'lucide-react';
import type { TimelineResponse, ReplaySessionsResponse } from '@/lib/api';

export function RunReplay() {
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [replaySessions, setReplaySessions] = useState<ReplaySessionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [isPlaying, setIsPlaying] = useState(false);
  const [position, setPosition] = useState(0);

  const fetchReplayData = async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) {
        setError('No runs found');
        setDataSource('ERROR');
        return;
      }
      const [timelineRes, replayRes] = await Promise.allSettled([
        api.getRunTimeline(latestRun.id),
        api.getReplaySessions(latestRun.id),
      ]);
      if (timelineRes.status === 'fulfilled') setTimeline(timelineRes.value);
      if (replayRes.status === 'fulfilled') setReplaySessions(replayRes.value);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch replay data');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReplayData();
  }, []);

  const events = (timeline?.events || mockProcessEvents).map(evt => ({
    ...evt,
    agent_id: (evt as any).agent_id || (evt as any).agent || 'system',
    type: (evt as any).type || (evt as any).result || 'info',
    phase: (evt as any).phase || 'Unknown',
  }));
  const currentEvent = events[position];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Run Replay & Time Travel" subtitle="Reconstruct the build timeline" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchReplayData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Playback controls */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <button className="p-1.5 rounded hover:bg-zinc-800/50 text-zinc-500" onClick={() => setPosition(0)}><SkipBack className="w-3.5 h-3.5" /></button>
            <button onClick={() => setIsPlaying(!isPlaying)} className="p-2 rounded bg-violet-500/20 text-violet-400 hover:bg-violet-500/30">
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button className="p-1.5 rounded hover:bg-zinc-800/50 text-zinc-500" onClick={() => setPosition(Math.min(events.length - 1, position + 1))}><SkipForward className="w-3.5 h-3.5" /></button>
          </div>
          <div className="flex-1">
            <input
              type="range" min={0} max={events.length - 1} value={position}
              onChange={(e) => setPosition(parseInt(e.target.value))}
              className="w-full h-1 bg-zinc-800 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-violet-400"
            />
            <div className="flex justify-between mt-1">
              <span className="text-[8px] text-zinc-700">{events[0]?.timestamp.slice(11, 16) || '06:00'}</span>
              <span className="text-[9px] text-zinc-500">{currentEvent?.timestamp.slice(11, 16) || '—'}</span>
              <span className="text-[8px] text-zinc-700">{events[events.length - 1]?.timestamp.slice(11, 16) || '08:15'}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[9px] text-zinc-600">
            <Clock className="w-3 h-3" />
            <span>Event {position + 1}/{events.length}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <SectionHeader title="Event Timeline" subtitle="Chronological agent actions" />
          <div className="space-y-0 mt-2">
            {events.map((evt, i) => (
              <div key={evt.id} className={`flex items-start gap-3 py-2 px-2 rounded transition-colors ${
                i === position ? 'bg-violet-500/10 border border-violet-500/20' : i < position ? 'opacity-60' : 'opacity-30'
              }`}>
                <div className="w-12 flex-shrink-0 pt-0.5">
                  <span className="text-[9px] font-mono text-zinc-600">{evt.timestamp.slice(11, 16)}</span>
                </div>
                <div className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                  evt.type?.includes('error') || evt.type?.includes('fail') ? 'bg-red-400' :
                  evt.type?.includes('warn') ? 'bg-amber-400' : 'bg-emerald-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-medium text-zinc-300">{evt.agent_id || evt.phase || 'System'}</span>
                    <span className="text-[10px] text-zinc-600">→</span>
                    <span className="text-[10px] text-zinc-400">{evt.type || 'event'}</span>
                  </div>
                </div>
                <StatusChip status={evt.type?.includes('error') || evt.type?.includes('fail') ? 'failed' : evt.type?.includes('warn') ? 'warning' : 'verified'} size="sm" />
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-4 space-y-4">
          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">System State at {currentEvent?.timestamp.slice(11, 16) || '—'}</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between"><span className="text-[10px] text-zinc-500">Phase</span><span className="text-[10px] text-zinc-300">{currentEvent?.phase || '—'}</span></div>
              <div className="flex items-center justify-between"><span className="text-[10px] text-zinc-500">Agent</span><span className="text-[10px] text-zinc-300">{currentEvent?.agent_id || '—'}</span></div>
              <div className="flex items-center justify-between"><span className="text-[10px] text-zinc-500">Event</span><span className="text-[10px] text-zinc-300">{currentEvent?.type || '—'}</span></div>
            </div>
          </div>

          {replaySessions?.sessions && replaySessions.sessions.length > 0 && (
            <div className="card p-4">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Replay Sessions</div>
              <div className="space-y-1.5">
                {replaySessions.sessions.map(session => (
                  <div key={session.id} className="flex items-center gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                    <StatusChip status={session.status === 'completed' ? 'verified' : 'active'} size="sm" />
                    <span className="text-[9px] text-zinc-500">{session.event_count} events</span>
                    {session.integrity_preserved && <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
