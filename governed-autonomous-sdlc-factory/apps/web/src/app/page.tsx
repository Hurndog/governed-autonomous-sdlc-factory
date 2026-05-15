'use client';

import { useEffect } from 'react';
import { Sidebar } from '@/components/ui/Sidebar';
import { useStore } from '@/lib/store';
import { useWebSocket } from '@/lib/useWebSocket';
import { CommandCenter } from '@/components/rooms/CommandCenter';
import { SpecRoom } from '@/components/rooms/SpecRoom';
import { ArchitectureRoom } from '@/components/rooms/ArchitectureRoom';
import { GovernanceRoom } from '@/components/rooms/GovernanceRoom';
import { ReplayChamber } from '@/components/rooms/ReplayChamber';
import { TopBar } from '@/components/ui/TopBar';

export default function Home() {
  const activeRoom = useStore((s) => s.activeRoom);
  useWebSocket();

  useEffect(() => {
    // Fetch initial data
    fetch('/api/v1/health')
      .then((r) => r.json())
      .then((data) => useStore.getState().setHealth(data as any))
      .catch(() => {});
  }, []);

  const renderRoom = () => {
    switch (activeRoom) {
      case 'command-center':
        return <CommandCenter />;
      case 'spec-room':
        return <SpecRoom />;
      case 'architecture-room':
        return <ArchitectureRoom />;
      case 'governance-room':
        return <GovernanceRoom />;
      case 'replay-chamber':
        return <ReplayChamber />;
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
