'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { mockProcessEvents, mockAgents } from '@/lib/mock-data';
import { Play, Pause, SkipBack, SkipForward, Clock, Bot, CheckCircle2, AlertTriangle, RotateCcw } from 'lucide-react';

export function RunReplay() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [position, setPosition] = useState(0);
  const events = mockProcessEvents;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Run Replay & Time Travel" subtitle="Reconstruct the build timeline" />

      {/* Playback controls */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <button className="p-1.5 rounded hover:bg-zinc-800/50 text-zinc-500"><SkipBack className="w-3.5 h-3.5" /></button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded bg-violet-500/20 text-violet-400 hover:bg-violet-500/30"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button className="p-1.5 rounded hover:bg-zinc-800/50 text-zinc-500"><SkipForward className="w-3.5 h-3.5" /></button>
          </div>

          <div className="flex-1">
            <input
              type="range"
              min={0}
              max={events.length - 1}
              value={position}
              onChange={(e) => setPosition(parseInt(e.target.value))}
              className="w-full h-1 bg-zinc-800 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-violet-400"
            />
            <div className="flex justify-between mt-1">
              <span className="text-[8px] text-zinc-700">06:00</span>
              <span className="text-[9px] text-zinc-500">{events[position]?.timestamp.slice(11, 16) || '06:00'}</span>
              <span className="text-[8px] text-zinc-700">08:15</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[9px] text-zinc-600">
            <Clock className="w-3 h-3" />
            <span>Event {position + 1}/{events.length}</span>
          </div>
        </div>
      </div>

      {/* Current state at position */}
      <div className="grid grid-cols-12 gap-4">
        {/* Timeline */}
        <div className="col-span-8 card p-4">
          <SectionHeader title="Event Timeline" subtitle="Chronological agent actions" />
          <div className="space-y-0 mt-2">
            {events.map((evt, i) => (
              <div
                key={evt.id}
                className={`flex items-start gap-3 py-2 px-2 rounded transition-colors ${
                  i === position ? 'bg-violet-500/10 border border-violet-500/20' :
                  i < position ? 'opacity-60' : 'opacity-30'
                }`}
              >
                <div className="w-12 flex-shrink-0 pt-0.5">
                  <span className="text-[9px] font-mono text-zinc-600">{evt.timestamp.slice(11, 16)}</span>
                </div>
                <div className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                  evt.result === 'success' ? 'bg-emerald-400' : evt.result === 'failure' ? 'bg-red-400' : 'bg-amber-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-medium text-zinc-300">{evt.agent}</span>
                    <span className="text-[10px] text-zinc-600">→</span>
                    <span className="text-[10px] text-zinc-400">{evt.action}</span>
                  </div>
                  <div className="text-[9px] text-zinc-600 mt-0.5">
                    Artifact: <span className="text-zinc-500">{evt.artifact}</span> • {(evt.tokenCost / 1000).toFixed(1)}k tokens
                  </div>
                </div>
                <StatusChip status={evt.result === 'success' ? 'verified' : evt.result === 'failure' ? 'failed' : 'warning'} size="sm" />
              </div>
            ))}
          </div>
        </div>

        {/* State at time */}
        <div className="col-span-4 space-y-4">
          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">System State at {events[position]?.timestamp.slice(11, 16)}</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-500">Phase</span>
                <span className="text-[10px] text-zinc-300">{events[position]?.phase || 'Intake'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-500">Active Agent</span>
                <span className="text-[10px] text-zinc-300">{events[position]?.agent || 'Product Analyst'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-500">Tokens Used</span>
                <span className="text-[10px] text-zinc-300">{events.slice(0, position + 1).reduce((s, e) => s + e.tokenCost, 0).toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-500">Artifacts Created</span>
                <span className="text-[10px] text-zinc-300">{position + 1}</span>
              </div>
            </div>
          </div>

          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Replay Integrity</div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] text-zinc-400">Hash chain intact</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] text-zinc-400">All events verifiable</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] text-zinc-400">No divergences detected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
