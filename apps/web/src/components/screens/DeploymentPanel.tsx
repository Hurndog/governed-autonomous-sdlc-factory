'use client';

import { useState } from 'react';
import { useStore } from '@/store';
import { api } from '@/lib/api';

export function DeploymentPanel() {
  const { selectedRun, deployment, setDeployment } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDeploy = async () => {
    if (!selectedRun) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.deployRun(selectedRun.id);
      setDeployment(result);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: 'shutdown' | 'restart') => {
    if (!selectedRun) return;
    setLoading(true);
    try {
      await api[action === 'shutdown' ? 'shutdownDeployment' : 'restartDeployment'](selectedRun.id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Deployment Panel</h1>

      {error && (
        <div className="bg-[var(--accent-red)]/10 border border-[var(--accent-red)] rounded-lg p-3 mb-4 text-sm text-[var(--accent-red)]">
          {error}
        </div>
      )}

      {!selectedRun ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🚀</div>
          <p className="text-sm text-[var(--text-muted)]">Select a run to manage deployment</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Deploy Button */}
          <div className="panel p-4">
            <h2 className="font-semibold mb-3">Deploy to Localhost</h2>
            <p className="text-sm text-[var(--text-muted)] mb-4">
              Deploy the generated application to localhost using Docker Compose.
            </p>
            <button
              onClick={handleDeploy}
              disabled={loading}
              className="bg-[var(--accent-green)] hover:bg-[var(--accent-green)]/80 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {loading ? 'Deploying...' : 'Deploy'}
            </button>
          </div>

          {/* Deployment Status */}
          {deployment && (
            <div className="panel p-4">
              <h2 className="font-semibold mb-3">Deployment Status</h2>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-[var(--text-muted)]">Status:</span>
                  <span className="ml-2">{deployment.status}</span>
                </div>
                <div>
                  <span className="text-[var(--text-muted)]">Health:</span>
                  <span className="ml-2">{deployment.health_status}</span>
                </div>
                <div>
                  <span className="text-[var(--text-muted)]">URL:</span>
                  <span className="ml-2 text-[var(--accent-cyan)]">{deployment.localhost_url || '—'}</span>
                </div>
                <div>
                  <span className="text-[var(--text-muted)]">Port:</span>
                  <span className="ml-2">{deployment.port || '—'}</span>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => handleAction('restart')}
                  disabled={loading}
                  className="bg-[var(--accent-amber)]/20 text-[var(--accent-amber)] hover:bg-[var(--accent-amber)]/30 px-3 py-1.5 rounded text-xs"
                >
                  Restart
                </button>
                <button
                  onClick={() => handleAction('shutdown')}
                  disabled={loading}
                  className="bg-[var(--accent-red)]/20 text-[var(--accent-red)] hover:bg-[var(--accent-red)]/30 px-3 py-1.5 rounded text-xs"
                >
                  Shutdown
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
