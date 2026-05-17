'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { Package, FileText, Code, TestTube, Shield, File, Hash, Clock, User, Tag, Search, RefreshCw } from 'lucide-react';
import type { ArtifactsResponse } from '@/lib/api';

export function ArtifactExplorer() {
  const [artifacts, setArtifacts] = useState<ArtifactsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');

  const fetchArtifacts = async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns({ page_size: 1 });
      const latestRun = runs.items?.[0];
      if (!latestRun) {
        setError('No runs found');
        setDataSource('ERROR');
        return;
      }
      const result = await api.listArtifacts(latestRun.id);
      setArtifacts(result);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch artifacts');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArtifacts();
  }, []);

  const mockArtifacts = [
    { id: 'art-001', type: 'specification', name: 'Product Specification v1', phase: 'Specification', agent: 'Product Analyst', status: 'accepted', version: 1, tokenCost: 4200, confidence: 0.92, date: '2026-05-14T06:12:00Z', hash: 'a1b2c3d4' },
    { id: 'art-002', type: 'requirement', name: 'Normalized Requirements', phase: 'Requirements', agent: 'Requirement Normalizer', status: 'accepted', version: 2, tokenCost: 18400, confidence: 0.88, date: '2026-05-14T06:47:00Z', hash: 'e5f6g7h8' },
    { id: 'art-003', type: 'architecture', name: 'Architecture Model v3', phase: 'Architecture', agent: 'Architecture Agent', status: 'accepted', version: 3, tokenCost: 34200, confidence: 0.85, date: '2026-05-14T07:39:00Z', hash: 'i9j0k1l2' },
    { id: 'art-004', type: 'code', name: 'Payment Service', phase: 'Implementation', agent: 'Code Generation', status: 'tested', version: 1, tokenCost: 18400, confidence: 0.78, date: '2026-05-14T07:22:00Z', hash: 'm3n4o5p6' },
    { id: 'art-005', type: 'code', name: 'Fraud Detection Service', phase: 'Implementation', agent: 'Code Generation', status: 'generated', version: 2, tokenCost: 16200, confidence: 0.65, date: '2026-05-14T07:48:00Z', hash: 'q7r8s9t0' },
    { id: 'art-006', type: 'test', name: 'Test Suite v1', phase: 'Test Generation', agent: 'Test Generation', status: 'accepted', version: 1, tokenCost: 22100, confidence: 0.82, date: '2026-05-14T07:54:00Z', hash: 'u1v2w3x4' },
    { id: 'art-007', type: 'coverage', name: 'Semantic Coverage Report', phase: 'Semantic Coverage', agent: 'Semantic Coverage', status: 'generated', version: 1, tokenCost: 15800, confidence: 0.72, date: '2026-05-14T08:14:00Z', hash: 'y5z6a7b8' },
    { id: 'art-008', type: 'evidence', name: 'Evidence Bundle', phase: 'Evidence', agent: 'Evidence Agent', status: 'generated', version: 1, tokenCost: 1200, confidence: 0.91, date: '2026-05-14T08:14:00Z', hash: 'c9d0e1f2' },
  ];

  interface DisplayArtifact {
    id: string;
    type: string;
    name: string;
    phase: string;
    agent: string;
    status: string;
    version: number;
    tokenCost: number;
    confidence: number;
    date: string;
    hash: string;
  }

  const displayArtifacts: DisplayArtifact[] = (dataSource === 'LIVE' && artifacts?.artifacts ? artifacts.artifacts : mockArtifacts).map(art => {
    const mock = mockArtifacts.find(m => m.id === art.id);
    return {
      id: art.id,
      type: art.type,
      name: art.name,
      phase: (art as any).phase || mock?.phase || 'Unknown',
      agent: (art as any).agent || mock?.agent || 'Unknown',
      status: (art as any).status || mock?.status || 'pending',
      version: (art as any).version || mock?.version || 1,
      tokenCost: (art as any).tokenCost || mock?.tokenCost || 0,
      confidence: (art as any).confidence || mock?.confidence || 0.5,
      date: (art as any).created_at || mock?.date || '',
      hash: (art as any).hash || mock?.hash || '',
    };
  });

  const typeIcons: Record<string, React.ReactNode> = {
    specification: <FileText className="w-3.5 h-3.5" />,
    requirement: <File className="w-3.5 h-3.5" />,
    architecture: <Shield className="w-3.5 h-3.5" />,
    code: <Code className="w-3.5 h-3.5" />,
    test: <TestTube className="w-3.5 h-3.5" />,
    coverage: <Hash className="w-3.5 h-3.5" />,
    evidence: <Package className="w-3.5 h-3.5" />,
  };

  const typeColors: Record<string, string> = {
    specification: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    requirement: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    architecture: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    code: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
    test: 'text-violet-400 bg-violet-400/10 border-violet-400/20',
    coverage: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
    evidence: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Artifact Explorer" subtitle={`${displayArtifacts.length} artifacts`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchArtifacts}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="card p-3">
        <div className="flex items-center gap-2">
          <Search className="w-3.5 h-3.5 text-zinc-600" />
          <input
            type="text"
            placeholder="Search artifacts by name, type, or agent..."
            className="flex-1 bg-transparent text-xs text-zinc-300 placeholder-zinc-700 outline-none"
          />
        </div>
      </div>

      <div className="card p-4">
        <div className="space-y-1">
          {displayArtifacts.map(art => (
            <div key={art.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-zinc-800/20 border border-transparent hover:border-zinc-800/40 transition-colors">
              <div className={`w-7 h-7 rounded flex items-center justify-center border ${typeColors[art.type] || 'text-zinc-400 bg-zinc-800/10 border-zinc-700/20'}`}>
                {typeIcons[art.type] || <File className="w-3.5 h-3.5" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-medium text-zinc-300">{art.name}</span>
                  {art.version && <span className="text-[9px] text-zinc-700">v{art.version}</span>}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[9px] text-zinc-600">{art.phase}</span>
                  <span className="text-[9px] text-zinc-700">•</span>
                  <span className="text-[9px] text-zinc-600">{art.agent}</span>
                  {art.tokenCost > 0 && (
                    <>
                      <span className="text-[9px] text-zinc-700">•</span>
                      <span className="text-[9px] text-zinc-600">{(art.tokenCost / 1000).toFixed(1)}k tok</span>
                    </>
                  )}
                  {art.hash && (
                    <>
                      <span className="text-[9px] text-zinc-700">•</span>
                      <span className="text-[9px] font-mono text-zinc-700">{art.hash.slice(0, 8)}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-16">
                  <ProgressBar value={art.confidence} size="sm" color={art.confidence >= 0.8 ? 'green' : art.confidence >= 0.5 ? 'amber' : 'red'} />
                </div>
                <span className="text-[9px] font-mono text-zinc-600 w-8 text-right">{Math.round(art.confidence * 100)}%</span>
                <StatusChip status={art.status === 'accepted' ? 'verified' : art.status === 'tested' ? 'tested' : art.status === 'generated' ? 'generated' : 'pending'} size="sm" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
