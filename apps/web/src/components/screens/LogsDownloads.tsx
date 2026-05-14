'use client';

import { useState } from 'react';
import { useStore } from '@/store';
import { api } from '@/lib/api';
import { LogViewer } from '@/components/ui/LogViewer';

export function LogsDownloads() {
  const { logs, selectedRun } = useStore();
  const [filter, setFilter] = useState('');
  const [severity, setSeverity] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  const filteredLogs = logs.filter((log) => {
    if (severity !== 'all' && log.severity !== severity) return false;
    if (filter && !log.message.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const handleExport = async () => {
    if (!selectedRun) return;
    setLoading(true);
    try {
      const result = await api.exportLogs(selectedRun.id);
      const blob = new Blob([result.content], { type: 'application/jsonl' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `run-${selectedRun.id}-logs.jsonl`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Logs & Downloads</h1>
        <button
          onClick={handleExport}
          disabled={loading || !selectedRun}
          className="bg-[var(--accent-blue)] hover:bg-[var(--accent-blue)]/80 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm"
        >
          {loading ? 'Exporting...' : 'Export JSONL'}
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-4">
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter logs..."
          className="flex-1 bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--accent-blue)]"
        />
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-md px-3 py-2 text-sm focus:outline-none"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="error">Error</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
        </select>
        <span className="text-xs text-[var(--text-muted)]">{filteredLogs.length} logs</span>
      </div>

      {/* Log Viewer */}
      <div className="flex-1 panel p-3 overflow-hidden">
        <LogViewer logs={filteredLogs} />
      </div>
    </div>
  );
}
