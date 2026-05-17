'use client';

import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { useStore } from '@/lib/store';
import { Package, FileText, Code, TestTube, Shield, File, Hash, Clock, User, Tag, Search } from 'lucide-react';

export function ArtifactExplorer() {
  const artifacts = useStore((s) => s.artifacts);

  const mockArtifacts = [
    { id: 'art-001', type: 'specification', name: 'Product Specification v1', phase: 'Specification', agent: 'Product Analyst', status: 'accepted', version: 1, tokenCost: 4200, confidence: 0.92, date: '2026-05-14T06:12:00Z' },
    { id: 'art-002', type: 'requirement', name: 'Normalized Requirements', phase: 'Requirements', agent: 'Requirement Normalizer', status: 'accepted', version: 2, tokenCost: 18400, confidence: 0.88, date: '2026-05-14T06:47:00Z' },
    { id: 'art-003', type: 'architecture', name: 'Architecture Model v3', phase: 'Architecture', agent: 'Architecture Agent', status: 'accepted', version: 3, tokenCost: 34200, confidence: 0.85, date: '2026-05-14T07:39:00Z' },
    { id: 'art-004', type: 'code', name: 'Payment Service', phase: 'Implementation', agent: 'Code Generation', status: 'tested', version: 1, tokenCost: 18400, confidence: 0.78, date: '2026-05-14T07:22:00Z' },
    { id: 'art-005', type: 'code', name: 'Fraud Detection Service', phase: 'Implementation', agent: 'Code Generation', status: 'generated', version: 2, tokenCost: 16200, confidence: 0.65, date: '2026-05-14T07:48:00Z' },
    { id: 'art-006', type: 'test', name: 'Test Suite v1', phase: 'Test Generation', agent: 'Test Generation', status: 'accepted', version: 1, tokenCost: 22100, confidence: 0.82, date: '2026-05-14T07:54:00Z' },
    { id: 'art-007', type: 'coverage', name: 'Semantic Coverage Report', phase: 'Semantic Coverage', agent: 'Semantic Coverage', status: 'generated', version: 1, tokenCost: 15800, confidence: 0.72, date: '2026-05-14T08:14:00Z' },
    { id: 'art-008', type: 'evidence', name: 'Evidence Bundle', phase: 'Evidence', agent: 'Evidence Agent', status: 'generated', version: 1, tokenCost: 1200, confidence: 0.91, date: '2026-05-14T08:14:00Z' },
  ];

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
      <SectionHeader title="Artifact Explorer" subtitle={`${mockArtifacts.length} artifacts across all phases`} />

      {/* Search */}
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

      {/* Artifact list */}
      <div className="card p-4">
        <div className="space-y-1">
          {mockArtifacts.map(art => (
            <div key={art.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-zinc-800/20 border border-transparent hover:border-zinc-800/40 transition-colors">
              <div className={`w-7 h-7 rounded flex items-center justify-center border ${typeColors[art.type]}`}>
                {typeIcons[art.type]}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-medium text-zinc-300">{art.name}</span>
                  <span className="text-[9px] text-zinc-700">v{art.version}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[9px] text-zinc-600">{art.phase}</span>
                  <span className="text-[9px] text-zinc-700">•</span>
                  <span className="text-[9px] text-zinc-600">{art.agent}</span>
                  <span className="text-[9px] text-zinc-700">•</span>
                  <span className="text-[9px] text-zinc-600">{(art.tokenCost / 1000).toFixed(1)}k tok</span>
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
