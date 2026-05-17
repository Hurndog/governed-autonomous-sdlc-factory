'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { Link2, ArrowRight, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import type { TraceabilityResponse, CoverageResponse } from '@/lib/api';

export function TraceabilityRoom() {
  const [traceability, setTraceability] = useState<TraceabilityResponse | null>(null);
  const [coverage, setCoverage] = useState<CoverageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchTraceability = async () => {
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
      const [traceRes, covRes] = await Promise.allSettled([
        api.getTraceability(latestRun.id),
        api.getTraceabilityCoverage(latestRun.id),
      ]);
      if (traceRes.status === 'fulfilled') setTraceability(traceRes.value);
      if (covRes.status === 'fulfilled') setCoverage(covRes.value);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch traceability');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTraceability();
  }, []);

  const mockLinks = [
    { source: 'REQ-001', target: 'test_payment_gateway', type: 'validates', confidence: 0.95 },
    { source: 'REQ-001', target: 'arch-api-gateway', type: 'implemented-by', confidence: 0.92 },
    { source: 'REQ-002', target: 'test_balance_validation', type: 'validates', confidence: 0.98 },
    { source: 'REQ-004', target: 'test_auth_check_exists', type: 'validates', confidence: 0.45 },
    { source: 'REQ-005', target: 'test_fraud_detect', type: 'validates', confidence: 0.32 },
    { source: 'ADR-001', target: 'REQ-001', type: 'supports', confidence: 0.88 },
    { source: 'ADR-003', target: 'REQ-004', type: 'enforces', confidence: 0.95 },
  ];

  const links = dataSource === 'LIVE' && traceability?.links
    ? traceability.links.map(l => ({
        source: l.source_id,
        target: l.target_id,
        type: l.link_type,
        confidence: l.confidence || 0.5,
      }))
    : mockLinks;

  const coveragePct = coverage?.coverage_pct ?? 0.75;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Traceability" subtitle="Requirement → Test → Code → Evidence links" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchTraceability}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <SectionHeader title="Traceability Links" subtitle={`${links.length} links mapped`} />
          <div className="space-y-1.5 mt-2">
            {links.map((link, i) => (
              <div key={i} className="flex items-center gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <Badge variant="blue" size="sm">{link.source}</Badge>
                <ArrowRight className="w-3 h-3 text-zinc-700 flex-shrink-0" />
                <span className="text-[10px] text-zinc-500">{link.type}</span>
                <ArrowRight className="w-3 h-3 text-zinc-700 flex-shrink-0" />
                <Badge variant="violet" size="sm">{link.target}</Badge>
                <div className="flex-1" />
                <div className="w-16">
                  <ProgressBar value={link.confidence} size="sm" color={link.confidence >= 0.8 ? 'green' : link.confidence >= 0.5 ? 'amber' : 'red'} />
                </div>
                <span className="text-[9px] font-mono text-zinc-600 w-8 text-right">{Math.round(link.confidence * 100)}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-4 card p-4">
          <SectionHeader title="Coverage Summary" />
          <div className="space-y-3 mt-2">
            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Requirements → Tests</div>
              <ProgressBar value={coveragePct} color="blue" showLabel />
            </div>
            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Tests → Code</div>
              <ProgressBar value={0.82} color="green" showLabel />
            </div>
            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Code → Evidence</div>
              <ProgressBar value={0.68} color="amber" showLabel />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1e2230]">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Weak Links</div>
            <div className="space-y-1.5">
              {links.filter(l => l.confidence < 0.5).map((link, i) => (
                <div key={i} className="flex items-center gap-2 text-[9px]">
                  <AlertTriangle className="w-2.5 h-2.5 text-red-400" />
                  <span className="text-zinc-500">{link.source} → {link.target}</span>
                  <span className="text-red-400">{Math.round(link.confidence * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
