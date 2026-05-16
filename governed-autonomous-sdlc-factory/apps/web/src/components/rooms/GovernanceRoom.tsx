'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Lock,
  Eye,
  Scale,
  Clock,
  Loader2,
  Search,
} from 'lucide-react';

export function GovernanceRoom() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const governanceEvaluations = useStore((s) => s.governanceEvaluations);
  const setGovernanceEvaluations = useStore((s) => s.setGovernanceEvaluations);
  const governancePolicies = useStore((s) => s.governancePolicies);
  const setGovernancePolicies = useStore((s) => s.setGovernancePolicies);
  const releaseGates = useStore((s) => s.releaseGates);
  const setReleaseGates = useStore((s) => s.setReleaseGates);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [loading, setLoading] = useState(false);

  const handleLoad = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setLoading(true);
    setLastError(null);
    try {
      const [evals, policies] = await Promise.allSettled([
        api.getGovernanceEvaluations(runIdInput.trim()),
        api.getGovernancePolicies(true),
      ]);
      if (evals.status === 'fulfilled') setGovernanceEvaluations((evals.value as any).evaluations || []);
      if (policies.status === 'fulfilled') setGovernancePolicies((policies.value as any).policies || []);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setLoading(false);
    }
  }, [runIdInput, setGovernanceEvaluations, setGovernancePolicies, setLastError]);

  const criticalCount = governanceEvaluations.filter((f) => f.severity === 'critical' || f.status === 'fail').length;
  const warningCount = governanceEvaluations.filter((f) => f.severity === 'warning' || f.status === 'warn').length;
  const passCount = governanceEvaluations.filter((f) => f.status === 'pass').length;

  const severityIcon = (sev: string) => {
    switch (sev) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default: return <CheckCircle2 className="w-4 h-4 text-blue-400" />;
    }
  };

  const severityVariant = (sev: string) => {
    switch (sev) {
      case 'critical': return 'red';
      case 'warning': return 'amber';
      default: return 'blue';
    }
  };

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            GOVERNANCE ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Policy Evaluation — Release Gates — Compliance Status — Audit Traces
          </p>
        </div>
        <Badge variant={criticalCount > 0 ? 'red' : warningCount > 0 ? 'amber' : 'emerald'}>
          <Shield className="w-3 h-3 mr-1" />
          {criticalCount > 0 ? `${criticalCount} Critical` : warningCount > 0 ? `${warningCount} Warnings` : 'Compliant'}
        </Badge>
      </div>

      {/* Controls */}
      <Card glow="emerald">
        <SectionHeader title="Load Governance Data" subtitle="Enter run ID" icon={<Shield className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <button
            onClick={handleLoad}
            disabled={loading || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>
      </Card>

      {/* Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <Card glow={criticalCount > 0 ? 'red' : 'none'}>
          <Metric label="Critical" value={criticalCount} color={criticalCount > 0 ? 'text-red-400' : 'text-zinc-500'} />
        </Card>
        <Card glow={warningCount > 0 ? 'amber' : 'none'}>
          <Metric label="Warnings" value={warningCount} color={warningCount > 0 ? 'text-amber-400' : 'text-zinc-500'} />
        </Card>
        <Card>
          <Metric label="Passing" value={passCount} color="text-emerald-400" />
        </Card>
        <Card>
          <Metric label="Policies" value={governancePolicies.length} color="text-zinc-200" />
        </Card>
        <Card>
          <Metric label="Compliance" value={criticalCount === 0 ? 'PASS' : 'FAIL'} color={criticalCount === 0 ? 'text-emerald-400' : 'text-red-400'} />
        </Card>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Evaluations */}
        <Card className="col-span-2">
          <SectionHeader
            title="Governance Evaluations"
            subtitle={`${governanceEvaluations.length} evaluations`}
            icon={<Shield className="w-4 h-4" />}
          />
          {governanceEvaluations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
              <Shield className="w-10 h-10 mb-3 opacity-20" />
              <p className="text-xs font-mono">No governance evaluations loaded</p>
              <p className="text-[10px] font-mono mt-1">Enter a run ID and click Load</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {governanceEvaluations.map((ev) => (
                <div
                  key={ev.id}
                  className={`px-4 py-3 rounded-md border ${
                    ev.status === 'fail'
                      ? 'bg-red-500/5 border-red-500/20'
                      : ev.status === 'warn'
                      ? 'bg-amber-500/5 border-amber-500/20'
                      : 'bg-emerald-500/5 border-emerald-500/20'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {severityIcon(ev.severity)}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono text-zinc-200 font-semibold">
                          {ev.policy_name || ev.policy_id}
                        </span>
                        <div className="flex items-center gap-2">
                          <Badge variant={severityVariant(ev.severity) as any}>{ev.severity}</Badge>
                          <Badge variant={ev.status === 'pass' ? 'emerald' : ev.status === 'warn' ? 'amber' : 'red'}>{ev.status}</Badge>
                        </div>
                      </div>
                      {ev.findings && ev.findings.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {ev.findings.map((f, i) => (
                            <div key={i} className="text-[10px] font-mono text-zinc-500 flex items-center gap-2">
                              <span className="text-zinc-600">•</span>
                              <span>{f.message || f.type}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      {ev.integrity_hash && (
                        <div className="mt-2 text-[9px] font-mono text-zinc-700">
                          Hash: {ev.integrity_hash.slice(0, 16)}...
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Policies */}
          <Card>
            <SectionHeader title="Policies" icon={<Scale className="w-4 h-4" />} />
            {governancePolicies.length === 0 ? (
              <p className="text-[10px] font-mono text-zinc-600">No policies loaded</p>
            ) : (
              <div className="space-y-2">
                {governancePolicies.map((policy) => (
                  <div
                    key={policy.id}
                    className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50"
                  >
                    <span className="text-[11px] font-mono text-zinc-300">{policy.name}</span>
                    <Badge variant={policy.active ? 'emerald' : 'zinc'} size="sm">
                      {policy.active ? 'active' : 'inactive'}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Release Gates */}
          <Card>
            <SectionHeader title="Release Gates" icon={<Lock className="w-4 h-4" />} />
            {releaseGates.length === 0 ? (
              <div className="text-[10px] font-mono text-zinc-600">
                <p>No release gates loaded</p>
                <p className="mt-1 text-zinc-700">Golden run has 1 release gate</p>
              </div>
            ) : (
              <div className="space-y-2">
                {releaseGates.map((gate) => (
                  <div
                    key={gate.gate_id}
                    className="flex items-center justify-between px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50"
                  >
                    <span className="text-[11px] font-mono text-zinc-300">{gate.name}</span>
                    <Badge
                      variant={gate.status === 'passed' ? 'emerald' : gate.status === 'failed' ? 'red' : 'amber'}
                      size="sm"
                    >
                      {gate.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
