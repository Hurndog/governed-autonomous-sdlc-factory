'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { Play, Square, RotateCcw, Clock, Bot, Coins, AlertTriangle, RefreshCw, Plus } from 'lucide-react';
import type { ListRunsResponse, RunItem } from '@/lib/api';

export function RunControlRoom() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [creating, setCreating] = useState(false);

  const fetchRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listRuns({ page_size: 10 });
      setRuns(result.items || []);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch runs');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleCreateRun = async () => {
    setCreating(true);
    try {
      await api.createRun({ intent: 'Frontend API integration test run', budget_limit: 5.0 });
      await fetchRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create run');
    } finally {
      setCreating(false);
    }
  };

  const handleRunAction = async (runId: string, action: 'start' | 'pause' | 'resume' | 'cancel') => {
    try {
      await api[action === 'start' ? 'startRun' : action === 'pause' ? 'pauseRun' : action === 'resume' ? 'resumeRun' : 'cancelRun'](runId);
      await fetchRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action} run`);
    }
  };

  // Mock runs for fallback
  const mockRuns: RunItem[] = [
    { id: 'run-7ff8a2fd', status: 'active', intent: 'PaymentHub v1.0', created_at: '2026-05-14T06:00:00Z', updated_at: '2026-05-14T08:14:00Z', started_at: '2026-05-14T06:00:00Z' },
    { id: 'run-3a1b2c3d', status: 'completed', intent: 'PaymentHub v0.9', created_at: '2026-05-13T10:00:00Z', updated_at: '2026-05-13T12:00:00Z', started_at: '2026-05-13T10:00:00Z', completed_at: '2026-05-13T12:00:00Z' },
    { id: 'run-5e6f7g8h', status: 'failed', intent: 'PaymentHub v0.8', created_at: '2026-05-12T14:00:00Z', updated_at: '2026-05-12T15:30:00Z', started_at: '2026-05-12T14:00:00Z' },
  ];

  const displayRuns = dataSource === 'LIVE' && runs.length > 0 ? runs : mockRuns;
  const isLive = dataSource === 'LIVE' && runs.length > 0;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Run Control" subtitle={`${displayRuns.length} runs`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchRuns}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleCreateRun}
            disabled={creating}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-violet-500/10 text-violet-400 border border-violet-500/20 text-[10px] hover:bg-violet-500/20 disabled:opacity-50"
          >
            <Plus className="w-3 h-3" />
            {creating ? 'Creating...' : 'New Run'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {displayRuns.map(run => (
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
              {isLive && (
                <div className="flex items-center gap-1">
                  {run.status === 'active' && (
                    <>
                      <button onClick={() => handleRunAction(run.id, 'pause')} className="p-1 rounded hover:bg-zinc-800/50 text-amber-400" title="Pause">
                        <Square className="w-3 h-3" />
                      </button>
                      <button onClick={() => handleRunAction(run.id, 'cancel')} className="p-1 rounded hover:bg-zinc-800/50 text-red-400" title="Cancel">
                        <RotateCcw className="w-3 h-3" />
                      </button>
                    </>
                  )}
                  {run.status === 'paused' && (
                    <button onClick={() => handleRunAction(run.id, 'resume')} className="p-1 rounded hover:bg-zinc-800/50 text-emerald-400" title="Resume">
                      <Play className="w-3 h-3" />
                    </button>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Status</span>
                <span className="text-zinc-400">{run.status}</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Intent</span>
                <span className="text-zinc-400 truncate ml-2">{run.intent || '—'}</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-600">Started</span>
                <span className="text-zinc-400">{run.started_at ? run.started_at.slice(0, 16).replace('T', ' ') : '—'}</span>
              </div>
              {run.cost_usd !== undefined && (
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-600">Cost</span>
                  <span className="text-zinc-400">${run.cost_usd.toFixed(3)}</span>
                </div>
              )}
              {run.event_count !== undefined && (
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-600">Events</span>
                  <span className="text-zinc-400">{run.event_count}</span>
                </div>
              )}
              {run.artifact_count !== undefined && (
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-600">Artifacts</span>
                  <span className="text-zinc-400">{run.artifact_count}</span>
                </div>
              )}
            </div>

            {!isLive && (
              <div className="mt-2 pt-2 border-t border-[#1e2230]">
                <span className="text-[8px] text-zinc-700">Controls disabled — showing mock data</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
