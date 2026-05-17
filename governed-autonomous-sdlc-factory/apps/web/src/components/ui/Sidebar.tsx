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
  Coins,
  Target,
  GitBranch,
  ListChecks,
  Gauge,
  Clock,
  Bot,
} from 'lucide-react';

const roomGroups = [
  {
    label: 'Overview',
    rooms: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'build-map', label: 'Build Map', icon: Network },
      { id: 'executive', label: 'Executive', icon: Gauge },
    ],
  },
  {
    label: 'Factory',
    rooms: [
      { id: 'sdlc-navigator', label: 'SDLC Navigator', icon: GitBranch },
      { id: 'agent-command', label: 'Agents', icon: Bot },
      { id: 'run-control', label: 'Run Control', icon: Play },
      { id: 'process-timeline', label: 'Process', icon: Clock },
    ],
  },
  {
    label: 'Quality',
    rooms: [
      { id: 'semantic-coverage', label: 'Semantics', icon: Target },
      { id: 'integrity-room', label: 'Integrity', icon: Shield },
      { id: 'traceability-room', label: 'Traceability', icon: Link2 },
      { id: 'backlog', label: 'Backlog', icon: ListChecks },
    ],
  },
  {
    label: 'Intelligence',
    rooms: [
      { id: 'tokenomics', label: 'Tokenomics', icon: Coins },
      { id: 'architecture-room', label: 'Architecture', icon: Network },
      { id: 'governance-room', label: 'Governance', icon: Scale },
    ],
  },
  {
    label: 'Evidence',
    rooms: [
      { id: 'artifact-explorer', label: 'Artifacts', icon: Package },
      { id: 'evidence-center', label: 'Evidence', icon: FolderOpen },
      { id: 'replay-chamber', label: 'Replay', icon: RotateCcw },
      { id: 'logs-diagnostics', label: 'Logs', icon: Terminal },
    ],
  },
  {
    label: 'Config',
    rooms: [
      { id: 'spec-room', label: 'Specification', icon: FileText },
      { id: 'settings-providers', label: 'Settings', icon: Settings },
    ],
  },
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
        'h-screen bg-[#0a0b0f] border-r border-[#1e2230] flex flex-col transition-all duration-300',
        sidebarCollapsed ? 'w-14' : 'w-52'
      )}
    >
      {/* Logo */}
      <div className="h-12 flex items-center justify-between px-3 border-b border-[#1e2230]">
        {!sidebarCollapsed ? (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-violet-500/15 border border-violet-500/25 flex items-center justify-center">
              <Activity className="w-3.5 h-3.5 text-violet-400" />
            </div>
            <span className="text-[10px] font-bold text-zinc-300 tracking-[0.15em]">
              FACTORY<span className="text-violet-400">OS</span>
            </span>
          </div>
        ) : (
          <div className="w-6 h-6 rounded bg-violet-500/15 border border-violet-500/25 flex items-center justify-center mx-auto">
            <Activity className="w-3.5 h-3.5 text-violet-400" />
          </div>
        )}
      </div>

      {/* WS Status */}
      <div className={cn('px-2.5 py-1.5 border-b border-[#1e2230]', sidebarCollapsed && 'px-1.5')}>
        <div className={cn('flex items-center gap-1.5', sidebarCollapsed && 'justify-center')}>
          <span className={cn('w-1.5 h-1.5 rounded-full', wsConnected ? 'bg-emerald-400' : 'bg-red-400')} />
          {!sidebarCollapsed && (
            <span className="text-[9px] text-zinc-600 uppercase tracking-wider">
              {wsConnected ? 'Connected' : 'Offline'}
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 px-1.5 space-y-3 overflow-y-auto scrollbar-thin">
        {roomGroups.map((group) => (
          <div key={group.label}>
            {!sidebarCollapsed && (
              <div className="px-2 mb-1">
                <span className="text-[9px] font-semibold text-zinc-700 uppercase tracking-[0.12em]">
                  {group.label}
                </span>
              </div>
            )}
            {group.rooms.map((room) => {
              const Icon = room.icon;
              const isActive = activeRoom === room.id;
              return (
                <button
                  key={room.id}
                  onClick={() => setActiveRoom(room.id)}
                  className={cn(
                    'w-full flex items-center gap-2.5 rounded-md transition-all duration-150',
                    sidebarCollapsed ? 'justify-center px-1.5 py-2' : 'px-2.5 py-1.5',
                    isActive
                      ? 'bg-violet-500/10 text-violet-300 border border-violet-500/20'
                      : 'text-zinc-600 hover:text-zinc-400 hover:bg-zinc-800/40 border border-transparent'
                  )}
                  title={sidebarCollapsed ? room.label : undefined}
                >
                  <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                  {!sidebarCollapsed && (
                    <span className="text-[10px] font-medium tracking-wide">
                      {room.label}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-[#1e2230] p-1.5">
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="w-full flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-md text-zinc-700 hover:text-zinc-400 hover:bg-zinc-800/40 transition-colors"
        >
          {sidebarCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          {!sidebarCollapsed && <span className="text-[9px] uppercase tracking-wider">Collapse</span>}
        </button>
      </div>
    </aside>
  );
}
