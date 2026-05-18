'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type SemanticCoverageSummary, type SemanticCoverageReport } from '@/lib/api';
import { mockSemanticCoverage, mockRequirements } from '@/lib/mock-data';
import { Target, AlertTriangle, CheckCircle2, XCircle, Shield, Eye, RefreshCw, Dna, Bug, FileWarning } from 'lucide-react';

interface MutationData { total: number; killed: number; survived: number; mutations: Array<{ mutation_id: string; requirement_id: string; mutation_type: string; mutated_component: string; killed: boolean; survived: boolean }>; }
interface VerifierData { total: number; critiques: Array<{ test_case_id: string; verdict: string; confidence: number; critique: string }>; }
interface NegativeData { total: number; pending: number; generated: number; }
interface RuntimeEvidenceData { total: number; bound: number; failed: number; }

export function SemanticCoverage() {
  const [summary, setSummary] = useState<SemanticCoverageSummary | null>(null);
  const [report, setReport] = useState<SemanticCoverageReport | null>(null);
  const [mutations, setMutations] = useState<MutationData | null>(null);
  const [verifier, setVerifier] = useState<VerifierData | null>(null);
  const [negative, setNegative] = useState<NegativeData | null>(null);
  const [runtimeEvidence, setRuntimeEvidence] = useState<RuntimeEvidenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchSemanticCoverage = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }

      const results = await Promise.allSettled([
        api.getSemanticCoverageSummary(latestRun.id),
        api.getSemanticCoverageReport(latestRun.id),
        api.getSemanticMutations(latestRun.id),
        api.getSemanticVerifierCritiques(latestRun.id),
        api.getSemanticNegativeCoverage(latestRun.id),
        api.getSemanticRuntimeEvidence(latestRun.id),
      ]);

      const [summaryRes, reportRes, mutationsRes, verifierRes, negativeRes, evidenceRes] = results;
      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value as SemanticCoverageSummary);
      if (reportRes.status === 'fulfilled') setReport(reportRes.value as SemanticCoverageReport);
      if (mutationsRes.status === 'fulfilled') setMutations(mutationsRes.value as MutationData);
      if (verifierRes.status === 'fulfilled') setVerifier(verifierRes.value as VerifierData);
      if (negativeRes.status === 'fulfilled') setNegative(negativeRes.value as NegativeData);
      if (evidenceRes.status === 'fulfilled') setRuntimeEvidence(evidenceRes.value as RuntimeEvidenceData);

      const successCount = results.filter(r => r.status === 'fulfilled').length;
      if (successCount >= 3) setDataSource('LIVE');
      else if (successCount >= 1) setDataSource('PARTIAL');
      else setDataSource('ERROR');
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchSemanticCoverage(); }, []);

  const overallScore = summary?.overall_semantic_coverage_score ?? mockSemanticCoverage.overallScore;
  const obligationCoverage = summary?.obligation_coverage_score ?? mockSemanticCoverage.obligationCoverage;
  const semanticAlignment = summary?.semantic_alignment_score ?? mockSemanticCoverage.semanticAlignment;
  const mutationScore = summary?.mutation_score ?? mockSemanticCoverage.mutationScore;
  const negativeCoverage = summary?.negative_coverage_score ?? mockSemanticCoverage.negativeCoverage;
  const runtimeEvidenceScore = summary?.runtime_evidence_score ?? mockSemanticCoverage.runtimeEvidence;
  const verifierConfidence = summary?.verifier_confidence_score ?? mockSemanticCoverage.verifierConfidence;
  const criticalPassed = summary?.critical_requirements_passed ?? mockSemanticCoverage.criticalRequirementsPassed;
  const gateStatus = summary?.release_gate_status ?? mockSemanticCoverage.releaseGateStatus;

  const mutationKilled = mutations?.killed ?? 0;
  const mutationSurvived = mutations?.survived ?? 0;
  const mutationTotal = mutations?.total ?? 0;
  const mutationList = mutations?.mutations ?? [];
  const verifierTotal = verifier?.total ?? 0;
  const verifierCritiques = verifier?.critiques ?? [];
  const negativeTotal = negative?.total ?? 0;
  const negativePending = negative?.pending ?? 0;
  const negativeGenerated = negative?.generated ?? 0;
  const evidenceTotal = runtimeEvidence?.total ?? 0;
  const evidenceBound = runtimeEvidence?.bound ?? 0;
  const evidenceFailed = runtimeEvidence?.failed ?? 0;
  const hasRealMutations = mutations !== null;
  const hasRealVerifier = verifier !== null;
  const hasRealNegative = negative !== null;
  const hasRealEvidence = runtimeEvidence !== null;

  const cellColors: Record<string, string> = {
    covered: 'bg-emerald-400/20 text-emerald-400', partial: 'bg-amber-400/20 text-amber-400',
    missing: 'bg-red-400/20 text-red-400', weak: 'bg-red-400/20 text-red-400',
    contradicted: 'bg-red-400/20 text-red-400', obsolete: 'bg-zinc-700/20 text-zinc-600',
  };
  const columns = ['Unit', 'Integ', 'Contract', 'E2E', 'Negative', 'Mutation', 'Runtime', 'Verifier'];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Semantic Coverage & Test Alignment" subtitle="Proving tests actually validate requirements" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchSemanticCoverage} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-8 gap-3">
        <div className="card p-3 flex flex-col items-center">
          <GaugeChart value={overallScore} label="Overall" size="md" color={overallScore >= 0.8 ? 'green' : overallScore >= 0.5 ? 'amber' : 'red'} />
        </div>
        {[
          { label: 'Obligation', value: obligationCoverage }, { label: 'Alignment', value: semanticAlignment },
          { label: 'Mutation', value: mutationScore }, { label: 'Negative', value: negativeCoverage },
          { label: 'Runtime', value: runtimeEvidenceScore }, { label: 'Verifier', value: verifierConfidence },
          { label: 'Critical', value: criticalPassed ? 1 : 0 }, { label: 'Gate', value: gateStatus === 'passed' ? 1 : 0 },
        ].map(g => (
          <div key={g.label} className="card p-3 flex flex-col items-center">
            <GaugeChart value={g.value} label={g.label} size="sm" color={g.value >= 0.8 ? 'green' : g.value >= 0.5 ? 'amber' : 'red'} />
          </div>
        ))}
      </div>

      <div className="card p-4">
        <SectionHeader title="Mutation Testing" subtitle={hasRealMutations ? `${mutationTotal} mutations — ${mutationKilled} killed, ${mutationSurvived} survived (live)` : 'Mutation test results'} icon={<Dna className="w-3.5 h-3.5 text-violet-400" />} />
        <div className="grid grid-cols-4 gap-3 mt-2">
          <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40"><div className="text-[9px] text-zinc-700 uppercase">Total</div><div className="text-lg font-semibold text-zinc-200">{mutationTotal || '—'}</div></div>
          <div className="p-3 rounded-lg bg-emerald-400/5 border border-emerald-400/10"><div className="text-[9px] text-emerald-400 uppercase">Killed</div><div className="text-lg font-semibold text-emerald-400">{mutationKilled || '—'}</div></div>
          <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10"><div className="text-[9px] text-red-400 uppercase">Survived</div><div className="text-lg font-semibold text-red-400">{mutationSurvived || '—'}</div></div>
          <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40"><div className="text-[9px] text-zinc-700 uppercase">Kill Rate</div><div className="text-lg font-semibold text-zinc-200">{mutationTotal > 0 ? `${Math.round((mutationKilled / mutationTotal) * 100)}%` : '—'}</div></div>
        </div>
        {mutationList.length > 0 && (
          <div className="mt-3 space-y-1 max-h-40 overflow-y-auto scrollbar-thin">
            {mutationList.slice(0, 10).map(m => (
              <div key={m.mutation_id} className="flex items-center gap-2 py-1 px-2 rounded bg-zinc-800/10 text-[10px]">
                {m.killed ? <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" /> : <Bug className="w-3 h-3 text-red-400 flex-shrink-0" />}
                <span className="text-zinc-500 font-mono">{m.mutation_id}</span>
                <span className="text-zinc-400">{m.mutation_type}</span>
                <span className="text-zinc-600">→ {m.mutated_component}</span>
                <Badge variant={m.killed ? 'green' : 'red'} size="sm">{m.killed ? 'killed' : 'survived'}</Badge>
              </div>
            ))}
          </div>
        )}
      </div>

      {hasRealVerifier && (
        <div className="card p-4">
          <SectionHeader title="Verifier Critiques" subtitle={`${verifierTotal} critiques from independent verifier`} icon={<Eye className="w-3.5 h-3.5 text-amber-400" />} />
          <div className="space-y-2 mt-2 max-h-48 overflow-y-auto scrollbar-thin">
            {verifierCritiques.slice(0, 10).map((c, i) => (
              <div key={i} className="flex items-start gap-2 p-2 rounded bg-zinc-800/10 text-[10px]">
                <Badge variant={c.verdict === 'pass' ? 'green' : c.verdict === 'fail' ? 'red' : 'amber'} size="sm">{c.verdict}</Badge>
                <span className="text-zinc-400 flex-1">{c.critique}</span>
                <span className="text-zinc-600">{Math.round(c.confidence * 100)}% conf</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {hasRealNegative && (
        <div className="card p-4">
          <SectionHeader title="Negative Test Coverage" subtitle={`${negativeTotal} requirements — ${negativeGenerated} generated, ${negativePending} pending`} icon={<FileWarning className="w-3.5 h-3.5 text-amber-400" />} />
          <div className="grid grid-cols-3 gap-3 mt-2">
            <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40"><div className="text-[9px] text-zinc-700 uppercase">Total</div><div className="text-lg font-semibold text-zinc-200">{negativeTotal}</div></div>
            <div className="p-3 rounded-lg bg-emerald-400/5 border border-emerald-400/10"><div className="text-[9px] text-emerald-400 uppercase">Generated</div><div className="text-lg font-semibold text-emerald-400">{negativeGenerated}</div></div>
            <div className="p-3 rounded-lg bg-amber-400/5 border border-amber-400/10"><div className="text-[9px] text-amber-400 uppercase">Pending</div><div className="text-lg font-semibold text-amber-400">{negativePending}</div></div>
          </div>
        </div>
      )}

      {hasRealEvidence && (
        <div className="card p-4">
          <SectionHeader title="Runtime Evidence Bindings" subtitle={`${evidenceTotal} bindings — ${evidenceBound} bound, ${evidenceFailed} failed`} icon={<Shield className="w-3.5 h-3.5 text-cyan-400" />} />
          <div className="grid grid-cols-3 gap-3 mt-2">
            <div className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40"><div className="text-[9px] text-zinc-700 uppercase">Total</div><div className="text-lg font-semibold text-zinc-200">{evidenceTotal}</div></div>
            <div className="p-3 rounded-lg bg-emerald-400/5 border border-emerald-400/10"><div className="text-[9px] text-emerald-400 uppercase">Bound</div><div className="text-lg font-semibold text-emerald-400">{evidenceBound}</div></div>
            <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10"><div className="text-[9px] text-red-400 uppercase">Failed</div><div className="text-lg font-semibold text-red-400">{evidenceFailed}</div></div>
          </div>
        </div>
      )}

      <div className="card p-4">
        <SectionHeader title="Coverage Matrix" subtitle="Requirements × test types" />
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="border-b border-[#1e2230]">
                <th className="text-left py-2 px-2 text-zinc-600 font-medium w-48">Requirement</th>
                {columns.map(col => (<th key={col} className="text-center py-2 px-1 text-zinc-600 font-medium w-16">{col}</th>))}
                <th className="text-center py-2 px-2 text-zinc-600 font-medium w-16">Score</th>
              </tr>
            </thead>
            <tbody>
              {mockSemanticCoverage.coverageMatrix.map((row, i) => {
                const req = mockRequirements[i];
                return (
                  <tr key={row.requirementId} className="border-b border-zinc-800/30 hover:bg-zinc-800/20">
                    <td className="py-1.5 px-2"><div className="flex items-center gap-1.5"><span className="font-mono text-zinc-400">{row.requirementId}</span>{req?.criticality === 'critical' && <Badge variant="red" size="sm">C</Badge>}</div></td>
                    {columns.map(col => {
                      const key = col === 'Unit' ? 'unitTest' : col === 'Integ' ? 'integrationTest' : col === 'Contract' ? 'contractTest' : col === 'E2E' ? 'e2eTest' : col === 'Negative' ? 'negativeTest' : col === 'Mutation' ? 'mutationTest' : col === 'Runtime' ? 'runtimeEvidence' : 'verifierApproval';
                      const val = row[key as keyof typeof row] as string;
                      return (<td key={col} className="text-center py-1.5 px-1"><span className={`inline-block w-5 h-5 rounded text-[8px] leading-5 font-medium ${cellColors[val] || 'bg-zinc-800/20 text-zinc-600'}`}>{val === 'covered' ? '✓' : val === 'partial' ? '~' : val === 'approved' ? '✓' : val === 'flagged' ? '!' : val === 'rejected' ? '✗' : val === 'pending' ? '○' : '✗'}</span></td>);
                    })}
                    <td className="text-center py-1.5 px-2"><span className={`font-mono ${req && req.semanticCoverageScore >= 0.8 ? 'text-emerald-400' : req && req.semanticCoverageScore >= 0.5 ? 'text-amber-400' : 'text-red-400'}`}>{req ? Math.round(req.semanticCoverageScore * 100) : 0}%</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-6 card p-4">
          <SectionHeader title="False Confidence Detector" subtitle="Tests that pass but don't prove requirements" icon={<Eye className="w-3.5 h-3.5 text-amber-400" />} />
          <div className="space-y-2 mt-2">
            {mockSemanticCoverage.falseConfidenceTests.map(t => (
              <div key={t.testId} className="p-3 rounded-lg bg-amber-400/5 border border-amber-400/10">
                <div className="flex items-center gap-2 mb-1"><AlertTriangle className="w-3 h-3 text-amber-400" /><span className="text-[10px] font-mono text-amber-400">{t.name}</span><Badge variant={t.severity === 'critical' ? 'red' : 'amber'} size="sm">{t.severity}</Badge></div>
                <div className="text-[9px] text-zinc-500 mb-1">{t.issue}</div>
                <div className="text-[9px] text-zinc-600">Linked: {t.requirementId}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="col-span-6 card p-4">
          <SectionHeader title="Release Gate Impact" subtitle="How semantic coverage affects release readiness" icon={<Shield className="w-3.5 h-3.5 text-violet-400" />} />
          <div className="space-y-3 mt-2">
            <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-2 mb-1"><XCircle className="w-3.5 h-3.5 text-red-400" /><span className="text-[11px] font-medium text-red-400">Release Gate: {gateStatus === 'passed' ? 'PASSED' : 'FAILED'}</span></div>
              <div className="text-[9px] text-zinc-500">Semantic coverage score {Math.round(overallScore * 100)}% is {overallScore >= 0.8 ? 'above' : 'below'} the 80% threshold.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
