'use client';

import React, { useState } from 'react';
import { Card, Badge, Metric, StatusDot, ProgressBar, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
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
} from 'lucide-react';

export function ReplayChamber() {
  const replaySessions = useStore((s) => s.replaySessions);
  const activeSession = useStore((s) => s.activeReplaySession);
  const timelinePos = useStore((s) => s.replayTimelinePosition);
  const setTimelinePos = useStore((s) => s.setReplayTimelinePosition);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const events = activeSession?.events || [];
  const currentEvent = events[timelinePos] || null;
  const integrityScore = activeSession?.integrity_score || 0;
  const divergenceCount = activeSession?.divergence_count || 0;

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

      {replaySessions.length === 0 && !activeSession ? (
        <div className="flex flex-col items-center justify-center py-24 text-zinc-600">
          <RotateCcw className="w-12 h-12 mb-4 opacity-20" />
          <p className="text-sm font-mono">No replay sessions available</p>
          <p className="text-[10px] font-mono mt-2">
            Execute a pipeline to generate replay data
          </p>
        </div>
      ) : (
        <>
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
              <Metric label="Semantic Transitions" value={events.filter((e: any) => e.semantic_transition).length} color="text-zinc-200" />
            </Card>
          </div>

          {/* Timeline Scrubber */}
          <Card glow={isPlaying ? 'emerald' : 'none'}>
            <SectionHeader
              title="Replay Timeline"
              subtitle={`Event ${timelinePos + 1} of ${events.length} — ${isPlaying ? 'Playing' : 'Paused'}`}
              icon={<Activity className="w-4 h-4" />}
              action={
                <div className="flex items-center gap-2">
                  <Badge variant="zinc">{playbackSpeed}x</Badge>
                </div>
              }
            />

            {/* Timeline Bar */}
            <div className="mb-4">
              <div className="relative h-8 bg-zinc-900 rounded-md border border-zinc-800 overflow-hidden">
                {/* Event markers */}
                <div className="absolute inset-0 flex">
                  {events.map((e: any, i: number) => (
                    <div
                      key={i}
                      onClick={() => setTimelinePos(i)}
                      className={`flex-1 border-r border-zinc-800/50 cursor-pointer transition-colors ${
                        i === timelinePos
                          ? 'bg-emerald-500/20'
                          : i < timelinePos
                          ? 'bg-emerald-500/5'
                          : 'hover:bg-zinc-800/50'
                      } ${e.divergence ? 'bg-red-500/10' : ''}`}
                    />
                  ))}
                </div>
                {/* Position indicator */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-emerald-400 transition-all duration-150"
                  style={{ left: `${events.length > 0 ? (timelinePos / (events.length - 1)) * 100 : 0}%` }}
                />
              </div>
              {/* Divergence markers */}
              <div className="flex mt-1">
                {events.map((e: any, i: number) => (
                  <div key={i} className="flex-1">
                    {e.divergence && (
                      <div className="flex justify-center">
                        <AlertTriangle className="w-3 h-3 text-red-400" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Playback Controls */}
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setTimelinePos(0)}
                className="p-2 rounded-md bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                <SkipBack className="w-4 h-4" />
              </button>
              <button
                onClick={() => setTimelinePos(Math.max(0, timelinePos - 1))}
                className="p-2 rounded-md bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                <SkipBack className="w-3 h-3" />
              </button>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-3 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 transition-colors"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              </button>
              <button
                onClick={() => setTimelinePos(Math.min(events.length - 1, timelinePos + 1))}
                className="p-2 rounded-md bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                <SkipForward className="w-3 h-3" />
              </button>
              <button
                onClick={() => setTimelinePos(events.length - 1)}
                className="p-2 rounded-md bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                <SkipForward className="w-4 h-4" />
              </button>
              <div className="ml-4 flex items-center gap-2">
                {[0.5, 1, 2, 4].map((speed) => (
                  <button
                    key={speed}
                    onClick={() => setPlaybackSpeed(speed)}
                    className={`px-2 py-1 rounded text-[10px] font-mono ${
                      playbackSpeed === speed
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-600 hover:text-zinc-400'
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>
            </div>
          </Card>

          {/* Event Detail + Causal Graph */}
          <div className="grid grid-cols-3 gap-4">
            {/* Current Event */}
            <Card className="col-span-2">
              <SectionHeader
                title="Event Detail"
                subtitle={currentEvent ? `Seq #${currentEvent.sequence} — ${currentEvent.type}` : 'No event selected'}
                icon={<Layers className="w-4 h-4" />}
                action={
                  currentEvent?.divergence ? (
                    <Badge variant="red">DIVERGENCE</Badge>
                  ) : (
                    <Badge variant="emerald">CLEAN</Badge>
                  )
                }
              />
              {currentEvent ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                      <span className="text-[9px] font-mono text-zinc-600 block mb-1">TYPE</span>
                      <span className="text-[11px] font-mono text-zinc-200">{currentEvent.type}</span>
                    </div>
                    <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                      <span className="text-[9px] font-mono text-zinc-600 block mb-1">TIMESTAMP</span>
                      <span className="text-[11px] font-mono text-zinc-200">
                        {new Date(currentEvent.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                      <span className="text-[9px] font-mono text-zinc-600 block mb-1">HASH</span>
                      <span className="text-[10px] font-mono text-zinc-400 truncate block">
                        {currentEvent.hash}
                      </span>
                    </div>
                    <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                      <span className="text-[9px] font-mono text-zinc-600 block mb-1">SEMANTIC TRANSITION</span>
                      <span className="text-[11px] font-mono text-zinc-200">
                        {currentEvent.semantic_transition || '—'}
                      </span>
                    </div>
                  </div>
                  {currentEvent.data && Object.keys(currentEvent.data).length > 0 && (
                    <div className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                      <span className="text-[9px] font-mono text-zinc-600 block mb-2">PAYLOAD</span>
                      <pre className="text-[10px] font-mono text-zinc-400 overflow-auto max-h-32">
                        {JSON.stringify(currentEvent.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-12 text-zinc-600">
                  <p className="text-xs font-mono">Select an event from the timeline</p>
                </div>
              )}
            </Card>

            {/* Causal Chain */}
            <Card>
              <SectionHeader title="Causal Chain" subtitle="Event lineage" icon={<GitBranch className="w-4 h-4" />} />
              <div className="space-y-1 max-h-[400px] overflow-y-auto">
                {events.slice(Math.max(0, timelinePos - 5), timelinePos + 6).map((e: any, i: number) => {
                  const actualIdx = Math.max(0, timelinePos - 5) + i;
                  const isCurrent = actualIdx === timelinePos;
                  return (
                    <div
                      key={actualIdx}
                      onClick={() => setTimelinePos(actualIdx)}
                      className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors ${
                        isCurrent
                          ? 'bg-emerald-500/10 border border-emerald-500/20'
                          : 'hover:bg-zinc-800/50 border border-transparent'
                      }`}
                    >
                      <span className="text-[9px] font-mono text-zinc-600 w-4">{actualIdx}</span>
                      {e.divergence ? (
                        <AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0" />
                      ) : (
                        <CheckCircle2 className="w-3 h-3 text-emerald-400/50 flex-shrink-0" />
                      )}
                      <span className="text-[10px] font-mono text-zinc-400 truncate">{e.type}</span>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>

          {/* Integrity Heatmap */}
          <Card>
            <SectionHeader
              title="Integrity Heatmap"
              subtitle="Per-event integrity verification"
              icon={<Hash className="w-4 h-4" />}
            />
            <div className="flex gap-0.5">
              {events.map((e: any, i: number) => (
                <div
                  key={i}
                  onClick={() => setTimelinePos(i)}
                  className={`h-6 flex-1 rounded-sm cursor-pointer transition-all ${
                    e.divergence
                      ? 'bg-red-500/40 hover:bg-red-500/60'
                      : i <= timelinePos
                      ? 'bg-emerald-500/30 hover:bg-emerald-500/50'
                      : 'bg-zinc-800/50 hover:bg-zinc-700/50'
                  }`}
                  title={`Event ${i}: ${e.type}${e.divergence ? ' (DIVERGENCE)' : ''}`}
                />
              ))}
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-[9px] font-mono text-zinc-600">0</span>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-sm bg-emerald-500/30" />
                  <span className="text-[9px] font-mono text-zinc-600">Verified</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-sm bg-red-500/40" />
                  <span className="text-[9px] font-mono text-zinc-600">Divergence</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-sm bg-zinc-800/50" />
                  <span className="text-[9px] font-mono text-zinc-600">Pending</span>
                </div>
              </div>
              <span className="text-[9px] font-mono text-zinc-600">{events.length}</span>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
