'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockArchComponents, mockADRs, mockArchDrift } from '@/lib/mock-data';
import { Network, AlertTriangle, CheckCircle2, FileText, TrendingUp } from 'lucide-react';

export function ArchitectureIntelligence() {
  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Architecture Intelligence" subtitle="System structure, drift analysis, and decision records" />

      <div className="grid grid-cols-12 gap-4">
        {/* Component Map */}
        <div className="col-span-8 card p-4">
          <SectionHeader title="Component Topology" subtitle={`${mockArchComponents.length} components`} />
          <div className="grid grid-cols-4 gap-2 mt-2">
            {mockArchComponents.map(comp => (
              <div key={comp.id} className={`p-2.5 rounded-lg border ${
                comp.status === 'verified' ? 'border-emerald-400/20 bg-emerald-400/5' :
                comp.status === 'tested' ? 'border-blue-400/20 bg-blue-400/5' :
                comp.status === 'generated' ? 'border-amber-400/20 bg-amber-400/5' :
                comp.status === 'blocked' ? 'border-red-400/20 bg-red-400/5' :
                'border-zinc-700/20 bg-zinc-800/20'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-medium text-zinc-300">{comp.name}</span>
                  <StatusChip status={comp.status === 'implemented' ? 'verified' : comp.status} size="sm" />
                </div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-[8px] text-zinc-700 uppercase">{comp.type}</span>
                  <span className="text-[8px] text-zinc-700">{(comp.tokenCost / 1000).toFixed(1)}k tok</span>
                </div>
                <ProgressBar value={comp.testCoverage} size="sm" color={comp.testCoverage >= 0.8 ? 'green' : comp.testCoverage >= 0.5 ? 'amber' : 'red'} />
                <div className="text-[8px] text-zinc-600 mt-0.5">{Math.round(comp.testCoverage * 100)}% coverage • {comp.changeFrequency} changes</div>
              </div>
            ))}
          </div>
        </div>

        {/* Drift Radar */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="Architecture Drift Radar" subtitle="Planned vs actual" />
          <div className="space-y-2 mt-2">
            {mockArchDrift.map(d => (
              <div key={d.domain}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-zinc-400">{d.domain}</span>
                  <span className={`text-[10px] font-mono ${d.score > 0.3 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {Math.round(d.score * 100)}%
                  </span>
                </div>
                <ProgressBar value={d.score} size="sm" color={d.score > 0.3 ? 'amber' : 'green'} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ADRs */}
      <div className="card p-4">
        <SectionHeader title="Architecture Decision Records" subtitle={`${mockADRs.length} decisions documented`} />
        <div className="grid grid-cols-2 gap-3 mt-2">
          {mockADRs.map(adr => (
            <div key={adr.id} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-3 h-3 text-violet-400" />
                <span className="text-[10px] font-mono text-violet-400">{adr.id}</span>
                <StatusChip status={adr.status === 'accepted' ? 'verified' : 'pending'} size="sm" />
              </div>
              <div className="text-[11px] font-medium text-zinc-300 mb-1">{adr.title}</div>
              <div className="text-[9px] text-zinc-600 mb-2">{adr.context}</div>
              <div className="text-[9px] text-zinc-500 mb-1"><span className="text-zinc-600">Decision:</span> {adr.decision}</div>
              <div className="text-[9px] text-zinc-600 mb-2"><span className="text-zinc-600">Impact:</span> {adr.consequences}</div>
              <div className="flex gap-1">
                {adr.linkedRequirements.map(req => (
                  <Badge key={req} variant="blue" size="sm">{req}</Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
