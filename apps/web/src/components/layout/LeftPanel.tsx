'use client';

import { useStore } from '@/store';
import { clsx } from 'clsx';
import { CommandConsole } from '@/components/ui/CommandConsole';
import type { ParsedCommand } from '@/types';

const NAV_ITEMS = [
  { id: 'command-center', label: 'Command Center', icon: '⚡' },
  { id: 'live-factory', label: 'Live Factory Run', icon: '🏭' },
  { id: 'agent-monitor', label: 'Agent Monitor', icon: '🤖' },
  { id: 'logs-downloads', label: 'Logs & Downloads', icon: '📋' },
  { id: 'deployment-panel', label: 'Deployment Panel', icon: '🚀' },
];

export function LeftPanel() {
  const { activeScreen, setActiveScreen, selectedProject, selectedRun } = useStore();

  const handleCommand = (cmd: ParsedCommand) => {
    console.log('[Command]', cmd.command, cmd.args);

    // Dispatch commands to appropriate screens
    switch (cmd.command) {
      case '/project.create':
        setActiveScreen('command-center');
        break;
      case '/build.run':
      case '/build.pause':
      case '/build.resume':
      case '/build.cancel':
        setActiveScreen('live-factory');
        break;
      case '/deploy.localhost':
        setActiveScreen('deployment-panel');
        break;
      case '/logs.download':
        setActiveScreen('logs-downloads');
        break;
      default:
        // For now, just log unknown commands
        console.log('Command not yet implemented:', cmd.command);
    }
  };

  return (
    <aside className="w-72 bg-[var(--bg-secondary)] border-r border-[var(--border-primary)] flex flex-col">
      {/* Project Info */}
      <div className="p-4 border-b border-[var(--border-primary)]">
        <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-1">Project</div>
        <div className="font-semibold text-sm truncate">
          {selectedProject?.name || 'No project selected'}
        </div>
        {selectedRun && (
          <div className="mt-2">
            <div className="text-xs text-[var(--text-muted)]">Active Run</div>
            <div className="text-sm text-[var(--accent-cyan)] truncate">{selectedRun.name}</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="p-2 space-y-1">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveScreen(item.id)}
            className={clsx(
              'w-full text-left px-3 py-2.5 rounded-md text-sm transition-colors',
              activeScreen === item.id
                ? 'bg-[var(--accent-blue)]/20 text-[var(--accent-blue)]'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-[var(--text-primary)]'
            )}
          >
            <span className="mr-2">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* AI Control Assistant */}
      <div className="flex-1 flex flex-col mt-auto border-t border-[var(--border-primary)]">
        <div className="panel-header">AI Control Assistant</div>
        <div className="flex-1 overflow-auto p-3">
          <div className="text-xs text-[var(--text-muted)]">
            Ask me anything or use slash commands to control the factory.
          </div>
        </div>
        <CommandConsole onCommand={handleCommand} />
      </div>
    </aside>
  );
}
