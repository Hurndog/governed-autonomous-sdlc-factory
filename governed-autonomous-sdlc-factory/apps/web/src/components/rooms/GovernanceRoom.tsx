'use client';

import React from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
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
} from 'lucide-react';

export function GovernanceRoom() {
  const findings = useStore((s) => s.governanceFindings);

  const criticalCount = findings.filter((f) => f.severity === 'critical').length;
  const warningCount = findings.filter((f) => f.severity === 'warning').length;
  const infoCount = findings.filter((f) => f.severity === 'info').length;

  const severityIcon = (sev: string) => {
    switch (sev) {
      case 'critical':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-blue-400" />;
    }
  };

  const severityVariant = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'red';
      case 'warning':
        return 'amber';
      default:
        return 'blue';
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

      {/* Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <Card glow={criticalCount > 0 ? 'red' : 'none'}>
          <Metric label="Critical" value={criticalCount} color={criticalCount > 0 ? 'text-red-400' : 'text-zinc-500'} />
        </Card>
        <Card glow={warningCount > 0 ? 'amber' : 'none'}>
          <Metric label="Warnings" value={warningCount} color={warningCount > 0 ? 'text-amber-400' : 'text-zinc-500'} />
        </Card>
        <Card>
          <Metric label="Info" value={infoCount} color="text-blue-400" />
        </Card>
        <Card>
          <Metric label="Release Gates" value="3" sub="2 passed, 1 pending" color="text-zinc-200" />
        </Card>
        <Card>
          <Metric label="Compliance" value={criticalCount === 0 ? 'PASS' : 'FAIL'} color={criticalCount === 0 ? 'text-emerald-400' : 'text-red-400'} />
        </Card>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Findings */}
        <Card className="col-span-2">
          <SectionHeader
            title="Governance Findings"
            subtitle="Runtime policy evaluations"
            icon={<Shield className="w-4 h-4" />}
          />
          {findings.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
              <Shield className="w-10 h-10 mb-3 opacity-20" />
              <p className="text-xs font-mono">No governance findings</p>
              <p className="text-[10px] font-mono mt-1">
                Findings are generated during pipeline execution
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {findings.map((f) => (
                <div
                  key={f.id}
                  className={`px-4 py-3 rounded-md border ${
                    f.severity === 'critical'
                      ? 'bg-red-500/5 border-red-500/20'
                      : f.severity === 'warning'
                      ? 'bg-amber-500/5 border-amber-500/20'
                      : 'bg-blue-500/5 border-blue-500/20'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {severityIcon(f.severity)}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono text-zinc-200 font-semibold">
                          {f.title}
                        </span>
                        <div className="flex items-center gap-2">
                          <Badge variant={severityVariant(f.severity) as any}>{f.severity}</Badge>
                          <Badge variant="zinc">{f.category}</Badge>
                        </div>
                      </div>
                      <p className="text-[10px] font-mono text-zinc-500">{f.description}</p>
                      {f.replay_session_id && (
                        <div className="flex items-center gap-1 mt-2">
                          <FileText className="w-3 h-3 text-zinc-600" />
                          <span className="text-[9px] font-mono text-zinc-600">
                            Replay: {f.replay_session_id}
                          </span>
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
          {/* Release Gates */}
          <Card>
            <SectionHeader title="Release Gates" icon={<Lock className="w-4 h-4" />} />
            <div className="space-y-2">
              {[
                { name: 'Governance Scan', status: 'passed' },
                { name: 'Integrity Check', status: 'passed' },
                { name: 'Evidence Bundle', status: 'pending' },
              ].map((gate) => (
                <div
                  key={gate.name}
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
          </Card>

          {/* Compliance */}
          <Card>
            <SectionHeader title="Compliance" icon={<Scale className="w-4 h-4" />} />
            <div className="space-y-2">
              {[
                { name: 'Data Governance', status: 'compliant' },
                { name: 'Security Policy', status: 'compliant' },
                { name: 'Audit Trail', status: 'compliant' },
                { name: 'Evidence Chain', status: 'partial' },
              ].map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between px-2 py-1.5"
                >
                  <span className="text-[10px] font-mono text-zinc-400">{item.name}</span>
                  <StatusDot
                    status={item.status === 'compliant' ? 'healthy' : 'degraded'}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </Card>

          {/* Audit */}
          <Card>
            <SectionHeader title="Audit Trail" icon={<Eye className="w-4 h-4" />} />
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-500">
                <Clock className="w-3 h-3" />
                <span>Last scan: 2 min ago</span>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-500">
                <FileText className="w-3 h-3" />
                <span>Evidence: 1 bundle</span>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-500">
                <Shield className="w-3 h-3" />
                <span>Policies: 4 active</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
