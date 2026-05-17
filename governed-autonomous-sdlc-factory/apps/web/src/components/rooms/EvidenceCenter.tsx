'use client';
import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { useStore } from '@/lib/store';
import { FileText, Download, Package, CheckCircle2, Clock } from 'lucide-react';

export function EvidenceCenter() {
  const bundles = useStore((s) => s.evidenceBundles);

  const mockBundles = [
    { id: 'eb-001', name: 'Requirements Evidence', artifacts: 12, size: '2.4 MB', date: '2026-05-14T06:47:00Z', status: 'complete' },
    { id: 'eb-002', name: 'Architecture Evidence', artifacts: 8, size: '1.8 MB', date: '2026-05-14T07:39:00Z', status: 'complete' },
    { id: 'eb-003', name: 'Test Coverage Evidence', artifacts: 18, size: '3.2 MB', date: '2026-05-14T08:14:00Z', status: 'complete' },
    { id: 'eb-004', name: 'Governance Evidence', artifacts: 6, size: '1.1 MB', date: '2026-05-14T06:57:00Z', status: 'complete' },
    { id: 'eb-005', name: 'Release Evidence', artifacts: 0, size: '0 MB', date: '', status: 'pending' },
  ];

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Evidence Center" subtitle="Forensic-grade evidence bundles" />

      <div className="grid grid-cols-3 gap-4">
        {mockBundles.map(bundle => (
          <div key={bundle.id} className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Package className="w-4 h-4 text-violet-400" />
              <span className="text-[11px] font-medium text-zinc-300">{bundle.name}</span>
              <StatusChip status={bundle.status === 'complete' ? 'verified' : 'pending'} size="sm" />
            </div>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div><div className="text-[8px] text-zinc-700 uppercase">Artifacts</div><div className="text-[10px] text-zinc-400">{bundle.artifacts}</div></div>
              <div><div className="text-[8px] text-zinc-700 uppercase">Size</div><div className="text-[10px] text-zinc-400">{bundle.size}</div></div>
              <div><div className="text-[8px] text-zinc-700 uppercase">Date</div><div className="text-[10px] text-zinc-400">{bundle.date ? bundle.date.slice(0, 10) : '—'}</div></div>
            </div>
            {bundle.status === 'complete' && (
              <button className="flex items-center gap-1 text-[9px] text-violet-400 hover:text-violet-300">
                <Download className="w-2.5 h-2.5" /> Export Bundle
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
