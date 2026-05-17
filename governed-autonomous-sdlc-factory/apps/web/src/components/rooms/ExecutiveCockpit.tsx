'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockScores, mockPhases, mockGovGates, mockTokenUsage, mockRequirements, mockHumanInterventions } from '@/lib/mock-data';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Clock, Coins, Shield, Target, Zap } from 'lucide-react';

export function ExecutiveCockpit() {
  const failedGates = mockGovGates.filter(g => g.status === 'failed');
  const criticalReqs = mockRequirements.filter(r => r.criticality === 'critical');
  const coveredCritical = criticalReqs.filter(r => r.semanticCoverageScore >= 0.8);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Executive Cockpit" subtitle="Portfolio overview and delivery confidence" />

      {/* Executive Narrative */}
      <div className="card-elevated p-5 border-l-2 border-l-violet-500/50">
        <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Executive Narrative</div>
        <p className="text-[12px] text-zinc-300 leading-relaxed">
          The application is <span className="text-violet-400 font-semibold">72% complete</span>. Core backend services are implemented, but release readiness is limited by <span className="text-amber-400 font-semibold">weak semantic coverage</span> in payment validation and <span className="text-red-400 font-semibold">missing negative tests</span> for authorization failure paths. Token burn is <span className="text-amber-400 font-semibold">above forecast</span> because the Architecture Agent regenerated the integration model three times after unresolved API ambiguity. Governance risk is <span className="text-amber-400 font-semibold">moderate</span>. Recommended action: resolve the API contract conflict before allowing further code generation.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-5 gap-3">
        <div className="card p-4 flex flex-col items-center">
          <GaugeChart value={mockScores.releaseReadiness} label="Release Ready" size="md" color={mockScores.releaseReadiness >= 0.8 ? 'green' : mockScores.releaseReadiness >= 0.5 ? 'amber' : 'red'} />
        </div>
        <MetricCard label="Value Delivered" value="72%" change="+8% this week" changeType="positive" icon={<TrendingUp className="w-3.5 h-3.5 text-emerald-400" />} />
        <MetricCard label="Cost to Date" value={`$${mockTokenUsage.totalCostUsd.toFixed(2)}`} change={`$${mockTokenUsage.budgetRemaining.toFixed(2)} remaining`} changeType="neutral" icon={<Coins className="w-3.5 h-3.5" />} />
        <MetricCard label="Risk Posture" value="Moderate" change={`${failedGates.length} gates failed`} changeType="warning" icon={<Shield className="w-3.5 h-3.5 text-amber-400" />} />
        <MetricCard label="Interventions" value={mockHumanInterventions.length.toString()} change="4 human actions" changeType="neutral" icon={<Clock className="w-3.5 h-3.5" />} />
      </div>

      {/* Trend Charts */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-3">Release Readiness Trend</div>
          <div className="flex items-end gap-1 h-20">
            {[0.45, 0.52, 0.58, 0.61, 0.65, 0.68, 0.70, 0.72, 0.62, 0.62].map((v, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                <div className="w-full bg-violet-500/30 rounded-t-sm" style={{ height: `${v * 100}%` }} />
                <span className="text-[7px] text-zinc-700">W{i + 1}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-1 mt-2">
            <TrendingDown className="w-3 h-3 text-red-400" />
            <span className="text-[9px] text-red-400">-10% this week (semantic coverage drop)</span>
          </div>
        </div>

        <div className="card p-4">
          <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-3">Semantic Coverage Trend</div>
          <div className="flex items-end gap-1 h-20">
            {[0.72, 0.75, 0.78, 0.82, 0.85, 0.83, 0.79, 0.74, 0.68, 0.66].map((v, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                <div className={`w-full rounded-t-sm ${v >= 0.8 ? 'bg-emerald-500/30' : v >= 0.6 ? 'bg-amber-500/30' : 'bg-red-500/30'}`} style={{ height: `${v * 100}%` }} />
                <span className="text-[7px] text-zinc-700">W{i + 1}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-1 mt-2">
            <TrendingDown className="w-3 h-3 text-red-400" />
            <span className="text-[9px] text-red-400">-16% this week (new requirements added)</span>
          </div>
        </div>

        <div className="card p-4">
          <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-3">Token Efficiency</div>
          <div className="flex items-end gap-1 h-20">
            {[0.65, 0.68, 0.72, 0.71, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84].map((v, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                <div className="w-full bg-blue-500/30 rounded-t-sm" style={{ height: `${v * 100}%` }} />
                <span className="text-[7px] text-zinc-700">W{i + 1}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-1 mt-2">
            <TrendingUp className="w-3 h-3 text-emerald-400" />
            <span className="text-[9px] text-emerald-400">+19% improvement</span>
          </div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-4">
          <SectionHeader title="Risk Distribution" subtitle="By category" />
          <div className="space-y-2 mt-2">
            {[
              { label: 'Semantic Coverage', value: 0.34, count: 3, color: 'red' },
              { label: 'Security', value: 0.15, count: 1, color: 'amber' },
              { label: 'Architecture Drift', value: 0.22, count: 2, color: 'amber' },
              { label: 'Token Budget', value: 0.05, count: 0, color: 'green' },
              { label: 'Test Coverage', value: 0.24, count: 2, color: 'amber' },
            ].map(r => (
              <div key={r.label} className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-500 w-32 flex-shrink-0">{r.label}</span>
                <div className="flex-1">
                  <ProgressBar value={r.value} size="sm" color={r.color === 'red' ? 'red' : r.color === 'amber' ? 'amber' : 'green'} />
                </div>
                <span className="text-[10px] font-mono text-zinc-600 w-6 text-right">{r.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-4">
          <SectionHeader title="Blocked Initiatives" subtitle="Requiring attention" />
          <div className="space-y-2 mt-2">
            {[
              { title: 'Fraud Detection Service', reason: 'ML model integration blocked — missing training data pipeline', impact: 'high' },
              { title: 'Transaction Dashboard', reason: 'Depends on fraud service completion', impact: 'medium' },
              { title: 'Release Gate', reason: 'Semantic coverage below 80% threshold', impact: 'critical' },
            ].map((b, i) => (
              <div key={i} className="flex items-start gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <AlertTriangle className={`w-3 h-3 mt-0.5 flex-shrink-0 ${b.impact === 'critical' ? 'text-red-400' : 'text-amber-400'}`} />
                <div>
                  <div className="text-[10px] font-medium text-zinc-300">{b.title}</div>
                  <div className="text-[9px] text-zinc-600">{b.reason}</div>
                </div>
                <Badge variant={b.impact === 'critical' ? 'red' : 'amber'} size="sm">{b.impact}</Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
