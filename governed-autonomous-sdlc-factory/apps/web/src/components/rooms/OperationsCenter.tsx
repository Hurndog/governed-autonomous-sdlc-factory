'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { StatusChip } from '@/components/ui/StatusChip';
import { MetricCard } from '@/components/ui/MetricCard';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { DataSourceBadge } from '@/components/ui/DataSourceBadge';

// ── Types ──────────────────────────────────────────────────────────────────

interface RunCounts {
  active: number;
  paused: number;
  failed: number;
  completed: number;
  pending: number;
  cancelled: number;
  total: number;
}

interface HealthStatus {
  runtime: string;
  governance: string;
  replay: string;
  memory: string;
  drift: string;
  trust: string;
  tokenomics: string;
  overall: string;
}

interface AlertSummary {
  governance_alerts: number;
  drift_events: number;
  replay_unchained: number;
  memory_poisoned: number;
  low_coverage_runs: number;
  total_critical: number;
  total_warnings: number;
}

interface OperationEvent {
  id: string;
  timestamp: string;
  run_id: string | null;
  event_type: string;
  severity: string;
  source: string;
  message: string;
  trust_impact: number;
  requires_operator_action: boolean;
}

interface OperationsSummary {
  generated_at: string;
  runs: RunCounts;
  health: HealthStatus;
  alerts: AlertSummary;
  providers: Record<string, { status: string; url?: string }>;
  recent_events: OperationEvent[];
}

// ── Helpers ────────────────────────────────────────────────────────────────

function mapHealthToStatus(health: string): 'verified' | 'warning' | 'error' | 'pending' | 'partial' {
  switch (health) {
    case 'healthy': return 'verified';
    case 'degraded': return 'partial';
    case 'warning': return 'warning';
    case 'critical': return 'error';
    case 'no_data': return 'pending';
    case 'initializing': return 'pending';
    default: return 'pending';
  }
}

function mapSeverityToStatus(severity: string): 'error' | 'warning' | 'verified' | 'pending' {
  switch (severity) {
    case 'critical': return 'error';
    case 'error': return 'error';
    case 'warning': return 'warning';
    case 'info': return 'verified';
    default: return 'pending';
  }
}

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return ts;
  }
}

// ── Main Component ─────────────────────────────────────────────────────────

