'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { GaugeChart } from '@/components/ui/GaugeChart';
import { Badge } from '@/components/ui/Badge';
import { mockSemanticCoverage, mockRequirements } from '@/lib/mock-data';
import { Target, AlertTriangle, CheckCircle2, XCircle, Shield, Eye } from 'lucide-react';

export function SemanticCoverage() {
  const [selectedReq, setSelectedReq] = useState<string | null>(null);
  const coverage = mockSemanticCoverage;

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
      <SectionHeader title="Semantic Coverage & Test Alignment" subtitle="Proving tests actually validate requirements" />

      {/* Score gauges */}
      <div className="grid grid-cols-8 gap-3">
        <div className="card p-3 flex flex-col items-center">
          <GaugeChart value={coverage.overallScore} label="Overall" size="md" color={coverage.overallScore >= 0.8 ? 'green' : coverage.overallScore >= 0.5 ? 'amber' : 'red'} />
        </div>
        {[
          { label: 'Obligation', value: coverage.obligationCoverage },
          { label: 'Alignment', value: coverage.semanticAlignment },
          { label: 'Mutation', value: coverage.mutationScore },
          { label: 'Negative', value: coverage.negativeCoverage },
          { label: 'Runtime', value: coverage.runtimeEvidence },
          { label: 'Verifier', value: coverage.verifierConfidence },
          { label: 'Gate', value: coverage.releaseGateStatus === 'passed' ? 1 : 0 },
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
              {coverage.coverageMatrix.map((row, i) => {
                const req = mockRequirements[i];
                return (
                  <tr
                    key={row.requirementId}
                    className={`border-b border-zinc-800/30 cursor-pointer hover:bg-zinc-800/20 ${selectedReq === row.requirementId ? 'bg-zinc-800/30' : ''}`}
                    onClick={() => setSelectedReq(selectedReq === row.requirementId ? null : row.requirementId)}
                  >
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
        {/* False Confidence Detector */}
        <div className="col-span-6 card p-4">
          <SectionHeader title="False Confidence Detector" subtitle="Tests that pass but don't prove requirements" icon={<Eye className="w-3.5 h-3.5 text-amber-400" />} />
          <div className="space-y-2 mt-2">
            {coverage.falseConfidenceTests.map(t => (
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

        {/* Release Gate Impact */}
        <div className="col-span-6 card p-4">
          <SectionHeader title="Release Gate Impact" subtitle="How semantic coverage affects release readiness" icon={<Shield className="w-3.5 h-3.5 text-violet-400" />} />
          <div className="space-y-3 mt-2">
            <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
              <div className="flex items-center gap-2 mb-1">
                <XCircle className="w-3.5 h-3.5 text-red-400" />
                <span className="text-[11px] font-medium text-red-400">Release Gate: FAILED</span>
              </div>
              <div className="text-[9px] text-zinc-500">Semantic coverage score 65.6% is below the 80% threshold required for release.</div>
            </div>

            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Blocking Issues</div>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="text-red-400">●</span>
                  <span className="text-zinc-400">REQ-005 (Fraud Detection): 42% coverage — missing negative tests</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="text-red-400">●</span>
                  <span className="text-zinc-400">REQ-008 (Dashboard): 35% coverage — only 1 test, no integration</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="text-amber-400">●</span>
                  <span className="text-zinc-400">REQ-003 (Reconciliation): 71% coverage — missing contract tests</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="text-amber-400">●</span>
                  <span className="text-zinc-400">3 false confidence tests detected — tests pass but don't prove requirements</span>
                </div>
              </div>
            </div>

            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Recommendations</div>
              <div className="space-y-1">
                {[
                  'Add negative test cases for REQ-005 fraud detection paths',
                  'Generate integration tests for REQ-008 dashboard components',
                  'Replace shallow test_auth_check_exists with behavioral auth test',
                  'Add contract tests for reconciliation API endpoints',
                ].map((rec, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-[9px] text-zinc-500">
                    <span className="text-violet-400 mt-0.5">→</span>
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
