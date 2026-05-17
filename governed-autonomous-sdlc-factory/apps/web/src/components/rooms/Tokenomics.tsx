'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockTokenUsage } from '@/lib/mock-data';
import { Coins, TrendingUp, TrendingDown, AlertTriangle, Flame, Brain, RotateCcw, MessageSquare, Layers } from 'lucide-react';

export function Tokenomics() {
  const burnData = mockTokenUsage.burnRate;
  const maxTokens = Math.max(...burnData.map(d => d.tokens));

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Tokenomics & Cost Intelligence" subtitle="Real-time token usage, cost analysis, and waste autopsy" />

      {/* Top metrics */}
      <div className="grid grid-cols-6 gap-3">
        <MetricCard label="Total Tokens" value={`${(mockTokenUsage.totalTokens / 1000).toFixed(1)}k`} change={`${(mockTokenUsage.inputTokens / 1000).toFixed(1)}k in / ${(mockTokenUsage.outputTokens / 1000).toFixed(1)}k out`} changeType="neutral" icon={<Brain className="w-3.5 h-3.5" />} />
        <MetricCard label="Total Cost" value={`$${mockTokenUsage.totalCostUsd.toFixed(3)}`} change={`$${mockTokenUsage.budgetRemaining.toFixed(2)} remaining`} changeType="positive" icon={<Coins className="w-3.5 h-3.5" />} badge={{ label: `${Math.round((mockTokenUsage.totalTokens / 250000) * 100)}% of budget`, variant: 'blue' }} />
        <MetricCard label="Wasted Tokens" value={`${(mockTokenUsage.wastedTokens.total / 1000).toFixed(1)}k`} change={`${Math.round((mockTokenUsage.wastedTokens.total / mockTokenUsage.totalTokens) * 100)}% of total`} changeType="negative" icon={<Flame className="w-3.5 h-3.5" />} badge={{ label: 'Waste', variant: 'red' }} />
        <MetricCard label="Cost / Req" value={`$${mockTokenUsage.costPerAcceptedRequirement.toFixed(3)}`} change="Per accepted requirement" changeType="neutral" />
        <MetricCard label="Cost / Test" value={`$${mockTokenUsage.costPerPassingTest.toFixed(3)}`} change="Per passing test" changeType="neutral" />
        <MetricCard label="Cost / Release" value={`$${mockTokenUsage.costPerReleaseCandidate.toFixed(3)}`} change="Per release candidate" changeType="neutral" />
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Token Burn Chart */}
        <div className="col-span-8 card p-4">
          <SectionHeader title="Token Burn Rate" subtitle="Cumulative tokens over time" />
          <div className="mt-4">
            {/* Simple bar chart */}
            <div className="flex items-end gap-1 h-40">
              {burnData.map((d, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div
                    className="w-full bg-gradient-to-t from-violet-500/40 to-violet-400/20 rounded-t-sm transition-all duration-500"
                    style={{ height: `${(d.tokens / maxTokens) * 100}%` }}
                  />
                  <span className="text-[7px] text-zinc-700">{d.time.slice(0, 5)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Token breakdown */}
          <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-[#1e2230]">
            {[
              { label: 'Input', value: mockTokenUsage.inputTokens, color: 'blue' as const },
              { label: 'Output', value: mockTokenUsage.outputTokens, color: 'violet' as const },
              { label: 'Cached', value: mockTokenUsage.cachedTokens, color: 'green' as const },
              { label: 'Reasoning', value: mockTokenUsage.reasoningTokens, color: 'amber' as const },
            ].map(t => (
              <div key={t.label}>
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">{t.label}</div>
                <div className="text-sm font-semibold text-zinc-300">{(t.value / 1000).toFixed(1)}k</div>
                <ProgressBar value={t.value / mockTokenUsage.totalTokens} size="sm" color={t.color} />
              </div>
            ))}
          </div>
        </div>

        {/* Cost by Agent */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="Cost by Agent" subtitle="Token distribution" />
          <div className="space-y-2 mt-2">
            {mockTokenUsage.byAgent.map((a, i) => (
              <div key={a.agent}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-zinc-400">{a.agent}</span>
                  <span className="text-[10px] font-mono text-zinc-600">${a.cost.toFixed(3)}</span>
                </div>
                <ProgressBar value={a.tokens / mockTokenUsage.totalTokens} size="sm" color={i === 0 ? 'violet' : i === 1 ? 'blue' : i === 2 ? 'amber' : 'green'} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Token Waste Autopsy */}
      <div className="card p-4">
        <SectionHeader title="Token Waste Autopsy" subtitle={`${(mockTokenUsage.wastedTokens.total / 1000).toFixed(1)}k tokens wasted — here's why`} icon={<AlertTriangle className="w-3.5 h-3.5 text-amber-400" />} />
        <div className="grid grid-cols-5 gap-3 mt-2">
          {mockTokenUsage.wastedTokens.byCategory.map((cat, i) => (
            <div key={i} className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-1.5 mb-1">
                {i === 0 ? <RotateCcw className="w-3 h-3 text-red-400" /> :
                 i === 1 ? <AlertTriangle className="w-3 h-3 text-red-400" /> :
                 i === 2 ? <Layers className="w-3 h-3 text-red-400" /> :
                 i === 3 ? <Brain className="w-3 h-3 text-red-400" /> :
                 <MessageSquare className="w-3 h-3 text-red-400" />}
                <span className="text-[10px] font-medium text-red-400">{cat.category}</span>
              </div>
              <div className="text-lg font-semibold text-zinc-200 mb-1">{(cat.tokens / 1000).toFixed(1)}k</div>
              <div className="text-[9px] text-zinc-600">{cat.reason}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost by Phase */}
      <div className="card p-4">
        <SectionHeader title="Cost by SDLC Phase" subtitle="Token expenditure across pipeline" />
        <div className="grid grid-cols-8 gap-2 mt-2">
          {mockTokenUsage.byPhase.map((phase, i) => (
            <div key={phase.phase} className="text-center">
              <div className="h-24 flex items-end justify-center mb-1">
                <div
                  className="w-8 rounded-t-sm transition-all duration-500"
                  style={{
                    height: `${(phase.tokens / 70000) * 100}%`,
                    backgroundColor: ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee', '#c084fc', '#fb923c'][i],
                    opacity: 0.6,
                  }}
                />
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
