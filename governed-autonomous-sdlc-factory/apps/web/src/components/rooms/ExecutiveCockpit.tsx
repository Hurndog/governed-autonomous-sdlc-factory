'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { MetricCard } from '@/components/ui/MetricCard';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockGovGates, mockTokenUsage, mockHumanInterventions } from '@/lib/mock-data';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Clock, Coins, Shield, RefreshCw, Activity, FileText, Package } from 'lucide-react';

interface ExecutiveMetrics {
  integrityScore: number | null;
  semCovScore: number | null;
  totalCost: number | null;
  totalTokens: number | null;
  artifactCount: number | null;
  evidenceCount: number | null;
  govFindings: number | null;
  govPassed: number | null;
  govFailed: number | null;
  traceabilityCoverage: number | null;
  runStatus: string | null;
  runId: string | null;
}

export function ExecutiveCockpit() {
  const [metrics, setMetrics] = useState<ExecutiveMetrics>({
    integrityScore: null, semCovScore: null, totalCost: null, totalTokens: null,
    artifactCount: null, evidenceCount: null, govFindings: null, govPassed: null,
    govFailed: null, traceabilityCoverage: null, runStatus: null, runId: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchExecutiveData = useCallback(async () => {
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
      const m: ExecutiveMetrics = { ...metrics, runId: latestRun.id, runStatus: latestRun.status };

      if (integrity.status === 'fulfilled') {
        const v = integrity.value as { integrity_score?: number; status?: string };
        m.integrityScore = v.integrity_score ?? null;
        successCount++;
      }
      if (semCoverage.status === 'fulfilled') {
        const v = semCoverage.value as { overall_semantic_coverage_score?: number };
        m.semCovScore = v.overall_semantic_coverage_score ?? null;
        successCount++;
      }
      if (costReport.status === 'fulfilled') {
        const v = costReport.value as { total_cost?: number; total_tokens?: number };
        m.totalCost = v.total_cost ?? null;
        m.totalTokens = v.total_tokens ?? null;
        successCount++;
      }
      if (artifacts.status === 'fulfilled') {
        const v = artifacts.value as { total?: number; items?: unknown[] };
        m.artifactCount = v.total ?? v.items?.length ?? null;
        successCount++;
      }
      if (evidence.status === 'fulfilled') {
        const v = evidence.value as { bundles?: unknown[] };
        m.evidenceCount = v.bundles?.length ?? null;
        successCount++;
      }
      if (governance.status === 'fulfilled') {
        const v = governance.value as { evaluations?: Array<{ status?: string }> };
        const evals = v.evaluations || [];
        m.govFindings = evals.length;
        m.govPassed = evals.filter(e => e.status === 'pass').length;
        m.govFailed = evals.filter(e => e.status === 'fail').length;
        successCount++;
      }
      if (traceability.status === 'fulfilled') {
        const v = traceability.value as { coverage_pct?: number };
        m.traceabilityCoverage = v.coverage_pct ?? null;
        successCount++;
      }

      setMetrics(m);
      setDataSource(successCount >= 4 ? 'LIVE' : successCount >= 2 ? 'PARTIAL' : 'MOCK');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch executive data');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchExecutiveData(); }, [fetchExecutiveData]);

  const effectiveIntegrity = metrics.integrityScore ?? 0.72;
  const effectiveSemCov = metrics.semCovScore ?? 0.66;
  const effectiveCost = metrics.totalCost ?? mockTokenUsage.totalCostUsd;
  const effectiveTokens = metrics.totalTokens ?? mockTokenUsage.totalTokens;
  const releaseReadiness = (effectiveIntegrity * 0.3 + effectiveSemCov * 0.3 + (metrics.traceabilityCoverage ?? 0.5) * 0.2 + (metrics.evidenceCount ? 0.2 : 0.1));
  const failedGates = mockGovGates.filter(g => g.status === 'failed');

  // Build narrative
  const narrativeParts: string[] = [];
  if (metrics.runId) {
    narrativeParts.push(`Run ${metrics.runId.slice(0, 8)} is ${metrics.runStatus ?? 'unknown'}.`);
  }
  if (metrics.integrityScore !== null) {
    narrativeParts.push(`Integrity score is ${Math.round(effectiveIntegrity * 100)}%.`);
  }
  if (metrics.semCovScore !== null) {
    narrativeParts.push(`Semantic coverage is ${Math.round(effectiveSemCov * 100)}%.`);
  }
  if (metrics.traceabilityCoverage !== null) {
    narrativeParts.push(`Traceability coverage is ${Math.round(metrics.traceabilityCoverage)}%.`);
  }
  if (metrics.govFailed !== null && metrics.govFailed > 0) {
    narrativeParts.push(`${metrics.govFailed} governance gate${metrics.govFailed > 1 ? 's' : ''} failing.`);
  }
  if (metrics.evidenceCount !== null && metrics.evidenceCount > 0) {
    narrativeParts.push(`${metrics.evidenceCount} evidence bundle${metrics.evidenceCount > 1 ? 's' : ''} available.`);
  }
  const narrative = narrativeParts.length > 0 ? narrativeParts.join(' ') : 'No live run data available. Showing mock metrics.';

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Executive Cockpit" subtitle={metrics.runId ? `Run ${metrics.runId.slice(0, 8)} • ${dataSource}` : 'Portfolio overview and delivery confidence'} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchExecutiveData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Executive Narrative */}
      <div className="card-elevated p-5 border-l-2 border-l-violet-500/50">
        <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Executive Narrative</div>
        <p className="text-[12px] text-zinc-300 leading-relaxed">
          {narrative}
          {dataSource === 'MOCK' && <span className="text-zinc-500"> (showing mock data — connect to a live run for real metrics)</span>}
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-5 gap-3">
        <div className="card p-4 flex flex-col items-center">
          <GaugeChart value={releaseReadiness} label="Release Ready" size="md" color={releaseReadiness >= 0.8 ? 'green' : releaseReadiness >= 0.5 ? 'amber' : 'red'} />
        </div>
        <MetricCard
          label="Cost to Date"
          value={metrics.totalCost !== null ? `$${effectiveCost.toFixed(2)}` : '—'}
          change={metrics.totalTokens !== null ? `${(effectiveTokens / 1000).toFixed(0)}k tokens` : undefined}
          changeType="neutral"
          icon={<Coins className="w-3.5 h-3.5" />}
        />
        <MetricCard
          label="Risk Posture"
          value={metrics.govFailed !== null ? (metrics.govFailed > 0 ? 'Moderate' : 'Low') : '—'}
          change={metrics.govFailed !== null ? `${metrics.govFailed} gates failed` : undefined}
          changeType={metrics.govFailed && metrics.govFailed > 0 ? 'warning' : 'positive'}
          icon={<Shield className="w-3.5 h-3.5 text-amber-400" />}
        />
        <MetricCard
          label="Artifacts"
          value={metrics.artifactCount !== null ? metrics.artifactCount.toString() : '—'}
          change={metrics.evidenceCount !== null ? `${metrics.evidenceCount} evidence` : undefined}
          changeType="neutral"
          icon={<Package className="w-3.5 h-3.5" />}
        />
        <MetricCard
          label="Traceability"
          value={metrics.traceabilityCoverage !== null ? `${Math.round(metrics.traceabilityCoverage)}%` : '—'}
          change={metrics.govFindings !== null ? `${metrics.govFindings} gov checks` : undefined}
          changeType="neutral"
          icon={<Activity className="w-3.5 h-3.5" />}
        />
      </div>

      {/* Live metrics grid */}
      {(dataSource === 'LIVE' || dataSource === 'PARTIAL') && (
        <div className="card p-4">
          <SectionHeader title="Live Run Metrics" subtitle="Aggregated from backend endpoints" />
          <div className="grid grid-cols-6 gap-3 mt-2">
            {metrics.integrityScore !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Integrity</div>
                <div className={`text-sm font-semibold ${effectiveIntegrity >= 0.8 ? 'text-emerald-400' : effectiveIntegrity >= 0.5 ? 'text-amber-400' : 'text-red-400'}`}>
                  {Math.round(effectiveIntegrity * 100)}%
                </div>
              </div>
            )}
            {metrics.semCovScore !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Sem Coverage</div>
                <div className={`text-sm font-semibold ${effectiveSemCov >= 0.8 ? 'text-emerald-400' : effectiveSemCov >= 0.5 ? 'text-amber-400' : 'text-red-400'}`}>
                  {Math.round(effectiveSemCov * 100)}%
                </div>
              </div>
            )}
            {metrics.artifactCount !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Artifacts</div>
                <div className="text-sm font-semibold text-zinc-300">{metrics.artifactCount}</div>
              </div>
            )}
            {metrics.evidenceCount !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Evidence</div>
                <div className="text-sm font-semibold text-zinc-300">{metrics.evidenceCount}</div>
              </div>
            )}
            {metrics.govFindings !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Gov Checks</div>
                <div className="text-sm font-semibold text-zinc-300">
                  {metrics.govPassed}/{metrics.govFindings}
                </div>
              </div>
            )}
            {metrics.traceabilityCoverage !== null && (
              <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="text-[9px] text-zinc-700 uppercase">Traceability</div>
                <div className="text-sm font-semibold text-zinc-300">{Math.round(metrics.traceabilityCoverage)}%</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Risk & Blocked — only show when we have real data */}
      {(dataSource === 'LIVE' || dataSource === 'PARTIAL') && metrics.govFailed !== null && metrics.govFailed > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card p-4">
            <SectionHeader title="Governance Risks" subtitle={`${metrics.govFailed} failing gates`} />
            <div className="space-y-2 mt-2">
              {failedGates.map((g, i) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                  <AlertTriangle className={`w-3 h-3 mt-0.5 flex-shrink-0 ${g.impact === 'critical' ? 'text-red-400' : 'text-amber-400'}`} />
                  <div>
                    <div className="text-[10px] font-medium text-zinc-300">{g.name}</div>
                    <div className="text-[9px] text-zinc-600">{g.policyBasis}</div>
                  </div>
                  <Badge variant={g.impact === 'critical' ? 'red' : 'amber'} size="sm">{g.impact}</Badge>
                </div>
              ))}
            </div>
          </div>
          <div className="card p-4">
            <SectionHeader title="Delivery Readiness" subtitle="Key quality indicators" />
            <div className="space-y-2 mt-2">
              {[
                { label: 'Integrity', value: effectiveIntegrity },
                { label: 'Semantic Coverage', value: effectiveSemCov },
                { label: 'Traceability', value: (metrics.traceabilityCoverage ?? 0) / 100 },
              ].map(r => (
                <div key={r.label} className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-500 w-32 flex-shrink-0">{r.label}</span>
                  <div className="flex-1">
                    <ProgressBar value={r.value} size="sm" color={r.value >= 0.8 ? 'green' : r.value >= 0.5 ? 'amber' : 'red'} />
                  </div>
                  <span className="text-[10px] font-mono text-zinc-600 w-10 text-right">{Math.round(r.value * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
