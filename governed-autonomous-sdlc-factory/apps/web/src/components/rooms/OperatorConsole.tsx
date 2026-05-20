'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { StatusChip } from '@/components/ui/StatusChip';
import { SectionHeader } from '@/components/ui/SectionHeader';

// ── Types ──────────────────────────────────────────────────────────────────

interface Intervention {
  id: string;
  run_id: string | null;
  operator_id: string | null;
  intervention_type: string;
  correction: string;
  governance_impact: any;
  created_at: string | null;
}

interface RunOption {
  id: string;
  name: string;
  status: string;
}

// ── Intervention Actions ───────────────────────────────────────────────────

const INTERVENTION_ACTIONS = [
  { type: 'PAUSE', label: 'Pause Run', permission: 'operations.pause_run', severity: 'warning', description: 'Pause a running run' },
  { type: 'RESUME', label: 'Resume Run', permission: 'operations.resume_run', severity: 'info', description: 'Resume a paused run' },
  { type: 'QUARANTINE_MEMORY', label: 'Quarantine Memory', permission: 'operations.quarantine_memory', severity: 'warning', description: 'Quarantine memory items for a run' },
  { type: 'FORCE_VERIFIER', label: 'Force Verifier', permission: 'operations.force_verifier', severity: 'warning', description: 'Force a verifier review' },
  { type: 'REDUCE_AUTONOMY', label: 'Reduce Autonomy', permission: 'operations.reduce_autonomy', severity: 'warning', description: 'Reduce autonomy level' },
  { type: 'REQUEST_HUMAN_REVIEW', label: 'Request Human Review', permission: 'operations.request_human_review', severity: 'warning', description: 'Request human review for a run' },
  { type: 'INVALIDATE_REPLAY', label: 'Invalidate Replay', permission: 'operations.invalidate_replay', severity: 'error', description: 'Invalidate replay chain' },
  { type: 'LOCK_EVIDENCE', label: 'Lock Evidence', permission: 'operations.lock_evidence', severity: 'warning', description: 'Lock evidence for a run' },
];

// ── Main Component ─────────────────────────────────────────────────────────

