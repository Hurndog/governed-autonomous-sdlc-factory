'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockScores, mockGovGates, mockTokenUsage, mockRequirements, mockHumanInterventions } from '@/lib/mock-data';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Clock, Coins, Shield, RefreshCw } from 'lucide-react';

export function ExecutiveCockpit() {
  const [integrityScore, setIntegrityScore] = useState<number | null>(null);
  const [semCovScore, setSemCovScore] = useState<number | null>(null);
  const [totalCost, setTotalCost] = useState<number | null>(null);
  const [artifactCount, setArtifactCount] = useState<number | null>(null);
  const [evidenceCount, setEvidenceCount] = useState<number | null>(null);
  const [govFindings, setGovFindings] = useState<number | null>(null);
  const [traceabilityCoverage, setTraceabilityCoverage] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchExecutiveData = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }

      const results = await Promise.allSettled([
        api.getRunIntegrity(latestRun.id),
        api.getSemanticCoverageSummary(latestRun.id),
        api.getCostReport(latestRun.id),
        api.listArtifacts(latestRun.id),
        api.getEvidenceByRun(latestRun.id),
        api.getGovernanceEvaluations(latestRun.id),
        api.getTraceabilityCoverage(latestRun.id),
      ]);

      const [integrity, semCoverage, costReport, artifacts, evidence, governance, traceability] = results;
      let successCount = 0;

      if (integrity.status === 'fulfilled') {
        const v = integrity.value as { integrity_score: number };
        setIntegrityScore(v.integrity_score);
        successCount++;
      }
      if (semCoverage.status === 'fulfilled') {
        const v = semCoverage.value as { overall_semantic_coverage_score: number };
        setSemCovScore(v.overall_semantic_coverage_score);
        successCount++;
      }
      if (costReport.status === 'fulfilled') {
        const v = costReport.value as { total_cost: number };
        setTotalCost(v.total_cost);
        successCount++;
      }
      if (artifacts.status === 'fulfilled') {
        const v = artifacts.value as { total: number };
        setArtifactCount(v.total);
        successCount++;
      }
      if (evidence.status === 'fulfilled') {
        const v = evidence.value as { bundles: unknown[] };
        setEvidenceCount(v.bundles?.length ?? 0);
        successCount++;
      }
      if (governance.status === 'fulfilled') {
        const v = governance.value as { evaluations: unknown[] };
        setGovFindings(v.evaluations?.length ?? 0);
        successCount++;
      }
      if (traceability.status === 'fulfilled') {
        const v = traceability.value as { coverage_pct: number };
        setTraceabilityCoverage(v.coverage_pct);
        successCount++;
      }

      setDataSource(successCount >= 3 ? 'PARTIAL' : successCount >= 1 ? 'PARTIAL' : 'MOCK');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch executive data');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchExecutiveData(); }, []);

  const failedGates = mockGovGates.filter(g => g.status === 'failed');
  const effectiveIntegrity = integrityScore ?? mockScores.integrityScore;
  const effectiveSemCov = semCovScore ?? mockScores.semanticCoverage;
  const effectiveCost = totalCost ?? mockTokenUsage.totalCostUsd;
  const releaseReadiness = mockScores.releaseReadiness;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Executive Cockpit" subtitle="Portfolio overview and delivery confidence" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchExecutiveData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="card-elevated p-5 border-l-2 border-l-violet-500/50">
        <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Executive Narrative</div>
        <p className="text-[12px] text-zinc-300 leading-relaxed">
          The application is <span className="text-violet-400 font-semibold">{Math.round(releaseReadiness * 100)}% complete</span>.
          {integrityScore !== null && <> Integrity score is <span className={effectiveIntegrity >= 0.8 ? 'text-emerald-400' : effectiveIntegrity >= 0.5 ? 'text-amber-400' : 'text-red-400'}>{Math.round(effectiveIntegrity * 100)}%</span>.</>}
          {semCovScore !== null && <> Semantic coverage is <span className={effectiveSemCov >= 0.8 ? 'text-emerald-400' : effectiveSemCov >= 0.5 ? 'text-amber-400' : 'text-red-400'}>{Math.round(effectiveSemCov * 100)}%</span>.</>}
          {dataSource === 'MOCK' && <span className="text-zinc-500"> (showing mock data — connect to a live run for real metrics)</span>}
          {dataSource === 'PARTIAL' && <span className="text-zinc-500"> (partial live data — some metrics from backend, others from mock)</span>}
        </p>
      </div>

      <div className="grid grid-cols-5 gap-3">
        <div className="card p-4 flex flex-col items-center">
          <GaugeChart value={releaseReadiness} label="Release Ready" size="md" color={releaseReadiness >= 0.8 ? 'green' : releaseReadiness >= 0.5 ? 'amber' : 'red'} />
        </div>
        <MetricCard label="Value Delivered" value={`${Math.round(releaseReadiness * 100)}%`} change="+8% this week" changeType="positive" icon={<TrendingUp className="w-3.5 h-3.5 text-emerald-400" />} />
        <MetricCard label="Cost to Date" value={`$${effectiveCost.toFixed(2)}`} change="From backend" changeType="neutral" icon={<Coins className="w-3.5 h-3.5" />} />
        <MetricCard label="Risk Posture" value={failedGates.length > 0 ? 'Moderate' : 'Low'} change={`${failedGates.length} gates failed`} changeType={failedGates.length > 0 ? 'warning' : 'positive'} icon={<Shield className="w-3.5 h-3.5 text-amber-400" />} />
        <MetricCard label="Interventions" value={mockHumanInterventions.length.toString()} change="4 human actions" changeType="neutral" icon={<Clock className="w-3.5 h-3.5" />} />
      </div>

      {dataSource === 'PARTIAL' && (
        <div className="card p-4">
          <SectionHeader title="Live Run Metrics" subtitle="Aggregated from backend endpoints" />
          <div className="grid grid-cols-6 gap-3 mt-2">
            {artifactCount !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Artifacts</div>
                <div className="text-sm font-semibold text-zinc-300">{artifactCount}</div>
              </div>
            )}
            {evidenceCount !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Evidence</div>
                <div className="text-sm font-semibold text-zinc-300">{evidenceCount}</div>
              </div>
            )}
            {govFindings !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Gov Findings</div>
                <div className="text-sm font-semibold text-zinc-300">{govFindings}</div>
              </div>
            )}
            {traceabilityCoverage !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Traceability</div>
                <div className="text-sm font-semibold text-zinc-300">{Math.round(traceabilityCoverage)}%</div>
              </div>
            )}
            {integrityScore !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Integrity</div>
                <div className={`text-sm font-semibold ${effectiveIntegrity >= 0.8 ? 'text-emerald-400' : 'text-amber-400'}`}>{Math.round(effectiveIntegrity * 100)}%</div>
              </div>
            )}
            {semCovScore !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Sem Coverage</div>
                <div className={`text-sm font-semibold ${effectiveSemCov >= 0.8 ? 'text-emerald-400' : 'text-amber-400'}`}>{Math.round(effectiveSemCov * 100)}%</div>
              </div>
            )}
          </div>
        </div>
      )}

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
            <span className="text-[9px] text-red-400">-16% this week</span>
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

      <div className="grid grid-cols-2 gap-4">
        <div className="card p-4">
          <SectionHeader title="Risk Distribution" subtitle="By category" />
          <div className="space-y-2 mt-2">
            {[
              { label: 'Semantic Coverage', value: 0.34, count: 3, color: 'red' as const },
              { label: 'Security', value: 0.15, count: 1, color: 'amber' as const },
              { label: 'Architecture Drift', value: 0.22, count: 2, color: 'amber' as const },
              { label: 'Token Budget', value: 0.05, count: 0, color: 'green' as const },
              { label: 'Test Coverage', value: 0.24, count: 2, color: 'amber' as const },
            ].map(r => (
              <div key={r.label} className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-500 w-32 flex-shrink-0">{r.label}</span>
                <div className="flex-1"><ProgressBar value={r.value} size="sm" color={r.color === 'red' ? 'red' : r.color === 'amber' ? 'amber' : 'green'} /></div>
                <span className="text-[10px] font-mono text-zinc-600 w-6 text-right">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card p-4">
          <SectionHeader title="Blocked Initiatives" subtitle="Requiring attention" />
          <div className="space-y-2 mt-2">
            {[
              { title: 'Fraud Detection Service', reason: 'ML model integration blocked', impact: 'high' },
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
