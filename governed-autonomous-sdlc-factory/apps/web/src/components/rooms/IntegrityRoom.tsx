'use client';

import React, { useState, useCallback } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Play,
  RotateCcw,
  Hash,
  Clock,
  ChevronDown,
  ChevronUp,
  Zap,
} from 'lucide-react';

export function IntegrityRoom() {
  const selectedRunId = useStore((s) => s.selectedRunId);
  const integrityResult = useStore((s) => s.integrityResult);
  const setIntegrityResult = useStore((s) => s.setIntegrityResult);
  const integrityLoading = useStore((s) => s.integrityLoading);
  const setIntegrityLoading = useStore((s) => s.setIntegrityLoading);
  const setLastError = useStore((s) => s.setLastError);

  const [runIdInput, setRunIdInput] = useState(selectedRunId || '6a7f7ea0-297f-435e-9bb2-899368c7d332');
  const [stabilityResults, setStabilityResults] = useState<number[]>([]);
  const [stabilityRunning, setStabilityRunning] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  const handleVerify = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setIntegrityLoading(true);
    setIntegrityResult(null);
    setLastError(null);
    try {
      const result = await api.verifyIntegrity(runIdInput.trim());
      setIntegrityResult(result);
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setIntegrityLoading(false);
    }
  }, [runIdInput, setIntegrityResult, setIntegrityLoading, setLastError]);

  const handleStabilityCheck = useCallback(async () => {
    if (!runIdInput.trim()) return;
    setStabilityRunning(true);
    setStabilityResults([]);
    const scores: number[] = [];
    try {
      for (let i = 0; i < 3; i++) {
        const result = await api.verifyIntegrity(runIdInput.trim());
        scores.push(result.integrity_score);
        setStabilityResults([...scores]);
        if (i < 2) await new Promise((r) => setTimeout(r, 500));
      }
    } catch (e: any) {
      setLastError(e.message);
    } finally {
      setStabilityRunning(false);
    }
  }, [runIdInput, setLastError]);

  const results = integrityResult?.report?.results || {};
  const componentEntries = Object.entries(results) as [string, { status: string; score: number; details: Record<string, unknown> }][];

  const statusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'warn': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'fail': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-zinc-500" />;
    }
  };

  const statusVariant = (status: string) => {
    switch (status) {
      case 'pass': return 'emerald';
      case 'warn': return 'amber';
      case 'fail': return 'red';
      default: return 'zinc';
    }
  };

  const overallScore = integrityResult?.integrity_score ?? integrityResult?.report?.overall_score;
  const overallStatus = integrityResult?.status;

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            INTEGRITY ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Forensic Verification — Component Scores — Stability Analysis
          </p>
        </div>
        {overallStatus && (
          <Badge variant={overallStatus === 'pass' ? 'emerald' : overallStatus === 'warn' ? 'amber' : 'red'}>
            <Shield className="w-3 h-3 mr-1" />
            {overallStatus === 'pass' ? 'ALL PASS' : overallStatus === 'warn' ? 'WARNINGS' : 'FAILURES'}
          </Badge>
        )}
      </div>

      {/* Run ID Input + Actions */}
      <Card glow="emerald">
        <SectionHeader title="Verify Integrity" subtitle="Enter run ID to verify" icon={<Shield className="w-4 h-4" />} />
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={runIdInput}
            onChange={(e) => setRunIdInput(e.target.value)}
            placeholder="Run ID (e.g., 6a7f7ea0-297f-435e-9bb2-899368c7d332)"
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 text-xs font-mono text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50"
          />
          <button
            onClick={handleVerify}
            disabled={integrityLoading || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-md text-emerald-400 text-xs font-mono font-medium hover:bg-emerald-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {integrityLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {integrityLoading ? 'Verifying...' : 'Verify'}
          </button>
          <button
            onClick={handleStabilityCheck}
            disabled={stabilityRunning || !runIdInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-md text-blue-400 text-xs font-mono font-medium hover:bg-blue-500/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {stabilityRunning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
            {stabilityRunning ? 'Running...' : 'Stability Check'}
          </button>
        </div>

        {/* Stability Results */}
        {stabilityResults.length > 0 && (
          <div className="mt-3 flex items-center gap-3">
            <span className="text-[10px] font-mono text-zinc-500">Stability:</span>
            {stabilityResults.map((score, i) => (
              <Badge key={i} variant={score === 1.0 ? 'emerald' : score >= 0.8 ? 'amber' : 'red'} size="sm">
                Call {i + 1}: {score.toFixed(2)}
              </Badge>
            ))}
            {stabilityResults.length === 3 && (
              <Badge variant={stabilityResults.every((s) => s === stabilityResults[0]) ? 'emerald' : 'amber'} size="sm">
                {stabilityResults.every((s) => s === stabilityResults[0]) ? '✓ Stable' : '⚠ Variance'}
              </Badge>
            )}
          </div>
        )}
      </Card>

      {/* Overall Score */}
      {overallScore !== undefined && (
        <div className="grid grid-cols-4 gap-4">
          <Card glow={overallScore === 1.0 ? 'emerald' : overallScore >= 0.8 ? 'amber' : 'red'}>
            <Metric
              label="Overall Score"
              value={overallScore.toFixed(2)}
              sub={overallStatus?.toUpperCase() || 'UNKNOWN'}
              color={overallScore === 1.0 ? 'text-emerald-400' : overallScore >= 0.8 ? 'text-amber-400' : 'text-red-400'}
            />
          </Card>
          <Card>
            <Metric label="Checks" value={integrityResult?.checks || 0} color="text-zinc-200" />
          </Card>
          <Card>
            <Metric label="Passed" value={integrityResult?.passed || 0} color="text-emerald-400" />
          </Card>
          <Card>
            <Metric label="Failed" value={integrityResult?.failed || 0} color={integrityResult?.failed ? 'text-red-400' : 'text-zinc-500'} />
          </Card>
        </div>
      )}

      {/* Component Scores */}
      {componentEntries.length > 0 && (
        <Card>
          <SectionHeader title="Component Scores" subtitle="Individual integrity components" icon={<Hash className="w-4 h-4" />} />
          <div className="grid grid-cols-2 gap-3">
            {componentEntries.map(([key, comp]) => (
              <div
                key={key}
                className={`px-4 py-3 rounded-md border ${
                  comp.status === 'pass'
                    ? 'bg-emerald-500/5 border-emerald-500/20'
                    : comp.status === 'warn'
                    ? 'bg-amber-500/5 border-amber-500/20'
                    : 'bg-red-500/5 border-red-500/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {statusIcon(comp.status)}
                    <span className="text-xs font-mono text-zinc-200 uppercase">{key.replace(/_/g, ' ')}</span>
                  </div>
                  <Badge variant={statusVariant(comp.status) as any}>{comp.score.toFixed(2)}</Badge>
                </div>
                <div className="text-[10px] font-mono text-zinc-500">
                  {Object.entries(comp.details).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span>{k}:</span>
                      <span className="text-zinc-400">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Raw Response */}
      {integrityResult && (
        <Card>
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="w-full flex items-center justify-between"
          >
            <SectionHeader title="Raw API Response" subtitle="Complete JSON response" icon={<Zap className="w-4 h-4" />} />
            {showRaw ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
          </button>
          {showRaw && (
            <pre className="text-[10px] font-mono text-zinc-400 bg-zinc-900/50 border border-zinc-800 rounded-md p-3 overflow-auto max-h-96">
              {JSON.stringify(integrityResult, null, 2)}
            </pre>
          )}
        </Card>
      )}

      {/* Empty State */}
      {!integrityResult && !integrityLoading && (
        <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
          <Shield className="w-10 h-10 mb-3 opacity-20" />
          <p className="text-xs font-mono">No integrity verification yet</p>
          <p className="text-[10px] font-mono mt-1">Enter a run ID and click Verify</p>
        </div>
      )}
    </div>
  );
}
