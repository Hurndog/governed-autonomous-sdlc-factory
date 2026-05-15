'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, Badge, Metric, StatusDot, SectionHeader } from '@/components/ui/Card';
import { useStore } from '@/lib/store';
import { Network, GitBranch, FileText, AlertTriangle, CheckCircle2, Box, ArrowRight } from 'lucide-react';

export function ArchitectureRoom() {
  const activeArch = useStore((s) => s.activeArch);
  const architectures = useStore((s) => s.architectures);
  const [mermaidError, setMermaidError] = useState<string | null>(null);
  const mermaidRef = useRef<HTMLDivElement>(null);

  const defaultMermaid = `graph TD
    A[API Gateway] --> B[Auth Service]
    A --> C[Task Service]
    A --> D[Audit Service]
    B --> E[(PostgreSQL)]
    C --> E
    D --> F[(Event Store)]
    C --> G[Message Queue]
    G --> D
    style A fill:#064e3b,stroke:#34d399,color:#fff
    style B fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style C fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style D fill:#451a03,stroke:#f59e0b,color:#fff`;

  useEffect(() => {
    if (mermaidRef.current && typeof window !== 'undefined') {
      import('mermaid').then((mermaid) => {
        mermaid.default.initialize({
          startOnLoad: false,
          theme: 'dark',
          themeVariables: {
            primaryColor: '#064e3b',
            primaryTextColor: '#d4d4d8',
            primaryBorderColor: '#34d399',
            lineColor: '#52525b',
            secondaryColor: '#1e3a5f',
            tertiaryColor: '#18181b',
          },
        });
        try {
          mermaidRef.current!.innerHTML = '';
          mermaid.default.render(
            'arch-diagram',
            activeArch?.mermaid_diagram || defaultMermaid
          ).then((result) => {
            if (mermaidRef.current && result.svg) {
              mermaidRef.current.innerHTML = result.svg;
            }
          });
          setMermaidError(null);
        } catch (e: any) {
          setMermaidError(e.message);
        }
      });
    }
  }, [activeArch]);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-zinc-100 tracking-wide">
            ARCHITECTURE ROOM
          </h1>
          <p className="text-[10px] font-mono text-zinc-600 mt-1">
            System Design — ADR Explorer — Dependency Graphs — Governance Overlays
          </p>
        </div>
        <Badge variant="blue">
          <Network className="w-3 h-3 mr-1" />
          {architectures.length} Architectures
        </Badge>
      </div>

      {architectures.length === 0 && !activeArch ? (
        <div className="flex flex-col items-center justify-center py-24 text-zinc-600">
          <Network className="w-12 h-12 mb-4 opacity-20" />
          <p className="text-sm font-mono">No architectures generated yet</p>
          <p className="text-[10px] font-mono mt-2">
            Generate a specification first, then create an architecture
          </p>
        </div>
      ) : (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <Metric label="Components" value={activeArch?.components?.length || 0} color="text-emerald-400" />
            </Card>
            <Card>
              <Metric label="ADRs" value={activeArch?.decisions?.length || 0} color="text-blue-400" />
            </Card>
            <Card>
              <Metric label="Dependencies" value={activeArch?.components?.reduce((acc: number, c: any) => acc + (c.dependencies?.length || 0), 0) || 0} color="text-amber-400" />
            </Card>
            <Card>
              <Metric label="Gov-Relevant" value={activeArch?.components?.filter((c: any) => c.governance_relevant).length || 0} color="text-red-400" />
            </Card>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Mermaid Diagram */}
            <Card className="col-span-2" glow="blue">
              <SectionHeader
                title="System Architecture"
                subtitle="Live component diagram"
                icon={<Network className="w-4 h-4" />}
              />
              <div
                ref={mermaidRef}
                className="min-h-[300px] bg-zinc-900/50 rounded-md border border-zinc-800/50 p-4 flex items-center justify-center overflow-auto"
              >
                {mermaidError ? (
                  <div className="text-red-400 text-xs font-mono">{mermaidError}</div>
                ) : (
                  <span className="text-zinc-600 text-xs font-mono">Loading diagram...</span>
                )}
              </div>
            </Card>

            {/* Components List */}
            <Card>
              <SectionHeader title="Components" icon={<Box className="w-4 h-4" />} />
              <div className="space-y-2">
                {activeArch?.components?.map((comp: any) => (
                  <div
                    key={comp.id}
                    className="px-3 py-2 bg-zinc-900/50 rounded border border-zinc-800/50"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] font-mono text-zinc-200">{comp.name}</span>
                      <div className="flex items-center gap-1">
                        {comp.governance_relevant && (
                          <Badge variant="red" size="sm">GOV</Badge>
                        )}
                        <Badge variant="zinc" size="sm">{comp.type}</Badge>
                      </div>
                    </div>
                    {comp.dependencies?.length > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <ArrowRight className="w-3 h-3 text-zinc-700" />
                        <span className="text-[9px] font-mono text-zinc-600">
                          {comp.dependencies.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* ADRs */}
          <Card>
            <SectionHeader
              title="Architecture Decision Records"
              subtitle="Design rationale & consequences"
              icon={<FileText className="w-4 h-4" />}
            />
            {activeArch?.decisions?.length === 0 ? (
              <p className="text-[10px] font-mono text-zinc-600 text-center py-8">
                No ADRs recorded yet
              </p>
            ) : (
              <div className="space-y-3">
                {activeArch?.decisions?.map((adr: any) => (
                  <div
                    key={adr.id}
                    className="px-4 py-3 bg-zinc-900/50 rounded border border-zinc-800/50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono text-zinc-200 font-semibold">
                        {adr.title}
                      </span>
                      <Badge
                        variant={
                          adr.status === 'accepted'
                            ? 'emerald'
                            : adr.status === 'proposed'
                            ? 'amber'
                            : 'zinc'
                        }
                      >
                        {adr.status}
                      </Badge>
                    </div>
                    <p className="text-[10px] font-mono text-zinc-500 mb-2">{adr.context}</p>
                    <div className="px-2 py-1.5 bg-emerald-500/5 border border-emerald-500/10 rounded mb-2">
                      <span className="text-[10px] font-mono text-emerald-300">{adr.decision}</span>
                    </div>
                    {adr.consequences?.length > 0 && (
                      <div className="space-y-1">
                        {adr.consequences.map((c: string, i: number) => (
                          <div key={i} className="flex items-start gap-2">
                            <span className="text-[10px] text-zinc-600">→</span>
                            <span className="text-[10px] font-mono text-zinc-500">{c}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
