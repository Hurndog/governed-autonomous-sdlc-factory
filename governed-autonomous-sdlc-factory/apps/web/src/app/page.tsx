'use client';

import { useEffect } from 'react';
import { Sidebar } from '@/components/ui/Sidebar';
import { TopBar } from '@/components/ui/TopBar';
import { useStore } from '@/lib/store';
import { useWebSocket } from '@/lib/useWebSocket';
import { api } from '@/lib/api';
import { Dashboard } from '@/components/rooms/Dashboard';
import { BuildMap } from '@/components/rooms/BuildMap';
import { SDLCNavigator } from '@/components/rooms/SDLCNavigator';
import { AgentCommandCenter } from '@/components/rooms/AgentCommandCenter';
import { Tokenomics } from '@/components/rooms/Tokenomics';
import { SemanticCoverage } from '@/components/rooms/SemanticCoverage';
import { GovernanceGates } from '@/components/rooms/GovernanceGates';
import { ArchitectureIntelligence } from '@/components/rooms/ArchitectureIntelligence';
import { ProcessTimeline } from '@/components/rooms/ProcessTimeline';
import { BacklogChecklist } from '@/components/rooms/BacklogChecklist';
import { ArtifactExplorer } from '@/components/rooms/ArtifactExplorer';
import { RunReplay } from '@/components/rooms/RunReplay';
import { ExecutiveCockpit } from '@/components/rooms/ExecutiveCockpit';
import { SettingsProviders } from '@/components/rooms/SettingsProviders';
import { SpecRoom } from '@/components/rooms/SpecRoom';
import { EvidenceCenter } from '@/components/rooms/EvidenceCenter';
import { LogsDiagnostics } from '@/components/rooms/LogsDiagnostics';
import { IntegrityRoom } from '@/components/rooms/IntegrityRoom';
import { TraceabilityRoom } from '@/components/rooms/TraceabilityRoom';
import { RunControlRoom } from '@/components/rooms/RunControlRoom';

export default function Home() {
  const activeRoom = useStore((s) => s.activeRoom);
  const setHealth = useStore((s) => s.setHealth);
  const setModelStatus = useStore((s) => s.setModelStatus);
  const setRuns = useStore((s) => s.setRuns);
  useWebSocket();

  useEffect(() => {
    const loadInitial = async () => {
      try {
        const [health, models, runs] = await Promise.allSettled([
          api.getHealth(),
          api.getModelStatus(),
          api.listRuns({ page_size: 20 }),
        ]);
        if (health.status === 'fulfilled') setHealth(health.value as any);
        if (models.status === 'fulfilled') setModelStatus(models.value as any);
        if (runs.status === 'fulfilled') setRuns((runs.value as any).items || (runs.value as any).runs || []);
      } catch {
        // Silent fail — rooms handle their own loading
      }
    };
    loadInitial();
    const interval = setInterval(loadInitial, 30000);
    return () => clearInterval(interval);
  }, [setHealth, setModelStatus, setRuns]);

  const renderRoom = () => {
    switch (activeRoom) {
      case 'dashboard': return <Dashboard />;
      case 'build-map': return <BuildMap />;
      case 'sdlc-navigator': return <SDLCNavigator />;
      case 'agent-command': return <AgentCommandCenter />;
      case 'tokenomics': return <Tokenomics />;
      case 'semantic-coverage': return <SemanticCoverage />;
      case 'governance-room': return <GovernanceGates />;
      case 'architecture-room': return <ArchitectureIntelligence />;
      case 'process-timeline': return <ProcessTimeline />;
      case 'backlog': return <BacklogChecklist />;
      case 'artifact-explorer': return <ArtifactExplorer />;
      case 'replay-chamber': return <RunReplay />;
      case 'executive': return <ExecutiveCockpit />;
      case 'settings-providers': return <SettingsProviders />;
      case 'spec-room': return <SpecRoom />;
      case 'evidence-center': return <EvidenceCenter />;
      case 'logs-diagnostics': return <LogsDiagnostics />;
      case 'integrity-room': return <IntegrityRoom />;
      case 'traceability-room': return <TraceabilityRoom />;
      case 'run-control': return <RunControlRoom />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0b0f]">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto scrollbar-thin">
          {renderRoom()}
        </main>
      </div>
    </div>
  );
}
