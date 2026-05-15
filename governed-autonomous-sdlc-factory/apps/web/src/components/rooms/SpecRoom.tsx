'use client';

import React, { useState } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { FileText, GitBranch, Tag, Shield, Clock, Hash, Brain, Layers } from 'lucide-react';

export function SpecRoom() {
  const activeSpec = useStore((s) => s.activeSpec);
  const specifications = useStore((s) => s.specifications);
  const [selectedReq, setSelectedReq] = useState<string | null>(null);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            SPECIFICATION ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            Requirements Engineering — Governance-Tagged — Inference-Traced
          </p>
        </div>
        <Badge variant="emerald">
          <StatusDot status="active" size="sm" />
          <span className="ml-1.5">{specifications.length} Specs</span>
        </Badge>
      </div>

      {specifications.length === 0 && !activeSpec ? (
        <div className="flex flex-col items-center justify-center py-24 text-zinc-600">
          <FileText className="w-12 h-12 mb-4 opacity-20" />
          <p className="text-sm font-mono">No specifications generated yet</p>
          <p className="text-[10px] font-mono mt-2">
            Go to Command Center and enter an intent to generate a specification
          </p>
        </div>
      ) : (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-5 gap-4">
            <Card>
              <Metric label="Functional Reqs" value={activeSpec?.functional_requirements?.length || 0} color="text-emerald-400" />
            </Card>
            <Card>
              <Metric label="Non-Functional" value={activeSpec?.non_functional_requirements?.length || 0} color="text-blue-400" />
            </Card>
            <Card>
              <Metric label="Acceptance Criteria" value={activeSpec?.acceptance_criteria?.length || 0} color="text-amber-400" />
            </Card>
            <Card>
              <Metric label="Governance Areas" value={activeSpec?.governance_areas?.length || 0} color="text-red-400" />
            </Card>
            <Card>
              <Metric label="Inferences" value={activeSpec?.inference_trace_id ? 1 : 0} color="text-zinc-200" />
            </Card>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Requirements List */}
            <Card className="col-span-2">
              <SectionHeader
                title="Requirements"
                subtitle="Functional & Non-functional"
                icon={<Layers className="w-4 h-4" />}
              />
              <div className="space-y-2">
                {activeSpec?.functional_requirements?.map((req: any) => (
                  <div
                    key={req.id}
                    onClick={() => setSelectedReq(selectedReq === req.id ? null : req.id)}
                    className={`px-3 py-2.5 rounded-md border cursor-pointer transition-colors ${
                      selectedReq === req.id
                        ? 'bg-emerald-500/5 border-emerald-500/20'
                        : 'bg-zinc-900/50 border-zinc-800/50 hover:border-zinc-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-zinc-600">{req.id}</span>
                        <span className="text-[11px] font-mono text-zinc-300">{req.text}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {req.governance_sensitive && (
                          <Badge variant="red" size="sm">GOV</Badge>
                        )}
                        <Badge
                          variant={
                            req.priority === 'must' ? 'emerald' : req.priority === 'should' ? 'amber' : 'zinc'
                          }
                          size="sm"
                        >
                          {req.priority}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
                {activeSpec?.non_functional_requirements?.map((req: any) => (
                  <div
                    key={req.id}
                    className="px-3 py-2.5 rounded-md border bg-blue-500/5 border-blue-500/10"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-blue-400/60">{req.id}</span>
                        <span className="text-[11px] font-mono text-zinc-300">{req.text}</span>
                      </div>
                      <Badge variant="blue" size="sm">NFR</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Right Panel */}
            <div className="space-y-4">
              {/* Acceptance Criteria */}
              <Card>
                <SectionHeader title="Acceptance Criteria" icon={<Tag className="w-4 h-4" />} />
                <div className="space-y-1.5">
                  {activeSpec?.acceptance_criteria?.map((ac: string, i: number) => (
                    <div key={i} className="flex items-start gap-2">
                      <span className="text-[10px] font-mono text-emerald-400 mt-0.5">✓</span>
                      <span className="text-[10px] font-mono text-zinc-400">{ac}</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Governance Areas */}
              <Card glow="amber">
                <SectionHeader title="Governance Areas" icon={<Shield className="w-4 h-4" />} />
                <div className="space-y-1.5">
                  {activeSpec?.governance_areas?.map((area: string, i: number) => (
                    <div key={i} className="flex items-center gap-2 px-2 py-1.5 bg-amber-500/5 rounded border border-amber-500/10">
                      <Shield className="w-3 h-3 text-amber-400" />
                      <span className="text-[10px] font-mono text-amber-300">{area}</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Inference Trace */}
              <Card>
                <SectionHeader title="Inference Trace" icon={<Brain className="w-4 h-4" />} />
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-zinc-600">Model</span>
                    <span className="text-[10px] font-mono text-zinc-300">gpt-oss:20b</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-zinc-600">Provider</span>
                    <span className="text-[10px] font-mono text-zinc-300">Ollama</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-zinc-600">Trace ID</span>
                    <span className="text-[10px] font-mono text-zinc-400">
                      {activeSpec?.inference_trace_id || '—'}
                    </span>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
