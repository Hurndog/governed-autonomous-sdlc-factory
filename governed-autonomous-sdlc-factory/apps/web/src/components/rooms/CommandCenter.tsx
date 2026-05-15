'use client';

import React, { useState } from 'react';
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
} from 'lucide-react';

export function CommandCenter() {
  const health = useStore((s) => s.health);
  const pipelines = useStore((s) => s.pipelines);
  const modelStatuses = useStore((s) => s.modelStatuses);
  const [intent, setIntent] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!intent.trim()) return;
    setLoading(true);
    try {
      const result = await api.generateSpec(intent);
      setLastResult(JSON.stringify(result, null, 2));
    } catch (e: any) {
      setLastResult(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const checks = health?.checks || {};
  const checkEntries = Object.entries(checks) as [string, string][];

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
          <Badge variant={health?.status === 'healthy' ? 'emerald' : health?.status === 'degraded' ? 'amber' : 'red'}>
            <StatusDot status={health?.status || 'inactive'} size="sm" pulse />
            <span className="ml-1.5">{health?.status?.toUpperCase() || 'UNKNOWN'}</span>
          </Badge>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-6 gap-4">
        <Card>
          <Metric
            label="Active Pipelines"
            value={pipelines.filter((p) => p.status === 'running').length}
            sub={`${pipelines.length} total`}
            color="text-emerald-400"
          />
        </Card>
        <Card>
          <Metric
            label="Replay Sessions"
            value={useStore.getState().replaySessions.length}
            sub="Forensic ready"
            color="text-blue-400"
          />
        </Card>
        <Card>
          <Metric
            label="Governance Findings"
            value={useStore.getState().governanceFindings.length}
            sub="Active"
            color="text-amber-400"
          />
        </Card>
        <Card>
          <Metric
            label="Models Online"
            value={modelStatuses.filter((m) => m.available).length}
            sub={`${modelStatuses.length} configured`}
            color="text-emerald-400"
          />
        </Card>
        <Card>
          <Metric
            label="Total Tokens"
            value="2.3K"
            sub="This session"
            color="text-zinc-200"
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
            <textarea
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              placeholder="E.g., Build a REST API for managing tasks with authentication, rate limiting, and audit logging..."
              className="w-full h-28 bg-zinc-900/50 border border-zinc-800 rounded-md p-3 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 resize-none"
            />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="zinc">Ollama gpt-oss:20b</Badge>
                <Badge variant="zinc">Spec → Arch → Gov → Tests</Badge>
              </div>
              <button
                onClick={handleGenerate}
                disabled={loading || !intent.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5" />
                )}
                {loading ? 'Generating...' : 'Generate Specification'}
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
              { label: 'New Pipeline', icon: Play, color: 'emerald' },
              { label: 'Run Replay', icon: RotateCcw, color: 'blue' },
              { label: 'Governance Audit', icon: Shield, color: 'amber' },
              { label: 'Model Benchmark', icon: Cpu, color: 'zinc' },
              { label: 'Export Evidence', icon: FileText, color: 'zinc' },
            ].map((action) => (
              <button
                key={action.label}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 transition-colors text-left"
              >
                <action.icon className="w-4 h-4 text-zinc-600" />
                <span className="text-[11px] font-mono">{action.label}</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* System Health Grid */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <SectionHeader
            title="System Health"
            subtitle="Runtime diagnostics"
            icon={<Database className="w-4 h-4" />}
          />
          <div className="grid grid-cols-3 gap-2">
            {checkEntries.map(([key, value]) => (
              <div
                key={key}
                className="flex items-center gap-2 px-2 py-1.5 bg-zinc-900/50 rounded border border-zinc-800/50"
              >
                <StatusDot
                  status={value === 'pass' ? 'healthy' : value === 'warn' ? 'degraded' : 'critical'}
                  size="sm"
                />
                <span className="text-[10px] font-mono text-zinc-500 uppercase">
                  {key.replace(/_/g, ' ')}
                </span>
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
            <div className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
              <div className="flex items-center gap-2">
                <StatusDot status="healthy" size="sm" pulse />
                <span className="text-[11px] font-mono text-zinc-300">Ollama</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="emerald" size="sm">3 models</Badge>
                <span className="text-[10px] font-mono text-zinc-600">localhost:11434</span>
              </div>
            </div>
            <div className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
              <div className="flex items-center gap-2">
                <StatusDot status="inactive" size="sm" />
                <span className="text-[11px] font-mono text-zinc-300">LM Studio</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="zinc" size="sm">Server off</Badge>
                <span className="text-[10px] font-mono text-zinc-600">localhost:1234</span>
              </div>
            </div>
            <div className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
              <div className="flex items-center gap-2">
                <StatusDot status="inactive" size="sm" />
                <span className="text-[11px] font-mono text-zinc-300">OpenAI</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="zinc" size="sm">No key</Badge>
                <span className="text-[10px] font-mono text-zinc-600">api.openai.com</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Pipelines */}
      <Card>
        <SectionHeader
          title="Active Pipelines"
          subtitle="SDLC execution status"
          icon={<Activity className="w-4 h-4" />}
        />
        {pipelines.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-600">
            <Activity className="w-8 h-8 mb-3 opacity-30" />
            <p className="text-xs font-mono">No active pipelines</p>
            <p className="text-[10px] font-mono mt-1">Enter an intent above to begin</p>
          </div>
        ) : (
          <div className="space-y-2">
            {pipelines.map((p) => (
              <div
                key={p.id}
                className="flex items-center gap-4 px-4 py-3 bg-zinc-900/50 rounded border border-zinc-800/50"
              >
                <StatusDot status={p.status} size="md" pulse={p.status === 'running'} />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-zinc-200">{p.name}</span>
                    <Badge
                      variant={
                        p.status === 'running'
                          ? 'emerald'
                          : p.status === 'completed'
                          ? 'emerald'
                          : p.status === 'failed'
                          ? 'red'
                          : 'amber'
                      }
                    >
                      {p.status}
                    </Badge>
                  </div>
                  <ProgressBar value={p.progress} size="sm" showLabel />
                </div>
                <span className="text-[10px] font-mono text-zinc-600">{p.stage}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
