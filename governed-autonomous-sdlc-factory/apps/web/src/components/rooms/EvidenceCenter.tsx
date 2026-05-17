'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { FileText, Download, Package, CheckCircle2, Clock, RefreshCw } from 'lucide-react';
import type { EvidenceResponse } from '@/lib/api';

export function EvidenceCenter() {
  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchEvidence = async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) {
        setError('No runs found');
        setDataSource('ERROR');
        return;
      }
      const result = await api.getEvidenceByRun(latestRun.id);
      setEvidence(result);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch evidence');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, []);

  const mockBundles = [
    { id: 'eb-001', name: 'Requirements Evidence', artifacts: 12, size: '2.4 MB', date: '2026-05-14T06:47:00Z', status: 'complete' },
    { id: 'eb-002', name: 'Architecture Evidence', artifacts: 8, size: '1.8 MB', date: '2026-05-14T07:39:00Z', status: 'complete' },
    { id: 'eb-003', name: 'Test Coverage Evidence', artifacts: 18, size: '3.2 MB', date: '2026-05-14T08:14:00Z', status: 'complete' },
    { id: 'eb-004', name: 'Governance Evidence', artifacts: 6, size: '1.1 MB', date: '2026-05-14T06:57:00Z', status: 'complete' },
    { id: 'eb-005', name: 'Release Evidence', artifacts: 0, size: '0 MB', date: '', status: 'pending' },
  ];

  const bundles = dataSource === 'LIVE' && evidence?.bundles
    ? evidence.bundles.map(b => ({
        id: b.id,
        name: (b as any).name || 'Evidence Bundle',
        artifacts: (b as any).file_count || 0,
        size: (b as any).size_bytes ? `${((b as any).size_bytes / 1048576).toFixed(1)} MB` : '—',
        date: (b as any).created_at || '',
        status: 'complete' as string,
      }))
    : mockBundles;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Evidence Center" subtitle="Forensic-grade evidence bundles" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchEvidence}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {bundles.map(bundle => (
          <div key={bundle.id} className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Package className="w-4 h-4 text-violet-400" />
              <span className="text-[11px] font-medium text-zinc-300">{bundle.name}</span>
              <StatusChip status={bundle.status === 'complete' ? 'verified' : 'pending'} size="sm" />
            </div>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div><div className="text-[8px] text-zinc-700 uppercase">Artifacts</div><div className="text-[10px] text-zinc-400">{bundle.artifacts}</div></div>
              <div><div className="text-[8px] text-zinc-700 uppercase">Size</div><div className="text-[10px] text-zinc-400">{bundle.size}</div></div>
              <div><div className="text-[8px] text-zinc-700 uppercase">Date</div><div className="text-[10px] text-zinc-400">{bundle.date ? bundle.date.slice(0, 10) : '—'}</div></div>
            </div>
            {bundle.status === 'complete' ? (
              <button className="flex items-center gap-1 text-[9px] text-violet-400 hover:text-violet-300">
                <Download className="w-2.5 h-2.5" /> Export Bundle
              </button>
            ) : (
              <span className="text-[9px] text-zinc-700">Not yet available</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
