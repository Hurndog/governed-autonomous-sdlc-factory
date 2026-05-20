'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { StatusChip } from '@/components/ui/StatusChip';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { DataSourceBadge } from '@/components/ui/DataSourceBadge';

// ── Types ──────────────────────────────────────────────────────────────────

interface RunOption {
  id: string;
  name: string;
  status: string;
}

interface RuntimeExplanation {
  run_id: string;
  generated_at: string;
  run_info: any;
  timeline: any[];
  trust_evolution: any[];
  drift_lineage: any[];
  governance_narrative: any[];
  replay_integrity: any;
  memory_lifecycle: any[];
  interventions: any[];
  autonomy_transitions: any[];
  causal_chains: any[];
  overall_assessment: any;
  recommendations: string[];
  uncertainty_disclosures: string[];
}

// ── Main Component ─────────────────────────────────────────────────────────

export function ExplainabilityRoom() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [explanation, setExplanation] = useState<RuntimeExplanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('timeline');

  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') || '' : '';

  // ── Fetch runs ──────────────────────────────────────────────────────────
  useEffect(() => {
    fetch('/api/v1/runs?limit=50', {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(json => {
        const runList = Array.isArray(json) ? json : json.runs || json.data || [];
        setRuns(runList.map((r: any) => ({ id: r.id, name: r.name || r.id, status: r.status })));
      })
      .catch(() => {});
  }, [token]);

  // ── Fetch explanation ───────────────────────────────────────────────────
  const fetchExplanation = useCallback(async (runId: string) => {
    if (!runId) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`/api/v1/explain/runtime/${runId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json: RuntimeExplanation = await resp.json();
      setExplanation(json);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch explanation');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (selectedRunId) fetchExplanation(selectedRunId);
  }, [selectedRunId, fetchExplanation]);

  const tabs = [
    { id: 'timeline', label: 'Cognitive Timeline' },
    { id: 'trust', label: 'Trust Evolution' },
    { id: 'drift', label: 'Drift Lineage' },
    { id: 'governance', label: 'Governance' },
    { id: 'replay', label: 'Replay Integrity' },
    { id: 'memory', label: 'Memory Lifecycle' },
    { id: 'interventions', label: 'Interventions' },
    { id: 'autonomy', label: 'Autonomy' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <SectionHeader
          title="Runtime Explainability"
          subtitle="Forensic cognitive runtime reconstruction. All explanations grounded in evidence."
        />
        <DataSourceBadge state={explanation ? 'LIVE' : 'PARTIAL'} />
      </div>

      {/* Run Selector */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Select Run</h3>
        <div className="flex items-center gap-3">
          <select
            value={selectedRunId}
            onChange={e => setSelectedRunId(e.target.value)}
            className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200"
          >
            <option value="">-- Select a run to explain --</option>
            {runs.map(run => (
              <option key={run.id} value={run.id}>{run.name} ({run.status})</option>
            ))}
          </select>
          {loading && <span className="text-xs text-gray-500">Loading...</span>}
        </div>
        {runs.length === 0 && <p className="text-xs text-gray-500 mt-2">No runs available.</p>}
      </Card>

      {error && (
        <Card className="border-red-500/30 bg-red-950/20">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Overall Assessment */}
      {explanation && (
        <Card className={`border-l-4 ${
          explanation.overall_assessment?.status === 'critical' ? 'border-red-500 bg-red-950/10' :
          explanation.overall_assessment?.status === 'degraded' ? 'border-amber-500 bg-amber-950/10' :
          'border-emerald-500 bg-emerald-950/10'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-200">Overall Assessment</h3>
            <StatusChip status={
              explanation.overall_assessment?.status === 'critical' ? 'error' :
              explanation.overall_assessment?.status === 'degraded' ? 'warning' : 'verified'
            } />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div><span className="text-gray-500">Events:</span> <span className="text-gray-300">{explanation.overall_assessment?.total_events || 0}</span></div>
            <div><span className="text-gray-500">Drift Events:</span> <span className="text-gray-300">{explanation.overall_assessment?.total_drift_events || 0}</span></div>
            <div><span className="text-gray-500">Interventions:</span> <span className="text-gray-300">{explanation.overall_assessment?.total_interventions || 0}</span></div>
            <div><span className="text-gray-500">Replay Integrity:</span> <span className="text-gray-300">{explanation.overall_assessment?.replay_integrity_pct || 0}%</span></div>
          </div>
        </Card>
      )}

      {/* Tabs */}
      {explanation && (
        <>
          <div className="flex items-center gap-1 overflow-x-auto pb-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 text-xs rounded font-medium whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Timeline Tab */}
          {activeTab === 'timeline' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Cognitive Timeline</h3>
              {explanation.timeline.length > 0 ? (
                <div className="space-y-1.5 max-h-96 overflow-y-auto">
                  {explanation.timeline.map((evt: any, i: number) => (
                    <div key={i} className={`flex items-start gap-2 p-2 rounded text-xs ${
                      evt.severity === 'critical' ? 'bg-red-950/30 border-l-2 border-red-500' :
                      evt.severity === 'error' ? 'bg-red-950/20 border-l-2 border-red-400' :
                      evt.severity === 'warning' ? 'bg-yellow-950/20 border-l-2 border-yellow-400' :
                      'bg-gray-800/30 border-l-2 border-gray-600'
                    }`}>
                      <StatusChip status={evt.severity === 'critical' || evt.severity === 'error' ? 'error' : evt.severity === 'warning' ? 'warning' : 'verified'} size="sm" />
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-300 truncate">{evt.description}</p>
                        <p className="text-[10px] text-gray-500">{evt.timestamp?.slice(0, 19).replace('T', ' ')}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No timeline events recorded.</p>
              )}
            </Card>
          )}

          {/* Trust Tab */}
          {activeTab === 'trust' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Trust Evolution</h3>
              {explanation.trust_evolution.length > 0 ? (
                <div className="space-y-2">
                  {explanation.trust_evolution.map((te: any, i: number) => (
                    <div key={i} className="flex items-center justify-between bg-gray-800/50 rounded p-2">
                      <div className="flex items-center gap-2">
                        <StatusChip status={te.trend === 'degrading' ? 'error' : te.trend === 'improving' ? 'verified' : 'pending'} size="sm" />
                        <span className="text-xs text-gray-300 font-mono">{te.dimension}</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs">
                        <span className="text-gray-500">{te.initial_score?.toFixed(2)}</span>
                        <span className="text-gray-600">→</span>
                        <span className={te.current_score < 0.5 ? 'text-red-400' : 'text-gray-300'}>{te.current_score?.toFixed(2)}</span>
                        <span className={`font-mono ${te.change < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                          {te.change > 0 ? '+' : ''}{te.change?.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No trust evolution data.</p>
              )}
            </Card>
          )}

          {/* Drift Tab */}
          {activeTab === 'drift' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Drift Lineage</h3>
              {explanation.drift_lineage.length > 0 ? (
                <div className="space-y-2">
                  {explanation.drift_lineage.map((d: any, i: number) => (
                    <div key={i} className="bg-gray-800/50 rounded p-2 text-xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <StatusChip status={d.severity === 'critical' ? 'error' : d.severity === 'warning' ? 'warning' : 'verified'} size="sm" />
                          <span className="text-gray-300">{d.drift_category} ({d.drift_type})</span>
                        </div>
                        <span className="text-gray-500">score: {d.drift_score?.toFixed(2)}</span>
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-[10px] text-gray-500">
                        <span>{d.detected_at?.slice(0, 19).replace('T', ' ')}</span>
                        {d.is_resolved ? <span className="text-emerald-400">RESOLVED</span> : <span className="text-amber-400">UNRESOLVED</span>}
                        {d.autonomy_impact && <span>Autonomy: {d.autonomy_impact}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No drift events recorded.</p>
              )}
            </Card>
          )}

          {/* Governance Tab */}
          {activeTab === 'governance' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Governance Decisions</h3>
              {explanation.governance_narrative.length > 0 ? (
                <div className="space-y-2">
                  {explanation.governance_narrative.map((g: any, i: number) => (
                    <div key={i} className="bg-gray-800/50 rounded p-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300 font-mono">{g.policy_name}</span>
                        <StatusChip status={g.decision === 'blocked' ? 'error' : g.decision === 'warning' ? 'warning' : 'verified'} size="sm" />
                      </div>
                      <p className="text-gray-500 mt-1">{g.evidence?.toString().slice(0, 200) || 'No evidence recorded'}</p>
                      <p className="text-[10px] text-gray-600 mt-1">{g.created_at?.slice(0, 19).replace('T', ' ')}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No governance decisions recorded.</p>
              )}
            </Card>
          )}

          {/* Replay Tab */}
          {activeTab === 'replay' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Replay Integrity</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                <div className="text-center">
                  <p className="text-lg font-bold text-gray-200">{explanation.replay_integrity?.total || 0}</p>
                  <p className="text-[10px] text-gray-500">Total Events</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-emerald-400">{explanation.replay_integrity?.chained || 0}</p>
                  <p className="text-[10px] text-gray-500">Chained</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-red-400">{explanation.replay_integrity?.unchained || 0}</p>
                  <p className="text-[10px] text-gray-500">Unchained</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-gray-200">{explanation.replay_integrity?.integrity_pct || 0}%</p>
                  <p className="text-[10px] text-gray-500">Integrity</p>
                </div>
              </div>
              {explanation.replay_integrity?.chain_breaks?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-400 mb-1">Chain Breaks:</p>
                  {explanation.replay_integrity.chain_breaks.slice(0, 10).map((cb: any, i: number) => (
                    <div key={i} className="text-[10px] text-red-400 font-mono bg-red-950/20 rounded px-2 py-1 mt-1">
                      {cb.id?.slice(0, 12)}... — {cb.path}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* Memory Tab */}
          {activeTab === 'memory' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Memory Lifecycle</h3>
              {explanation.memory_lifecycle.length > 0 ? (
                <div className="space-y-1.5 max-h-80 overflow-y-auto">
                  {explanation.memory_lifecycle.slice(0, 30).map((m: any, i: number) => (
                    <div key={i} className="flex items-center justify-between bg-gray-800/30 rounded px-2 py-1.5 text-xs">
                      <div className="flex items-center gap-2">
                        <StatusChip status={m.is_active ? 'verified' : 'pending'} size="sm" />
                        <span className="text-gray-400 font-mono">{m.memory_type}</span>
                        <span className="text-gray-600">{m.lifecycle_state}</span>
                      </div>
                      <div className="flex items-center gap-3 text-[10px] text-gray-500">
                        <span>drift: {m.drift_score?.toFixed(2)}</span>
                        <span>conf: {m.confidence?.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No memory lifecycle data.</p>
              )}
            </Card>
          )}

          {/* Interventions Tab */}
          {activeTab === 'interventions' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Interventions</h3>
              {explanation.interventions.length > 0 ? (
                <div className="space-y-2">
                  {explanation.interventions.map((iv: any, i: number) => (
                    <div key={i} className="bg-gray-800/50 rounded p-2 text-xs">
                      <div className="flex items-center justify-between">
                        <StatusChip status={iv.intervention_type === 'INVALIDATE_REPLAY' ? 'error' : 'warning'} size="sm" />
                        <span className="text-gray-500">{iv.created_at?.slice(0, 19).replace('T', ' ')}</span>
                      </div>
                      <p className="text-gray-300 mt-1">{iv.correction}</p>
                      <p className="text-[10px] text-gray-500 mt-1">By: {iv.operator_id?.slice(0, 12)}...</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No operator interventions recorded.</p>
              )}
            </Card>
          )}

          {/* Autonomy Tab */}
          {activeTab === 'autonomy' && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Autonomy Transitions</h3>
              {explanation.autonomy_transitions.length > 0 ? (
                <div className="space-y-2">
                  {explanation.autonomy_transitions.map((at: any, i: number) => (
                    <div key={i} className="flex items-center justify-between bg-gray-800/50 rounded p-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">{at.from_level || 'unknown'}</span>
                        <span className="text-gray-600">→</span>
                        <StatusChip status={at.to_level === 'full' ? 'verified' : at.to_level === 'reduced' ? 'warning' : 'error'} size="sm" />
                        <span className="text-gray-300">{at.to_level}</span>
                      </div>
                      <span className="text-[10px] text-gray-500">{at.updated_at?.slice(0, 19).replace('T', ' ')}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No autonomy transitions recorded.</p>
              )}
            </Card>
          )}

          {/* Recommendations */}
          {explanation.recommendations.length > 0 && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Recommendations</h3>
              <div className="space-y-1">
                {explanation.recommendations.map((rec: string, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <span className="text-blue-400 mt-0.5">→</span>
                    <span className="text-gray-300">{rec}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Uncertainty Disclosures */}
          {explanation.uncertainty_disclosures.length > 0 && (
            <Card className="border-amber-500/20 bg-amber-950/10">
              <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-3">⚠ Uncertainty Disclosures</h3>
              <div className="space-y-1">
                {explanation.uncertainty_disclosures.map((disc: string, i: number) => (
                  <p key={i} className="text-xs text-amber-300/80">{disc}</p>
                ))}
              </div>
            </Card>
          )}

          {/* Causal Chains */}
          {explanation.causal_chains.length > 0 && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Causal Chains</h3>
              <div className="space-y-2">
                {explanation.causal_chains.map((chain: any, i: number) => (
                  <div key={i} className="bg-gray-800/50 rounded p-2 text-xs">
                    <div className="flex items-center gap-2 mb-1">
                      <StatusChip status={chain.type === 'operator_intervention' ? 'warning' : 'error'} size="sm" />
                      <span className="text-gray-300 font-mono">{chain.type}</span>
                    </div>
                    <p className="text-gray-400">{chain.root_cause}</p>
                    {chain.propagated_to?.length > 0 && (
                      <div className="mt-1 ml-3 border-l-2 border-gray-600 pl-2">
                        {chain.propagated_to.map((p: string, j: number) => (
                          <p key={j} className="text-[10px] text-gray-500">→ {p}</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}

      {!explanation && !loading && selectedRunId && (
        <Card>
          <p className="text-xs text-gray-500">Select a run to view its explanation.</p>
        </Card>
      )}
    </div>
  );
}
