'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Network,
  Loader2,
  Search,
  Filter,
  ArrowRight,
  Hash,
  Link2,
} from 'lucide-react';

export function TraceabilityRoom() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const traceabilityLinks = useStore((s) => s.traceabilityLinks);
  const setTraceabilityLinks = useStore((s) => s.setTraceabilityLinks);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [filterTarget, setFilterTarget] = useState('');

  const handleLoad = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.getTraceability(runIdInput.trim());
      setTraceabilityLinks(result.links || []);
    } catch (e: any) {
      setLastError(e.message);
      setTraceabilityLinks([]);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, setTraceabilityLinks, setLastError]);

  const filteredLinks = traceabilityLinks.filter((link) => {
    if (filterType && link.link_type !== filterType) return false;
    if (filterSource && link.source_type !== filterSource) return false;
    if (filterTarget && link.target_type !== filterTarget) return false;
    return true;
  });

  const linkTypes = [...new Set(traceabilityLinks.map((l) => l.link_type))];
  const sourceTypes = [...new Set(traceabilityLinks.map((l) => l.source_type))];
  const targetTypes = [...new Set(traceabilityLinks.map((l) => l.target_type))];

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            TRACEABILITY ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Requirement Lineage — Artifact Links — Coverage Analysis
          </p>
        </div>
        <Badge variant="emerald">
          <Link2 className="w-3 h-3 mr-1" />
          {traceabilityLinks.length} Links
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Load Traceability" subtitle="Enter run ID" icon={<Network className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <button
            onClick={handleLoad}
            disabled={loading || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>
      </Card>

      {/* Metrics */}
      {traceabilityLinks.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <Metric label="Total Links" value={traceabilityLinks.length} color="text-zinc-200" />
          </Card>
          <Card>
            <Metric label="Link Types" value={linkTypes.length} color="text-blue-400" />
          </Card>
          <Card>
            <Metric label="Source Types" value={sourceTypes.length} color="text-emerald-400" />
          </Card>
          <Card>
            <Metric label="Target Types" value={targetTypes.length} color="text-amber-400" />
          </Card>
        </div>
      )}

      {/* Filters */}
      {traceabilityLinks.length > 0 && (
        <Card>
          <SectionHeader title="Filters" subtitle="Filter traceability links" icon={<Filter className="w-4 h-4" />} />
          <div className="grid grid-cols-3 gap-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">All Link Types</option>
              {linkTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">All Source Types</option>
              {sourceTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <select
              value={filterTarget}
              onChange={(e) => setFilterTarget(e.target.value)}
              className="bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">All Target Types</option>
              {targetTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="mt-2 text-[10px] font-mono text-zinc-600">
            Showing {filteredLinks.length} of {traceabilityLinks.length} links
          </div>
        </Card>
      )}

      {/* Links Table */}
      {filteredLinks.length > 0 && (
        <Card>
          <SectionHeader title="Traceability Links" subtitle={`${filteredLinks.length} links`} icon={<Link2 className="w-4 h-4" />} />
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-2 px-3 text-zinc-500 uppercase text-[10px]">Source</th>
                  <th className="text-left py-2 px-3 text-zinc-500 uppercase text-[10px]">Type</th>
                  <th className="text-left py-2 px-3 text-zinc-500 uppercase text-[10px]">Target</th>
                  <th className="text-left py-2 px-3 text-zinc-500 uppercase text-[10px]">Confidence</th>
                  <th className="text-left py-2 px-3 text-zinc-500 uppercase text-[10px]">Hash</th>
                </tr>
              </thead>
              <tbody>
                {filteredLinks.slice(0, 100).map((link) => (
                  <tr key={link.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/20">
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-1">
                        <Badge variant="zinc" size="sm">{link.source_type}</Badge>
                        <span className="text-zinc-400 truncate max-w-[120px]" title={link.source_id}>
                          {link.source_id.slice(0, 12)}...
                        </span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-1">
                        <ArrowRight className="w-3 h-3 text-zinc-600" />
                        <span className="text-zinc-300">{link.link_type}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-1">
                        <Badge variant="zinc" size="sm">{link.target_type}</Badge>
                        <span className="text-zinc-400 truncate max-w-[120px]" title={link.target_id}>
                          {link.target_id.slice(0, 12)}...
                        </span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <Badge variant={link.confidence && link.confidence >= 0.8 ? 'emerald' : link.confidence && link.confidence >= 0.5 ? 'amber' : 'red'} size="sm">
                        {link.confidence ? link.confidence.toFixed(2) : '—'}
                      </Badge>
                    </td>
                    <td className="py-2 px-3 text-zinc-600 truncate max-w-[100px]" title={link.edge_hash}>
                      {link.edge_hash ? `${link.edge_hash.slice(0, 8)}...` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredLinks.length > 100 && (
              <div className="mt-3 text-center text-[10px] font-mono text-zinc-600">
                Showing 100 of {filteredLinks.length} links. Use filters to narrow results.
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {traceabilityLinks.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
          <Network className="w-10 h-10 mb-3 opacity-20" />
          <p className="text-xs font-mono">No traceability data loaded</p>
          <p className="text-[10px] font-mono mt-1">Enter a run ID and click Load</p>
        </div>
      )}
    </div>
  );
}
