'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockBacklog } from '@/lib/mock-data';
import { CheckSquare, Square, AlertTriangle, Filter, RefreshCw, Shield, FileText, Bug, XCircle } from 'lucide-react';

interface RequirementData {
  requirement_id: string; normalized_statement: string; actor?: string;
  criticality?: string; testability_score?: number; status?: string;
}

interface TestObligation {
  obligation_id: string; requirement_id: string; obligation_type: string;
  proof_statement: string; required_test_type: string; status?: string;
}

interface BacklogItem {
  id: string; title: string; type: string;
  status: string; risk: string; phase: string;
  owner: string; releaseImpact: string;
  governanceStatus?: string;
  hasEvidence?: boolean;
  mutationStatus?: string;
  verifierCritique?: string;
}

export function BacklogChecklist() {
  const [requirements, setRequirements] = useState<RequirementData[]>([]);
  const [obligations, setObligations] = useState<TestObligation[]>([]);
  const [governanceEvals, setGovernanceEvals] = useState<Array<{ requirement_id?: string; status: string; policy_name?: string }>>([]);
  const [mutationTests, setMutationTests] = useState<Array<{ survived: boolean; requirement_id?: string }>>([]);
  const [verifierCritiques, setVerifierCritiques] = useState<Array<{ requirement_id?: string; critique: string; verdict: string; confidence: number }>>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [viewFilter, setViewFilter] = useState<string>('all');
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  const fetchBacklogData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      setRunId(latestRun.id);

      const results = await Promise.allSettled([
        api.getSemanticRequirements(latestRun.id) as Promise<{ requirements: RequirementData[] }>,
        api.getSemanticTestObligations(latestRun.id) as Promise<{ obligations: TestObligation[] }>,
        api.getGovernanceEvaluations(latestRun.id) as Promise<{ evaluations: Array<{ requirement_id?: string; status: string; policy_name?: string }> }>,
        api.getSemanticMutations(latestRun.id) as unknown as Promise<{ mutations: Array<{ survived: boolean; requirement_id?: string }> }>,
        api.getSemanticVerifierCritiques(latestRun.id) as unknown as Promise<{ critiques: Array<{ requirement_id?: string; critique: string; verdict: string; confidence: number }> }>,
      ]);

      const [reqsRes, obsRes, govRes, mutRes, verRes] = results;
      let successCount = 0;

      if (reqsRes.status === 'fulfilled' && reqsRes.value.requirements?.length > 0) {
        setRequirements(reqsRes.value.requirements);
        successCount++;
      }
      if (obsRes.status === 'fulfilled' && obsRes.value.obligations?.length > 0) {
        setObligations(obsRes.value.obligations);
        successCount++;
      }
      if (govRes.status === 'fulfilled') {
        setGovernanceEvals((govRes.value as { evaluations: Array<{ requirement_id?: string; status: string; policy_name?: string }> }).evaluations || []);
        successCount++;
      }
      if (mutRes.status === 'fulfilled') {
        const v = mutRes.value as { mutations?: Array<{ survived: boolean; requirement_id?: string }> };
        setMutationTests(v.mutations || []);
        successCount++;
      }
      if (verRes.status === 'fulfilled') {
        const v = verRes.value as { critiques?: Array<{ requirement_id?: string; critique: string; verdict: string; confidence: number }> };
        setVerifierCritiques(v.critiques || []);
        successCount++;
      }

      setDataSource(successCount >= 3 ? 'LIVE' : successCount >= 1 ? 'PARTIAL' : 'MOCK');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
      setDataSource('ERROR');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchBacklogData(); }, [fetchBacklogData]);

  const toggleCheck = (id: string) => {
    setCheckedItems(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  };

  // Build enriched backlog items from real data
  const buildRealItems = (): BacklogItem[] => {
    const items: BacklogItem[] = [];

    requirements.forEach(req => {
      const gov = governanceEvals.find(g => g.requirement_id === req.requirement_id);
      const mutations = mutationTests.filter(m => m.requirement_id === req.requirement_id);
      const critiques = verifierCritiques.filter(v => v.requirement_id === req.requirement_id);
      const survivedMutations = mutations.filter(m => m.survived).length;

      let risk = req.criticality || 'medium';
      if (gov?.status === 'fail') risk = 'critical';
      else if (survivedMutations > 0) risk = 'high';
      else if (critiques.some(c => c.verdict === 'fail' || c.confidence < 0.5)) risk = 'high';

      items.push({
        id: req.requirement_id,
        title: req.normalized_statement,
        type: 'requirement',
        status: gov?.status === 'fail' ? 'blocked' : req.status || 'pending',
        risk,
        phase: 'Requirements',
        owner: req.actor || 'System',
        releaseImpact: req.criticality === 'critical' ? 'critical' : 'normal',
        governanceStatus: gov?.status,
        hasEvidence: false,
        mutationStatus: survivedMutations > 0 ? 'weak' : mutations.length > 0 ? 'strong' : 'untested',
        verifierCritique: critiques[0]?.critique,
      });
    });

    obligations.forEach(obs => {
      const req = requirements.find(r => r.requirement_id === obs.requirement_id);
      items.push({
        id: obs.obligation_id,
        title: obs.proof_statement,
        type: 'test',
        status: obs.status || 'pending',
        risk: 'medium',
        phase: 'Testing',
        owner: obs.required_test_type,
        releaseImpact: req?.criticality === 'critical' ? 'critical' : 'normal',
      });
    });

    return items;
  };

  const realItems = buildRealItems();
  const items = realItems.length > 0 ? realItems : mockBacklog;
  const effectiveDataSource = realItems.length > 0 ? (dataSource === 'LIVE' ? 'LIVE' : 'PARTIAL') : 'MOCK';

  const filtered = viewFilter === 'all' ? items :
    viewFilter === 'blocked' ? items.filter(i => i.status === 'blocked' || (i as any).governanceStatus === 'fail') :
    viewFilter === 'weak' ? items.filter(i => (i as any).mutationStatus === 'weak') :
    viewFilter === 'critical' ? items.filter(i => i.risk === 'critical' || i.releaseImpact === 'critical') :
    items.filter(i => i.status === viewFilter || i.risk === viewFilter);

  const checkedCount = items.filter(i => checkedItems.has(i.id)).length;
  const criticalCount = items.filter(i => i.risk === 'critical' || i.releaseImpact === 'critical').length;
  const blockedCount = items.filter(i => i.status === 'blocked' || (i as any).governanceStatus === 'fail').length;
  const weakMutationCount = items.filter(i => (i as any).mutationStatus === 'weak').length;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={effectiveDataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Backlog & Build Checklist"
          subtitle={effectiveDataSource === 'LIVE' && runId
            ? `Run ${runId.slice(0, 8)} • ${checkedCount}/${items.length} checked • ${criticalCount} critical`
            : `${checkedCount}/${items.length} items checked`}
        />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={effectiveDataSource} />
          <button onClick={fetchBacklogData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Summary */}
      {effectiveDataSource !== 'MOCK' && (
        <div className="card p-3 flex items-center gap-4">
          <div className="text-[10px] text-zinc-500">Total: <span className="text-zinc-300 font-mono">{items.length}</span></div>
          <div className="text-[10px] text-zinc-500">Critical: <span className="text-red-400 font-mono">{criticalCount}</span></div>
          <div className="text-[10px] text-zinc-500">Blocked: <span className="text-red-400 font-mono">{blockedCount}</span></div>
          {weakMutationCount > 0 && (
            <div className="text-[10px] text-zinc-500">Weak Mutations: <span className="text-amber-400 font-mono">{weakMutationCount}</span></div>
          )}
          <div className="ml-auto"><DataSourceBadge state={effectiveDataSource} /></div>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-2">
        <Filter className="w-3 h-3 text-zinc-600" />
        {['all', 'blocked', 'weak', 'critical', 'pending', 'verified', 'high'].map(f => (
          <button key={f} onClick={() => setViewFilter(f)}
            className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${viewFilter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* Checklist */}
      <div className="card p-4">
        <div className="space-y-1">
          {filtered.map(item => (
            <div key={item.id} className={`flex items-center gap-3 p-2.5 rounded-lg border transition-colors ${checkedItems.has(item.id) ? 'bg-emerald-400/5 border-emerald-400/10' : item.risk === 'critical' || item.status === 'blocked' ? 'bg-red-400/5 border-red-400/10' : 'bg-zinc-800/10 border-zinc-800/30 hover:bg-zinc-800/20'}`}>
              <button onClick={() => toggleCheck(item.id)} className="flex-shrink-0">
                {checkedItems.has(item.id) ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-zinc-700" />}
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-medium ${checkedItems.has(item.id) ? 'text-zinc-500 line-through' : 'text-zinc-300'}`}>{item.title}</span>
                  <Badge variant={item.type === 'test' ? 'violet' : 'blue'} size="sm">{item.type}</Badge>
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-[9px] text-zinc-600">{item.phase}</span>
                  <span className="text-[9px] text-zinc-700">•</span>
                  <span className="text-[9px] text-zinc-600">{item.owner}</span>
                  {(item as any).governanceStatus === 'fail' && (
                    <><span className="text-[9px] text-zinc-700">•</span><span className="text-[9px] text-red-400 flex items-center gap-0.5"><Shield className="w-2.5 h-2.5" />gov failed</span></>
                  )}
                  {(item as any).mutationStatus === 'weak' && (
                    <><span className="text-[9px] text-zinc-700">•</span><span className="text-[9px] text-amber-400 flex items-center gap-0.5"><Bug className="w-2.5 h-2.5" />weak mutations</span></>
                  )}
                  {(item as any).verifierCritique && (
                    <><span className="text-[9px] text-zinc-700">•</span><span className="text-[9px] text-amber-400 truncate max-w-[200px]">{(item as any).verifierCritique}</span></>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {item.risk === 'critical' && <Badge variant="red" size="sm">CRIT</Badge>}
                {item.releaseImpact === 'critical' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                {item.status === 'blocked' && <XCircle className="w-3 h-3 text-red-400" />}
                <StatusChip status={item.status === 'blocked' ? 'blocked' : item.status === 'verified' ? 'verified' : 'pending'} size="sm" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
