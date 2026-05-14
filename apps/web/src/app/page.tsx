'use client';

import { useState, useEffect, useCallback } from 'react';
import { useStore } from '@/store';
import { api } from '@/lib/api';
import { WSClient } from '@/lib/ws';
import { TopBar } from '@/components/layout/TopBar';
import { LeftPanel } from '@/components/layout/LeftPanel';
import { CenterPanel } from '@/components/layout/CenterPanel';
import { RightPanel } from '@/components/layout/RightPanel';
import { CommandCenter } from '@/components/screens/CommandCenter';
import { LiveFactoryRun } from '@/components/screens/LiveFactoryRun';
import { AgentMonitor } from '@/components/screens/AgentMonitor';
import { LogsDownloads } from '@/components/screens/LogsDownloads';
import { DeploymentPanel } from '@/components/screens/DeploymentPanel';
import type { WSEvent } from '@/types';

const SCREENS: Record<string, React.FC> = {
  'command-center': CommandCenter,
  'live-factory': LiveFactoryRun,
  'agent-monitor': AgentMonitor,
  'logs-downloads': LogsDownloads,
  'deployment-panel': DeploymentPanel,
};

export default function Home() {
  const { activeScreen, selectedRun, addLiveEvent, addLog, updateRunStatus, updatePhase, addArtifact } = useStore();
  const [ws, setWs] = useState<WSClient | null>(null);

  // Load initial data
  useEffect(() => {
    api.listProjects().then((res) => {
      useStore.getState().setProjects(res.items);
    }).catch(console.error);

    api.listAgents().then((res) => {
      const agents = Array.isArray(res) ? res : (res as any).items || [];
      useStore.getState().setAgents(agents);
    }).catch(console.error);
  }, []);

  // WebSocket connection when run is selected
  useEffect(() => {
    if (!selectedRun) {
      ws?.disconnect();
      setWs(null);
      return;
    }

    const client = new WSClient(selectedRun.id);
    client.connect();
    setWs(client);

    client.on((event: WSEvent) => {
      addLiveEvent(event);

      switch (event.type) {
        case 'log.entry':
          if (event.data) addLog(event.data as any);
          break;
        case 'run.status_changed':
          if (event.data?.status) updateRunStatus(selectedRun.id, event.data.status as any);
          break;
        case 'phase.started':
        case 'phase.completed':
        case 'phase.failed':
          if (event.data) updatePhase((event.data as any).id, event.data as any);
          break;
        case 'artifact.created':
          if (event.data) addArtifact(event.data as any);
          break;
      }
    });

    return () => {
      client.disconnect();
    };
  }, [selectedRun?.id]);

  const ScreenComponent = SCREENS[activeScreen] || CommandCenter;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <TopBar />
      <div className="flex-1 flex overflow-hidden">
        <LeftPanel />
        <CenterPanel>
          <ScreenComponent />
        </CenterPanel>
        <RightPanel />
      </div>
    </div>
  );
}
