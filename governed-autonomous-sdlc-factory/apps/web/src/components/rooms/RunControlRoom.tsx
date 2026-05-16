'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, StatusDot, ProgressBar, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Play,
  Pause,
  Square,
  RotateCcw,
  Loader2,
  Zap,
  Clock,
  Activity,
  ChevronRight,
} from 'lucide-react';

export function RunControlRoom() {
  const runs = useStore((s) => s.runs);
  const setRuns = useStore((s) => s.setRuns);
  const selectedRunId = useStore((s) => s.selectedRunId);
  const setSelectedRunId = useStore((s) => s.setSelectedRunId);
  const selectedRunDetail = useStore((s) => s.selectedRunDetail);
  const setSelectedRunDetail = useStore((s) => s.setSelectedRunDetail);
  const timelineEvents = useStore((s) => s.timelineEvents);
  const setTimelineEvents = useStore((s) => s.setTimelineEvents);
  const setLastError = useStore((s) => s.setLastError);

  const [intent, setIntent] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const handleLoadRuns = useCallback(async () => {
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.listRuns({ page_size: 50 });
      setRuns(result.items || (result as any).runs || []);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [setRuns, setLastError]);

  const handleSelectRun = useCallback(async (runId: string) => {
    setSelectedRunId(runId);
    setDetailLoading(true);
    setLastError(null);
    try {
      const [detail, timeline] = await Promise.allSettled([
        api.getRun(runId),
        api.getRunTimeline(runId),
      ]);
      if (detail.status === 'fulfilled') setSelectedRunDetail(detail.value as any);
      if (timeline.status === 'fulfilled') setTimelineEvents((timeline.value as any).events || []);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setDetailLoading(false);
    }
  }, [setSelectedRunId, setSelectedRunDetail, setTimelineEvents, setLastError]);

  const handleStartRun = useCallback(async () => {
    if (!selectedRunId) return;
    setLoading(true);
    try {
      await api.startRun(selectedRunId);
      await handleSelectRun(selectedRunId);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [selectedRunId, handleSelectRun, setLastError]);

  const handlePauseRun = useCallback(async () => {
    if (!selectedRunId) return;
    try {
      await api.pauseRun(selectedRunId);
      await handleSelectRun(selectedRunId);
    } catch (e: any) {
      setLastError(e.message);
    }
  }, [selectedRunId, handleSelectRun, setLastError]);

  const handleCancelRun = useCallback(async () => {
    if (!selectedRunId) return;
    try {
      await api.cancelRun(selectedRunId);
      await handleSelectRun(selectedRunId);
    } catch (e: any) {
      setLastError(e.message);
    }
  }, [selectedRunId, handleSelectRun, setLastError]);

  const handleNewRun = useCallback(async () => {
    if (!intent.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.runFullPipeline({
        intent: intent.trim(),
        project_name: projectName || undefined,
      });
      setIntent('');
      setProjectName('');
      await handleLoadRuns();
      if (result.run_id) {
        handleSelectRun(result.run_id);
      }
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [intent, projectName, handleLoadRuns, handleSelectRun, setLastError]);

  const statusVariant = (status: string) => {
    switch (status) {
      case 'running': return 'emerald';
      case 'completed': return 'emerald';
      case 'failed': return 'red';
      case 'paused': return 'amber';
      default: return 'zinc';
    }
  };

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            RUN CONTROL ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Launch Pipelines — Monitor Execution — Control Runs
          </p>
        </div>
        <button
          onClick={handleLoadRuns}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 border border-zinc-700 rounded-md text-zinc-400 text-xs font-mono hover:bg-zinc-800 transition-colors"
        >
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RotateCcw className="w-3 h-3" />}
          Refresh
        </button>
      </div>

      {/* New Run Launcher */}
      <Card glow="emerald">
        <SectionHeader title="New Run" subtitle="Launch a governed SDLC pipeline" icon={<Zap className="w-4 h-4" />} />
        <div className="space-y-3">
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="Project name (optional)"
            className="w-full bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <textarea
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Describe what you want to build..."
            className="w-full h-20 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 resize-none"
          />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="zinc">Full Pipeline</Badge>
              <Badge variant="zinc">Spec → Arch → Gov → Tests</Badge>
            </div>
            <button
              onClick={handleNewRun}
              disabled={loading || !intent.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
              {loading ? 'Launching...' : 'Launch Pipeline'}
            </button>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-4">
        {/* Run List */}
        <Card className="col-span-1">
          <SectionHeader title="Runs" subtitle={`${runs.length} runs`} icon={<Activity className="w-4 h-4" />} />
          {runs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-zinc-600">
              <Activity className="w-6 h-6 mb-2 opacity-20" />
              <p className="text-[10px] font-mono">No runs loaded</p>
              <p className="text-[9px] font-mono mt-1">Click Refresh or launch a new run</p>
            </div>
          ) : (
            <div className="space-y-1 max-h-[400px] overflow-y-auto">
              {runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => handleSelectRun(run.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded text-left transition-colors ${
                    selectedRunId === run.id
                      ? 'bg-emerald-500/10 border border-emerald-500/20'
                      : 'hover:bg-zinc-800/50 border border-transparent'
                  }`}
                >
                  <StatusDot status={run.status === 'running' ? 'running' : run.status === 'completed' ? 'completed' : run.status === 'failed' ? 'failed' : 'pending'} size="sm" />
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-mono text-zinc-300 truncate">
                      {run.intent || run.id.slice(0, 12)}
                    </div>
                    <div className="text-[9px] font-mono text-zinc-600">
                      {new Date(run.created_at).toLocaleString()}
                    </div>
                  </div>
                  <Badge variant={statusVariant(run.status) as any} size="sm">{run.status}</Badge>
                  <ChevronRight className="w-3 h-3 text-zinc-600" />
                </button>
              ))}
            </div>
          )}
        </Card>

        {/* Run Detail */}
        <Card className="col-span-2">
          <SectionHeader
            title="Run Detail"
            subtitle={selectedRunDetail ? selectedRunDetail.id : 'Select a run'}
            icon={<Activity className="w-4 h-4" />}
            action={
              selectedRunId && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleStartRun}
                    disabled={loading}
                    className="p-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded text-emerald-400 hover:bg-emerald-500/20 transition-colors disabled:opacity-30"
                    title="Start"
                  >
                    <Play className="w-3 h-3" />
                  </button>
                  <button
                    onClick={handlePauseRun}
                    disabled={loading}
                    className="p-1.5 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 hover:bg-amber-500/20 transition-colors disabled:opacity-30"
                    title="Pause"
                  >
                    <Pause className="w-3 h-3" />
                  </button>
                  <button
                    onClick={handleCancelRun}
                    disabled={loading}
                    className="p-1.5 bg-red-500/10 border border-red-500/30 rounded text-red-400 hover:bg-red-500/20 transition-colors disabled:opacity-30"
                    title="Cancel"
                  >
                    <Square className="w-3 h-3" />
                  </button>
                </div>
              )
            }
          />
          {detailLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
            </div>
          ) : selectedRunDetail ? (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-3">
                <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                  <span className="text-[9px] font-mono text-zinc-600 block">STATUS</span>
                  <Badge variant={statusVariant(selectedRunDetail.status) as any}>{selectedRunDetail.status}</Badge>
                </div>
                <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                  <span className="text-[9px] font-mono text-zinc-600 block">EVENTS</span>
                  <span className="text-[11px] font-mono text-zinc-200">{timelineEvents.length}</span>
                </div>
                <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                  <span className="text-[9px] font-mono text-zinc-600 block">MODEL</span>
                  <span className="text-[11px] font-mono text-zinc-200">{selectedRunDetail.model_provider || '—'}</span>
                </div>
                <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                  <span className="text-[9px] font-mono text-zinc-600 block">COST</span>
                  <span className="text-[11px] font-mono text-zinc-200">${selectedRunDetail.cost_usd?.toFixed(4) || '0.0000'}</span>
                </div>
              </div>
              {selectedRunDetail.intent && (
                <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                  <span className="text-[9px] font-mono text-zinc-600 block mb-1">INTENT</span>
                  <span className="text-[11px] font-mono text-zinc-300">{selectedRunDetail.intent}</span>
                </div>
              )}
              {/* Timeline Events */}
              {timelineEvents.length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-zinc-600 block mb-2">TIMELINE ({timelineEvents.length} events)</span>
                  <div className="max-h-48 overflow-y-auto space-y-1">
                    {timelineEvents.slice(0, 50).map((event) => (
                      <div key={event.id} className="flex items-center gap-2 px-2 py-1 bg-zinc-900/30 rounded text-[10px] font-mono">
                        <span className="text-zinc-600 w-6">{event.sequence}</span>
                        <span className="text-zinc-400">{event.type}</span>
                        {event.phase && <Badge variant="zinc" size="sm">{event.phase}</Badge>}
                        <span className="text-zinc-700 ml-auto">{new Date(event.timestamp).toLocaleTimeString()}</span>
                      </div>
                    ))}
                    {timelineEvents.length > 50 && (
                      <div className="text-[9px] font-mono text-zinc-600 text-center">
                        ... {timelineEvents.length - 50} more events
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-zinc-600">
              <Activity className="w-8 h-8 mb-2 opacity-20" />
              <p className="text-xs font-mono">Select a run to view details</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
