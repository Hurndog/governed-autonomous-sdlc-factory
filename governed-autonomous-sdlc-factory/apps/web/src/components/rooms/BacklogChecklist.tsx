'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockBacklog } from '@/lib/mock-data';
import { CheckSquare, Square, AlertTriangle, Filter } from 'lucide-react';

export function BacklogChecklist() {
  const [items, setItems] = useState(mockBacklog);
  const [viewFilter, setViewFilter] = useState<string>('all');

  const toggleCheck = (id: string) => {
    setItems(prev => prev.map(item =>
      item.id === id ? { ...item, checked: !item.checked } : item
    ));
  };

  const filtered = viewFilter === 'all' ? items : items.filter(i => i.status === viewFilter || i.risk === viewFilter);
  const checkedCount = items.filter(i => i.checked).length;
  const totalTokens = items.reduce((sum, i) => sum + i.tokenCost, 0);

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Backlog & Build Checklist" subtitle={`${checkedCount}/${items.length} items checked • ${(totalTokens / 1000).toFixed(1)}k tokens`} />

      {/* Filters */}
      <div className="flex items-center gap-2">
        <Filter className="w-3 h-3 text-zinc-600" />
        {['all', 'verified', 'tested', 'blocked', 'pending', 'critical', 'high'].map(f => (
          <button
            key={f}
            onClick={() => setViewFilter(f)}
            className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${
              viewFilter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Checklist */}
      <div className="card p-4">
        <div className="space-y-1">
          {filtered.map(item => (
            <div
              key={item.id}
              className={`flex items-center gap-3 p-2.5 rounded-lg border transition-colors ${
                item.checked ? 'bg-emerald-400/5 border-emerald-400/10' : 'bg-zinc-800/10 border-zinc-800/30 hover:bg-zinc-800/20'
              }`}
            >
              <button onClick={() => toggleCheck(item.id)} className="flex-shrink-0">
                {item.checked ? (
                  <CheckSquare className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Square className="w-4 h-4 text-zinc-700" />
                )}
              </button>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-medium ${item.checked ? 'text-zinc-500 line-through' : 'text-zinc-300'}`}>
                    {item.title}
                  </span>
                  <Badge variant={
                    item.type === 'feature' ? 'blue' :
                    item.type === 'component' ? 'cyan' :
                    item.type === 'test' ? 'violet' :
                    item.type === 'policy' ? 'amber' :
                    'zinc'
                  } size="sm">{item.type}</Badge>
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-[9px] text-zinc-600">{item.phase}</span>
                  <span className="text-[9px] text-zinc-700">•</span>
                  <span className="text-[9px] text-zinc-600">{item.owner}</span>
                  {item.tokenCost > 0 && (
                    <>
                      <span className="text-[9px] text-zinc-700">•</span>
                      <span className="text-[9px] text-zinc-600">{(item.tokenCost / 1000).toFixed(1)}k tok</span>
                    </>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                {item.risk === 'critical' && <Badge variant="red" size="sm">CRIT</Badge>}
                {item.releaseImpact === 'critical' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                <StatusChip status={item.status === 'accepted' ? 'verified' : item.status} size="sm" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
