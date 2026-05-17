'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { StatusChip } from '@/components/ui/StatusChip';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { Badge } from '@/components/ui/Badge';
import {
  mockApplication, mockBuildRun, mockScores, mockPhases, mockAgents,
  mockRequirements, mockTokenUsage, mockGovGates, mockProcessEvents,
} from '@/lib/mock-data';
import {
  Activity, AlertTriangle, Bot, CheckCircle2, Clock, Coins,
  GitBranch, Shield, Target, Zap, TrendingUp, TrendingDown,
  ArrowRight, CircleDot,
} from 'lucide-react';

export function Dashboard() {
  const activeAgents = mockAgents.filter(a => a.status === 'working');
  const completedPhases = mockPhases.filter(p => p.status === 'completed').length;
  const failedGates = mockGovGates.filter(g => g.status === 'failed');
  const criticalReqs = mockRequirements.filter(r => r.criticality === 'critical');
  const coveredCritical = criticalReqs.filter(r => r.semanticCoverageScore >= 0.8);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Hero Section */}
      <div className="card-elevated p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 via-transparent to-blue-500/5" />
        <div className="relative flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-violet-500/15 border border-violet-500/25 flex items-center justify-center">
                <Zap className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-zinc-100">{mockApplication.name}</h1>
                <p className="text-xs text-zinc-500">{mockApplication.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 mt-4">
              <Badge variant="violet" dot>Building</Badge>
              <span className="text-xs text-zinc-600">Phase {mockBuildRun.currentPhase}/{mockBuildRun.totalPhases}: {mockPhases.find(p => p.status === 'active')?.name}</span>
              <span className="text-xs text-zinc-600">•</span>
              <span className="text-xs text-zinc-600">{activeAgents.length} agents active</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <GaugeChart value={mockScores.overallProgress} label="Overall" size="lg" color="violet" />
          </div>
        </div>

        {/* Multi-ring progress */}
        <div className="grid grid-cols-5 gap-4 mt-6 pt-6 border-t border-[#1e2230]">
          {[
            { label: 'SDLC Phase', value: completedPhases / mockPhases.length, color: 'blue' as const, icon: GitBranch },
            { label: 'Artifacts', value: 0.78, color: 'green' as const, icon: CheckCircle2 },
            { label: 'Test Coverage', value: mockScores.testCoverage, color: 'cyan' as const, icon: Target },
            { label: 'Governance', value: 1 - mockScores.governanceRisk, color: 'amber' as const, icon: Shield },
            { label: 'Release Ready', value: mockScores.releaseReadiness, color: 'violet' as const, icon: Zap },
          ].map((ring) => (
            <div key={ring.label} className="flex flex-col items-center gap-2">
              <GaugeChart value={ring.value} label={ring.label} size="sm" color={ring.color} />
            </div>
          ))}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-6 gap-3">
        <MetricCard
          label="Release Readiness"
          value={`${Math.round(mockScores.releaseReadiness * 100)}%`}
          change={failedGates.length > 0 ? `${failedGates.length} gates failed` : 'All clear'}
          changeType={failedGates.length > 0 ? 'negative' : 'positive'}
          badge={{ label: failedGates.length > 0 ? 'Blocked' : 'Ready', variant: failedGates.length > 0 ? 'red' : 'green' }}
        />
        <MetricCard
          label="Semantic Coverage"
          value={`${Math.round(mockScores.semanticCoverage * 100)}%`}
          change={`${coveredCritical.length}/${criticalReqs.length} critical covered`}
          changeType={coveredCritical.length === criticalReqs.length ? 'positive' : 'negative'}
          badge={{ label: mockScores.semanticCoverage >= 0.8 ? 'Pass' : 'Below Threshold', variant: mockScores.semanticCoverage >= 0.8 ? 'green' : 'amber' }}
        />
        <MetricCard
          label="Evidence Maturity"
          value={`${Math.round(mockScores.evidenceMaturity * 100)}%`}
          change="+5% from last run"
          changeType="positive"
          badge={{ label: 'Strong', variant: 'green' }}
        />
        <MetricCard
          label="Token Usage"
          value={`${(mockTokenUsage.totalTokens / 1000).toFixed(1)}k`}
          change={`$${mockTokenUsage.totalCostUsd.toFixed(2)} spent`}
          changeType="neutral"
          badge={{ label: `${Math.round((mockTokenUsage.totalTokens / 250000) * 100)}% of budget`, variant: 'blue' }}
        />
        <MetricCard
          label="Architecture Drift"
          value={`${Math.round(mockScores.architectureDrift * 100)}%`}
          change="2 warnings"
          changeType="warning"
          badge={{ label: 'Low', variant: 'amber' }}
        />
        <MetricCard
          label="Integrity Score"
          value={`${Math.round(mockScores.integrityScore * 100)}%`}
          change="6/7 components pass"
          changeType="positive"
          badge={{ label: 'Excellent', variant: 'green' }}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-12 gap-4">
        {/* SDLC Phase Progress */}
        <div className="col-span-8 card p-4">
          <SectionHeader title="SDLC Phase Progress" subtitle={`${completedPhases} of ${mockPhases.length} phases completed`} />
          <div className="space-y-2.5">
            {mockPhases.map((phase) => (
              <div key={phase.id} className="flex items-center gap-3 group">
                <div className="w-24 flex-shrink-0">
                  <StatusChip status={phase.status === 'completed' ? 'verified' : phase.status === 'active' ? 'active' : phase.status === 'blocked' ? 'blocked' : 'pending'} />
                </div>
                <span className="text-xs text-zinc-400 w-20 flex-shrink-0">{phase.shortName}</span>
                <div className="flex-1">
                  <ProgressBar
                    value={phase.progress}
                    size="sm"
                    color={phase.status === 'completed' ? 'green' : phase.status === 'active' ? 'blue' : phase.status === 'blocked' ? 'red' : 'blue'}
                  />
                </div>
                <span className="text-[10px] font-mono text-zinc-600 w-8 text-right">{Math.round(phase.progress * 100)}%</span>
                {phase.failedChecks > 0 && (
                  <span className="text-[10px] text-red-400 flex items-center gap-0.5">
                    <AlertTriangle className="w-2.5 h-2.5" />
                    {phase.failedChecks}
                  </span>
                )}
                {phase.activeAgents > 0 && (
                  <span className="text-[10px] text-blue-400 flex items-center gap-0.5">
                    <Bot className="w-2.5 h-2.5" />
                    {phase.activeAgents}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Active Agents */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="Active Agents" subtitle={`${activeAgents.length} working`} />
          <div className="space-y-2">
            {mockAgents.filter(a => a.status !== 'idle').map((agent) => (
              <div key={agent.id} className="flex items-center gap-2.5 p-2 rounded-md bg-zinc-800/30 border border-zinc-800/50">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: agent.color, boxShadow: `0 0 6px ${agent.color}40` }} />
                <div className="flex-1 min-w-0">
                  <div className="text-[11px] font-medium text-zinc-300 truncate">{agent.name}</div>
                  <div className="text-[9px] text-zinc-600 truncate">{agent.currentTask}</div>
                </div>
                <StatusChip status={agent.status === 'working' ? 'active' : agent.status === 'waiting' ? 'pending' : 'idle'} size="sm" />
              </div>
            ))}
          </div>

          {/* Recent Events */}
          <div className="mt-4 pt-3 border-t border-[#1e2230]">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Recent Events</div>
            <div className="space-y-1.5 max-h-32 overflow-y-auto scrollbar-thin">
              {mockProcessEvents.slice(-5).reverse().map((evt) => (
                <div key={evt.id} className="flex items-start gap-2 text-[10px]">
                  <span className="text-zinc-700 font-mono w-12 flex-shrink-0">{evt.timestamp.slice(11, 16)}</span>
                  <span className={evt.result === 'success' ? 'text-emerald-400' : evt.result === 'failure' ? 'text-red-400' : 'text-amber-400'}>●</span>
                  <span className="text-zinc-500 truncate">{evt.agent} — {evt.action}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Critical Requirements */}
        <div className="card p-4">
          <SectionHeader title="Critical Requirements" subtitle={`${coveredCritical.length}/${criticalReqs.length} covered`} />
          <div className="space-y-2">
            {criticalReqs.map((req) => (
              <div key={req.id} className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${req.semanticCoverageScore >= 0.8 ? 'bg-emerald-400' : req.semanticCoverageScore >= 0.5 ? 'bg-amber-400' : 'bg-red-400'}`} />
                <span className="text-[10px] text-zinc-400 flex-1 truncate">{req.id}: {req.normalizedStatement.slice(0, 50)}...</span>
                <span className="text-[10px] font-mono text-zinc-600">{Math.round(req.semanticCoverageScore * 100)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Governance Gates */}
        <div className="card p-4">
          <SectionHeader title="Governance Gates" subtitle={`${mockGovGates.filter(g => g.status === 'passed').length}/${mockGovGates.length} passed`} />
          <div className="space-y-2">
            {mockGovGates.slice(0, 6).map((gate) => (
              <div key={gate.id} className="flex items-center gap-2">
                <StatusChip status={gate.status === 'passed' ? 'verified' : gate.status === 'failed' ? 'failed' : gate.status === 'blocked' ? 'blocked' : 'pending'} size="sm" />
                <span className="text-[10px] text-zinc-400 flex-1 truncate">{gate.name}</span>
                {gate.impact === 'critical' && <Badge variant="red" className="text-[8px] px-1 py-0">CRIT</Badge>}
              </div>
            ))}
          </div>
        </div>

        {/* Token Burn */}
        <div className="card p-4">
          <SectionHeader title="Token Burn" subtitle={`$${mockTokenUsage.budgetRemaining.toFixed(2)} remaining`} />
          <div className="space-y-2">
            {mockTokenUsage.byPhase.slice(0, 5).map((phase) => (
              <div key={phase.phase} className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-500 w-16 flex-shrink-0">{phase.phase}</span>
                <div className="flex-1">
                  <ProgressBar value={phase.tokens / 70000} size="sm" color="blue" />
                </div>
                <span className="text-[10px] font-mono text-zinc-600 w-12 text-right">{(phase.tokens / 1000).toFixed(1)}k</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
