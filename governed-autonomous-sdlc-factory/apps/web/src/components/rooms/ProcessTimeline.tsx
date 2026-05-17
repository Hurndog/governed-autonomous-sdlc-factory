'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { mockProcessEvents, mockPhases, mockAgents } from '@/lib/mock-data';
import { Clock, AlertTriangle, CheckCircle2, ArrowRight, Bot, User } from 'lucide-react';

export function ProcessTimeline() {
  const lanes = [
    { id: 'user', label: 'User', icon: User, color: '#e8eaed' },
    { id: 'product', label: 'Product', icon: Bot, color: '#60a5fa' },
    { id: 'arch', label: 'Arch', icon: Bot, color: '#fbbf24' },
    { id: 'governance', label: 'Gov', icon: Bot, color: '#a78bfa' },
    { id: 'coding', label: 'Code', icon: Bot, color: '#22d3ee' },
    { id: 'testing', label: 'Test', icon: Bot, color: '#c084fc' },
    { id: 'verifier', label: 'Verify', icon: Bot, color: '#f87171' },
  ];

  const laneAgentMap: Record<string, string[]> = {
    'user': ['Marco'],
    'product': ['Product Analyst', 'Requirement Normalizer'],
    'arch': ['Architecture Agent'],
    'governance': ['Governance Agent'],
    'coding': ['Code Generation'],
    'testing': ['Test Generation', 'Semantic Coverage', 'Evidence Agent'],
    'verifier': ['Verifier'],
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Process Timeline" subtitle="SDLC workflow visualization with swimlanes" />

      {/* Timeline scrubber */}
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
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600">
            <Clock className="w-3 h-3" /> Elapsed: 2h 14m
          </div>
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600">
            <AlertTriangle className="w-3 h-3 text-amber-400" /> 3 rework loops
          </div>
          <div className="flex items-center gap-1.5 text-[9px] text-zinc-600">
            <User className="w-3 h-3" /> 4 human interventions
          </div>
        </div>
      </div>

      {/* Swimlanes */}
      <div className="card p-4">
        <div className="space-y-1">
          {lanes.map(lane => {
            const Icon = lane.icon;
            const laneEvents = mockProcessEvents.filter(evt =>
              laneAgentMap[lane.id]?.includes(evt.agent)
            );
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
                    const pos = ((evtHour - startHour) * 60 + evtMin) / (135) * 100; // 2h15m = 135min
                    return (
                      <div
                        key={evt.id}
                        className={`absolute top-0.5 h-5 rounded text-[7px] flex items-center px-1.5 truncate ${
                          evt.result === 'success' ? 'bg-emerald-400/20 text-emerald-400 border border-emerald-400/30' :
                          evt.result === 'failure' ? 'bg-red-400/20 text-red-400 border border-red-400/30' :
                          'bg-amber-400/20 text-amber-400 border border-amber-400/30'
                        }`}
                        style={{ left: `${pos}%`, width: '120px' }}
                        title={`${evt.agent}: ${evt.action}`}
                      >
                        {evt.action.slice(0, 20)}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Process Friction */}
      <div className="card p-4">
        <SectionHeader title="Process Friction Analysis" subtitle="Main causes of delay" />
        <div className="grid grid-cols-4 gap-3 mt-2">
          {[
            { cause: 'API Contract Ambiguity', impact: '3 regenerations', tokens: '11.2k', severity: 'high' },
            { cause: 'Security Policy Violation', impact: '1 rework cycle', tokens: '4.8k', severity: 'medium' },
            { cause: 'Weak Requirements (REQ-005)', impact: 'Low testability', tokens: '3.4k', severity: 'high' },
            { cause: 'Missing Human Approval', impact: '18min wait', tokens: '0', severity: 'low' },
          ].map((f, i) => (
            <div key={i} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-1.5 mb-1">
                <AlertTriangle className={`w-3 h-3 ${f.severity === 'high' ? 'text-red-400' : f.severity === 'medium' ? 'text-amber-400' : 'text-zinc-500'}`} />
                <span className="text-[10px] font-medium text-zinc-300">{f.cause}</span>
              </div>
              <div className="text-[9px] text-zinc-600">{f.impact}</div>
              <div className="text-[9px] text-zinc-700 mt-0.5">{f.tokens} tokens wasted</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
