'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type SpecificationDetail, type ArtifactItem } from '@/lib/api';
import { FileText, CheckCircle2, Link2, RefreshCw } from 'lucide-react';

export function SpecRoom() {
  const [spec, setSpec] = useState<SpecificationDetail | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchSpec = async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) {
        setError('No runs found');
        setDataSource('ERROR');
        setLoading(false);
        return;
      }

      const [specRes, artifactsRes] = await Promise.allSettled([
        api.getLatestSpec(latestRun.id) as Promise<SpecificationDetail>,
        api.listArtifacts(latestRun.id) as Promise<{ artifacts: ArtifactItem[]; total: number }>,
      ]);

      if (specRes.status === 'fulfilled') {
        setSpec(specRes.value);
      }

      if (artifactsRes.status === 'fulfilled') {
        setArtifacts(artifactsRes.value.artifacts || []);
      }

      if (specRes.status === 'fulfilled') {
        const s = specRes.value;
        const hasRequirements = (s.acceptance_criteria && s.acceptance_criteria.length > 0) ||
          (s.functional_requirements && s.functional_requirements.length > 0);
        setDataSource(hasRequirements ? 'LIVE' : 'PARTIAL');
      } else {
        setDataSource('ERROR');
        setError('Failed to fetch specification from backend');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch specification');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSpec();
  }, []);

  const functionalRequirements: string[] = spec?.acceptance_criteria?.length
    ? spec.acceptance_criteria
    : spec?.functional_requirements || [];

  const nonFunctionalRequirements: string[] = spec?.non_functional_requirements || [];
  const specArtifacts = artifacts.filter(a =>
    a.type === 'specification' || a.type === 'requirement' || a.name.toLowerCase().includes('spec')
  );

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Specification" subtitle="Product specification and requirements" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchSpec} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold text-zinc-200">
              {spec ? `Specification v${spec.version || '1.0'}` : 'Specification'}
            </span>
            <DataSourceBadge state={dataSource} />
          </div>

          {spec?.content && <p className="text-xs text-zinc-400 mb-4">{spec.content}</p>}

          <div className="mb-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Functional Requirements</div>
            {functionalRequirements.length > 0 ? (
              <div className="space-y-1">
                {functionalRequirements.map((req, i) => (
                  <div key={i} className="flex items-start gap-2 text-[10px]">
                    <span className="text-zinc-600 font-mono w-6 flex-shrink-0">FR{i + 1}</span>
                    <span className="text-zinc-400">{req}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-[10px] text-zinc-600">No functional requirements available from backend</div>
            )}
          </div>

          <div>
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Non-Functional Requirements</div>
            {nonFunctionalRequirements.length > 0 ? (
              <div className="space-y-1">
                {nonFunctionalRequirements.map((req, i) => (
                  <div key={i} className="flex items-start gap-2 text-[10px]">
                    <span className="text-zinc-600 font-mono w-6 flex-shrink-0">NFR{i + 1}</span>
                    <span className="text-zinc-400">{req}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-[10px] text-zinc-600">No non-functional requirements available from backend</div>
            )}
          </div>
        </div>

        <div className="col-span-4 space-y-4">
          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Metadata</div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Version</span><span className="text-zinc-400">{spec?.version || '—'}</span></div>
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Data Source</span><DataSourceBadge state={dataSource} /></div>
            </div>
          </div>
          {specArtifacts.length > 0 && (
            <div className="card p-4">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Linked Artifacts</div>
              <div className="space-y-1.5">
                {specArtifacts.slice(0, 5).map(a => (
                  <div key={a.id} className="flex items-center gap-1.5 text-[10px]">
                    <Link2 className="w-2.5 h-2.5 text-zinc-600" />
                    <span className="text-zinc-500 truncate">{a.name}</span>
                    <Badge variant="zinc" size="sm">{a.type}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
