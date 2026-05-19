'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import {
  api,
  type ArchitectureDetail,
  type ArtifactItem,
  type TraceabilityLink,
  type GovernanceEvaluation,
  type CostReportResponse,
  type CoverageResponse,
} from '@/lib/api';
import { mockArchComponents, mockADRs } from '@/lib/mock-data';
import { Box, Database, Globe, Layers, Server, Wifi, RefreshCw, Link2, Shield, FileCode, AlertTriangle, DollarSign } from 'lucide-react';

type ArchComponent = {
  id: string; name: string; type: string; status: string;
  dependencies: string[]; testCoverage: number; tokenCost: number; changeFrequency: number;
  traceabilityLinks: { incoming: TraceabilityLink[]; outgoing: TraceabilityLink[] };
  governanceEvaluations: GovernanceEvaluation[];
  artifacts: ArtifactItem[];
  riskScore: number;
};

const typeIcons: Record<string, React.ReactNode> = {
  service: <Server className="w-3.5 h-3.5" />, api: <Globe className="w-3.5 h-3.5" />,
  database: <Database className="w-3.5 h-3.5" />, frontend: <Layers className="w-3.5 h-3.5" />,
  integration: <Wifi className="w-3.5 h-3.5" />, queue: <Box className="w-3.5 h-3.5" />,
  cache: <Box className="w-3.5 h-3.5" />,
};

const statusColor: Record<string, string> = {
  verified: 'border-emerald-400/30 bg-emerald-400/5', tested: 'border-blue-400/30 bg-blue-400/5',
  generated: 'border-amber-400/30 bg-amber-400/5', blocked: 'border-red-400/30 bg-red-400/5',
  pending: 'border-zinc-700/30 bg-zinc-800/30', implemented: 'border-cyan-400/30 bg-cyan-400/5',
};

function parseArchComponents(
  arch: ArchitectureDetail | null,
  traceability: TraceabilityLink[] | null,
  governance: GovernanceEvaluation[] | null,
  artifacts: ArtifactItem[] | null,
  costReport: CostReportResponse | null,
): ArchComponent[] {
  if (!arch?.components) return [];
  return arch.components.map((c, i) => {
    const id = c.id || `comp-${i}`;
    // Traceability links where this component is source or target
    const incoming = (traceability || []).filter(l => l.target_id === id || l.target_type === id);
    const outgoing = (traceability || []).filter(l => l.source_id === id || l.source_type === id);
    // Governance evaluations referencing this component
    const govEvals = (governance || []).filter(g =>
      g.findings?.some(f => f.artifact_id === id || f.requirement_id === id) ||
      g.input_data && JSON.stringify(g.input_data).includes(id)
    );
    // Artifacts linked to this component
    const compArtifacts = (artifacts || []).filter(a =>
      a.name?.includes(c.name) || a.metadata && JSON.stringify(a.metadata).includes(id)
    );
    // Token cost: sum from cost report by_phase entries that mention this component
    let tokenCost = 0;
    if (costReport) {
      const costEntries = [
        ...Object.values(costReport.by_phase || {}),
        ...Object.values(costReport.by_agent || {}),
      ];
      for (const entry of costEntries) {
        if (entry.key?.includes(c.name) || entry.label?.includes(c.name) || entry.key === id) {
          tokenCost += entry.total_tokens || 0;
        }
      }
      // If no direct match, distribute proportionally
      if (tokenCost === 0 && arch.components && arch.components.length > 0) {
        tokenCost = Math.round((costReport.total_tokens || 0) / arch.components.length);
      }
    }
    // Risk score: derived from governance failures and missing traceability
    let riskScore = 0;
    if (govEvals.some(g => g.status === 'fail')) riskScore += 0.5;
    else if (govEvals.some(g => g.status === 'warn')) riskScore += 0.25;
    if (incoming.length === 0 && outgoing.length === 0) riskScore += 0.2;
    if (compArtifacts.length === 0) riskScore += 0.1;
    riskScore = Math.min(riskScore, 1);

    return {
      id,
      name: c.name,
      type: c.type,
      status: 'generated',
      dependencies: c.dependencies || [],
      testCoverage: 0,
      tokenCost,
      changeFrequency: 0,
      traceabilityLinks: { incoming, outgoing },
      governanceEvaluations: govEvals,
      artifacts: compArtifacts,
      riskScore,
    };
  });
}

