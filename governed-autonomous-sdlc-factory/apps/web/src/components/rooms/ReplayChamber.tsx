'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, StatusDot, ProgressBar, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  RotateCcw,
  Play,
  Pause,
  SkipForward,
  SkipBack,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  Hash,
  Clock,
  Layers,
  ArrowRight,
  Activity,
  Loader2,
  Search,
} from 'lucide-react';

export function ReplayChamber() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const replaySessions = useStore((s) => s.replaySessions);
  const setReplaySessions = useStore((s) => s.setReplaySessions);
  const activeReplaySession = useStore((s) => s.activeReplaySession);
  const setActiveReplaySession = useStore((s) => s.setActiveReplaySession);
  const timelinePos = useStore((s) => s.replayTimelinePosition);
  const setTimelinePos = useStore((s) => s.setReplayTimelinePosition);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [loading, setLoading] = useState(false);
  const [replaying, setReplaying] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const events = activeReplaySession?.events || [];
  const currentEvent = events[timelinePos] || null;
  const integrityScore = (activeReplaySession as any)?.integrity_score || (activeReplaySession as any)?.integrity_preserved ? 1.0 : 0;
  const divergenceCount = (activeReplaySession as any)?.divergence_count || 0;

  const handleLoadSessions = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.getReplaySessions(runIdInput.trim());
      const sessions = (result as any).sessions || [];
      setReplaySessions(sessions);
      if (sessions.length > 0) {
        setActiveReplaySession(sessions[0] as any);
      }
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, setReplaySessions, setActiveReplaySession, setLastError]);

  const handleReplay = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setReplaying(true);
    setLastError(null);
    try {
      const result = await api.replayRun(runIdInput.trim());
      // Reload sessions
      await handleLoadSessions();
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setReplaying(false);
    }
  }, [runIdInput, handleLoadSessions, setLastError]);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            REPLAY CHAMBER
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Forensic Cognitive Investigation — Black Box Analysis — Deterministic Reconstruction
          </p>
        </div>
        <Badge variant={integrityScore >= 0.95 ? 'emerald' : integrityScore >= 0.8 ? 'amber' : 'red'}>
          <RotateCcw className="w-3 h-3 mr-1" />
          Integrity: {(integrityScore * 100).toFixed(1)}%
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Replay Control" subtitle="Load or execute replay" icon={<RotateCcw className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <button
            onClick={handleLoadSessions}
            disabled={loading || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-md text-blue-400 text-xs font-mono font-medium hover:bg-blue-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            {loading ? 'Loading...' : 'Load Sessions'}
          </button>
          <button
            onClick={handleReplay}
            disabled={replaying || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {replaying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {replaying ? 'Replaying...' : 'Execute Replay'}
          </button>
        </div>
      </Card>

      {replaySessions.length === 0 && !activeReplaySession && !loading && (
        <div className="flex flex-col items-center justify-center py-24 text-zinc-600">
          <RotateCcw className="w-12 h-12 mb-4 opacity-20" />
          <p className="text-sm font-mono">No replay sessions available</p>
          <p className="text-[10px] font-mono mt-2">
            Enter a run ID and click Load Sessions or Execute Replay
          </p>
        </div>
      )}

      {(replaySessions.length > 0 || activeReplaySession) && (
        <>
          {/* Replay Sessions */}
          {replaySessions.length > 0 && (
            <Card>
              <SectionHeader title="Replay Sessions" subtitle={`${replaySessions.length} sessions`} icon={<Layers className="w-4 h-4" />} />
              <div className="space-y-2">
                {replaySessions.map((session: any) => (
                  <button
                    key={session.id}
                    onClick={() => setActiveReplaySession(session)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-md border text-left transition-colors ${
                      activeReplaySession?.id === session.id
                        ? 'bg-emerald-500/5 border-emerald-500/20'
                        : 'bg-zinc-900/50 border-zinc-800/50 hover:bg-zinc-800/50'
                    }`}
                  >
                    <StatusDot status={session.status === 'completed' ? 'completed' : session.status === 'running' ? 'running' : 'failed'} size="sm" />
                    <div className="flex-1">
                      <span className="text-xs font-mono text-zinc-200">{session.id.slice(0, 24)}...</span>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-[9px] font-mono text-zinc-600">{session.event_count || 0} events</span>
                        <span className="text-[9px] font-mono text-zinc-600">{session.divergence_count || 0} divergences</span>
                      </div>
                    </div>
                    <Badge variant={session.status === 'completed' ? 'emerald' : session.status === 'running' ? 'amber' : 'red'}>
                      {session.status}
                    </Badge>
                  </button>
                ))}
              </div>
            </Card>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-5 gap-4">
            <Card>
              <Metric label="Events" value={events.length} color="text-zinc-200" />
            </Card>
            <Card>
              <Metric label="Divergences" value={divergenceCount} color={divergenceCount > 0 ? 'text-red-400' : 'text-emerald-400'} />
            </Card>
            <Card>
              <Metric label="Integrity" value={`${(integrityScore * 100).toFixed(1)}%`} color={integrityScore >= 0.95 ? 'text-emerald-400' : 'text-amber-400'} />
            </Card>
            <Card>
              <Metric label="Snapshots" value={Math.floor(events.length / 10)} color="text-blue-400" />
            </Card>
            <Card>
              <Metric label="Session" value={activeReplaySession?.id?.slice(0, 8) || '—'} color="text-zinc-200" />
            </Card>
          </div>

          {/* Raw Response */}
          {activeReplaySession && (
            <Card>
              <SectionHeader title="Replay Session Data" subtitle="Raw session response" icon={<Activity className="w-4 h-4" />} />
              <pre className="text-[10px] font-mono text-zinc-400 bg-zinc-900/50 border border-zinc-800 rounded-md p-3 overflow-auto max-h-64">
                {JSON.stringify(activeReplaySession, null, 2)}
              </pre>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