export function OperationsCenter() {
  const [data, setData] = useState<OperationsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'live' | 'fallback' | 'error'>('fallback');
  const [lastRefresh, setLastRefresh] = useState<string>('');

  const fetchSummary = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token') || '';
      const resp = await fetch('/api/v1/operations/summary', {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: AbortSignal.timeout(10000),
      });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
      }

      const json: OperationsSummary = await resp.json();
      setData(json);
      setDataSource('live');
      setError(null);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e: any) {
      setError(e.message || 'Failed to fetch operations summary');
      setDataSource('error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 30000);
    return () => clearInterval(interval);
  }, [fetchSummary]);

  if (loading) {
    return (
      <div className="p-6">
        <SectionHeader title="Operations Center" subtitle="Loading operational state..." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {[1, 2, 3].map(i => (
            <Card key={i} className="h-24 animate-pulse bg-gray-800"><div /></Card>
          ))}
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-6">
        <SectionHeader title="Operations Center" subtitle="Unable to load operational state" />
        <Card className="mt-4 border-red-500/30 bg-red-950/20">
          <div className="text-red-400 text-sm">
            <p className="font-semibold">Connection Error</p>
            <p className="mt-1">{error}</p>
            <p className="mt-2 text-xs text-red-500">
              This may be because the operations endpoint is not yet deployed or the backend is unreachable.
            </p>
          </div>
          <button
            onClick={fetchSummary}
            className="mt-3 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded"
          >
            Retry
          </button>
        </Card>
      </div>
    );
  }

  const health = data?.health;
  const alerts = data?.alerts;
  const runs = data?.runs;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Operations Center"
          subtitle={`Real-time operational state${lastRefresh ? ` — Last updated: ${lastRefresh}` : ''}`}
        />
        <div className="flex items-center gap-3">
          <DataSourceBadge state={dataSource === 'live' ? 'LIVE' : dataSource === 'error' ? 'ERROR' : 'PARTIAL'} />
          <button
            onClick={fetchSummary}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Overall Health */}
      {health && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">System Health</h3>
            <StatusChip status={mapHealthToStatus(health.overall)} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {Object.entries(health).filter(([k]) => k !== 'overall').map(([key, value]) => (
              <div key={key} className="text-center">
                <StatusChip status={mapHealthToStatus(value)} />
                <p className="text-[10px] text-gray-500 mt-1 capitalize">{key}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Run Status + Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {runs && (
          <Card>
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Run Status</h3>
            <div className="grid grid-cols-3 gap-3">
              <MetricCard label="Active" value={runs.active} badge={{ label: 'Running', variant: 'green' }} />
              <MetricCard label="Paused" value={runs.paused} badge={{ label: 'Paused', variant: 'amber' }} />
              <MetricCard label="Failed" value={runs.failed} badge={{ label: 'Failed', variant: 'red' }} />
              <MetricCard label="Completed" value={runs.completed} badge={{ label: 'Done', variant: 'blue' }} />
              <MetricCard label="Pending" value={runs.pending} badge={{ label: 'Pending', variant: 'zinc' }} />
              <MetricCard label="Total" value={runs.total} />
            </div>
          </Card>
        )}

        {alerts && (
          <Card>
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Alerts</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Critical</span>
                <span className={`text-sm font-bold ${alerts.total_critical > 0 ? 'text-red-400' : 'text-gray-500'}`}>
                  {alerts.total_critical}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Warnings</span>
                <span className={`text-sm font-bold ${alerts.total_warnings > 0 ? 'text-yellow-400' : 'text-gray-500'}`}>
                  {alerts.total_warnings}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Drift Events</span>
                <span className="text-sm text-gray-300">{alerts.drift_events}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Memory Poisoned</span>
                <span className="text-sm text-gray-300">{alerts.memory_poisoned}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Replay Unchained</span>
                <span className="text-sm text-gray-300">{alerts.replay_unchained}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Governance Alerts</span>
                <span className="text-sm text-gray-300">{alerts.governance_alerts}</span>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Providers */}
      {data?.providers && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">LLM Providers</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.entries(data.providers).map(([name, info]) => (
              <div key={name} className="flex items-center justify-between bg-gray-800/50 rounded px-3 py-2">
                <span className="text-sm text-gray-300 capitalize">{name}</span>
                <StatusChip status={info.status === 'configured' ? 'verified' : 'pending'} />
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recent Events */}
      {data?.recent_events && data.recent_events.length > 0 && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Recent Events</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.recent_events.map(event => (
              <div
                key={event.id}
                className={`flex items-start gap-3 p-2 rounded text-xs ${
                  event.severity === 'critical' ? 'bg-red-950/30 border-l-2 border-red-500' :
                  event.severity === 'error' ? 'bg-red-950/20 border-l-2 border-red-400' :
                  event.severity === 'warning' ? 'bg-yellow-950/20 border-l-2 border-yellow-400' :
                  'bg-gray-800/30 border-l-2 border-gray-600'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <StatusChip status={mapSeverityToStatus(event.severity)} size="sm" />
                    <span className="text-gray-400 truncate">{event.message}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-[10px] text-gray-500">
                    <span>{formatTimestamp(event.timestamp)}</span>
                    {event.run_id && <span>Run: {event.run_id.slice(0, 8)}...</span>}
                    <span>Source: {event.source}</span>
                    {event.requires_operator_action && (
                      <span className="text-yellow-400 font-semibold">⚠ REQUIRES ACTION</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {data?.recent_events && data.recent_events.length === 0 && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Recent Events</h3>
          <p className="text-xs text-gray-500">No recent events. This may indicate no runtime activity or no log events recorded yet.</p>
        </Card>
      )}
    </div>
  );
}
