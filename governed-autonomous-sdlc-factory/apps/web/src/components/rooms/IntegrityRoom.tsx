'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockScores } from '@/lib/mock-data';
import { Shield, CheckCircle2, AlertTriangle, FileText, Hash, Link2, Eye, RotateCcw, RefreshCw } from 'lucide-react';
import type { IntegrityResponse } from '@/lib/api';

export function IntegrityRoom() {
  const [integrity, setIntegrity] = useState<IntegrityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('MOCK');

  const fetchIntegrity = async () => {
    setLoading(true);
    setError(null);
    setDataSource('LOADING');
    try {
      // Try to get the latest run first, then check integrity
      const runsRes = await api.listRuns({ page_size: 1 });
      const latestRun = runsRes.items?.[0];
      if (!latestRun) {
        setError('No runs found — cannot verify integrity');
        setDataSource('ERROR');
        return;
      }
      const result = await api.verifyIntegrity(latestRun.id);
      setIntegrity(result);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify integrity');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  // Mock components for fallback
  const mockComponents = [
    { name: 'Artifact Hashing', score: 0.98, status: 'pass' as const, icon: Hash, details: 'SHA256 hashes for all artifacts verified' },
    { name: 'Event Sourcing', score: 0.96, status: 'pass' as const, icon: Link2, details: 'Hash chain intact across all events' },
    { name: 'Snapshot Integrity', score: 0.94, status: 'pass' as const, icon: Eye, details: 'All phase snapshots verified' },
    { name: 'Lineage Tracking', score: 0.92, status: 'pass' as const, icon: FileText, details: 'Full provenance from spec to code' },
    { name: 'Evidence Binding', score: 0.95, status: 'pass' as const, icon: Shield, details: 'Evidence bundles bound to run' },
    { name: 'Replay Verification', score: 0.97, status: 'pass' as const, icon: RotateCcw, details: 'Deterministic replay verified' },
    { name: 'Semantic Coverage', score: 0.66, status: 'warn' as const, icon: AlertTriangle, details: 'Score below threshold' },
  ];

  // Use real data if available
  const components = integrity?.report?.results
    ? Object.entries(integrity.report.results).map(([key, val]) => ({
        name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        score: val.score,
        status: val.status,
        icon: Shield,
        details: JSON.stringify(val.details || {}).slice(0, 80),
      }))
    : mockComponents;

  const overallScore = integrity?.integrity_score ?? mockScores.integrityScore;
  const overallStatus = integrity?.status ?? 'pass';

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner
        state={dataSource}
        message={error || undefined}
      />

      <div className="flex items-center justify-between">
        <SectionHeader title="Integrity Room" subtitle="Seven-component integrity verification" />
        <button
          onClick={fetchIntegrity}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-violet-500/10 text-violet-400 border border-violet-500/20 text-[10px] hover:bg-violet-500/20 disabled:opacity-50"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Verifying...' : 'Verify Integrity'}
        </button>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <MetricCard
          label="Overall Score"
          value={`${Math.round(overallScore * 100)}%`}
          change={integrity ? `From run ${integrity.run_id.slice(0, 8)}` : 'Mock data'}
          changeType={overallScore >= 0.9 ? 'positive' : 'warning'}
          icon={<Shield className="w-3.5 h-3.5 text-emerald-400" />}
        />
        <MetricCard label="Components" value={components.length.toString()} change={integrity ? 'From backend' : 'Mock'} changeType="neutral" />
        <MetricCard label="Artifacts Hashed" value={integrity ? String(integrity.checks) : '47'} change="Verified" changeType="positive" icon={<Hash className="w-3.5 h-3.5" />} />
        <MetricCard
          label="Chain Intact"
          value={overallStatus === 'pass' ? 'Yes' : overallStatus === 'warn' ? 'Warning' : 'No'}
          change={integrity?.duration_ms ? `${integrity.duration_ms}ms` : 'Mock'}
          changeType={overallStatus === 'pass' ? 'positive' : 'warning'}
          icon={<CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
        />
      </div>

      <div className="card p-4">
        <SectionHeader title="Component Breakdown" />
        <div className="space-y-3 mt-2">
          {components.map(comp => {
            const Icon = comp.icon;
            return (
              <div key={comp.name} className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  comp.status === 'pass' ? 'bg-emerald-400/10' : comp.status === 'warn' ? 'bg-amber-400/10' : 'bg-red-400/10'
                }`}>
                  <Icon className={`w-4 h-4 ${comp.status === 'pass' ? 'text-emerald-400' : comp.status === 'warn' ? 'text-amber-400' : 'text-red-400'}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[11px] font-medium text-zinc-300">{comp.name}</span>
                    <StatusChip status={comp.status === 'pass' ? 'verified' : comp.status === 'warn' ? 'warning' : 'failed'} size="sm" />
                  </div>
                  <div className="text-[9px] text-zinc-600">{comp.details}</div>
                </div>
                <div className="w-24">
                  <ProgressBar value={comp.score} size="sm" color={comp.status === 'pass' ? 'green' : comp.status === 'warn' ? 'amber' : 'red'} showLabel />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
