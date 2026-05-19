'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockPhases } from '@/lib/mock-data';
import {
  CheckCircle2, Clock, AlertTriangle, Bot, ChevronRight, ChevronDown,
  RefreshCw, Shield, FileText, Package, Coins, Activity, XCircle,
} from 'lucide-react';

type PhaseStatus = 'completed' | 'active' | 'pending' | 'blocked' | 'failed';

interface PhaseData {
  id: string; run_id: string; name: string; order_index: number;
  status: PhaseStatus; agent_id?: string; model_used?: string;
  tokens_in?: number; tokens_out?: number; cost?: number;
  error_message?: string; started_at?: string; completed_at?: string;
  created_at?: string;
}

interface PhaseEnrichment {
  governance: { passed: number; failed: number; warnings: number; total: number };
  semanticCoverage: number | null;
  artifacts: number;
  evidence: boolean;
  tokensIn: number;
  tokensOut: number;
  cost: number;
}

const STATUS_ICON: Record<PhaseStatus, React.ReactNode> = {
  completed: <CheckCircle2 className="w-3 h-3" />,
  active: <Clock className="w-3 h-3 animate-pulse" />,
  pending: <div className="w-3 h-3 rounded-full border border-zinc-600" />,
  blocked: <AlertTriangle className="w-3 h-3" />,
  failed: <XCircle className="w-3 h-3" />,
};

const STATUS_STYLE: Record<PhaseStatus, string> = {
  completed: 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20',
  active: 'bg-blue-400/10 text-blue-400 border border-blue-400/20 ring-1 ring-blue-400/30',
  pending: 'bg-zinc-800/30 text-zinc-600 border border-zinc-700/30',
  blocked: 'bg-red-400/10 text-red-400 border border-red-400/20',
  failed: 'bg-red-400/10 text-red-400 border border-red-400/20',
};

