'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockGovGates } from '@/lib/mock-data';
import { Shield, CheckCircle2, XCircle, Clock, AlertTriangle, ArrowRight, FileText, Download, RefreshCw } from 'lucide-react';
import type { GovernanceEvaluationsResponse, ReleaseGateResponse } from '@/lib/api';

export function GovernanceGates() {
  const [evaluations, setEvaluations] = useState<GovernanceEvaluationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchGovernance = async () => {
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
      const result = await api.getGovernanceEvaluations(latestRun.id);
      setEvaluations(result);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch governance data');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGovernance();
  }, []);

  // Use real evaluations if available, otherwise mock
  const gates = dataSource === 'LIVE' && evaluations?.evaluations
    ? evaluations.evaluations.map(ev => ({
        id: ev.id,
        name: ev.policy_name || ev.policy_id,
        status: ev.status === 'pass' ? 'passed' : ev.status === 'fail' ? 'failed' : 'pending',
        owner: 'Governance Agent',
        timestamp: ev.created_at || '',
        policyBasis: ev.policy_id,
        impact: ev.severity === 'critical' ? 'critical' : ev.severity === 'warning' ? 'high' : 'medium',
        evidence: ev.findings?.map(f => f.message) || [],
      }))
    : mockGovGates;

  const passed = gates.filter(g => g.status === 'passed').length;
  const failed = gates.filter(g => g.status === 'failed').length;
  const blocked = gates.filter(g => g.status === 'blocked').length;
  const pending = gates.filter(g => g.status === 'pending').length;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Governance & Release Gates" subtitle="Policy enforcement and release readiness" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchGovernance}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-400/10 flex items-center justify-center"><CheckCircle2 className="w-4 h-4 text-emerald-400" /></div>
          <div><div className="text-lg font-semibold text-zinc-200">{passed}</div><div className="text-[9px] text-zinc-600 uppercase">Passed</div></div>
        </div>
        <div className="card p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-400/10 flex items-center justify-center"><XCircle className="w-4 h-4 text-red-400" /></div>
          <div><div className="text-lg font-semibold text-zinc-200">{failed}</div><div className="text-[9px] text-zinc-600 uppercase">Failed</div></div>
        </div>
        <div className="card p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-700/30 flex items-center justify-center"><Clock className="w-4 h-4 text-zinc-400" /></div>
          <div><div className="text-lg font-semibold text-zinc-200">{pending}</div><div className="text-[9px] text-zinc-600 uppercase">Pending</div></div>
        </div>
        <div className="card p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-400/10 flex items-center justify-center"><AlertTriangle className="w-4 h-4 text-red-400" /></div>
          <div><div className="text-lg font-semibold text-zinc-200">{blocked}</div><div className="text-[9px] text-zinc-600 uppercase">Blocked</div></div>
        </div>
      </div>

      {/* Gate Flow */}
      <div className="card p-4">
        <SectionHeader title="Governance Flow" subtitle="Sequential gate evaluation" />
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin py-2">
          {gates.map((gate, i) => (
            <React.Fragment key={gate.id}>
              <div className={`flex-shrink-0 w-44 p-3 rounded-lg border ${
                gate.status === 'passed' ? 'border-emerald-400/20 bg-emerald-400/5' :
                gate.status === 'failed' ? 'border-red-400/20 bg-red-400/5' :
                gate.status === 'blocked' ? 'border-red-400/20 bg-red-400/5' :
                'border-zinc-700/20 bg-zinc-800/20'
              }`}>
                <div className="flex items-center gap-1.5 mb-1">
                  {gate.impact === 'critical' && <Badge variant="red" size="sm">CRIT</Badge>}
                  <StatusChip status={gate.status === 'passed' ? 'verified' : gate.status === 'failed' ? 'failed' : gate.status === 'blocked' ? 'blocked' : 'pending'} size="sm" />
                </div>
                <div className="text-[10px] font-medium text-zinc-300 mb-0.5">{gate.name}</div>
                <div className="text-[8px] text-zinc-600">{gate.owner}</div>
                {gate.timestamp && <div className="text-[8px] text-zinc-700 mt-0.5">{gate.timestamp.slice(11, 16)}</div>}
              </div>
              {i < gates.length - 1 && (
                <ArrowRight className={`w-3 h-3 flex-shrink-0 ${
                  gate.status === 'passed' ? 'text-emerald-400/40' : 'text-zinc-800'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Evidence Bundles */}
      <div className="card p-4">
        <SectionHeader title="Evidence Bundles" subtitle="Artifacts for release decision reconstruction" />
        <div className="grid grid-cols-3 gap-3 mt-2">
          {[
            { id: 'eb-001', name: 'Requirements Evidence', artifacts: 12, size: '2.4 MB', date: '2026-05-14T06:47:00Z' },
            { id: 'eb-002', name: 'Architecture Evidence', artifacts: 8, size: '1.8 MB', date: '2026-05-14T07:39:00Z' },
            { id: 'eb-003', name: 'Test Coverage Evidence', artifacts: 18, size: '3.2 MB', date: '2026-05-14T08:14:00Z' },
          ].map(bundle => (
            <div key={bundle.id} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-3.5 h-3.5 text-violet-400" />
                <span className="text-[11px] font-medium text-zinc-300">{bundle.name}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mb-2">
                <div><div className="text-[8px] text-zinc-700 uppercase">Artifacts</div><div className="text-[10px] text-zinc-400">{bundle.artifacts}</div></div>
                <div><div className="text-[8px] text-zinc-700 uppercase">Size</div><div className="text-[10px] text-zinc-400">{bundle.size}</div></div>
                <div><div className="text-[8px] text-zinc-700 uppercase">Date</div><div className="text-[10px] text-zinc-400">{bundle.date.slice(0, 10)}</div></div>
              </div>
              <button className="flex items-center gap-1 text-[9px] text-violet-400 hover:text-violet-300">
                <Download className="w-2.5 h-2.5" /> Export
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
