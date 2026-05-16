'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  FileText,
  Loader2,
  Search,
  Download,
  FolderOpen,
  ChevronDown,
  ChevronUp,
  Archive,
} from 'lucide-react';

export function EvidenceCenter() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const evidenceBundles = useStore((s) => s.evidenceBundles);
  const setEvidenceBundles = useStore((s) => s.setEvidenceBundles);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [loading, setLoading] = useState(false);
  const [expandedBundle, setExpandedBundle] = useState<string | null>(null);
  const [bundleContent, setBundleContent] = useState<Record<string, string>>({});
  const [loadingContent, setLoadingContent] = useState<string | null>(null);

  const handleLoad = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.getEvidenceByRun(runIdInput.trim());
      setEvidenceBundles(result.bundles || []);
    } catch (e: any) {
      setLastError(e.message);
      setEvidenceBundles([]);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, setEvidenceBundles, setLastError]);

  const handleDownload = useCallback(async (bundleId: string) => {
    setLoadingContent(bundleId);
    try {
      const content = await api.downloadEvidence(bundleId);
      setBundleContent((prev) => ({ ...prev, [bundleId]: content }));
      setExpandedBundle(bundleId);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoadingContent(null);
    }
  }, [setLastError]);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            EVIDENCE CENTER
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Evidence Reports — Baseline Documentation — Audit Trail
          </p>
        </div>
        <Badge variant="emerald">
          <Archive className="w-3 h-3 mr-1" />
          {evidenceBundles.length} Bundles
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Load Evidence" subtitle="Enter run ID" icon={<FolderOpen className="w-4 h-4" />} />
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
      {evidenceBundles.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <Metric label="Bundles" value={evidenceBundles.length} color="text-zinc-200" />
          </Card>
          <Card>
            <Metric label="Total Files" value={evidenceBundles.reduce((sum, b) => sum + (b.file_count || 0), 0)} color="text-blue-400" />
          </Card>
          <Card>
            <Metric label="Total Size" value={`${(evidenceBundles.reduce((sum, b) => sum + (b.size_bytes || 0), 0) / 1024).toFixed(1)} KB`} color="text-emerald-400" />
          </Card>
        </div>
      )}

      {/* Bundle List */}
      {evidenceBundles.length > 0 && (
        <Card>
          <SectionHeader title="Evidence Bundles" subtitle={`${evidenceBundles.length} bundles`} icon={<Archive className="w-4 h-4" />} />
          <div className="space-y-2">
            {evidenceBundles.map((bundle) => (
              <div key={bundle.id} className="border border-zinc-800 rounded-md overflow-hidden">
                <div className="flex items-center gap-3 px-4 py-3">
                  <FileText className="w-4 h-4 text-zinc-500" />
                  <span className="text-xs font-mono text-zinc-200 flex-1">{bundle.id}</span>
                  <Badge variant="zinc" size="sm">{bundle.file_count || 0} files</Badge>
                  <span className="text-[10px] font-mono text-zinc-600">
                    {bundle.size_bytes ? `${(bundle.size_bytes / 1024).toFixed(1)} KB` : '—'}
                  </span>
                  <button
                    onClick={() => handleDownload(bundle.id)}
                    disabled={loadingContent === bundle.id}
                    className="flex items-center gap-1 px-2 py-1 bg-blue-500/10 border border-blue-500/30 rounded text-blue-400 text-[10px] font-mono hover:bg-blue-500/20 transition-colors disabled:opacity-30"
                  >
                    {loadingContent === bundle.id ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <Download className="w-3 h-3" />
                    )}
                    View
                  </button>
                  {expandedBundle === bundle.id ? (
                    <ChevronUp className="w-3 h-3 text-zinc-500" />
                  ) : (
                    <ChevronDown className="w-3 h-3 text-zinc-500" />
                  )}
                </div>
                {expandedBundle === bundle.id && bundleContent[bundle.id] && (
                  <div className="px-4 py-3 bg-zinc-900/50 border-t border-zinc-800">
                    <pre className="text-[10px] font-mono text-zinc-400 whitespace-pre-wrap max-h-96 overflow-y-auto">
                      {bundleContent[bundle.id]}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {evidenceBundles.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
          <FolderOpen className="w-10 h-10 mb-3 opacity-20" />
          <p className="text-xs font-mono">No evidence bundles loaded</p>
          <p className="text-[10px] font-mono mt-1">Enter a run ID and click Load</p>
        </div>
      )}
    </div>
  );
}