export function SDLCNavigator() {
  const [phases, setPhases] = useState<PhaseData[]>([]);
  const [enrichment, setEnrichment] = useState<Record<string, PhaseEnrichment>>({});
  const [runId, setRunId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      setRunId(latestRun.id);

      // Fetch phases
      let phaseList: PhaseData[] = [];
      try {
        const res = await api.listPhasesByRun(latestRun.id);
        phaseList = (Array.isArray(res) ? res : (res as { phases: PhaseData[] }).phases || []) as PhaseData[];
      } catch { /* phases endpoint may not exist */ }

      if (phaseList.length === 0) {
        setDataSource('MOCK'); setLoading(false); return;
      }

      setPhases(phaseList);
      const active = phaseList.find(p => p.status === 'active');
      if (active) setExpandedPhase(active.id);

      // Enrich each phase with parallel backend calls
      const enrichments: Record<string, PhaseEnrichment> = {};
      await Promise.all(phaseList.map(async (phase) => {
        const [govRes, semRes, artRes, evRes, costRes] = await Promise.allSettled([
          api.getGovernanceEvaluations(latestRun.id),
          api.getSemanticCoverageSummary(latestRun.id),
          api.listArtifacts(latestRun.id),
          api.getEvidenceByRun(latestRun.id),
          api.getCostReport(latestRun.id),
        ]);

        let govPassed = 0, govFailed = 0, govWarnings = 0;
        if (govRes.status === 'fulfilled') {
          const evals = (govRes.value as { evaluations: Array<{ status: string }> }).evaluations || [];
          evals.forEach(e => {
            if (e.status === 'pass') govPassed++;
            else if (e.status === 'fail') govFailed++;
            else govWarnings++;
          });
        }

        let semCov: number | null = null;
        if (semRes.status === 'fulfilled') {
          const v = semRes.value as { overall_semantic_coverage_score?: number };
          semCov = v.overall_semantic_coverage_score ?? null;
        }

        let artifacts = 0;
        if (artRes.status === 'fulfilled') {
          const v = artRes.value as { total?: number; items?: unknown[] };
          artifacts = v.total ?? v.items?.length ?? 0;
        }

        let evidence = false;
        if (evRes.status === 'fulfilled') {
          const v = evRes.value as { bundles?: unknown[] };
          evidence = (v.bundles?.length ?? 0) > 0;
        }

        let tokensIn = 0, tokensOut = 0, cost = 0;
        if (costRes.status === 'fulfilled') {
          const v = costRes.value as {
            total_input_tokens?: number; total_output_tokens?: number; total_cost?: number;
            by_phase?: Record<string, { input_tokens?: number; output_tokens?: number; cost?: number }>;
          };
          // Try to get phase-specific cost from by_phase
          const phaseKey = Object.keys(v.by_phase || {}).find(k =>
            k.toLowerCase().includes(phase.name.toLowerCase()) || phase.name.toLowerCase().includes(k.toLowerCase())
          );
          if (phaseKey && v.by_phase?.[phaseKey]) {
            tokensIn = v.by_phase[phaseKey].input_tokens ?? 0;
            tokensOut = v.by_phase[phaseKey].output_tokens ?? 0;
            cost = v.by_phase[phaseKey].cost ?? 0;
          } else {
            // Use phase's own data
            tokensIn = phase.tokens_in ?? 0;
            tokensOut = phase.tokens_out ?? 0;
            cost = phase.cost ?? 0;
          }
        } else {
          tokensIn = phase.tokens_in ?? 0;
          tokensOut = phase.tokens_out ?? 0;
          cost = phase.cost ?? 0;
        }

        enrichments[phase.id] = {
          governance: { passed: govPassed, failed: govFailed, warnings: govWarnings, total: govPassed + govFailed + govWarnings },
          semanticCoverage: semCov,
          artifacts,
          evidence,
          tokensIn,
          tokensOut,
          cost,
        };
      }));

      setEnrichment(enrichments);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const displayPhases: PhaseData[] = phases.length > 0 ? phases : mockPhases.map(p => ({
    id: p.id, run_id: '', name: p.name, order_index: p.order, status: p.status as PhaseStatus,
    tokens_in: p.tokenUsage, tokens_out: 0, cost: 0,
  }));

  const totalTokens = displayPhases.reduce((sum, p) => sum + (enrichment[p.id]?.tokensIn ?? p.tokens_in ?? 0) + (enrichment[p.id]?.tokensOut ?? p.tokens_out ?? 0), 0);
  const totalCost = displayPhases.reduce((sum, p) => sum + (enrichment[p.id]?.cost ?? p.cost ?? 0), 0);
  const completedCount = displayPhases.filter(p => p.status === 'completed').length;
  const failedCount = displayPhases.filter(p => p.status === 'failed' || p.status === 'blocked').length;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader
          title="SDLC Phase Navigator"
          subtitle={dataSource === 'LIVE' ? `Run ${runId?.slice(0, 8)} • ${completedCount}/${displayPhases.length} phases complete` : `${displayPhases.length} phases from intake to retrospective`}
        />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Summary bar */}
      {dataSource === 'LIVE' && (
        <div className="card p-3 flex items-center gap-4">
          <div className="text-[10px] text-zinc-500">Tokens: <span className="text-zinc-300 font-mono">{(totalTokens / 1000).toFixed(1)}k</span></div>
          <div className="text-[10px] text-zinc-500">Cost: <span className="text-zinc-300 font-mono">${totalCost.toFixed(3)}</span></div>
          <div className="text-[10px] text-zinc-500">Completed: <span className="text-emerald-400 font-mono">{completedCount}/{displayPhases.length}</span></div>
          {failedCount > 0 && <div className="text-[10px] text-zinc-500">Failed: <span className="text-red-400 font-mono">{failedCount}</span></div>}
          <div className="ml-auto"><DataSourceBadge state={dataSource} /></div>
        </div>
      )}

      {/* Phase pipeline visualization */}
      <div className="card p-4">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-thin pb-2">
          {displayPhases.map((phase, i) => (
            <React.Fragment key={phase.id}>
              <button
                onClick={() => setExpandedPhase(expandedPhase === phase.id ? null : phase.id)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[10px] font-medium transition-all ${STATUS_STYLE[phase.status]}`}
              >
                {STATUS_ICON[phase.status]}
                {phase.name}
                {enrichment[phase.id]?.governance?.failed > 0 && (
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                )}
              </button>
              {i < displayPhases.length - 1 && (
                <ChevronRight className={`w-3 h-3 flex-shrink-0 ${phase.status === 'completed' ? 'text-emerald-400/40' : 'text-zinc-800'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Expanded phase detail */}
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          {expandedPhase && (() => {
            const phase = displayPhases.find(p => p.id === expandedPhase);
            const enrich = enrichment[expandedPhase];
            if (!phase) return null;
            return (
              <div className="card p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-200">{phase.name}</h3>
                    <p className="text-[10px] text-zinc-600">
                      Status: {phase.status}
                      {phase.model_used ? ` • Model: ${phase.model_used}` : ''}
                      {phase.agent_id ? ` • Agent: ${phase.agent_id.slice(0, 8)}` : ''}
                      {phase.started_at ? ` • Started: ${new Date(phase.started_at).toLocaleTimeString()}` : ''}
                      {phase.completed_at ? ` • Completed: ${new Date(phase.completed_at).toLocaleTimeString()}` : ''}
                    </p>
                  </div>
                  <StatusChip status={phase.status === 'completed' ? 'verified' : phase.status === 'active' ? 'active' : phase.status === 'failed' ? 'failed' : 'pending'} />
                </div>

                {phase.error_message && (
                  <div className="p-3 rounded-lg bg-red-400/5 border border-red-400/10">
                    <div className="text-[10px] text-red-400">{phase.error_message}</div>
                  </div>
                )}

                {/* Metrics grid */}
                <div className="grid grid-cols-4 gap-3">
                  <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                    <div className="text-[9px] text-zinc-700 uppercase">Tokens</div>
                    <div className="text-sm font-semibold text-zinc-300">
                      {((enrich?.tokensIn ?? phase.tokens_in ?? 0) + (enrich?.tokensOut ?? phase.tokens_out ?? 0)) > 0
                        ? `${(((enrich?.tokensIn ?? 0) + (enrich?.tokensOut ?? 0)) / 1000).toFixed(1)}k`
                        : '—'}
                    </div>
                  </div>
                  <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                    <div className="text-[9px] text-zinc-700 uppercase">Cost</div>
                    <div className="text-sm font-semibold text-zinc-300">
                      {enrich?.cost ? `$${enrich.cost.toFixed(4)}` : phase.cost ? `$${phase.cost.toFixed(4)}` : '—'}
                    </div>
                  </div>
                  <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                    <div className="text-[9px] text-zinc-700 uppercase">Artifacts</div>
                    <div className="text-sm font-semibold text-zinc-300">{enrich?.artifacts ?? '—'}</div>
                  </div>
                  <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                    <div className="text-[9px] text-zinc-700 uppercase">Evidence</div>
                    <div className="text-sm font-semibold text-zinc-300">{enrich?.evidence ? '✅ Available' : '—'}</div>
                  </div>
                </div>

                {/* Governance */}
                {enrich && enrich.governance.total > 0 && (
                  <div>
                    <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Governance</div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        <span className="text-[10px] text-emerald-400">{enrich.governance.passed} passed</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-amber-400" />
                        <span className="text-[10px] text-amber-400">{enrich.governance.warnings} warnings</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <XCircle className="w-3 h-3 text-red-400" />
                        <span className="text-[10px] text-red-400">{enrich.governance.failed} failed</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Semantic Coverage */}
                {enrich?.semanticCoverage !== null && enrich?.semanticCoverage !== undefined && (
                  <div>
                    <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Semantic Coverage</div>
                    <ProgressBar
                      value={enrich.semanticCoverage}
                      color={enrich.semanticCoverage >= 0.8 ? 'green' : enrich.semanticCoverage >= 0.5 ? 'amber' : 'red'}
                      showLabel
                    />
                  </div>
                )}

                <div className="flex items-center gap-2 text-[9px] text-zinc-600">
                  <DataSourceBadge state={dataSource} />
                  {dataSource === 'LIVE' && <span>Phase data enriched from governance, coverage, artifacts, evidence, and cost endpoints</span>}
                </div>
              </div>
            );
          })()}
        </div>

        {/* Right sidebar: phase list */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="All Phases" subtitle={`${displayPhases.length} phases`} />
          <div className="space-y-1 mt-2">
            {displayPhases.map(phase => {
              const enrich = enrichment[phase.id];
              return (
                <button
                  key={phase.id}
                  onClick={() => setExpandedPhase(expandedPhase === phase.id ? null : phase.id)}
                  className={`w-full flex items-center gap-2 p-2 rounded text-left transition-colors ${expandedPhase === phase.id ? 'bg-zinc-800/40 border border-zinc-700/40' : 'hover:bg-zinc-800/20 border border-transparent'}`}
                >
                  <div className={`w-2 h-2 rounded-full ${phase.status === 'completed' ? 'bg-emerald-400' : phase.status === 'active' ? 'bg-blue-400 animate-pulse' : phase.status === 'failed' || phase.status === 'blocked' ? 'bg-red-400' : 'bg-zinc-600'}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-medium text-zinc-400 truncate">{phase.name}</div>
                    {enrich && (
                      <div className="text-[8px] text-zinc-600">
                        {((enrich.tokensIn + enrich.tokensOut) / 1000).toFixed(1)}k tokens
                        {enrich.governance.total > 0 && ` • ${enrich.governance.passed}/${enrich.governance.total} gov`}
                      </div>
                    )}
                  </div>
                  {enrich?.evidence && <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" title="Evidence available" />}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
