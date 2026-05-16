'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Card, Badge, Metric, StatusDot, ProgressBar, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Activity,
  Cpu,
  Database,
  Shield,
  RotateCcw,
  Zap,
  DollarSign,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  Play,
  FileText,
  Network,
  RefreshCw,
} from 'lucide-react';

export function CommandCenter() {
  const health = useStore((s) => s.health);
  const setHealth = useStore((s) => s.setHealth);
  const runs = useStore((s) => s.runs);
  const setRuns = useStore((s) => s.setRuns);
  const modelStatus = useStore((s) => s.modelStatus);
  const setModelStatus = useStore((s) => s.setModelStatus);
  const setLastError = useStore((s) => s.setLastError);

  const [intent, setIntent] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    setRefreshing(true);
    try {
      const [h, m, r] = await Promise.allSettled([
        api.getHealth(),
        api.getModelStatus(),
        api.listRuns({ page_size: 10 }),
      ]);
      if (h.status === 'fulfilled') setHealth(h.value as any);
      if (m.status === 'fulfilled') setModelStatus(m.value as any);
      if (r.status === 'fulfilled') setRuns((r.value as any).items || (r.value as any).runs || []);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setRefreshing(false);
    }
  }, [setHealth, setModelStatus, setRuns, setLastError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleLaunchPipeline = async () => {
    if (!intent.trim()) return;
    setLoading(true);
    setLastResult(null);
    try {
      const result = await api.runFullPipeline({
        intent: intent.trim(),
        project_name: projectName || undefined,
      });
      setLastResult(JSON.stringify(result, null, 2));
      setIntent('');
      setProjectName('');
      // Refresh runs
      const r = await api.listRuns({ page_size: 10 });
      setRuns((r as any).items || (r as any).runs || []);
    } catch (e: any) {
      setLastResult(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const providers = modelStatus?.providers || [];
  const routingPolicy = modelStatus?.routing_policy || {};
  const activeRuns = runs.filter((r) => r.status === 'running');
  const goldenRun = runs.find((r) => r.id === '6a7f7ea0-297f-435e-9bb2-899368c7d332');

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            COMMAND CENTER
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Cognitive Operations Overview — Real-time Factory Telemetry
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={refreshing}
            className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 border border-zinc-700 rounded-md text-zinc-400 text-xs font-mono hover:bg-zinc-800 transition-colors"
          >
            {refreshing ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
            Refresh
          </button>
          <Badge variant={health?.status === 'ok' ? 'emerald' : 'red'}>
            <StatusDot status={health?.status === 'ok' ? 'healthy' : 'critical'} size="sm" pulse />
            <span className="ml-1.5">{(health?.status || 'UNKNOWN').toUpperCase()}</span>
          </Badge>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-6 gap-4">
        <Card>
          <Metric
            label="Active Runs"
            value={activeRuns.length}
            sub={`${runs.length} total`}
            color="text-emerald-400"
          />
        </Card>
        <Card>
          <Metric
            label="Models Online"
            value={providers.filter((p: any) => p.status === 'online').length}
            sub={`${providers.length} configured`}
            color="text-emerald-400"
          />
        </Card>
        <Card>
          <Metric
            label="Golden Run"
            value={goldenRun ? (goldenRun.integrity_score?.toFixed(2) || '—') : '—'}
            sub={goldenRun ? goldenRun.status : 'Not found'}
            color={goldenRun?.integrity_score === 1.0 ? 'text-emerald-400' : 'text-zinc-200'}
          />
        </Card>
        <Card>
          <Metric
            label="Uptime"
            value={health?.uptime_seconds ? `${Math.floor(health.uptime_seconds / 3600)}h ${Math.floor((health.uptime_seconds % 3600) / 60)}m` : '—'}
            sub={`v${health?.version || '—'}`}
            color="text-zinc-200"
          />
        </Card>
        <Card>
          <Metric
            label="Database"
            value={health?.database === 'connected' ? 'OK' : 'Error'}
            sub={health?.redis === 'connected' ? 'Redis OK' : 'Redis ?'}
            color={health?.database === 'connected' ? 'text-emerald-400' : 'text-red-400'}
          />
        </Card>
        <Card>
          <Metric
            label="Cost"
            value="$0.0000"
            sub="Local inference"
            color="text-emerald-400"
          />
        </Card>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Intent Input + Generation */}
        <Card className="col-span-2" glow="emerald">
          <SectionHeader
            title="Cognitive Intent"
            subtitle="Describe what you want to build"
            icon={<Zap className="w-4 h-4" />}
          />
          <div className="space-y-3">
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Project name (optional)"
              className="w-full bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
            />
            <textarea
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              placeholder="E.g., Build a REST API for managing tasks with authentication, rate limiting, and audit logging..."
              className="w-full h-24 bg-zinc-900/50 border border-zinc-800 rounded-md p-3 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 resize-none"
            />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="zinc">Full Pipeline</Badge>
                <Badge variant="zinc">Spec → Arch → Gov → Tests</Badge>
              </div>
              <button
                onClick={handleLaunchPipeline}
                disabled={loading || !intent.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5" />
                )}
                {loading ? 'Launching...' : 'Launch Pipeline'}
              </button>
            </div>
            {lastResult && (
              <div className="mt-3 p-3 bg-zinc-900/80 border border-zinc-800 rounded-md max-h-48 overflow-y-auto">
                <pre className="text-[10px] font-mono text-zinc-400 whitespace-pre-wrap">
                  {lastResult}
                </pre>
              </div>
            )}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card>
          <SectionHeader title="Quick Actions" subtitle="Common operations" icon={<Activity className="w-4 h-4" />}
          />
          <div className="space-y-2">
            {[
              { label: 'Verify Golden Run', icon: Shield, color: 'emerald', action: 'integrity-room' },
              { label: 'View Traceability', icon: Network, color: 'blue', action: 'traceability-room' },
              { label: 'Browse Artifacts', icon: FileText, color: 'zinc', action: 'artifact-explorer' },
              { label: 'View Evidence', icon: FileText, color: 'zinc', action: 'evidence-center' },
              { label: 'Provider Status', icon: Cpu, color: 'zinc', action: 'settings-providers' },
            ].map((action) => (
              <button
                key={action.label}
                onClick={() => useStore.getState().setActiveRoom(action.action)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 transition-colors text-left"
              >
                <action.icon className="w-4 h-4 text-zinc-600" />
                <span className="text-[11px] font-mono">{action.label}</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* System Health + Model Router */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <SectionHeader
            title="System Health"
            subtitle="Runtime diagnostics"
            icon={<Database className="w-4 h-4" />}
          />
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'API', value: health?.status || 'unknown' },
              { label: 'Database', value: health?.database || 'unknown' },
              { label: 'Redis', value: health?.redis || 'unknown' },
            ].map(({ label, value }) => (
              <div
                key={label}
                className="flex items-center gap-2 px-2 py-1.5 bg-zinc-900/50 rounded border border-zinc-800/50"
              >
                <StatusDot
                  status={value === 'connected' || value === 'ok' ? 'healthy' : value === 'degraded' ? 'degraded' : 'critical'}
                  size="sm"
                />
                <span className="text-[10px] font-mono text-zinc-500 uppercase">{label}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <SectionHeader
            title="Model Router"
            subtitle="Provider status"
            icon={<Cpu className="w-4 h-4" />}
          />
          <div className="space-y-2">
            {providers.length === 0 ? (
              <p className="text-[10px] font-mono text-zinc-600">No provider data — click Refresh</p>
            ) : (
              providers.map((provider: any) => (
                <div
                  key={provider.name}
                  className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50"
                >
                  <div className="flex items-center gap-2">
                    <StatusDot status={provider.status === 'online' ? 'healthy' : 'inactive'} size="sm" pulse={provider.status === 'online'} />
                    <span className="text-[11px] font-mono text-zinc-300">{provider.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={provider.status === 'online' ? 'emerald' : 'zinc'} size="sm">
                      {provider.models?.length || 0} models
                    </Badge>
                    <span className="text-[10px] font-mono text-zinc-600">{provider.base_url}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Active Runs */}
      <Card>
        <SectionHeader
          title="Recent Runs"
          subtitle="SDLC execution status"
          icon={<Activity className="w-4 h-4" />}
        />
        {runs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-600">
            <Activity className="w-8 h-8 mb-3 opacity-30" />
            <p className="text-xs font-mono">No runs loaded</p>
            <p className="text-[10px] font-mono mt-1">Click Refresh or launch a pipeline</p>
          </div>
        ) : (
          <div className="space-y-2">
            {runs.slice(0, 10).map((r) => (
              <div
                key={r.id}
                className="flex items-center gap-4 px-4 py-3 bg-zinc-900/50 rounded border border-zinc-800/50"
              >
                <StatusDot status={r.status === 'running' ? 'running' : r.status === 'completed' ? 'completed' : r.status === 'failed' ? 'failed' : 'pending'} size="md" pulse={r.status === 'running'} />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-zinc-200">{r.intent || r.id.slice(0, 24)}</span>
                    <Badge
                      variant={
                        r.status === 'running'
                          ? 'emerald'
                          : r.status === 'completed'
                          ? 'emerald'
                          : r.status === 'failed'
                          ? 'red'
                          : 'amber'
                      }
                    >
                      {r.status}
                    </Badge>
                    {r.id === '6a7f7ea0-297f-435e-9bb2-899368c7d332' && (
                      <Badge variant="emerald" size="sm">GOLDEN</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-[9px] font-mono text-zinc-600">{new Date(r.created_at).toLocaleString()}</span>
                    {r.model_provider && <span className="text-[9px] font-mono text-zinc-600">{r.model_provider}</span>}
                    {r.integrity_score !== undefined && <span className="text-[9px] font-mono text-zinc-600">Integrity: {r.integrity_score.toFixed(2)}</span>}
                  </div>
                </div>
                <span className="text-[10px] font-mono text-zinc-600">{r.event_count || 0} events</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
