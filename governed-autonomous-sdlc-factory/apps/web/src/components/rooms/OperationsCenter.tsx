'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
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

type ConnectionState = 'connected' | 'reconnecting' | 'disconnected' | 'error';

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
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [liveEvents, setLiveEvents] = useState<OperationEvent[]>([]);
  const [eventCount, setEventCount] = useState(0);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ── Fetch summary (polling fallback) ────────────────────────────────────
  const fetchSummary = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token') || '';
      const resp = await fetch('/api/v1/operations/summary', {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: AbortSignal.timeout(10000),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
      const json: OperationsSummary = await resp.json();
      setData(json);
      setDataSource('live');
      setError(null);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e: any) {
      setError(e.message || 'Failed to fetch operations summary');
      if (!data) setDataSource('error');
    } finally {
      setLoading(false);
    }
  }, [data]);

  // ── SSE Connection ──────────────────────────────────────────────────────
  const connectSSE = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setConnectionState('reconnecting');
    const token = localStorage.getItem('auth_token') || '';

    const es = new EventSource(`/api/v1/operations/events/stream?token=${encodeURIComponent(token)}`);
    eventSourceRef.current = es;

    es.onopen = () => {
      setConnectionState('connected');
    };

    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.event_type === 'KEEPALIVE' || parsed.event_type === 'connected') return;

        const newEvent: OperationEvent = {
          id: parsed.id,
          timestamp: parsed.timestamp,
          run_id: parsed.run_id,
          event_type: parsed.event_type,
          severity: parsed.severity,
          source: parsed.source,
          message: parsed.message,
          trust_impact: parsed.trust_impact || 0,
          requires_operator_action: parsed.requires_operator_action || false,
        };

        setLiveEvents(prev => [newEvent, ...prev].slice(0, 100));
        setEventCount(prev => prev + 1);
        setDataSource('live');
      } catch {
        // Ignore parse errors
      }
    };

    es.onerror = () => {
      setConnectionState('disconnected');
      es.close();
      eventSourceRef.current = null;

      // Auto-reconnect after 5s
      reconnectTimeoutRef.current = setTimeout(() => {
        connectSSE();
      }, 5000);
    };
  }, []);

  // ── Initial load + SSE connect ──────────────────────────────────────────
  useEffect(() => {
    fetchSummary();
    connectSSE();

    // Polling fallback every 30s
    const pollInterval = setInterval(fetchSummary, 30000);

    return () => {
      clearInterval(pollInterval);
      if (eventSourceRef.current) eventSourceRef.current.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Render ──────────────────────────────────────────────────────────────
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
            <button onClick={fetchSummary} className="mt-3 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded">
              Retry
            </button>
          </div>
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
          {/* Connection state indicator */}
          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-semibold uppercase tracking-wider border ${
            connectionState === 'connected' ? 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20' :
            connectionState === 'reconnecting' ? 'bg-amber-400/10 text-amber-400 border-amber-400/20' :
            'bg-red-400/10 text-red-400 border-red-400/20'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              connectionState === 'connected' ? 'bg-emerald-400' :
              connectionState === 'reconnecting' ? 'bg-amber-400 animate-pulse' :
              'bg-red-400'
            }`} />
            {connectionState}
          </span>
          <DataSourceBadge state={dataSource === 'live' ? 'LIVE' : dataSource === 'error' ? 'ERROR' : 'PARTIAL'} />
          <button onClick={fetchSummary} className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded">
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
                <span className={`text-sm font-bold ${alerts.total_critical > 0 ? 'text-red-400' : 'text-gray-500'}`}>{alerts.total_critical}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Warnings</span>
                <span className={`text-sm font-bold ${alerts.total_warnings > 0 ? 'text-yellow-400' : 'text-gray-500'}`}>{alerts.total_warnings}</span>
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

      {/* Live Event Stream */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Live Event Stream</h3>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-500">{eventCount} events received</span>
            {connectionState === 'connected' && (
              <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                LIVE
              </span>
            )}
          </div>
        </div>

        {liveEvents.length > 0 ? (
          <div className="space-y-1.5 max-h-80 overflow-y-auto">
            {liveEvents.slice(0, 50).map(event => (
              <div
                key={event.id}
                className={`flex items-start gap-2 p-2 rounded text-xs ${
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
                    <span>{event.source}</span>
                    {event.requires_operator_action && (
                      <span className="text-yellow-400 font-semibold">⚠ ACTION</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-xs text-gray-500">
              {connectionState === 'connected'
                ? 'Waiting for events...'
                : connectionState === 'reconnecting'
                ? 'Reconnecting to event stream...'
                : 'Stream disconnected. Events will appear when connection is restored.'}
            </p>
          </div>
        )}
      </Card>
    </div>
  );
}
