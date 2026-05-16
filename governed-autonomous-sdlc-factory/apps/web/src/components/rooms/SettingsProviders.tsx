'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Settings,
  Cpu,
  Wifi,
  WifiOff,
  Key,
  Shield,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from 'lucide-react';

export function SettingsProviders() {
  const modelStatus = useStore((s) => s.modelStatus);
  const setModelStatus = useStore((s) => s.setModelStatus);
  const health = useStore((s) => s.health);
  const setHealth = useStore((s) => s.setHealth);
  const setLastError = useStore((s) => s.setLastError);

  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState<Array<{ key: string; value: string; value_type: string }>>([]);
  const [githubStatus, setGithubStatus] = useState<{ configured: boolean; token_valid: boolean; error?: string } | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setLastError(null);
    try {
      const [ms, h, s, gs] = await Promise.allSettled([
        api.getModelStatus(),
        api.getHealth(),
        api.getSettings(),
        api.getGithubStatus(),
      ]);
      if (ms.status === 'fulfilled') setModelStatus(ms.value as any);
      if (h.status === 'fulfilled') setHealth(h.value as any);
      if (s.status === 'fulfilled') setSettings((s.value as any).settings || []);
      if (gs.status === 'fulfilled') setGithubStatus(gs.value as any);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [setModelStatus, setHealth, setLastError]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const providers = modelStatus?.providers || [];
  const routingPolicy = modelStatus?.routing_policy || {};

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            SETTINGS & PROVIDERS
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Model Providers — Routing Policy — System Configuration
          </p>
        </div>
        <button
          onClick={loadAll}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 border border-zinc-700 rounded-md text-zinc-400 text-xs font-mono hover:bg-zinc-800 transition-colors disabled:opacity-30"
        >
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
          Refresh
        </button>
      </div>

      {/* Runtime Health */}
      <Card>
        <SectionHeader title="Runtime Health" subtitle="System status" icon={<Shield className="w-4 h-4" />} />
        <div className="grid grid-cols-4 gap-3">
          <div className="flex items-center gap-2 px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
            <StatusDot status={health?.status === 'ok' ? 'healthy' : 'critical'} size="sm" />
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
            <StatusDot status={health?.database === 'connected' ? 'healthy' : 'critical'} size="sm" />
            <span className="text-[10px] font-mono text-zinc-400">Database</span>
            <span className="text-[10px] font-mono text-zinc-200 ml-auto">{health?.database || 'unknown'}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
            <StatusDot status={health?.redis === 'connected' ? 'healthy' : 'critical'} size="sm" />
            <span className="text-[10px] font-mono text-zinc-400">Redis</span>
            <span className="text-[10px] font-mono text-zinc-200 ml-auto">{health?.redis || 'unknown'}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
            <StatusDot status={githubStatus?.token_valid ? 'healthy' : 'inactive'} size="sm" />
            <span className="text-[10px] font-mono text-zinc-400">GitHub</span>
            <span className="text-[10px] font-mono text-zinc-200 ml-auto">{githubStatus?.token_valid ? 'Connected' : 'Not configured'}</span>
          </div>
        </div>
      </Card>

      {/* Model Providers */}
      <Card>
        <SectionHeader title="Model Providers" subtitle="Available LLM providers" icon={<Cpu className="w-4 h-4" />} />
        {providers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-zinc-600">
            <Cpu className="w-8 h-8 mb-2 opacity-20" />
            <p className="text-xs font-mono">No provider data</p>
            <p className="text-[10px] font-mono mt-1">Click Refresh to load</p>
          </div>
        ) : (
          <div className="space-y-3">
            {providers.map((provider) => (
              <div key={provider.name} className="border border-zinc-800 rounded-md p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {provider.status === 'online' ? (
                      <Wifi className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-zinc-600" />
                    )}
                    <span className="text-sm font-mono text-zinc-200 font-semibold">{provider.name}</span>
                    <Badge variant={provider.status === 'online' ? 'emerald' : 'zinc'} size="sm">
                      {provider.status}
                    </Badge>
                    {provider.is_local && (
                      <Badge variant="blue" size="sm">Local</Badge>
                    )}
                  </div>
                  <span className="text-[10px] font-mono text-zinc-600">{provider.base_url}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {provider.models.map((model) => (
                    <div
                      key={model.name}
                      className="flex items-center gap-2 px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50"
                    >
                      <StatusDot status={model.available ? 'healthy' : 'inactive'} size="sm" />
                      <span className="text-[11px] font-mono text-zinc-300 flex-1">{model.name}</span>
                      {model.size && (
                        <span className="text-[9px] font-mono text-zinc-600">{model.size}</span>
                      )}
                    </div>
                  ))}
                </div>
                {provider.default_model && (
                  <div className="mt-2 text-[10px] font-mono text-zinc-600">
                    Default: <span className="text-zinc-400">{provider.default_model}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Routing Policy */}
      <Card>
        <SectionHeader title="Routing Policy" subtitle="Task-to-model routing" icon={<Settings className="w-4 h-4" />} />
        {Object.keys(routingPolicy).length === 0 ? (
          <p className="text-xs font-mono text-zinc-600">No routing policy loaded</p>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(routingPolicy).map(([task, model]) => (
              <div key={task} className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                <span className="text-[11px] font-mono text-zinc-400">{task}</span>
                <span className="text-[11px] font-mono text-zinc-200">{model as string}</span>
              </div>
            ))}
          </div>
        )}
        {modelStatus?.default_provider && (
          <div className="mt-3 text-[10px] font-mono text-zinc-600">
            Default: <span className="text-zinc-400">{modelStatus.default_provider}/{modelStatus.default_model}</span>
          </div>
        )}
      </Card>

      {/* API Keys (presence only) */}
      <Card>
        <SectionHeader title="API Keys" subtitle="Key presence (values never shown)" icon={<Key className="w-4 h-4" />} />
        <div className="grid grid-cols-2 gap-2">
          {[
            { key: 'OPENAI_API_KEY', label: 'OpenAI' },
            { key: 'ANTHROPIC_API_KEY', label: 'Anthropic' },
            { key: 'GITHUB_TOKEN', label: 'GitHub' },
          ].map(({ key, label }) => {
            const setting = settings.find((s) => s.key === key);
            const hasKey = setting && setting.value && setting.value.length > 0;
            return (
              <div key={key} className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50">
                <span className="text-[11px] font-mono text-zinc-400">{label}</span>
                {hasKey ? (
                  <Badge variant="emerald" size="sm">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Set
                  </Badge>
                ) : (
                  <Badge variant="zinc" size="sm">
                    <XCircle className="w-3 h-3 mr-1" />
                    Not set
                  </Badge>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* System Settings */}
      {settings.length > 0 && (
        <Card>
          <SectionHeader title="System Settings" subtitle="Runtime configuration" icon={<Settings className="w-4 h-4" />} />
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {settings
              .filter((s) => !s.key.includes('KEY') && !s.key.includes('TOKEN') && !s.key.includes('SECRET'))
              .map((s) => (
                <div key={s.key} className="flex items-center justify-between px-3 py-1.5 hover:bg-zinc-800/20">
                  <span className="text-[10px] font-mono text-zinc-500">{s.key}</span>
                  <span className="text-[10px] font-mono text-zinc-300">{s.value}</span>
                </div>
              ))}
          </div>
        </Card>
      )}
    </div>
  );
}
