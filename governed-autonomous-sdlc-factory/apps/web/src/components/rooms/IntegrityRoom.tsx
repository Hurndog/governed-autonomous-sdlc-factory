'use client';
import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { useStore } from '@/lib/store';
import { mockScores } from '@/lib/mock-data';
import { Shield, CheckCircle2, AlertTriangle, FileText, Hash, Link2, Eye, RotateCcw } from 'lucide-react';

export function IntegrityRoom() {
  const integrity = useStore((s) => s.integrityResult);

  const components = [
    { name: 'Artifact Hashing', score: 0.98, status: 'pass' as const, icon: Hash, details: 'SHA256 hashes for all 47 artifacts verified' },
    { name: 'Event Sourcing', score: 0.96, status: 'pass' as const, icon: Link2, details: 'Hash chain intact across 14 events' },
    { name: 'Snapshot Integrity', score: 0.94, status: 'pass' as const, icon: Eye, details: '8 phase snapshots verified' },
    { name: 'Lineage Tracking', score: 0.92, status: 'pass' as const, icon: FileText, details: 'Full provenance from spec to code' },
    { name: 'Evidence Binding', score: 0.95, status: 'pass' as const, icon: Shield, details: '3 evidence bundles bound to run' },
    { name: 'Replay Verification', score: 0.97, status: 'pass' as const, icon: RotateCcw, details: 'Deterministic replay verified' },
    { name: 'Semantic Coverage', score: 0.66, status: 'warn' as const, icon: AlertTriangle, details: 'Score 65.6% below 80% threshold' },
  ];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Integrity Room" subtitle="Seven-component integrity verification" />

      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Overall Score" value={`${Math.round(mockScores.integrityScore * 100)}%`} change="6/7 pass" changeType="positive" icon={<Shield className="w-3.5 h-3.5 text-emerald-400" />} />
        <MetricCard label="Components" value="7" change="1 warning" changeType="warning" />
        <MetricCard label="Artifacts Hashed" value="47" change="All verified" changeType="positive" icon={<Hash className="w-3.5 h-3.5" />} />
        <MetricCard label="Chain Intact" value="Yes" change="No divergences" changeType="positive" icon={<CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />} />
      </div>

      <div className="card p-4">
        <SectionHeader title="Component Breakdown" />
        <div className="space-y-3 mt-2">
          {components.map(comp => {
            const Icon = comp.icon;
            return (
              <div key={comp.name} className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  comp.status === 'pass' ? 'bg-emerald-400/10' : 'bg-amber-400/10'
                }`}>
                  <Icon className={`w-4 h-4 ${comp.status === 'pass' ? 'text-emerald-400' : 'text-amber-400'}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[11px] font-medium text-zinc-300">{comp.name}</span>
                    <StatusChip status={comp.status === 'pass' ? 'verified' : 'warning'} size="sm" />
                  </div>
                  <div className="text-[9px] text-zinc-600">{comp.details}</div>
                </div>
                <div className="w-24">
                  <ProgressBar value={comp.score} size="sm" color={comp.status === 'pass' ? 'green' : 'amber'} showLabel />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
