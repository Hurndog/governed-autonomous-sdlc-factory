'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { mockArchComponents, mockADRs, mockArchDrift, mockRequirements } from '@/lib/mock-data';
import { Box, Database, Globe, Layers, Server, Wifi, AlertTriangle, CheckCircle2, Clock, Coins } from 'lucide-react';

const typeIcons: Record<string, React.ReactNode> = {
  service: <Server className="w-3.5 h-3.5" />,
  api: <Globe className="w-3.5 h-3.5" />,
  database: <Database className="w-3.5 h-3.5" />,
  frontend: <Layers className="w-3.5 h-3.5" />,
  integration: <Wifi className="w-3.5 h-3.5" />,
  queue: <Box className="w-3.5 h-3.5" />,
  cache: <Box className="w-3.5 h-3.5" />,
};

const statusColor: Record<string, string> = {
  verified: 'border-emerald-400/30 bg-emerald-400/5',
  tested: 'border-blue-400/30 bg-blue-400/5',
  generated: 'border-amber-400/30 bg-amber-400/5',
  blocked: 'border-red-400/30 bg-red-400/5',
  pending: 'border-zinc-700/30 bg-zinc-800/30',
  implemented: 'border-cyan-400/30 bg-cyan-400/5',
};

export function BuildMap() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const selected = mockArchComponents.find(c => c.id === selectedNode);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Application Build Map" subtitle="PaymentHub — component dependency graph" />

      <div className="grid grid-cols-12 gap-4">
        {/* Graph Area */}
        <div className="col-span-9 card p-4 min-h-[600px] relative">
          <div className="absolute inset-0 bg-dots opacity-30" />
          {/* Layer labels */}
          <div className="relative z-10">
            {/* Frontend Layer */}
            <div className="mb-6">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Frontend</div>
              <div className="flex gap-3">
                {mockArchComponents.filter(c => c.type === 'frontend').map(c => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedNode(c.id)}
                    className={`p-3 rounded-lg border ${statusColor[c.status]} hover:brightness-125 transition-all w-36`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {typeIcons[c.type]}
                      <span className="text-[10px] font-medium text-zinc-300">{c.name}</span>
                    </div>
                    <StatusChip status={c.status === 'implemented' ? 'verified' : c.status} size="sm" />
                  </button>
                ))}
              </div>
            </div>

            {/* API Layer */}
            <div className="mb-6">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">API Layer</div>
              <div className="flex gap-3">
                {mockArchComponents.filter(c => c.type === 'api').map(c => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedNode(c.id)}
                    className={`p-3 rounded-lg border ${statusColor[c.status]} hover:brightness-125 transition-all w-36`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {typeIcons[c.type]}
                      <span className="text-[10px] font-medium text-zinc-300">{c.name}</span>
                    </div>
                    <StatusChip status={c.status} size="sm" />
                  </button>
                ))}
              </div>
            </div>

            {/* Services Layer */}
            <div className="mb-6">
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Services</div>
              <div className="flex flex-wrap gap-3">
                {mockArchComponents.filter(c => c.type === 'service').map(c => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedNode(c.id)}
                    className={`p-3 rounded-lg border ${statusColor[c.status]} hover:brightness-125 transition-all w-40`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {typeIcons[c.type]}
                      <span className="text-[10px] font-medium text-zinc-300">{c.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <StatusChip status={c.status === 'implemented' ? 'verified' : c.status} size="sm" />
                      <span className="text-[9px] text-zinc-600">{Math.round(c.testCoverage * 100)}% cov</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Infrastructure Layer */}
            <div>
              <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Infrastructure</div>
              <div className="flex flex-wrap gap-3">
                {mockArchComponents.filter(c => ['database', 'queue', 'cache', 'integration'].includes(c.type)).map(c => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedNode(c.id)}
                    className={`p-3 rounded-lg border ${statusColor[c.status]} hover:brightness-125 transition-all w-36`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {typeIcons[c.type]}
                      <span className="text-[10px] font-medium text-zinc-300">{c.name}</span>
                    </div>
                    <StatusChip status={c.status} size="sm" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Detail Drawer */}
        <div className="col-span-3 card p-4">
          {selected ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  {typeIcons[selected.type]}
                  <h3 className="text-sm font-semibold text-zinc-200">{selected.name}</h3>
                </div>
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
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Change Frequency</div>
                  <span className="text-xs text-zinc-400">{selected.changeFrequency} revisions</span>
                </div>
              </div>

              {selected.dependencies.length > 0 && (
                <div>
                  <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Dependencies</div>
                  <div className="space-y-1">
                    {selected.dependencies.map(dep => {
                      const depComp = mockArchComponents.find(c => c.id === dep);
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

              {/* Linked Requirements */}
              <div>
                <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-1">Linked Requirements</div>
                <div className="space-y-1">
                  {mockRequirements.filter(r => r.status !== 'pending').slice(0, 3).map(req => (
                    <div key={req.id} className="text-[10px] text-zinc-500">{req.id}: {req.normalizedStatement.slice(0, 40)}...</div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-zinc-700">
              <Box className="w-8 h-8 mb-2" />
              <span className="text-[10px]">Select a component to inspect</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
