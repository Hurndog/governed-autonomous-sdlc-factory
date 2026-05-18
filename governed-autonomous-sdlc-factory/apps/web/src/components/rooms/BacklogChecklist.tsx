'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { mockBacklog } from '@/lib/mock-data';
import { CheckSquare, Square, AlertTriangle, Filter, RefreshCw } from 'lucide-react';

interface RequirementData {
  requirement_id: string; normalized_statement: string; actor?: string;
  criticality?: string; testability_score?: number;
}

interface TestObligation {
  obligation_id: string; requirement_id: string; obligation_type: string;
  proof_statement: string; required_test_type: string; status?: string;
}

export function BacklogChecklist() {
  const [requirements, setRequirements] = useState<RequirementData[]>([]);
  const [obligations, setObligations] = useState<TestObligation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [viewFilter, setViewFilter] = useState<string>('all');
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  const fetchBacklogData = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }

      const [reqsRes, obsRes] = await Promise.allSettled([
        api.getSemanticRequirements(latestRun.id) as Promise<{ requirements: RequirementData[] }>,
        api.getSemanticTestObligations(latestRun.id) as Promise<{ obligations: TestObligation[] }>,
      ]);

      let hasRealData = false;
      if (reqsRes.status === 'fulfilled' && reqsRes.value.requirements?.length > 0) {
        setRequirements(reqsRes.value.requirements); hasRealData = true;
      }
      if (obsRes.status === 'fulfilled' && obsRes.value.obligations?.length > 0) {
        setObligations(obsRes.value.obligations); hasRealData = true;
      }
      setDataSource(hasRealData ? 'PARTIAL' : 'MOCK');
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchBacklogData(); }, []);

  const toggleCheck = (id: string) => {
    setCheckedItems(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  };

  const realChecklistItems = requirements.map(req => ({
    id: req.requirement_id, title: req.normalized_statement, type: 'requirement' as const,
    status: req.criticality === 'critical' ? 'critical' : 'verified', risk: req.criticality || 'medium',
    phase: 'Requirements', owner: req.actor || 'System', tokenCost: 0, releaseImpact: req.criticality === 'critical' ? 'critical' as const : 'normal' as const,
  }));

  const realObligationItems = obligations.map(obs => ({
    id: obs.obligation_id, title: obs.proof_statement, type: 'test' as const,
    status: obs.status || 'pending', risk: 'medium', phase: 'Testing',
    owner: obs.required_test_type, tokenCost: 0, releaseImpact: 'normal' as const,
  }));

  const realItems = [...realChecklistItems, ...realObligationItems];
  const mockItems = mockBacklog;
  const items = realItems.length > 0 ? realItems : mockItems;
  const effectiveDataSource = realItems.length > 0 ? 'PARTIAL' : 'MOCK';

  const filtered = viewFilter === 'all' ? items : items.filter(i => i.status === viewFilter || i.risk === viewFilter);
  const checkedCount = items.filter(i => checkedItems.has(i.id)).length;

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={effectiveDataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Backlog & Build Checklist" subtitle={`${checkedCount}/${items.length} items checked`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={effectiveDataSource} />
          <button onClick={fetchBacklogData} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Filter className="w-3 h-3 text-zinc-600" />
        {['all', 'verified', 'tested', 'blocked', 'pending', 'critical', 'high'].map(f => (
          <button key={f} onClick={() => setViewFilter(f)}
            className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${viewFilter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'}`}>
            {f}
          </button>
        ))}
      </div>

      <div className="card p-4">
        <div className="space-y-1">
          {filtered.map(item => (
            <div key={item.id} className={`flex items-center gap-3 p-2.5 rounded-lg border transition-colors ${checkedItems.has(item.id) ? 'bg-emerald-400/5 border-emerald-400/10' : 'bg-zinc-800/10 border-zinc-800/30 hover:bg-zinc-800/20'}`}>
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
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {item.risk === 'critical' && <Badge variant="red" size="sm">CRIT</Badge>}
                {item.releaseImpact === 'critical' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                <StatusChip status={item.status === 'critical' ? 'blocked' : item.status === 'verified' ? 'verified' : 'pending'} size="sm" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
