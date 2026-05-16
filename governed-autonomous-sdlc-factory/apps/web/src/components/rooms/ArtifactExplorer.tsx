'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  FileText,
  Loader2,
  Search,
  Lock,
  Unlock,
  Hash,
  Eye,
  ChevronDown,
  ChevronUp,
  Package,
} from 'lucide-react';

export function ArtifactExplorer() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const artifacts = useStore((s) => s.artifacts);
  const setArtifacts = useStore((s) => s.setArtifacts);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [expandedArtifact, setExpandedArtifact] = useState<string | null>(null);
  const [artifactContent, setArtifactContent] = useState<Record<string, string>>({});
  const [loadingContent, setLoadingContent] = useState<string | null>(null);

  const handleLoad = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.listArtifacts(runIdInput.trim(), filterType || undefined);
      setArtifacts(result.artifacts || []);
    } catch (e: any) {
      setLastError(e.message);
      setArtifacts([]);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, filterType, setArtifacts, setLastError]);

  const handleViewContent = useCallback(async (artifactId: string) => {
    if (artifactContent[artifactId]) {
      setExpandedArtifact(expandedArtifact === artifactId ? null : artifactId);
      return;
    }
    setLoadingContent(artifactId);
    try {
      const detail = await api.getArtifact(artifactId);
      setArtifactContent((prev) => ({ ...prev, [artifactId]: detail.content || 'No content available' }));
      setExpandedArtifact(artifactId);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoadingContent(null);
    }
  }, [artifactContent, expandedArtifact, setLastError]);

  const artifactTypes = [...new Set(artifacts.map((a) => a.type))];
  const filteredArtifacts = filterType ? artifacts.filter((a) => a.type === filterType) : artifacts;

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            ARTIFACT EXPLORER
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Browse Artifacts — View Content — Verify Hashes
          </p>
        </div>
        <Badge variant="emerald">
          <Package className="w-3 h-3 mr-1" />
          {artifacts.length} Artifacts
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Load Artifacts" subtitle="Enter run ID" icon={<FileText className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 focus:outline-none focus:border-emerald-500/50"
          >
            <option value="">All Types</option>
            {artifactTypes.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
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
      {artifacts.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <Metric label="Total" value={artifacts.length} color="text-zinc-200" />
          </Card>
          <Card>
            <Metric label="Types" value={artifactTypes.length} color="text-blue-400" />
          </Card>
          <Card>
            <Metric label="Locked" value={artifacts.filter((a) => a.locked).length} color="text-amber-400" />
          </Card>
          <Card>
            <Metric label="With Hash" value={artifacts.filter((a) => a.hash).length} color="text-emerald-400" />
          </Card>
        </div>
      )}

      {/* Artifact List */}
      {filteredArtifacts.length > 0 && (
        <Card>
          <SectionHeader title="Artifacts" subtitle={`${filteredArtifacts.length} artifacts`} icon={<Package className="w-4 h-4" />} />
          <div className="space-y-2">
            {filteredArtifacts.map((artifact) => (
              <div key={artifact.id} className="border border-zinc-800 rounded-md overflow-hidden">
                <div
                  className="flex items-center gap-3 px-4 py-3 hover:bg-zinc-800/30 cursor-pointer"
                  onClick={() => handleViewContent(artifact.id)}
                >
                  <Badge variant="zinc" size="sm">{artifact.type}</Badge>
                  <span className="text-xs font-mono text-zinc-200 flex-1">{artifact.name}</span>
                  {artifact.locked ? (
                    <Lock className="w-3 h-3 text-amber-400" />
                  ) : (
                    <Unlock className="w-3 h-3 text-zinc-600" />
                  )}
                  {artifact.hash && (
                    <span className="text-[9px] font-mono text-zinc-600 flex items-center gap-1">
                      <Hash className="w-3 h-3" />
                      {artifact.hash.slice(0, 8)}...
                    </span>
                  )}
                  {loadingContent === artifact.id ? (
                    <Loader2 className="w-3 h-3 animate-spin text-zinc-500" />
                  ) : expandedArtifact === artifact.id ? (
                    <ChevronUp className="w-3 h-3 text-zinc-500" />
                  ) : (
                    <ChevronDown className="w-3 h-3 text-zinc-500" />
                  )}
                </div>
                {expandedArtifact === artifact.id && artifactContent[artifact.id] && (
                  <div className="px-4 py-3 bg-zinc-900/50 border-t border-zinc-800">
                    <pre className="text-[10px] font-mono text-zinc-400 whitespace-pre-wrap max-h-64 overflow-y-auto">
                      {artifactContent[artifact.id]}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {artifacts.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
          <FileText className="w-10 h-10 mb-3 opacity-20" />
          <p className="text-xs font-mono">No artifacts loaded</p>
          <p className="text-[10px] font-mono mt-1">Enter a run ID and click Load</p>
        </div>
      )}
    </div>
  );
}
