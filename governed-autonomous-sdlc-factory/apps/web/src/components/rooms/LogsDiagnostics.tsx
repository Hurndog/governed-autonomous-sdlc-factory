'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Terminal,
  Loader2,
  Search,
  AlertTriangle,
  Info,
  AlertCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Download,
} from 'lucide-react';

export function LogsDiagnostics() {
  const logs = useStore((s) => s.logs);
  const setLogs = useStore((s) => s.setLogs);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [errorOnly, setErrorOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  const handleLoad = useCallback(async () => {
    setLoading(true);
    setLastError(null);
    try {
      const result = await api.getLogs({
        run_id: runIdInput || undefined,
        severity: severityFilter || undefined,
        error_only: errorOnly || undefined,
        limit: 200,
      });
      setLogs(result.logs || []);
    } catch (e: any) {
      setLastError(e.message);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, severityFilter, errorOnly, setLogs, setLastError]);

  const severityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-3 h-3 text-red-400" />;
      case 'error': return <AlertCircle className="w-3 h-3 text-red-400" />;
      case 'warning': return <AlertTriangle className="w-3 h-3 text-amber-400" />;
      case 'info': return <Info className="w-3 h-3 text-blue-400" />;
      default: return <Terminal className="w-3 h-3 text-zinc-500" />;
    }
  };

  const severityVariant = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'error': return 'red';
      case 'warning': return 'amber';
      case 'info': return 'blue';
      default: return 'zinc';
    }
  };

  const errorCount = logs.filter((l) => l.severity === 'error' || l.severity === 'critical').length;
  const warnCount = logs.filter((l) => l.severity === 'warning').length;

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            LOGS & DIAGNOSTICS
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Runtime Logs — Error Tracking — Diagnostic Events
          </p>
        </div>
        <Badge variant={errorCount > 0 ? 'red' : warnCount > 0 ? 'amber' : 'emerald'}>
          <Terminal className="w-3 h-3 mr-1" />
          {logs.length} Entries
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Load Logs" subtitle="Filter and load log entries" icon={<Terminal className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID (optional)"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 focus:outline-none focus:border-emerald-500/50"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
            <option value="debug">Debug</option>
          </select>
          <label className="flex items-center gap-2 text-xs font-mono text-zinc-400">
            <input
              type="checkbox"
              checked={errorOnly}
              onChange={(e) => setErrorOnly(e.target.checked)}
              className="rounded border-zinc-700 bg-zinc-900"
            />
            Errors only
          </label>
          <button
            onClick={handleLoad}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>
      </Card>

      {/* Metrics */}
      {logs.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <Metric label="Total" value={logs.length} color="text-zinc-200" />
          </Card>
          <Card>
            <Metric label="Errors" value={errorCount} color={errorCount > 0 ? 'text-red-400' : 'text-zinc-500'} />
          </Card>
          <Card>
            <Metric label="Warnings" value={warnCount} color={warnCount > 0 ? 'text-amber-400' : 'text-zinc-500'} />
          </Card>
          <Card>
            <Metric label="Info" value={logs.filter((l) => l.severity === 'info').length} color="text-blue-400" />
          </Card>
        </div>
      )}

      {/* Log Entries */}
      {logs.length > 0 && (
        <Card>
          <SectionHeader title="Log Entries" subtitle={`${logs.length} entries`} icon={<Terminal className="w-4 h-4" />} />
          <div className="space-y-1 max-h-[600px] overflow-y-auto">
            {logs.map((log) => (
              <div
                key={log.id}
                className={`flex items-start gap-3 px-3 py-2 rounded border ${
                  log.severity === 'critical' || log.severity === 'error'
                    ? 'bg-red-500/5 border-red-500/10'
                    : log.severity === 'warning'
                    ? 'bg-amber-500/5 border-amber-500/10'
                    : 'bg-zinc-900/30 border-zinc-800/30'
                }`}
              >
                {severityIcon(log.severity)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge variant={severityVariant(log.severity) as any} size="sm">{log.severity}</Badge>
                    <span className="text-[9px] font-mono text-zinc-600">{new Date(log.timestamp).toLocaleString()}</span>
                    {log.run_id && <span className="text-[9px] font-mono text-zinc-700">run: {log.run_id.slice(0, 8)}...</span>}
                  </div>
                  <p className="text-[11px] font-mono text-zinc-300 mt-1 break-all">{log.message}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {logs.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
          <Terminal className="w-10 h-10 mb-3 opacity-20" />
          <p className="text-xs font-mono">No logs loaded</p>
          <p className="text-[10px] font-mono mt-1">Click Load to fetch log entries</p>
        </div>
      )}
    </div>
  );
}
