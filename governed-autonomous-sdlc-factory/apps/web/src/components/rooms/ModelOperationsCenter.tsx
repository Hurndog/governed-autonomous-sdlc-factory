'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { StatusChip } from '@/components/ui/StatusChip';
import { MetricCard } from '@/components/ui/MetricCard';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { DataSourceBadge } from '@/components/ui/DataSourceBadge';

// ── Types ──────────────────────────────────────────────────────────────────

interface ModelCapability {
  provider: string;
  model: string;
  coding_quality: number;
  reasoning_quality: number;
  governance_reliability: number;
  hallucination_risk: number;
  latency_score: number;
  cost_score: number;
  context_window: number;
  sovereignty_level: string;
  operator_trust: number;
  availability: number;
}

interface SovereigntyDashboard {
  summary: {
    total_models: number;
    local_only: number;
    sovereign_preferred: number;
    frontier_only: number;
    hybrid: number;
  };
  sovereignty_ratio: Record<string, number>;
  models: Record<string, Array<{ provider: string; model: string }>>;
  provider_concentration: { risk: string; providers: Record<string, number> };
}

// ── Main Component ─────────────────────────────────────────────────────────

export function ModelOperationsCenter() {
  const [capabilities, setCapabilities] = useState<ModelCapability[]>([]);
  const [sovereignty, setSovereignty] = useState<SovereigntyDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('models');

  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') || '' : '';

  const fetchData = useCallback(async () => {
    try {
      const [capResp, sovResp] = await Promise.all([
        fetch('/api/v1/models/capabilities', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/models/sovereignty', { headers: { 'Authorization': `Bearer ${token}` } }),
      ]);

      if (capResp.ok) {
        const capJson = await capResp.json();
        setCapabilities(capJson.models || []);
      }
      if (sovResp.ok) {
        const sovJson = await sovResp.json();
        setSovereignty(sovJson);
      }
      setError(null);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch model data');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="p-6">
        <SectionHeader title="Model Operations Center" subtitle="Loading model registry..." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {[1, 2, 3].map(i => <Card key={i} className="h-24 animate-pulse bg-gray-800"><div /></Card>)}
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'models', label: 'Active Models' },
    { id: 'sovereignty', label: 'Sovereignty' },
    { id: 'routing', label: 'Routing' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Model Operations Center"
          subtitle="Multi-model cognitive governance. Provider abstraction, capability registry, sovereignty-aware routing."
        />
        <DataSourceBadge state={capabilities.length > 0 ? 'LIVE' : 'PARTIAL'} />
      </div>

      {error && (
        <Card className="border-red-500/30 bg-red-950/20">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-1 overflow-x-auto pb-1">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 text-xs rounded font-medium whitespace-nowrap ${
              activeTab === tab.id ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Models Tab */}
      {activeTab === 'models' && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">
              Registered Models ({capabilities.length})
            </h3>
            {capabilities.length > 0 ? (
              <div className="space-y-2">
                {capabilities.map((cap, i) => (
                  <div key={i} className="bg-gray-800/50 rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-mono text-gray-200">{cap.provider}/{cap.model}</span>
                        <StatusChip
                          status={cap.sovereignty_level === 'local_only' ? 'verified' : cap.sovereignty_level === 'frontier_only' ? 'error' : 'warning'}
                          size="sm"
                        />
                        <span className="text-[10px] text-gray-500">{cap.sovereignty_level}</span>
                      </div>
                      <StatusChip status={cap.availability > 0.5 ? 'verified' : 'error'} size="sm" />
                    </div>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-2 text-[10px]">
                      <div><span className="text-gray-500">Coding:</span> <span className="text-gray-300">{cap.coding_quality.toFixed(2)}</span></div>
                      <div><span className="text-gray-500">Reasoning:</span> <span className="text-gray-300">{cap.reasoning_quality.toFixed(2)}</span></div>
                      <div><span className="text-gray-500">Gov:</span> <span className="text-gray-300">{cap.governance_reliability.toFixed(2)}</span></div>
                      <div><span className="text-gray-500">Hall.Risk:</span> <span className={cap.hallucination_risk > 0.3 ? 'text-amber-400' : 'text-gray-300'}>{cap.hallucination_risk.toFixed(2)}</span></div>
                      <div><span className="text-gray-500">Trust:</span> <span className="text-gray-300">{cap.operator_trust.toFixed(2)}</span></div>
                      <div><span className="text-gray-500">Ctx:</span> <span className="text-gray-300">{(cap.context_window / 1000).toFixed(0)}k</span></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No models registered.</p>
            )}
          </Card>
        </div>
      )}

      {/* Sovereignty Tab */}
      {activeTab === 'sovereignty' && sovereignty && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard label="Total Models" value={sovereignty.summary.total_models} />
            <MetricCard label="Local Only" value={sovereignty.summary.local_only} badge={{ label: 'Local', variant: 'green' }} />
            <MetricCard label="Sovereign" value={sovereignty.summary.sovereign_preferred} badge={{ label: 'Sovereign', variant: 'cyan' }} />
            <MetricCard label="Frontier" value={sovereignty.summary.frontier_only} badge={{ label: 'Frontier', variant: 'amber' }} />
            <MetricCard label="Hybrid" value={sovereignty.summary.hybrid} badge={{ label: 'Hybrid', variant: 'blue' }} />
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Sovereignty Ratio</h3>
            <div className="space-y-2">
              {Object.entries(sovereignty.sovereignty_ratio).map(([key, value]) => (
                <div key={key} className="flex items-center gap-3">
                  <span className="text-xs text-gray-400 w-20 capitalize">{key}</span>
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${key === 'local' ? 'bg-emerald-500' : key === 'sovereign' ? 'bg-cyan-500' : 'bg-amber-500'}`}
                      style={{ width: `${(value as number) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-300 w-12 text-right">{((value as number) * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Provider Concentration Risk</h3>
            <div className="flex items-center gap-2 mb-2">
              <StatusChip status={sovereignty.provider_concentration.risk === 'low' ? 'verified' : sovereignty.provider_concentration.risk === 'medium' ? 'warning' : 'error'} size="sm" />
              <span className="text-xs text-gray-400">Risk: {sovereignty.provider_concentration.risk}</span>
            </div>
            <div className="space-y-1">
              {Object.entries(sovereignty.provider_concentration.providers).map(([provider, ratio]) => (
                <div key={provider} className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{provider}</span>
                  <span className="text-gray-300">{((ratio as number) * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Routing Tab */}
      {activeTab === 'routing' && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Routing Configuration</h3>
          <div className="space-y-3 text-xs text-gray-400">
            <div className="bg-gray-800/50 rounded p-3">
              <p className="text-gray-300 font-semibold mb-1">Supported Task Types</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-1">
                {['code_generation', 'architecture_reasoning', 'governance_analysis', 'replay_analysis', 'semantic_evaluation', 'specification_generation', 'mutation_reasoning', 'drift_analysis', 'operator_explanation', 'memory_classification'].map(t => (
                  <span key={t} className="text-gray-500 font-mono">{t}</span>
                ))}
              </div>
            </div>
            <div className="bg-gray-800/50 rounded p-3">
              <p className="text-gray-300 font-semibold mb-1">Sovereignty Levels</p>
              <div className="grid grid-cols-2 gap-1">
                {['frontier_only', 'sovereign_preferred', 'sovereign_required', 'local_only', 'hybrid'].map(s => (
                  <span key={s} className="text-gray-500 font-mono">{s}</span>
                ))}
              </div>
            </div>
            <div className="bg-gray-800/50 rounded p-3">
              <p className="text-gray-300 font-semibold mb-1">Capability Dimensions</p>
              <div className="grid grid-cols-2 gap-1">
                {['coding_quality', 'reasoning_quality', 'governance_reliability', 'hallucination_risk', 'latency_score', 'cost_score', 'replay_stability', 'semantic_consistency', 'operator_trust'].map(d => (
                  <span key={d} className="text-gray-500 font-mono">{d}</span>
                ))}
              </div>
            </div>
            <p className="text-gray-500 mt-2">
              Use POST /api/v1/models/route with a RoutingRequest to get a model recommendation.
              Use POST /api/v1/models/arbitrate to run multi-model arbitration.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
