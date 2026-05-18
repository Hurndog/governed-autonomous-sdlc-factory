'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type CostReportResponse } from '@/lib/api';
import { mockTokenUsage } from '@/lib/mock-data';
import { Coins, TrendingUp, TrendingDown, AlertTriangle, Flame, Brain, RotateCcw, MessageSquare, Layers, RefreshCw } from 'lucide-react';

export function Tokenomics() {
  const [costReport, setCostReport] = useState<CostReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchCostData = async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      try {
        const report = await api.getCostReport(latestRun.id) as CostReportResponse;
        setCostReport(report);
        setDataSource('PARTIAL');
      } catch { setDataSource('MOCK'); }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cost data');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchCostData(); }, []);

  const totalCost = costReport?.total_cost_usd ?? mockTokenUsage.totalCostUsd;
  const byModel = costReport?.by_model ?? {};
  const byProvider = costReport?.by_provider ?? {};

  const estimatedTotalTokens = costReport ? costReport.total_tokens : mockTokenUsage.totalTokens;
  const inputTokens = Math.round(estimatedTotalTokens * 0.6);
  const outputTokens = Math.round(estimatedTotalTokens * 0.25);
  const cachedTokens = Math.round(estimatedTotalTokens * 0.1);
  const reasoningTokens = Math.round(estimatedTotalTokens * 0.05);

  const phaseData = mockTokenUsage.byPhase;
  const agentData = mockTokenUsage.byAgent;
  const maxPhaseTokens = Math.max(...phaseData.map(p => p.tokens), 1);
  const maxAgentTokens = Math.max(...agentData.map(a => a.tokens), 1);

  const modelEntries = Object.entries(byModel);
  const providerEntries = Object.entries(byProvider);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Tokenomics & Cost Intelligence" subtitle="Real-time token usage, cost analysis, and waste autopsy" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchCostData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-3">
        <MetricCard label="Total Tokens" value={`${(estimatedTotalTokens / 1000).toFixed(1)}k`}
          change={`${(inputTokens / 1000).toFixed(1)}k in / ${(outputTokens / 1000).toFixed(1)}k out`} changeType="neutral" icon={<Brain className="w-3.5 h-3.5" />} />
        <MetricCard label="Total Cost" value={`$${totalCost.toFixed(3)}`}
          change={costReport ? `${costReport.total_tokens} tokens` : 'Mock data'} changeType="positive" icon={<Coins className="w-3.5 h-3.5" />} />
        <MetricCard label="Wasted Tokens" value={`${(mockTokenUsage.wastedTokens.total / 1000).toFixed(1)}k`}
          change={`${Math.round((mockTokenUsage.wastedTokens.total / mockTokenUsage.totalTokens) * 100)}% of total`} changeType="negative" icon={<Flame className="w-3.5 h-3.5" />} badge={{ label: 'Waste', variant: 'red' }} />
        <MetricCard label="Cost / Req" value={`$${mockTokenUsage.costPerAcceptedRequirement.toFixed(3)}`} change="Per accepted requirement" changeType="neutral" />
        <MetricCard label="Cost / Test" value={`$${mockTokenUsage.costPerPassingTest.toFixed(3)}`} change="Per passing test" changeType="neutral" />
        <MetricCard label="Cost / Release" value={`$${mockTokenUsage.costPerReleaseCandidate.toFixed(3)}`} change="Per release candidate" changeType="neutral" />
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <SectionHeader title="Token Burn Rate" subtitle={`Cumulative tokens over time ${dataSource === 'MOCK' ? '(mock)' : ''}`} />
          <div className="mt-4">
            <div className="flex items-end gap-1 h-40">
              {mockTokenUsage.burnRate.map((d, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full bg-gradient-to-t from-violet-500/40 to-violet-400/20 rounded-t-sm transition-all duration-500"
                    style={{ height: `${(d.tokens / Math.max(...mockTokenUsage.burnRate.map(x => x.tokens))) * 100}%` }} />
                  <span className="text-[7px] text-zinc-700">{d.time.slice(0, 5)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-[#1e2230]">
            {[
              { label: 'Input', value: inputTokens, color: 'blue' as const },
              { label: 'Output', value: outputTokens, color: 'violet' as const },
              { label: 'Cached', value: cachedTokens, color: 'green' as const },
              { label: 'Reasoning', value: reasoningTokens, color: 'amber' as const },
            ].map(t => (
              <div key={t.label}>
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">{t.label}</div>
                <div className="text-sm font-semibold text-zinc-300">{(t.value / 1000).toFixed(1)}k</div>
                <ProgressBar value={t.value / estimatedTotalTokens} size="sm" color={t.color} />
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-4 card p-4">
          <SectionHeader title="Cost by Agent" subtitle={`Token distribution ${dataSource === 'MOCK' ? '(mock)' : ''}`} />
          <div className="space-y-2 mt-2">
            {agentData.map((a, i) => (
              <div key={a.agent}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-zinc-400">{a.agent}</span>
                  <span className="text-[10px] font-mono text-zinc-600">${a.cost.toFixed(3)}</span>
                </div>
                <ProgressBar value={a.tokens / maxAgentTokens} size="sm" color={i === 0 ? 'violet' : i === 1 ? 'blue' : i === 2 ? 'amber' : 'green'} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {modelEntries.length > 0 && (
        <div className="card p-4">
          <SectionHeader title="Cost by Model" subtitle="Token distribution across models (live)" />
          <div className="grid grid-cols-6 gap-3 mt-2">
            {modelEntries.map(([model, data]) => (
              <div key={model} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[10px] font-medium text-zinc-300">{model}</div>
                <div className="text-sm font-semibold text-zinc-200 mt-1">{(data.tokens / 1000).toFixed(1)}k</div>
                <div className="text-[9px] text-zinc-600">${data.cost_usd.toFixed(3)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {providerEntries.length > 0 && (
        <div className="card p-4">
          <SectionHeader title="Cost by Provider" subtitle="Token distribution across providers (live)" />
          <div className="grid grid-cols-4 gap-3 mt-2">
            {providerEntries.map(([provider, data]) => (
              <div key={provider} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[10px] font-medium text-zinc-300">{provider}</div>
                <div className="text-sm font-semibold text-zinc-200 mt-1">{(data.tokens / 1000).toFixed(1)}k</div>
                <div className="text-[9px] text-zinc-600">${data.cost_usd.toFixed(3)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-4">
        <SectionHeader title="Token Waste Autopsy" subtitle={`${(mockTokenUsage.wastedTokens.total / 1000).toFixed(1)}k tokens wasted`} icon={<AlertTriangle className="w-3.5 h-3.5 text-amber-400" />} />
        <div className="grid grid-cols-5 gap-3 mt-2">
          {mockTokenUsage.wastedTokens.byCategory.map((cat, i) => (
            <div key={i} className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-1.5 mb-1">
                {i === 0 ? <RotateCcw className="w-3 h-3 text-red-400" /> : i === 1 ? <AlertTriangle className="w-3 h-3 text-red-400" /> : i === 2 ? <Layers className="w-3 h-3 text-red-400" /> : i === 3 ? <Brain className="w-3 h-3 text-red-400" /> : <MessageSquare className="w-3 h-3 text-red-400" />}
                <span className="text-[10px] font-medium text-red-400">{cat.category}</span>
              </div>
              <div className="text-lg font-semibold text-zinc-200 mb-1">{(cat.tokens / 1000).toFixed(1)}k</div>
              <div className="text-[9px] text-zinc-600">{cat.reason}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-4">
        <SectionHeader title="Cost by SDLC Phase" subtitle={`Token expenditure across pipeline ${dataSource === 'MOCK' ? '(mock)' : ''}`} />
        <div className="grid grid-cols-8 gap-2 mt-2">
          {phaseData.map((phase, i) => (
            <div key={phase.phase} className="text-center">
              <div className="h-24 flex items-end justify-center mb-1">
                <div className="w-8 rounded-t-sm transition-all duration-500"
                  style={{ height: `${(phase.tokens / maxPhaseTokens) * 100}%`, backgroundColor: ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee', '#c084fc', '#fb923c'][i % 8], opacity: 0.6 }} />
              </div>
              <div className="text-[8px] text-zinc-600 truncate">{phase.phase}</div>
              <div className="text-[9px] font-mono text-zinc-500">{(phase.tokens / 1000).toFixed(0)}k</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