export function OperatorConsole() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionReason, setActionReason] = useState<Record<string, string>>({});
  const [confirmAction, setConfirmAction] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<{ type: string; message: string; success: boolean } | null>(null);

  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') || '' : '';

  // ── Fetch runs ──────────────────────────────────────────────────────────
  const fetchRuns = useCallback(async () => {
    try {
      const resp = await fetch('/api/v1/runs?limit=50', {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: AbortSignal.timeout(10000),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json = await resp.json();
      const runList = Array.isArray(json) ? json : json.runs || json.data || [];
      setRuns(runList.map((r: any) => ({ id: r.id, name: r.name || r.id, status: r.status })));
    } catch (e: any) {
      // Silently fail — runs list is optional
    }
  }, [token]);

  // ── Fetch interventions ─────────────────────────────────────────────────
  const fetchInterventions = useCallback(async () => {
    try {
      const resp = await fetch('/api/v1/operations/interventions?limit=50', {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: AbortSignal.timeout(10000),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json = await resp.json();
      setInterventions(json.interventions || []);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch interventions');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchRuns();
    fetchInterventions();
  }, [fetchRuns, fetchInterventions]);

  // ── Execute intervention ────────────────────────────────────────────────
  const executeAction = async (actionType: string) => {
    if (!selectedRunId) {
      setActionResult({ type: actionType, message: 'Please select a run first', success: false });
      return;
    }

    const reason = actionReason[actionType] || 'No reason provided';
    if (reason.length < 3) {
      setActionResult({ type: actionType, message: 'Please provide a reason (min 3 characters)', success: false });
      return;
    }

    try {
      const resp = await fetch(`/api/v1/operations/runs/${selectedRunId}/${actionType.toLowerCase().replace('_', '-')}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (!resp.ok) {
        const errBody = await resp.json().catch(() => ({}));
        throw new Error(errBody.detail || `HTTP ${resp.status}`);
      }

      const result = await resp.json();
      setActionResult({ type: actionType, message: result.message || 'Action executed successfully', success: true });
      setActionReason(prev => ({ ...prev, [actionType]: '' }));
      setConfirmAction(null);
      fetchInterventions(); // Refresh history
    } catch (e: any) {
      setActionResult({ type: actionType, message: e.message || 'Action failed', success: false });
      setConfirmAction(null);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <SectionHeader title="Operator Console" subtitle="Loading..." />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {[1, 2].map(i => <Card key={i} className="h-32 animate-pulse bg-gray-800"><div /></Card>)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <SectionHeader
        title="Operator Console"
        subtitle="Intervene in runtime operations safely. All actions are audited."
      />

      {error && (
        <Card className="border-red-500/30 bg-red-950/20">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {actionResult && (
        <Card className={actionResult.success ? 'border-emerald-500/30 bg-emerald-950/20' : 'border-red-500/30 bg-red-950/20'}>
          <div className="flex items-center justify-between">
            <p className={`text-sm ${actionResult.success ? 'text-emerald-400' : 'text-red-400'}`}>
              {actionResult.message}
            </p>
            <button onClick={() => setActionResult(null)} className="text-xs text-gray-500 hover:text-gray-300">✕</button>
          </div>
        </Card>
      )}

      {/* Run Selector */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Select Run</h3>
        <select
          value={selectedRunId}
          onChange={e => setSelectedRunId(e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200"
        >
          <option value="">-- Select a run --</option>
          {runs.map(run => (
            <option key={run.id} value={run.id}>
              {run.name} ({run.status})
            </option>
          ))}
        </select>
        {runs.length === 0 && (
          <p className="text-xs text-gray-500 mt-2">No runs available. Runs will appear here when created.</p>
        )}
      </Card>

      {/* Intervention Actions */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Intervention Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {INTERVENTION_ACTIONS.map(action => (
            <div key={action.type} className="bg-gray-800/50 rounded p-3 border border-gray-700/50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-200">{action.label}</span>
                <StatusChip
                  status={action.severity === 'error' ? 'error' : action.severity === 'warning' ? 'warning' : 'verified'}
                  size="sm"
                />
              </div>
              <p className="text-[10px] text-gray-500 mb-2">{action.description}</p>

              {confirmAction === action.type ? (
                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Reason for intervention (required)"
                    value={actionReason[action.type] || ''}
                    onChange={e => setActionReason(prev => ({ ...prev, [action.type]: e.target.value }))}
                    className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1.5 text-xs text-gray-200 placeholder-gray-500"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => executeAction(action.type)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded font-semibold"
                    >
                      Confirm {action.label}
                    </button>
                    <button
                      onClick={() => setConfirmAction(null)}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmAction(action.type)}
                  disabled={!selectedRunId}
                  className={`px-3 py-1.5 text-xs rounded font-medium ${
                    selectedRunId
                      ? action.severity === 'error'
                        ? 'bg-red-600/20 text-red-400 hover:bg-red-600/30 border border-red-500/30'
                        : 'bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 border border-amber-500/30'
                      : 'bg-gray-700/50 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {selectedRunId ? 'Execute' : 'Select a run first'}
                </button>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Intervention History */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Intervention History</h3>
        {interventions.length > 0 ? (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {interventions.map(iv => (
              <div key={iv.id} className="flex items-start gap-3 p-2 rounded bg-gray-800/30 border-l-2 border-gray-600">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <StatusChip
                      status={iv.intervention_type === 'INVALIDATE_REPLAY' ? 'error' : 'warning'}
                      size="sm"
                    />
                    <span className="text-xs text-gray-300 font-mono">{iv.intervention_type}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{iv.correction}</p>
                  <div className="flex items-center gap-3 mt-1 text-[10px] text-gray-500">
                    <span>{iv.created_at ? new Date(iv.created_at).toLocaleString() : 'Unknown'}</span>
                    {iv.run_id && <span>Run: {iv.run_id.slice(0, 8)}...</span>}
                    <span>By: {iv.operator_id?.slice(0, 8) || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-gray-500">No interventions recorded yet.</p>
        )}
      </Card>
    </div>
  );
}
