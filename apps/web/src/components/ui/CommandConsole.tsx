'use client';

import { useState, useRef, useEffect } from 'react';
import { clsx } from 'clsx';
import type { ParsedCommand, SlashCommand } from '@/types';

const SLASH_COMMANDS: { command: SlashCommand; description: string }[] = [
  { command: '/project.create', description: 'Create a new project' },
  { command: '/spec.generate', description: 'Generate specification from idea' },
  { command: '/spec.revise', description: 'Revise current specification' },
  { command: '/spec.approve', description: 'Approve specification baseline' },
  { command: '/fd.generate', description: 'Generate functional design' },
  { command: '/architecture.generate', description: 'Generate technical architecture' },
  { command: '/architecture.review', description: 'Review architecture' },
  { command: '/design.generate', description: 'Generate design proposal' },
  { command: '/governance.generate', description: 'Generate governance requirements' },
  { command: '/tests.generate', description: 'Generate test plan' },
  { command: '/build.prepare', description: 'Prepare build environment' },
  { command: '/build.run', description: 'Execute build' },
  { command: '/build.pause', description: 'Pause running build' },
  { command: '/build.resume', description: 'Resume paused build' },
  { command: '/build.cancel', description: 'Cancel running build' },
  { command: '/refactor.run', description: 'Run refactor cycle' },
  { command: '/security.scan', description: 'Run security scan' },
  { command: '/governance.check', description: 'Run governance checks' },
  { command: '/evidence.export', description: 'Export evidence bundle' },
  { command: '/logs.download', description: 'Download run logs' },
  { command: '/cost.report', description: 'Generate cost report' },
  { command: '/deploy.localhost', description: 'Deploy to localhost' },
  { command: '/patterns.extract', description: 'Extract patterns' },
  { command: '/memory.search', description: 'Search memory' },
  { command: '/github.sync', description: 'Sync with GitHub' },
];

export function parseCommand(input: string): ParsedCommand | null {
  const trimmed = input.trim();
  if (!trimmed.startsWith('/')) return null;

  const parts = trimmed.split(/\s+/);
  const cmd = parts[0];
  const args = parts.slice(1).join(' ');

  const validCommands = SLASH_COMMANDS.map((c) => c.command);
  if (!validCommands.includes(cmd as SlashCommand)) return null;

  return { command: cmd as SlashCommand, args, raw: trimmed };
}

interface CommandConsoleProps {
  onCommand?: (cmd: ParsedCommand) => void;
}

export function CommandConsole({ onCommand }: CommandConsoleProps) {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredCommands, setFilteredCommands] = useState(SLASH_COMMANDS);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (input.startsWith('/')) {
      const filtered = SLASH_COMMANDS.filter((c) =>
        c.command.toLowerCase().includes(input.toLowerCase())
      );
      setFilteredCommands(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [input]);

  const handleSubmit = () => {
    if (!input.trim()) return;

    setHistory((h) => [...h, input]);

    const parsed = parseCommand(input);
    if (parsed && onCommand) {
      onCommand(parsed);
    }

    setInput('');
    setShowSuggestions(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="border-t border-[var(--border-primary)] bg-[var(--bg-secondary)]">
      {/* History */}
      {history.length > 0 && (
        <div className="max-h-32 overflow-auto px-3 py-2 border-b border-[var(--border-primary)]">
          {history.slice(-5).map((h, i) => (
            <div key={i} className="text-xs text-[var(--text-muted)] font-mono">
              {'>'} {h}
            </div>
          ))}
        </div>
      )}

      {/* Suggestions */}
      {showSuggestions && filteredCommands.length > 0 && (
        <div className="max-h-48 overflow-auto border-b border-[var(--border-primary)]">
          {filteredCommands.slice(0, 8).map((c) => (
            <button
              key={c.command}
              onClick={() => {
                setInput(c.command + ' ');
                setShowSuggestions(false);
                inputRef.current?.focus();
              }}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-[var(--bg-tertiary)] flex items-center gap-2"
            >
              <span className="font-mono text-[var(--accent-cyan)] w-40 shrink-0">{c.command}</span>
              <span className="text-[var(--text-muted)] truncate">{c.description}</span>
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex items-center px-3 py-2">
        <span className="text-[var(--accent-cyan)] font-mono mr-2">{'>'}</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a command or / for slash commands..."
          className="flex-1 bg-transparent text-sm focus:outline-none font-mono"
        />
        <button
          onClick={handleSubmit}
          className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
        >
          Enter
        </button>
      </div>
    </div>
  );
}
