'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type CostReportResponse, type CostAggregationItem } from '@/lib/api';
import { mockTokenUsage } from '@/lib/mock-data';
import { Coins, TrendingUp, TrendingDown, AlertTriangle, Flame, Brain, RotateCcw, RefreshCw, Activity, Zap, Shield } from 'lucide-react';

function aggEntries(record: Record<string, CostAggregationItem> | undefined): CostAggregationItem[] {
  if (!record) return [];
  return Object.values(record);
}

function aggMaxToken(items: CostAggregationItem[]): number {
  return Math.max(...items.map(i => i.total_tokens), 1);
}

export function Tokenomics() {
  const [report, setReport] = useState<CostReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchCostData = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      try {
        const r = await api.getCostReport(latestRun.id) as CostReportResponse;
        setReport(r);
        // LIVE if we have real data with tokens or calls
        const hasRealData = (r.total_tokens > 0 || r.total_calls > 0 || r.aggregation_confidence !== 'none');
        setDataSource(hasRealData ? 'LIVE' : 'PARTIAL');
      } catch { setDataSource('MOCK'); }
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchCostData(); }, []);

  // Backend data (LIVE)
  const totalTokens = report?.total_tokens ?? 0;
  const totalInput = report?.total_input_tokens ?? 0;
  const totalOutput = report?.total_output_tokens ?? 0;
  const totalCost = report?.total_cost ?? 0;
  const totalCalls = report?.total_calls ?? 0;
  const totalErrors = report?.total_errors ?? 0;
  const totalRetries = report?.total_retries ?? 0;
  const byPhase = aggEntries(report?.by_phase);
  const byModel = aggEntries(report?.by_model);
  const byProvider = aggEntries(report?.by_provider);
  const byAgent = aggEntries(report?.by_agent);
  const waste = report?.waste_summary;
  const missingFields = report?.missing_fields ?? [];
  const qualityWarnings = report?.data_quality_warnings ?? [];

  // Mock fallback only for panels without backend data
  const hasAgentData = byAgent.length > 0;
  const hasWasteData = waste !== undefined && (waste.retry_tokens > 0 || waste.failed_call_tokens > 0);

  const maxPhaseTokens = aggMaxToken(byPhase);
  const maxModelTokens = aggMaxToken(byModel);
  const maxAgentTokens = Math.max(...byAgent.map(a => a.total_tokens), 1);

  // Determine effective data source
  // LIVE = primary panels (totals, by_phase, by_model, by_provider) are backend-driven
  const effectiveSource = report && (report.total_tokens > 0 || report.total_calls > 0) ? 'LIVE' : dataSource;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={effectiveSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Tokenomics & Cost Intelligence" subtitle="Real-time token usage, cost analysis, and waste autopsy" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={effectiveSource} />
          <button onClick={fetchCostData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Data quality warnings */}
      {qualityWarnings.length > 0 && (
        <div className="card p-3 border-amber-400/20 bg-amber-400/5">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span className="text-[9px] text-amber-400 uppercase tracking-widest">Data Quality</span>
          </div>
          {qualityWarnings.map((w, i) => (
            <div key={i} className="text-[9px] text-amber-300">{w}</div>
          ))}
        </div>
      )}

      {/* Top metrics — all backend-driven */}
      <div className="grid grid-cols-6 gap-3">
        <MetricCard label="Total Tokens" value={totalTokens > 0 ? `${(totalTokens / 1000).toFixed(1)}k` : '—'}
          change={totalTokens > 0 ? `${(totalInput / 1000).toFixed(1)}k in / ${(totalOutput / 1000).toFixed(1)}k out` : 'No data'} changeType="neutral" icon={<Brain className="w-3.5 h-3.5" />} />
        <MetricCard label="Total Cost" value={totalCost > 0 ? `$${totalCost.toFixed(4)}` : '$0.0000'}
          change={report?.remaining_budget != null ? `$${report.remaining_budget.toFixed(2)} remaining` : (totalCost === 0 ? 'Local/free inference' : 'No budget set')}
          changeType={totalCost > 0 ? 'positive' : 'neutral'} icon={<Coins className="w-3.5 h-3.5" />} />
        <MetricCard label="Total Calls" value={totalCalls > 0 ? totalCalls.toString() : '—'}
          change={totalErrors > 0 ? `${totalErrors} errors` : 'No errors'} changeType={totalErrors > 0 ? 'warning' : 'positive'} icon={<Activity className="w-3.5 h-3.5" />} />
        <MetricCard label="Retries" value={totalRetries > 0 ? totalRetries.toString() : '0'}
          change={totalRetries > 0 ? 'Wasted tokens' : 'Clean run'} changeType={totalRetries > 0 ? 'warning' : 'positive'} icon={<RotateCcw className="w-3.5 h-3.5" />} />
        <MetricCard label="Failed Tokens" value={waste?.failed_call_tokens ? `${(waste.failed_call_tokens / 1000).toFixed(1)}k` : '0'}
          change="From failed calls" changeType={waste && waste.failed_call_tokens > 0 ? 'negative' : 'positive'} icon={<Flame className="w-3.5 h-3.5" />} />
        <MetricCard label="Retry Tokens" value={waste?.retry_tokens ? `${(waste.retry_tokens / 1000).toFixed(1)}k` : '0'}
          change="From retries" changeType={waste && waste.retry_tokens > 0 ? 'negative' : 'positive'} icon={<Zap className="w-3.5 h-3.5" />} />
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Token breakdown — backend */}
        <div className="col-span-8 card p-4">
          <SectionHeader title="Token Usage Breakdown" subtitle={`Total: ${totalTokens > 0 ? (totalTokens / 1000).toFixed(1) + 'k tokens' : 'No data'}`} />
          {totalTokens > 0 ? (
            <div className="grid grid-cols-4 gap-3 mt-4">
              {[
                { label: 'Input', value: totalInput, color: 'blue' as const },
                { label: 'Output', value: totalOutput, color: 'violet' as const },
                { label: 'Cached', value: 0, color: 'green' as const, missing: true },
                { label: 'Reasoning', value: 0, color: 'amber' as const, missing: true },
              ].map(t => (
                <div key={t.label}>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">
                    {t.label} {t.missing && <span className="text-zinc-600">(N/A)</span>}
                  </div>
                  <div className="text-sm font-semibold text-zinc-300">
                    {(t.value / 1000).toFixed(1)}k
                  </div>
                  {!t.missing && <ProgressBar value={t.value / totalTokens} size="sm" color={t.color} />}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-[10px] text-zinc-600 mt-4">No token data available from backend</div>
          )}

          {/* By Phase — backend */}
          {byPhase.length > 0 && (
            <div className="mt-4 pt-4 border-t border-[#1e2230]">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Tokens by Phase</div>
              <div className="grid grid-cols-8 gap-2">
                {byPhase.map(phase => (
                  <div key={phase.key} className="text-center">
                    <div className="h-24 flex items-end justify-center mb-1">
                      <div className="w-8 rounded-t-sm transition-all duration-500"
                        style={{ height: `${(phase.total_tokens / maxPhaseTokens) * 100}%`, backgroundColor: '#60a5fa', opacity: 0.6 }} />
                    </div>
                    <div className="text-[8px] text-zinc-600 truncate">{phase.label}</div>
                    <div className="text-[9px] font-mono text-zinc-500">{(phase.total_tokens / 1000).toFixed(0)}k</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* By Agent — backend if available, otherwise mock */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="Cost by Agent" subtitle={hasAgentData ? 'Token distribution (live)' : 'Token distribution (mock)'} />
          <div className="space-y-2 mt-2">
            {(hasAgentData
              ? byAgent.map(a => ({ label: a.label, tokens: a.total_tokens, cost: a.cost }))
              : mockTokenUsage.byAgent.map(a => ({ label: a.agent, tokens: a.tokens, cost: a.cost }))
            ).map((a, i) => (
              <div key={a.label}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-zinc-400">{a.label}</span>
                  <span className="text-[10px] font-mono text-zinc-600">${a.cost.toFixed(3)}</span>
                </div>
                <ProgressBar value={a.tokens / (hasAgentData ? maxAgentTokens : Math.max(...mockTokenUsage.byAgent.map(x => x.tokens), 1))} size="sm" color={i === 0 ? 'violet' : i === 1 ? 'blue' : i === 2 ? 'amber' : 'green'} />
              </div>
            ))}
            {!hasAgentData && (
              <div className="text-[8px] text-zinc-600 mt-1">Mock data — agent_id not set in cost events</div>
            )}
          </div>
        </div>
      </div>

      {/* By Model — backend */}
      {byModel.length > 0 && (
        <div className="card p-4">
          <SectionHeader title="Tokens by Model" subtitle={`${byModel.length} models used (live)`} />
          <div className="grid grid-cols-6 gap-3 mt-2">
            {byModel.map(m => (
              <div key={m.key} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[10px] font-medium text-zinc-300">{m.label}</div>
                <div className="text-sm font-semibold text-zinc-200 mt-1">{(m.total_tokens / 1000).toFixed(1)}k</div>
                <div className="text-[9px] text-zinc-600">${m.cost.toFixed(4)}</div>
                <div className="text-[8px] text-zinc-700 mt-1">{m.call_count} calls · {m.error_count} errors</div>
                <ProgressBar value={m.total_tokens / maxModelTokens} size="sm" color="blue" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* By Provider — backend */}
      {byProvider.length > 0 && (
        <div className="card p-4">
          <SectionHeader title="Tokens by Provider" subtitle={`${byProvider.length} providers (live)`} />
          <div className="grid grid-cols-4 gap-3 mt-2">
            {byProvider.map(p => (
              <div key={p.key} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[10px] font-medium text-zinc-300">{p.label}</div>
                <div className="text-sm font-semibold text-zinc-200 mt-1">{(p.total_tokens / 1000).toFixed(1)}k</div>
                <div className="text-[9px] text-zinc-600">${p.cost.toFixed(4)}</div>
                <div className="text-[8px] text-zinc-700 mt-1">{p.percentage_of_total}% of total</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Waste Summary — backend-derived */}
      {hasWasteData && (
        <div className="card p-4">
          <SectionHeader title="Token Waste Analysis" subtitle="Derived from retry and failed call events" icon={<AlertTriangle className="w-3.5 h-3.5 text-amber-400" />} />
          <div className="grid grid-cols-5 gap-3 mt-2">
            <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-1.5 mb-1">
                <RotateCcw className="w-3 h-3 text-red-400" />
                <span className="text-[10px] font-medium text-red-400">Retry Waste</span>
              </div>
              <div className="text-lg font-semibold text-zinc-200 mb-1">{waste ? (waste.retry_tokens / 1000).toFixed(1) + 'k' : '—'}</div>
              <div className="text-[9px] text-zinc-600">Tokens from retry events</div>
            </div>
            <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-1.5 mb-1">
                <Flame className="w-3 h-3 text-red-400" />
                <span className="text-[10px] font-medium text-red-400">Failed Calls</span>
              </div>
              <div className="text-lg font-semibold text-zinc-200 mb-1">{waste ? (waste.failed_call_tokens / 1000).toFixed(1) + 'k' : '—'}</div>
              <div className="text-[9px] text-zinc-600">Tokens from failed model calls</div>
            </div>
            <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-1.5 mb-1">
                <Shield className="w-3 h-3 text-zinc-500" />
                <span className="text-[10px] font-medium text-zinc-500">Oversized Prompts</span>
              </div>
              <div className="text-lg font-semibold text-zinc-500 mb-1">N/A</div>
              <div className="text-[9px] text-zinc-600">Not tracked by backend</div>
            </div>
            <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-1.5 mb-1">
                <Brain className="w-3 h-3 text-zinc-500" />
                <span className="text-[10px] font-medium text-zinc-500">Unused Context</span>
              </div>
              <div className="text-lg font-semibold text-zinc-500 mb-1">N/A</div>
              <div className="text-[9px] text-zinc-600">Not tracked by backend</div>
            </div>
            <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
              <div className="flex items-center gap-1.5 mb-1">
                <Zap className="w-3 h-3 text-zinc-500" />
                <span className="text-[10px] font-medium text-zinc-500">Total Waste</span>
              </div>
              <div className="text-lg font-semibold text-zinc-200 mb-1">
                {waste ? ((waste.retry_tokens + waste.failed_call_tokens) / 1000).toFixed(1) + 'k' : '—'}
              </div>
              <div className="text-[9px] text-zinc-600">
                {waste && totalTokens > 0 ? `${(((waste.retry_tokens + waste.failed_call_tokens) / totalTokens) * 100).toFixed(1)}% of total` : ''}
              </div>
            </div>
          </div>
          {waste?.notes && (
            <div className="mt-2 text-[8px] text-zinc-600">{waste.notes}</div>
          )}
        </div>
      )}

      {/* Missing fields notice */}
      {missingFields.length > 0 && (
        <div className="card p-3 border-zinc-700/30 bg-zinc-800/10">
          <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1">Missing Backend Data</div>
          <div className="flex gap-2">
            {missingFields.map(f => (
              <Badge key={f} variant="zinc" size="sm">{f}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
