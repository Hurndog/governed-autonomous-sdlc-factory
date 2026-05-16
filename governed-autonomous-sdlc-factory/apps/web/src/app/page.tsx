'use client';

import { useEffect } from 'react';
import { Sidebar } from '@/components/ui/Sidebar';
import { TopBar } from '@/components/ui/TopBar';
import { useStore } from '@/lib/store';
import { useWebSocket } from '@/lib/useWebSocket';
import { api } from '@/lib/api';
import { CommandCenter } from '@/components/rooms/CommandCenter';
import { RunControlRoom } from '@/components/rooms/RunControlRoom';
import { IntegrityRoom } from '@/components/rooms/IntegrityRoom';
import { TraceabilityRoom } from '@/components/rooms/TraceabilityRoom';
import { GovernanceRoom } from '@/components/rooms/GovernanceRoom';
import { ReplayChamber } from '@/components/rooms/ReplayChamber';
import { ArtifactExplorer } from '@/components/rooms/ArtifactExplorer';
import { EvidenceCenter } from '@/components/rooms/EvidenceCenter';
import { LogsDiagnostics } from '@/components/rooms/LogsDiagnostics';
import { SettingsProviders } from '@/components/rooms/SettingsProviders';
import { SpecRoom } from '@/components/rooms/SpecRoom';
import { ArchitectureRoom } from '@/components/rooms/ArchitectureRoom';

export default function Home() {
  const activeRoom = useStore((s) => s.activeRoom);
  const setHealth = useStore((s) => s.setHealth);
  const setModelStatus = useStore((s) => s.setModelStatus);
  const setRuns = useStore((s) => s.setRuns);
  useWebSocket();

  useEffect(() => {
    // Fetch initial data
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
    // Refresh health every 30s
    const interval = setInterval(loadInitial, 30000);
    return () => clearInterval(interval);
  }, [setHealth, setModelStatus, setRuns]);

  const renderRoom = () => {
    switch (activeRoom) {
      case 'command-center':
        return <CommandCenter />;
      case 'run-control':
        return <RunControlRoom />;
      case 'integrity-room':
        return <IntegrityRoom />;
      case 'traceability-room':
        return <TraceabilityRoom />;
      case 'governance-room':
        return <GovernanceRoom />;
      case 'replay-chamber':
        return <ReplayChamber />;
      case 'artifact-explorer':
        return <ArtifactExplorer />;
      case 'evidence-center':
        return <EvidenceCenter />;
      case 'logs-diagnostics':
        return <LogsDiagnostics />;
      case 'settings-providers':
        return <SettingsProviders />;
      case 'spec-room':
        return <SpecRoom />;
      case 'architecture-room':
        return <ArchitectureRoom />;
      default:
        return <CommandCenter />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">{renderRoom()}</main>
      </div>
    </div>
  );
}
