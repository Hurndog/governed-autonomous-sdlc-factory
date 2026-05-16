'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { useStore } from '@/lib/store';
import {
  LayoutDashboard,
  FileText,
  Network,
  Shield,
  RotateCcw,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
  Play,
  Link2,
  Package,
  FolderOpen,
  Terminal,
  Scale,
} from 'lucide-react';

const rooms = [
  { id: 'command-center', label: 'Command Center', icon: LayoutDashboard },
  { id: 'run-control', label: 'Run Control', icon: Play },
  { id: 'integrity-room', label: 'Integrity', icon: Shield },
  { id: 'traceability-room', label: 'Traceability', icon: Link2 },
  { id: 'governance-room', label: 'Governance', icon: Scale },
  { id: 'replay-chamber', label: 'Replay Chamber', icon: RotateCcw },
  { id: 'artifact-explorer', label: 'Artifacts', icon: Package },
  { id: 'evidence-center', label: 'Evidence', icon: FolderOpen },
  { id: 'logs-diagnostics', label: 'Logs', icon: Terminal },
  { id: 'settings-providers', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const activeRoom = useStore((s) => s.activeRoom);
  const setActiveRoom = useStore((s) => s.setActiveRoom);
  const sidebarCollapsed = useStore((s) => s.sidebarCollapsed);
  const setSidebarCollapsed = useStore((s) => s.setSidebarCollapsed);
  const wsConnected = useStore((s) => s.wsConnected);

  return (
    <aside
      className={cn(
        'h-screen bg-zinc-950 border-r border-zinc-800 flex flex-col transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-56'
      )}
    >
      {/* Logo */}
      <div className="h-14 flex items-center justify-between px-4 border-b border-zinc-800/50">
        {!sidebarCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <span className="text-xs font-mono font-bold text-zinc-200 tracking-wider">
              COGNITIVE<span className="text-emerald-400">CORTEX</span>
            </span>
          </div>
        )}
        {sidebarCollapsed && (
          <div className="w-6 h-6 rounded bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
          </div>
        )}
      </div>

      {/* WS Status */}
      <div className={cn('px-3 py-2 border-b border-zinc-800/50', sidebarCollapsed && 'px-2')}>
        <div className={cn('flex items-center gap-2', sidebarCollapsed && 'justify-center')}>
          <span
            className={cn(
              'w-1.5 h-1.5 rounded-full',
              wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
            )}
          />
          {!sidebarCollapsed && (
            <span className="text-[9px] font-mono text-zinc-500 uppercase">
              {wsConnected ? 'Live' : 'Offline'}
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
        {rooms.map((room) => {
          const Icon = room.icon;
          const isActive = activeRoom === room.id;
          return (
            <button
              key={room.id}
              onClick={() => setActiveRoom(room.id)}
              className={cn(
                'w-full flex items-center gap-3 rounded-md transition-all duration-150',
                sidebarCollapsed ? 'justify-center px-2 py-2.5' : 'px-3 py-2.5',
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50 border border-transparent'
              )}
              title={sidebarCollapsed ? room.label : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!sidebarCollapsed && (
                <span className="text-[11px] font-mono font-medium tracking-wide">
                  {room.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-zinc-800/50 p-2">
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md text-zinc-600 hover:text-zinc-400 hover:bg-zinc-800/50 transition-colors"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span className="text-[10px] font-mono">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
