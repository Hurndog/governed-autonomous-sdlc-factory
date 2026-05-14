'use client';

import { useState } from 'react';
import { useStore } from '@/store';
import { api } from '@/lib/api';

export function CommandCenter() {
  const { projects, setProjects, selectProject, setRuns, selectRun, agents, setAgents } = useStore();
  const [idea, setIdea] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateProject = async () => {
    if (!projectName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const project = await api.createProject({
        name: projectName,
        idea_text: idea || undefined,
      });
      const updated = await api.listProjects();
      setProjects(updated.items);
      selectProject(project);
      setProjectName('');
      setIdea('');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartRun = async (projectId: string) => {
    setLoading(true);
    setError(null);
    try {
      const run = await api.createRun({
        project_id: projectId,
        name: `Run ${new Date().toISOString().slice(0, 19)}`,
        is_demo: true,
      });
      const runs = await api.listRuns(projectId);
      setRuns(runs.items);
      selectRun(run);
      useStore.getState().setActiveScreen('live-factory');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Command Center</h1>

      {error && (
        <div className="bg-[var(--accent-red)]/10 border border-[var(--accent-red)] rounded-lg p-3 mb-4 text-sm text-[var(--accent-red)]">
          {error}
        </div>
      )}

      {/* Create Project */}
      <div className="panel p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">New Project</h2>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-[var(--text-muted)] block mb-1">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. Task Manager Pro"
              className="w-full bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--accent-blue)]"
            />
          </div>
          <div>
            <label className="text-xs text-[var(--text-muted)] block mb-1">Idea (natural language)</label>
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your software idea..."
              rows={4}
              className="w-full bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--accent-blue)] resize-none"
            />
          </div>
          <button
            onClick={handleCreateProject}
            disabled={loading || !projectName.trim()}
            className="bg-[var(--accent-blue)] hover:bg-[var(--accent-blue)]/80 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </div>

      {/* Projects List */}
      <div className="panel p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Projects ({projects.length})</h2>
        {projects.length === 0 ? (
          <div className="text-sm text-[(--text-muted)]">No projects yet. Create one above.</div>
        ) : (
          <div className="space-y-2">
            {projects.map((p) => (
              <div key={p.id} className="flex items-center justify-between bg-[var(--bg-tertiary)] rounded-md p-3">
                <div>
                  <div className="font-medium text-sm">{p.name}</div>
                  <div className="text-xs text-[var(--text-muted)]">{p.slug} · {p.status}</div>
                </div>
                <button
                  onClick={() => handleStartRun(p.id)}
                  disabled={loading}
                  className="bg-[var(--accent-green)]/20 text-[var(--accent-green)] hover:bg-[var(--accent-green)]/30 px-3 py-1.5 rounded text-xs font-medium transition-colors"
                >
                  Start Run
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Agents Overview */}
      <div className="panel p-4">
        <h2 className="text-lg font-semibold mb-4">Agent Registry ({agents.length})</h2>
        <div className="grid grid-cols-2 gap-2">
          {agents.map((a) => (
            <div key={a.id} className="bg-[var(--bg-tertiary)] rounded-md p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className={`status-dot ${a.is_active ? 'status-completed' : 'status-pending'}`} />
                <span className="text-sm font-medium">{a.name}</span>
              </div>
              <div className="text-xs text-[var(--text-muted)]">{a.role}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
