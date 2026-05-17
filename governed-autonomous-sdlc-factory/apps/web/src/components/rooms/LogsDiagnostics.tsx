'use client';

import React, { useState, useEffect } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { DataSourceBadge, DataSourceBanner } from '@/components/ui/DataSourceBadge';
import { api } from '@/lib/api';
import { Terminal, Filter, AlertTriangle, Info, AlertCircle, RefreshCw } from 'lucide-react';
import type { LogsResponse } from '@/lib/api';

export function LogsDiagnostics() {
  const [logs, setLogs] = useState<LogsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'LIVE' | 'MOCK' | 'ERROR' | 'LOADING'>('LOADING');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getLogs({ limit: 100 });
      setLogs(result);
      setDataSource('LIVE');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs');
      setDataSource('ERROR');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  // Mock logs for fallback
  const mockLogEntries = [
    { id: 'log-001', severity: 'info', message: 'Run started: PaymentHub v1.0 build', timestamp: '2026-05-14T06:00:00Z', agent_id: 'system' },
    { id: 'log-002', severity: 'info', message: 'Product analysis complete — 8 requirements extracted', timestamp: '2026-05-14T06:12:00Z', agent_id: 'product-analyst' },
    { id: 'log-003', severity: 'warning', message: 'Requirement REQ-005 has high ambiguity score (0.35)', timestamp: '2026-05-14T06:35:00Z', agent_id: 'req-normalizer' },
    { id: 'log-004', severity: 'info', message: 'Architecture v1 generated — 12 components', timestamp: '2026-05-14T07:05:00Z', agent_id: 'architect' },
    { id: 'log-005', severity: 'warning', message: 'API contract conflict detected between Payment and Fraud services', timestamp: '2026-05-14T07:10:00Z', agent_id: 'architect' },
    { id: 'log-006', severity: 'info', message: 'Architecture regenerated (v2) — conflict resolved', timestamp: '2026-05-14T07:22:00Z', agent_id: 'architect' },
    { id: 'log-007', severity: 'error', message: 'Code generation failed: security policy violation in fraud-svc', timestamp: '2026-05-14T07:45:00Z', agent_id: 'code-gen' },
    { id: 'log-008', severity: 'info', message: 'Code regenerated — policy violation fixed', timestamp: '2026-05-14T07:48:00Z', agent_id: 'code-gen' },
    { id: 'log-009', severity: 'info', message: 'Test suite generated — 18 test cases', timestamp: '2026-05-14T07:54:00Z', agent_id: 'test-gen' },
    { id: 'log-010', severity: 'warning', message: 'Semantic coverage for REQ-005 below threshold (42%)', timestamp: '2026-05-14T08:10:00Z', agent_id: 'semantic-cov' },
    { id: 'log-011', severity: 'warning', message: 'False confidence detected: test_auth_check_exists', timestamp: '2026-05-14T08:13:00Z', agent_id: 'verifier' },
    { id: 'log-012', severity: 'info', message: 'Evidence binding complete — 3 items bound', timestamp: '2026-05-14T08:14:00Z', agent_id: 'evidence' },
  ];

  const displayLogs = dataSource === 'LIVE' && logs?.logs ? logs.logs : mockLogEntries;
  const filtered = severityFilter === 'all' ? displayLogs : displayLogs.filter(l => l.severity === severityFilter);

  const severityIcon = (sev: string) => {
    if (sev === 'error' || sev === 'critical') return <AlertCircle className="w-3 h-3 text-red-400" />;
    if (sev === 'warning') return <AlertTriangle className="w-3 h-3 text-amber-400" />;
    return <Info className="w-3 h-3 text-blue-400" />;
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <DataSourceBanner state={dataSource} message={error || undefined} />

      <div className="flex items-center justify-between">
        <SectionHeader title="Logs & Diagnostics" subtitle={`${filtered.length} log entries`} />
        <div className="flex items-center gap-2">
          <DataSourceBadge state={dataSource} />
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px] hover:bg-zinc-700/50 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Filter className="w-3 h-3 text-zinc-600" />
        {['all', 'info', 'warning', 'error', 'critical'].map(f => (
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
              <span className="text-zinc-600 w-24 flex-shrink-0">{log.agent_id}</span>
              <span className={log.severity === 'error' || log.severity === 'critical' ? 'text-red-400' : log.severity === 'warning' ? 'text-amber-400' : 'text-zinc-400'}>
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