export function BuildMap() {
  const [arch, setArch] = useState<ArchitectureDetail | null>(null);
  const [components, setComponents] = useState<ArchComponent[]>(mockArchComponents);
  const [traceability, setTraceability] = useState<TraceabilityLink[] | null>(null);
  const [traceCoverage, setTraceCoverage] = useState<CoverageResponse | null>(null);
  const [governance, setGovernance] = useState<GovernanceEvaluation[] | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactItem[] | null>(null);
  const [costReport, setCostReport] = useState<CostReportResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchAll = useCallback(async () => {
    setLoading(true); setError(null); setDataSource('LOADING');
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }

      // Fetch all endpoints in parallel
      const results = await Promise.allSettled([
        api.getLatestArch(latestRun.id),
        api.getTraceability(latestRun.id),
        api.getTraceabilityCoverage(latestRun.id),
        api.getGovernanceEvaluations(latestRun.id),
        api.listArtifacts(latestRun.id),
        api.getCostReport(latestRun.id),
      ]);

      const archResult = results[0].status === 'fulfilled' ? results[0].value as ArchitectureDetail : null;
      const traceResult = results[1].status === 'fulfilled' ? (results[1].value as { links: TraceabilityLink[]; total: number }).links : null;
      const traceCovResult = results[2].status === 'fulfilled' ? results[2].value as CoverageResponse : null;
      const govResult = results[3].status === 'fulfilled' ? (results[3].value as { evaluations: GovernanceEvaluation[]; total: number }).evaluations : null;
      const artifactsResult = results[4].status === 'fulfilled' ? (results[4].value as { artifacts: ArtifactItem[]; total: number }).artifacts : null;
      const costResult = results[5].status === 'fulfilled' ? results[5].value as CostReportResponse : null;

      setArch(archResult);
      setTraceability(traceResult);
      setTraceCoverage(traceCovResult);
      setGovernance(govResult);
      setArtifacts(artifactsResult);
      setCostReport(costResult);

      // Parse enriched components
      const parsed = parseArchComponents(archResult, traceResult, govResult, artifactsResult, costResult);

      // Determine data source state
      const succeededCount = results.filter(r => r.status === 'fulfilled').length;
      const totalEndpoints = results.length;

      if (succeededCount === totalEndpoints && parsed.length > 0) {
        setDataSource('LIVE');
      } else if (succeededCount > 0 && parsed.length > 0) {
        setDataSource('PARTIAL');
      } else if (succeededCount > 0 && (archResult?.content || archResult?.mermaid_diagram)) {
        setDataSource('PARTIAL');
      } else {
        setDataSource('MOCK');
      }

      if (parsed.length > 0) {
        setComponents(parsed);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch build map data');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const selected = components.find(c => c.id === selectedNode);
  const adrs = arch?.decisions || mockADRs;
  const frontendComponents = components.filter(c => c.type === 'frontend');
  const apiComponents = components.filter(c => c.type === 'api');
  const serviceComponents = components.filter(c => c.type === 'service');
  const infraComponents = components.filter(c => ['database', 'queue', 'cache', 'integration'].includes(c.type));

  const totalTraceLinks = traceability?.length || 0;
  const totalArtifacts = artifacts?.length || 0;
  const totalGovFailures = governance?.filter(g => g.status === 'fail').length || 0;
  const totalGovWarnings = governance?.filter(g => g.status === 'warn').length || 0;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Application Build Map" subtitle="Component dependency graph" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchAll} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Summary bar */}
      <div className="card p-3 flex items-center gap-4 flex-wrap">
        <div className="text-[10px] text-zinc-500">Version: <span className="text-zinc-300">{arch?.version || '—'}</span></div>
        <div className="text-[10px] text-zinc-500">Components: <span className="text-zinc-300">{components.length}</span></div>
        <div className="text-[10px] text-zinc-500">ADRs: <span className="text-zinc-300">{adrs.length}</span></div>
        {dataSource === 'LIVE' && (
          <>
            <div className="text-[10px] text-zinc-500 flex items-center gap-1"><Link2 className="w-3 h-3" /> Traceability: <span className="text-zinc-300">{totalTraceLinks} links</span></div>
            <div className="text-[10px] text-zinc-500 flex items-center gap-1"><FileCode className="w-3 h-3" /> Artifacts: <span className="text-zinc-300">{totalArtifacts}</span></div>
            <div className="text-[10px] text-zinc-500 flex items-center gap-1"><Shield className="w-3 h-3" /> Governance: {totalGovFailures > 0 ? <span className="text-red-400">{totalGovFailures} failing</span> : <span className="text-emerald-400">all passing</span>}{totalGovWarnings > 0 && <span className="text-amber-400">, {totalGovWarnings} warnings</span>}</div>
            {costReport && <div className="text-[10px] text-zinc-500 flex items-center gap-1"><DollarSign className="w-3 h-3" /> Cost: <span className="text-zinc-300">${costReport.total_cost?.toFixed(4) || '—'}</span></div>}
            {traceCoverage && <div className="text-[10px] text-zinc-500">Coverage: <span className="text-zinc-300">{Math.round((traceCoverage.coverage_pct || 0) * 100)}%</span></div>}
          </>
        )}
        <div className="ml-auto"><DataSourceBadge state={dataSource} /></div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Topology map */}
        <div className="col-span-9 card p-4 min-h-[600px] relative">
          <div className="absolute inset-0 bg-dots opacity-30" />
          <div className="relative z-10">
            {frontendComponents.length > 0 && (
              <div className="mb-6">
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Frontend</div>
                <div className="flex gap-3">
                  {frontendComponents.map(c => (
                    <button key={c.id} onClick={() => setSelectedNode(c.id)}
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36 relative`}>
                      {c.riskScore > 0.3 && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500/80 flex items-center justify-center">
                          <AlertTriangle className="w-2 h-2 text-white" />
                        </div>
                      )}
                      <div className="flex items-center gap-2 mb-1">{typeIcons[c.type]}<span className="text-[10px] font-medium text-zinc-300">{c.name}</span></div>
                      <StatusChip status={c.status === 'implemented' ? 'verified' : c.status} size="sm" />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {apiComponents.length > 0 && (
              <div className="mb-6">
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">API Layer</div>
                <div className="flex gap-3">
                  {apiComponents.map(c => (
                    <button key={c.id} onClick={() => setSelectedNode(c.id)}
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36 relative`}>
                      {c.riskScore > 0.3 && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500/80 flex items-center justify-center">
                          <AlertTriangle className="w-2 h-2 text-white" />
                        </div>
                      )}
                      <div className="flex items-center gap-2 mb-1">{typeIcons[c.type]}<span className="text-[10px] font-medium text-zinc-300">{c.name}</span></div>
                      <StatusChip status={c.status} size="sm" />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {serviceComponents.length > 0 && (
              <div className="mb-6">
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Services</div>
                <div className="flex flex-wrap gap-3">
                  {serviceComponents.map(c => (
                    <button key={c.id} onClick={() => setSelectedNode(c.id)}
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-40 relative`}>
                      {c.riskScore > 0.3 && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500/80 flex items-center justify-center">
                          <AlertTriangle className="w-2 h-2 text-white" />
                        </div>
                      )}
                      <div className="flex items-center gap-2 mb-1">{typeIcons[c.type]}<span className="text-[10px] font-medium text-zinc-300">{c.name}</span></div>
                      <div className="flex items-center gap-2">
                        <StatusChip status={c.status === 'implemented' ? 'verified' : c.status} size="sm" />
                        <span className="text-[9px] text-zinc-600">{Math.round(c.testCoverage * 100)}% cov</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {infraComponents.length > 0 && (
              <div>
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Infrastructure</div>
                <div className="flex flex-wrap gap-3">
                  {infraComponents.map(c => (
                    <button key={c.id} onClick={() => setSelectedNode(c.id)}
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36 relative`}>
                      {c.riskScore > 0.3 && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500/80 flex items-center justify-center">
                          <AlertTriangle className="w-2 h-2 text-white" />
                        </div>
                      )}
                      <div className="flex items-center gap-2 mb-1">{typeIcons[c.type]}<span className="text-[10px] font-medium text-zinc-300">{c.name}</span></div>
                      <StatusChip status={c.status} size="sm" />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {components.length === 0 && dataSource === 'MOCK' && (
              <div className="text-[10px] text-zinc-600 p-4">No architecture data available from backend. Showing mock topology.</div>
            )}
          </div>
        </div>

        {/* Detail panel */}
        <div className="col-span-3 card p-4">
          {selected ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-1">{typeIcons[selected.type]}<h3 className="text-sm font-semibold text-zinc-200">{selected.name}</h3></div>
                <StatusChip status={selected.status === 'implemented' ? 'verified' : selected.status} />
              </div>
              <div className="space-y-3">
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Test Coverage</div>
                  <ProgressBar value={selected.testCoverage} color={selected.testCoverage >= 0.8 ? 'green' : selected.testCoverage >= 0.5 ? 'amber' : 'red'} showLabel />
                </div>
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Token Cost</div>
                  <span className="text-xs text-zinc-400">{(selected.tokenCost / 1000).toFixed(1)}k tokens</span>
                </div>
                {/* Semantic risk overlay */}
                {selected.riskScore > 0 && (
                  <div>
                    <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3 text-red-400" /> Risk Score
                    </div>
                    <ProgressBar value={selected.riskScore} color={selected.riskScore >= 0.5 ? 'red' : 'amber'} showLabel />
                  </div>
                )}
              </div>

              {/* Traceability links */}
              {(selected.traceabilityLinks.incoming.length > 0 || selected.traceabilityLinks.outgoing.length > 0) && (
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1 flex items-center gap-1">
                    <Link2 className="w-3 h-3" /> Traceability
                  </div>
                  <div className="space-y-1">
                    {selected.traceabilityLinks.outgoing.map(l => (
                      <div key={l.id} className="flex items-center gap-1.5 text-[10px]">
                        <span className="text-zinc-400">→</span>
                        <span className="text-zinc-500">{l.target_id}</span>
                        <span className="text-[8px] text-zinc-700">({l.link_type})</span>
                        {l.confidence != null && <span className="text-[8px] text-zinc-600">{Math.round(l.confidence * 100)}%</span>}
                      </div>
                    ))}
                    {selected.traceabilityLinks.incoming.map(l => (
                      <div key={l.id} className="flex items-center gap-1.5 text-[10px]">
                        <span className="text-zinc-400">←</span>
                        <span className="text-zinc-500">{l.source_id}</span>
                        <span className="text-[8px] text-zinc-700">({l.link_type})</span>
                        {l.confidence != null && <span className="text-[8px] text-zinc-600">{Math.round(l.confidence * 100)}%</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Governance state */}
              {selected.governanceEvaluations.length > 0 && (
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1 flex items-center gap-1">
                    <Shield className="w-3 h-3" /> Governance
                  </div>
                  <div className="space-y-1">
                    {selected.governanceEvaluations.map(g => (
                      <div key={g.id} className="flex items-center gap-1.5 text-[10px]">
                        <StatusChip status={g.status} size="sm" />
                        <span className="text-zinc-500">{g.policy_name || g.policy_id}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Artifact linkage */}
              {selected.artifacts.length > 0 && (
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1 flex items-center gap-1">
                    <FileCode className="w-3 h-3" /> Artifacts
                  </div>
                  <div className="space-y-1">
                    {selected.artifacts.map(a => (
                      <div key={a.id} className="flex items-center gap-1.5 text-[10px]">
                        <span className="text-zinc-400">{a.name}</span>
                        <span className="text-[8px] text-zinc-700">({a.type})</span>
                        {a.locked && <span className="text-[8px] text-amber-400">🔒</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selected.dependencies.length > 0 && (
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Dependencies</div>
                  <div className="space-y-1">
                    {selected.dependencies.map(dep => {
                      const depComp = components.find(c => c.id === dep);
                      return (
                        <div key={dep} className="flex items-center gap-1.5 text-[10px]">
                          <span className="text-zinc-500">{depComp?.name || dep}</span>
                          {depComp && <StatusChip status={depComp.status === 'implemented' ? 'verified' : depComp.status} size="sm" />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-zinc-700">
              <Box className="w-8 h-8 mb-2" /><span className="text-[10px]">Select a component to inspect</span>
            </div>
          )}
        </div>
      </div>

      {/* ADRs from architecture document */}
      {adrs.length > 0 && (
        <div className="card p-4">
          <SectionHeader title="Architecture Decision Records" subtitle={`${adrs.length} decisions documented`} />
          <div className="grid grid-cols-3 gap-3 mt-2">
            {adrs.slice(0, 6).map((adr, i) => (
              <div key={i} className="p-3 rounded-lg bg-zinc-800/20 border border-zinc-800/40">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-medium text-zinc-300">{adr.title}</span>
                  <StatusChip status={adr.status === 'accepted' ? 'verified' : 'active'} size="sm" />
                </div>
                <div className="text-[9px] text-zinc-600 line-clamp-2">{adr.decision}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
