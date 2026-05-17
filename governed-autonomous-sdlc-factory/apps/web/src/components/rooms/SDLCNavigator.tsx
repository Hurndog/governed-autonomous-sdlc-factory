'use client';

import React, { useState } from 'react';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusChip } from '@/components/ui/StatusChip';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Badge } from '@/components/ui/Badge';
import { mockPhases, mockAgents } from '@/lib/mock-data';
import { CheckCircle2, Clock, AlertTriangle, Bot, ChevronRight, User } from 'lucide-react';

export function SDLCNavigator() {
  const [expandedPhase, setExpandedPhase] = useState<string | null>('phase-sem-cov');

  const phaseChecklists: Record<string, { label: string; status: string }[]> = {
    'phase-intake': [
      { label: 'User intent captured', status: 'done' },
      { label: 'Project scope defined', status: 'done' },
      { label: 'Initial constraints identified', status: 'done' },
    ],
    'phase-spec': [
      { label: 'Product specification generated', status: 'done' },
      { label: 'Functional requirements extracted', status: 'done' },
      { label: 'Non-functional requirements extracted', status: 'done' },
      { label: 'Acceptance criteria drafted', status: 'done' },
      { label: 'Governance areas identified', status: 'done' },
    ],
    'phase-req': [
      { label: 'Requirements normalized', status: 'done' },
      { label: 'Ambiguity scoring complete', status: 'done' },
      { label: 'Testability assessment done', status: 'done' },
      { label: 'Actor-action-object extraction', status: 'done' },
      { label: 'Criticality classification', status: 'done' },
      { label: 'Security relevance tagged', status: 'done' },
      { label: 'Governance relevance tagged', status: 'done' },
      { label: 'Human review completed', status: 'done' },
    ],
    'phase-arch': [
      { label: 'System context diagram', status: 'done' },
      { label: 'Component model', status: 'done' },
      { label: 'API contracts defined', status: 'done' },
      { label: 'Data model designed', status: 'done' },
      { label: 'ADRs documented', status: 'done' },
      { label: 'Integration strategy', status: 'done' },
      { label: 'Security boundaries defined', status: 'done' },
      { label: 'Runtime topology', status: 'done' },
      { label: 'Failure modes analyzed', status: 'done' },
      { label: 'Observability design', status: 'done' },
      { label: 'Architecture review passed', status: 'done' },
      { label: 'Human approval obtained', status: 'done' },
    ],
    'phase-sem-cov': [
      { label: 'Normalized requirements', status: 'done' },
      { label: 'Acceptance criteria extraction', status: 'done' },
      { label: 'Test obligation generation', status: 'done' },
      { label: 'Test mapping', status: 'active' },
      { label: 'Independent verifier critique', status: 'active' },
      { label: 'Mutation testing', status: 'pending' },
      { label: 'Negative test generation', status: 'pending' },
      { label: 'Evidence binding', status: 'active' },
      { label: 'Semantic coverage score', status: 'pending' },
      { label: 'False confidence detection', status: 'pending' },
      { label: 'Release gate impact assessment', status: 'pending' },
      { label: 'Human review', status: 'pending' },
    ],
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto">
      <SectionHeader title="SDLC Phase Navigator" subtitle="14 phases from intake to retrospective" />

      {/* Horizontal phase bar */}
      <div className="card p-4">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-thin pb-2">
          {mockPhases.map((phase, i) => (
            <React.Fragment key={phase.id}>
              <button
                onClick={() => setExpandedPhase(expandedPhase === phase.id ? null : phase.id)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[10px] font-medium transition-all ${
                  phase.status === 'completed' ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20' :
                  phase.status === 'active' ? 'bg-blue-400/10 text-blue-400 border border-blue-400/20 ring-1 ring-blue-400/30' :
                  phase.status === 'blocked' ? 'bg-red-400/10 text-red-400 border border-red-400/20' :
                  'bg-zinc-800/30 text-zinc-600 border border-zinc-700/30'
                }`}
              >
                {phase.status === 'completed' ? <CheckCircle2 className="w-3 h-3" /> :
                 phase.status === 'active' ? <Clock className="w-3 h-3 animate-pulse" /> :
                 phase.status === 'blocked' ? <AlertTriangle className="w-3 h-3" /> :
                 <div className="w-3 h-3 rounded-full border border-zinc-600" />}
                {phase.shortName}
              </button>
              {i < mockPhases.length - 1 && (
                <ChevronRight className={`w-3 h-3 flex-shrink-0 ${
                  mockPhases[i].status === 'completed' ? 'text-emerald-400/40' : 'text-zinc-800'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Phase detail */}
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          {expandedPhase && (
            <div className="card p-4">
              {(() => {
                const phase = mockPhases.find(p => p.id === expandedPhase);
                if (!phase) return null;
                const checklist = phaseChecklists[expandedPhase] || [];
                const phaseAgents = mockAgents.filter(a =>
                  (phase.status === 'active' && a.status !== 'idle') ||
                  (phase.status === 'completed' && a.tokenUsage > 0)
                );

                return (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-zinc-200">{phase.name}</h3>
                        <p className="text-[10px] text-zinc-600">{phase.completedArtifacts}/{phase.totalArtifacts} artifacts • {phase.elapsedMinutes}min elapsed</p>
                      </div>
                      <StatusChip status={phase.status === 'completed' ? 'verified' : phase.status === 'active' ? 'active' : 'pending'} />
                    </div>

                    <ProgressBar value={phase.progress} color={phase.status === 'completed' ? 'green' : 'blue'} showLabel />

                    {/* Checklist */}
                    <div>
                      <div className="text-[9px] text-zinc-700 uppercase tracking-widest mb-2">Deliverables Checklist</div>
                      <div className="space-y-1.5">
                        {checklist.map((item, i) => (
                          <div key={i} className="flex items-center gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                            {item.status === 'done' ? (
                              <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                            ) : item.status === 'active' ? (
                              <Clock className="w-3 h-3 text-blue-400 flex-shrink-0 animate-pulse" />
                            ) : (
                              <div className="w-3 h-3 rounded-full border border-zinc-700 flex-shrink-0" />
                            )}
                            <span className={`text-[10px] ${item.status === 'done' ? 'text-zinc-400' : item.status === 'active' ? 'text-blue-300' : 'text-zinc-600'}`}>
                              {item.label}
                            </span>
                            {item.status === 'active' && <Badge variant="blue" size="sm">In Progress</Badge>}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Phase stats */}
                    <div className="grid grid-cols-4 gap-3">
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Artifacts</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.completedArtifacts}/{phase.totalArtifacts}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Tokens</div>
                        <div className="text-sm font-semibold text-zinc-300">{(phase.tokenUsage / 1000).toFixed(1)}k</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Failed Checks</div>
                        <div className={`text-sm font-semibold ${phase.failedChecks > 0 ? 'text-red-400' : 'text-emerald-400'}`}>{phase.failedChecks}</div>
                      </div>
                      <div className="p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                        <div className="text-[9px] text-zinc-700 uppercase">Human Interventions</div>
                        <div className="text-sm font-semibold text-zinc-300">{phase.humanInterventions}</div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        {/* Agent activity for phase */}
        <div className="col-span-4 card p-4">
          <SectionHeader title="Phase Agents" subtitle="Active and completed" />
          <div className="space-y-2">
            {mockAgents.filter(a => a.tokenUsage > 0).slice(0, 6).map(agent => (
              <div key={agent.id} className="flex items-center gap-2 p-2 rounded bg-zinc-800/20 border border-zinc-800/40">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: agent.color }} />
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-medium text-zinc-400 truncate">{agent.name}</div>
                  <div className="text-[9px] text-zinc-700">{(agent.tokenUsage / 1000).toFixed(1)}k tokens</div>
                </div>
                <StatusChip status={agent.status === 'working' ? 'active' : 'idle'} size="sm" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
