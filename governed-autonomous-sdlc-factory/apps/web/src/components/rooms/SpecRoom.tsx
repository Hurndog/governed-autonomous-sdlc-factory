'use client';
import React from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { Badge } from '@/components/ui/Badge';
import { useStore } from '@/lib/store';
import { FileText, CheckCircle2, Clock } from 'lucide-react';

export function SpecRoom() {
  const spec = {
    title: 'PaymentHub v1.0',
    content: 'Enterprise payment processing platform with multi-gateway support, fraud detection, and real-time reconciliation.',
    functionalRequirements: [
      'The system shall process payments through multiple gateway providers',
      'The system shall validate payment amounts against account balance',
      'The system shall generate real-time reconciliation reports',
      'The system shall enforce role-based access control on all financial operations',
      'The system shall detect and flag suspicious transactions using ML models',
      'The system shall maintain audit logs for all transactions',
      'The system shall support webhook notifications for payment events',
      'The system shall provide a dashboard for transaction monitoring',
    ],
    nonFunctionalRequirements: [
      'Response time < 200ms for payment processing',
      '99.99% uptime SLA',
      'PCI DSS compliance',
      'Support 10,000 concurrent transactions',
    ],
    acceptanceCriteria: [
      'Payment processed within 200ms',
      'Fraud detection accuracy > 95%',
      'Reconciliation report generated within 5 seconds',
      'RBAC enforced on all financial endpoints',
    ],
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="Specification" subtitle="Product specification and requirements" />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8 card p-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold text-zinc-200">{spec.title}</span>
            <StatusChip status="verified" />
          </div>
          <p className="text-xs text-zinc-400 mb-4">{spec.content}</p>

          <div className="mb-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Functional Requirements</div>
            <div className="space-y-1">
              {spec.functionalRequirements.map((req, i) => (
                <div key={i} className="flex items-start gap-2 text-[10px]">
                  <span className="text-zinc-600 font-mono w-6 flex-shrink-0">FR{i + 1}</span>
                  <span className="text-zinc-400">{req}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Non-Functional Requirements</div>
            <div className="space-y-1">
              {spec.nonFunctionalRequirements.map((req, i) => (
                <div key={i} className="flex items-start gap-2 text-[10px]">
                  <span className="text-zinc-600 font-mono w-6 flex-shrink-0">NFR{i + 1}</span>
                  <span className="text-zinc-400">{req}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-4 space-y-4">
          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Acceptance Criteria</div>
            <div className="space-y-1.5">
              {spec.acceptanceCriteria.map((ac, i) => (
                <div key={i} className="flex items-start gap-1.5 text-[9px]">
                  <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <span className="text-zinc-500">{ac}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-4">
            <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Metadata</div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Status</span><StatusChip status="verified" size="sm" /></div>
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Version</span><span className="text-zinc-400">1.0</span></div>
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Author</span><span className="text-zinc-400">Product Analyst</span></div>
              <div className="flex justify-between text-[10px]"><span className="text-zinc-600">Approved</span><span className="text-zinc-400">Marco</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
