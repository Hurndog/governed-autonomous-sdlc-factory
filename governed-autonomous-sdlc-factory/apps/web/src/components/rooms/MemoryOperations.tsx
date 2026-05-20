'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { StatusChip } from '@/components/ui/StatusChip';
import { MetricCard } from '@/components/ui/MetricCard';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { DataSourceBadge } from '@/components/ui/DataSourceBadge';

// ── Types ──────────────────────────────────────────────────────────────────

interface MemorySummary {
  generated_at: string;
  semantic_memory: {
    total: number;
    active: number;
    inactive: number;
    expired: number;
    high_drift: number;
    medium_drift: number;
    low_confidence: number;
    avg_drift: number;
    avg_confidence: number;
  };
  memory_items: {
    total: number;
    types: Record<string, number>;
  };
  context_validity: {
    total: number;
    active: number;
    stale: number;
    expired: number;
    avg_staleness: number;
  };
  memory_versions: {
    total: number;
    types: number;
    projects: number;
    max_version: number;
  };
  aging: {
    stale_threshold_hours: number;
    expiry_threshold_hours: number;
    archival_threshold_hours: number;
    last_aging_run: string | null;
  };
}

// ── Main Component ─────────────────────────────────────────────────────────

export function MemoryOperations() {
  const [data, setData] = useState<MemorySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'live' | 'fallback' | 'error'>('fallback');
  const [lastRefresh, setLastRefresh] = useState('');
  const [agingResult, setAgingResult] = useState<any>(null);
  const [actionResult, setActionResult] = useState<{ message: string; success: boolean } | null>(null);

  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') || '' : '';

  const fetchSummary = useCallback(async () => {
    try {
      const resp = await fetch('/api/v1/memory/lifecycle/summary', {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: AbortSignal.timeout(10000),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json: MemorySummary = await resp.json();
      setData(json);
      setDataSource('live');
      setError(null);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e: any) {
      setError(e.message || 'Failed to fetch memory summary');
      setDataSource('error');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const runAging = async () => {
    try {
      const resp = await fetch('/api/v1/memory/aging/run', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const result = await resp.json();
      setAgingResult(result);
      setActionResult({ message: `Aging completed: ${JSON.stringify(result.results)}`, success: true });
      fetchSummary();
    } catch (e: any) {
      setActionResult({ message: e.message || 'Aging failed', success: false });
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <SectionHeader title="Memory Operations" subtitle="Loading memory lifecycle state..." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {[1, 2, 3].map(i => <Card key={i} className="h-24 animate-pulse bg-gray-800"><div /></Card>)}
        </div>
      </div>
    );
  }

  const sm = data?.semantic_memory;
  const cv = data?.context_validity;
  const mi = data?.memory_items;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Memory Operations"
          subtitle={`Memory lifecycle management${lastRefresh ? ` — Last updated: ${lastRefresh}` : ''}`}
        />
        <div className="flex items-center gap-3">
          <DataSourceBadge state={dataSource === 'live' ? 'LIVE' : dataSource === 'error' ? 'ERROR' : 'PARTIAL'} />
          <button onClick={fetchSummary} className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded">
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <Card className="border-red-500/30 bg-red-950/20">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {actionResult && (
        <Card className={actionResult.success ? 'border-emerald-500/30 bg-emerald-950/20' : 'border-red-500/30 bg-red-950/20'}>
          <div className="flex items-center justify-between">
            <p className={`text-sm ${actionResult.success ? 'text-emerald-400' : 'text-red-400'}`}>{actionResult.message}</p>
            <button onClick={() => setActionResult(null)} className="text-xs text-gray-500 hover:text-gray-300">✕</button>
          </div>
        </Card>
      )}

      {/* Semantic Memory Overview */}
      {sm && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Semantic Memory</h3>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            <MetricCard label="Total" value={sm.total} />
            <MetricCard label="Active" value={sm.active} badge={{ label: 'Active', variant: 'green' }} />
            <MetricCard label="Inactive" value={sm.inactive} badge={{ label: 'Inactive', variant: 'zinc' }} />
            <MetricCard label="Expired" value={sm.expired} badge={{ label: 'Expired', variant: 'red' }} />
            <MetricCard label="High Drift" value={sm.high_drift} badge={{ label: 'Drift', variant: 'amber' }} />
            <MetricCard label="Low Conf." value={sm.low_confidence} badge={{ label: 'Conf', variant: 'amber' }} />
          </div>
          <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
            <span>Avg Drift: <span className={sm.avg_drift > 0.3 ? 'text-amber-400' : 'text-gray-300'}>{sm.avg_drift}</span></span>
            <span>Avg Confidence: <span className={sm.avg_confidence < 0.5 ? 'text-amber-400' : 'text-gray-300'}>{sm.avg_confidence}</span></span>
          </div>
        </Card>
      )}

      {/* Context Validity */}
      {cv && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Context Validity</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard label="Total" value={cv.total} />
            <MetricCard label="Active" value={cv.active} badge={{ label: 'Active', variant: 'green' }} />
            <MetricCard label="Stale" value={cv.stale} badge={{ label: 'Stale', variant: 'amber' }} />
            <MetricCard label="Expired" value={cv.expired} badge={{ label: 'Expired', variant: 'red' }} />
            <MetricCard label="Avg Staleness" value={cv.avg_staleness.toFixed(2)} badge={{ label: 'Stale', variant: cv.avg_staleness > 0.3 ? 'amber' : 'green' }} />
          </div>
        </Card>
      )}

      {/* Memory Items */}
      {mi && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Memory Items</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard label="Total" value={mi.total} />
            {Object.entries(mi.types).slice(0, 3).map(([type, count]) => (
              <MetricCard key={type} label={type} value={count} badge={{ label: type, variant: 'blue' }} />
            ))}
          </div>
        </Card>
      )}

      {/* Aging Controls */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Memory Aging</h3>
        <p className="text-xs text-gray-500 mb-3">
          Run memory aging to apply lifecycle transitions: stale (24h), expired (7d), confidence decay, auto-archive (30d).
          Evidence links are preserved. No critical evidence is silently deleted.
        </p>
        <div className="flex items-center gap-3">
          <button
            onClick={runAging}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs rounded font-semibold"
          >
            Run Memory Aging
          </button>
          {data?.aging && (
            <span className="text-[10px] text-gray-500">
              Thresholds: Stale {data.aging.stale_threshold_hours}h → Expired {data.aging.expiry_threshold_hours}h → Archive {data.aging.archival_threshold_hours}h
            </span>
          )}
        </div>
        {agingResult && (
          <div className="mt-3 p-2 bg-gray-800/50 rounded text-xs">
            <p className="text-gray-300">Last aging run: {agingResult.run_at}</p>
            <p className="text-gray-400">Results: stale={agingResult.results.stale}, expired={agingResult.results.expired}, archived={agingResult.results.archived}, confidence_decayed={agingResult.results.confidence_decayed}</p>
          </div>
        )}
      </Card>

      {/* Lifecycle States Legend */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Lifecycle States</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            { state: 'active', label: 'Active', desc: 'Currently in use', status: 'verified' as const },
            { state: 'stale', label: 'Stale', desc: 'Not verified in 24h', status: 'warning' as const },
            { state: 'expired', label: 'Expired', desc: 'Past validity period', status: 'error' as const },
            { state: 'quarantined', label: 'Quarantined', desc: 'Isolated for review', status: 'warning' as const },
            { state: 'archived', label: 'Archived', desc: 'Inactive for 30d+', status: 'pending' as const },
            { state: 'superseded', label: 'Superseded', desc: 'Replaced by newer', status: 'pending' as const },
            { state: 'invalidated', label: 'Invalidated', desc: 'Marked invalid', status: 'error' as const },
          ].map(item => (
            <div key={item.state} className="flex items-center gap-2 bg-gray-800/30 rounded px-2 py-1.5">
              <StatusChip status={item.status} size="sm" />
              <div>
                <p className="text-xs text-gray-300 font-medium">{item.label}</p>
                <p className="text-[10px] text-gray-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
