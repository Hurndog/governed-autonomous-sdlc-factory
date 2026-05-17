'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockSemanticCoverage, mockRequirements } from '@/lib/mock-data';
import { Target, AlertTriangle, CheckCircle2, XCircle, Shield, Eye, RefreshCw } from 'lucide-react';
import type { SemanticCoverageReport, SemanticCoverageSummary } from '@/lib/types';

export function SemanticCoverage() {
  const [report, setReport] = useState<SemanticCoverageReport | null>(null);
  const [summary, setSummary] = useState<SemanticCoverageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchSemanticCoverage = async () => {
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
      const [summaryRes, reportRes] = await Promise.allSettled([
        api.getSemanticCoverageSummary(latestRun.id),
        api.getSemanticCoverageReport(latestRun.id),
      ]);
      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value);
      if (reportRes.status === 'fulfilled') setReport(reportRes.value);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch semantic coverage');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSemanticCoverage();
  }, []);

  // Use real data if available
  const overallScore = summary?.overall_semantic_coverage_score ?? mockSemanticCoverage.overallScore;
  const obligationCoverage = summary?.obligation_coverage_score ?? mockSemanticCoverage.obligationCoverage;
  const semanticAlignment = summary?.semantic_alignment_score ?? mockSemanticCoverage.semanticAlignment;
  const mutationScore = summary?.mutation_score ?? mockSemanticCoverage.mutationScore;
  const negativeCoverage = summary?.negative_coverage_score ?? mockSemanticCoverage.negativeCoverage;
  const runtimeEvidence = summary?.runtime_evidence_score ?? mockSemanticCoverage.runtimeEvidence;
  const verifierConfidence = summary?.verifier_confidence_score ?? mockSemanticCoverage.verifierConfidence;
  const criticalPassed = summary?.critical_requirements_passed ?? mockSemanticCoverage.criticalRequirementsPassed;
  const gateStatus = summary?.release_gate_status ?? mockSemanticCoverage.releaseGateStatus;

  const cellColors: Record<string, string> = {
    covered: 'bg-emerald-400/20 text-emerald-400',
    partial: 'bg-amber-400/20 text-amber-400',
    missing: 'bg-red-400/20 text-red-400',
    weak: 'bg-red-400/20 text-red-400',
    contradicted: 'bg-red-400/20 text-red-400',
    obsolete: 'bg-zinc-700/20 text-zinc-600',
  };

  const columns = ['Unit', 'Integ', 'Contract', 'E2E', 'Negative', 'Mutation', 'Runtime', 'Verifier'];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Semantic Coverage & Test Alignment" subtitle="Proving tests actually validate requirements" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchSemanticCoverage}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Score gauges */}
      <div className="grid grid-cols-8 gap-3">
        <div className="card p-3 flex flex-col items-center">
          <GaugeChart value={overallScore} label="Overall" size="md" color={overallScore >= 0.8 ? 'green' : overallScore >= 0.5 ? 'amber' : 'red'} />
        </div>
        {[
          { label: 'Obligation', value: obligationCoverage },
          { label: 'Alignment', value: semanticAlignment },
          { label: 'Mutation', value: mutationScore },
          { label: 'Negative', value: negativeCoverage },
          { label: 'Runtime', value: runtimeEvidence },
          { label: 'Verifier', value: verifierConfidence },
          { label: 'Critical', value: criticalPassed ? 1 : 0 },
          { label: 'Gate', value: gateStatus === 'passed' ? 1 : 0 },
        ].map(g => (
          <div key={g.label} className="card p-3 flex flex-col items-center">
            <GaugeChart value={g.value} label={g.label} size="sm" color={g.value >= 0.8 ? 'green' : g.value >= 0.5 ? 'amber' : 'red'} />
          </div>
        ))}
      </div>

      {/* Coverage Matrix */}
      <div className="card p-4">
        <SectionHeader title="Coverage Matrix" subtitle="Requirements × test types" />
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="border-b border-[#1e2230]">
                <th className="text-left py-2 px-2 text-zinc-600 font-medium w-48">Requirement</th>
                {columns.map(col => (
                  <th key={col} className="text-center py-2 px-1 text-zinc-600 font-medium w-16">{col}</th>
                ))}
                <th className="text-center py-2 px-2 text-zinc-600 font-medium w-16">Score</th>
              </tr>
            </thead>
            <tbody>
              {mockSemanticCoverage.coverageMatrix.map((row, i) => {
                const req = mockRequirements[i];
                return (
                  <tr key={row.requirementId} className="border-b border-zinc-800/30 hover:bg-zinc-800/20">
                    <td className="py-1.5 px-2">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-zinc-400">{row.requirementId}</span>
                        {req?.criticality === 'critical' && <Badge variant="red" size="sm">C</Badge>}
                      </div>
                    </td>
                    {columns.map(col => {
                      const key = col === 'Unit' ? 'unitTest' : col === 'Integ' ? 'integrationTest' : col === 'Contract' ? 'contractTest' : col === 'E2E' ? 'e2eTest' : col === 'Negative' ? 'negativeTest' : col === 'Mutation' ? 'mutationTest' : col === 'Runtime' ? 'runtimeEvidence' : 'verifierApproval';
                      const val = row[key as keyof typeof row] as string;
                      return (
                        <td key={col} className="text-center py-1.5 px-1">
                          <span className={`inline-block w-5 h-5 rounded text-[8px] leading-5 font-medium ${cellColors[val] || 'bg-zinc-800/20 text-zinc-600'}`}>
                            {val === 'covered' ? '✓' : val === 'partial' ? '~' : val === 'approved' ? '✓' : val === 'flagged' ? '!' : val === 'rejected' ? '✗' : val === 'pending' ? '○' : '✗'}
                          </span>
                        </td>
                      );
                    })}
                    <td className="text-center py-1.5 px-2">
                      <span className={`font-mono ${req && req.semanticCoverageScore >= 0.8 ? 'text-emerald-400' : req && req.semanticCoverageScore >= 0.5 ? 'text-amber-400' : 'text-red-400'}`}>
                        {req ? Math.round(req.semanticCoverageScore * 100) : 0}%
                      </span>
                    </td>
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
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="w-3 h-3 text-amber-400" />
                  <span className="text-[10px] font-mono text-amber-400">{t.name}</span>
                  <Badge variant={t.severity === 'critical' ? 'red' : 'amber'} size="sm">{t.severity}</Badge>
                </div>
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
              <div className="flex items-center gap-2 mb-1">
                <XCircle className="w-3.5 h-3.5 text-red-400" />
                <span className="text-[11px] font-medium text-red-400">Release Gate: {gateStatus === 'passed' ? 'PASSED' : 'FAILED'}</span>
              </div>
              <div className="text-[9px] text-zinc-500">Semantic coverage score {Math.round(overallScore * 100)}% is {overallScore >= 0.8 ? 'above' : 'below'} the 80% threshold.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
