'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api, type ArchitectureDetail, type ArtifactItem } from '@/lib/api';
import { mockArchComponents, mockADRs } from '@/lib/mock-data';
import { Box, Database, Globe, Layers, Server, Wifi, RefreshCw } from 'lucide-react';

type ArchComponent = {
  id: string; name: string; type: string; status: string;
  dependencies: string[]; testCoverage: number; tokenCost: number; changeFrequency: number;
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

function parseArchComponents(arch: ArchitectureDetail | null): ArchComponent[] {
  if (!arch?.components) return [];
  return arch.components.map((c, i) => ({
    id: c.id || `comp-${i}`, name: c.name, type: c.type, status: 'generated',
    dependencies: c.dependencies || [], testCoverage: 0, tokenCost: 0, changeFrequency: 0,
  }));
}

export function BuildMap() {
  const [arch, setArch] = useState<ArchitectureDetail | null>(null);
  const [components, setComponents] = useState<ArchComponent[]>(mockArchComponents);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchArch = async () => {
    setLoading(true); setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) { setError('No runs found'); setDataSource('ERROR'); setLoading(false); return; }
      try {
        const archData = await api.getLatestArch(latestRun.id) as ArchitectureDetail;
        setArch(archData);
        const parsed = parseArchComponents(archData);
        if (parsed.length > 0) { setComponents(parsed); setDataSource('PARTIAL'); }
        else if (archData.content || archData.mermaid_diagram) { setDataSource('PARTIAL'); }
        else { setDataSource('MOCK'); }
      } catch { setDataSource('MOCK'); }
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); setDataSource('ERROR'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchArch(); }, []);

  const selected = components.find(c => c.id === selectedNode);
  const adrs = arch?.decisions || mockADRs;
  const frontendComponents = components.filter(c => c.type === 'frontend');
  const apiComponents = components.filter(c => c.type === 'api');
  const serviceComponents = components.filter(c => c.type === 'service');
  const infraComponents = components.filter(c => ['database', 'queue', 'cache', 'integration'].includes(c.type));

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />
      <div className="flex items-center justify-between">
        <SectionHeader title="Application Build Map" subtitle="Component dependency graph" />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button onClick={fetchArch} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </div>

      {arch && (
        <div className="card p-3 flex items-center gap-4">
          <div className="text-[10px] text-zinc-500">Version: <span className="text-zinc-300">{arch.version || '—'}</span></div>
          <div className="text-[10px] text-zinc-500">Components: <span className="text-zinc-300">{components.length}</span></div>
          <div className="text-[10px] text-zinc-500">ADRs: <span className="text-zinc-300">{adrs.length}</span></div>
          <div className="ml-auto"><DataSourceBadge state={dataSource} /></div>
        </div>
      )}

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-9 card p-4 min-h-[600px] relative">
          <div className="absolute inset-0 bg-dots opacity-30" />
          <div className="relative z-10">
            {frontendComponents.length > 0 && (
              <div className="mb-6">
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Frontend</div>
                <div className="flex gap-3">
                  {frontendComponents.map(c => (
                    <button key={c.id} onClick={() => setSelectedNode(c.id)}
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36`}>
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
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36`}>
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
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-40`}>
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
                      className={`p-3 rounded-lg border ${statusColor[c.status] || statusColor.generated} hover:brightness-125 transition-all w-36`}>
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
              </div>
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
