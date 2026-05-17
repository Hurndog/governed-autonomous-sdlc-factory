'use client';
import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { useStore } from '@/lib/store';
import { Terminal, Filter, AlertTriangle, Info, AlertCircle } from 'lucide-react';

export function LogsDiagnostics() {
  const logs = useStore((s) => s.logs);
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const mockLogs = [
    { id: 'log-001', severity: 'info', message: 'Run started: PaymentHub v1.0 build', timestamp: '2026-05-14T06:00:00Z', agent: 'System' },
    { id: 'log-002', severity: 'info', message: 'Product analysis complete — 8 requirements extracted', timestamp: '2026-05-14T06:12:00Z', agent: 'Product Analyst' },
    { id: 'log-003', severity: 'warning', message: 'Requirement REQ-005 has high ambiguity score (0.35)', timestamp: '2026-05-14T06:35:00Z', agent: 'Requirement Normalizer' },
    { id: 'log-004', severity: 'info', message: 'Architecture v1 generated — 12 components', timestamp: '2026-05-14T07:05:00Z', agent: 'Architecture Agent' },
    { id: 'log-005', severity: 'warning', message: 'API contract conflict detected between Payment and Fraud services', timestamp: '2026-05-14T07:10:00Z', agent: 'Architecture Agent' },
    { id: 'log-006', severity: 'info', message: 'Architecture regenerated (v2) — conflict resolved', timestamp: '2026-05-14T07:22:00Z', agent: 'Architecture Agent' },
    { id: 'log-007', severity: 'error', message: 'Code generation failed: security policy violation in fraud-svc', timestamp: '2026-05-14T07:45:00Z', agent: 'Code Generation' },
    { id: 'log-008', severity: 'info', message: 'Code regenerated — policy violation fixed', timestamp: '2026-05-14T07:48:00Z', agent: 'Code Generation' },
    { id: 'log-009', severity: 'info', message: 'Test suite generated — 18 test cases', timestamp: '2026-05-14T07:54:00Z', agent: 'Test Generation' },
    { id: 'log-010', severity: 'warning', message: 'Semantic coverage for REQ-005 below threshold (42%)', timestamp: '2026-05-14T08:10:00Z', agent: 'Semantic Coverage' },
    { id: 'log-011', severity: 'warning', message: 'False confidence detected: test_auth_check_exists', timestamp: '2026-05-14T08:13:00Z', agent: 'Verifier' },
    { id: 'log-012', severity: 'info', message: 'Evidence binding complete — 3 items bound', timestamp: '2026-05-14T08:14:00Z', agent: 'Evidence Agent' },
  ];

  const filtered = severityFilter === 'all' ? mockLogs : mockLogs.filter(l => l.severity === severityFilter);

  const severityIcon = (sev: string) => {
    if (sev === 'error') return <AlertCircle className="w-3 h-3 text-red-400" />;
    if (sev === 'warning') return <AlertTriangle className="w-3 h-3 text-amber-400" />;
    return <Info className="w-3 h-3 text-blue-400" />;
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Logs & Diagnostics" subtitle={`${mockLogs.length} log entries`} />

      <div className="flex items-center gap-2">
        <Filter className="w-3 h-3 text-zinc-600" />
        {['all', 'info', 'warning', 'error'].map(f => (
          <button
            key={f}
            onClick={() => setSeverityFilter(f)}
            className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-wider ${
              severityFilter === f ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-zinc-600 hover:text-zinc-400'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="card p-4 font-mono">
        <div className="space-y-0.5 max-h-[600px] overflow-y-auto scrollbar-thin">
          {filtered.map(log => (
            <div key={log.id} className="flex items-start gap-2 py-1 px-2 rounded hover:bg-zinc-800/30 text-[10px]">
              <span className="text-zinc-700 w-16 flex-shrink-0">{log.timestamp.slice(11, 19)}</span>
              {severityIcon(log.severity)}
              <span className="text-zinc-600 w-24 flex-shrink-0">{log.agent}</span>
              <span className={log.severity === 'error' ? 'text-red-400' : log.severity === 'warning' ? 'text-amber-400' : 'text-zinc-400'}>
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
