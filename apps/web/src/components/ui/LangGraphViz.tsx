'use client';

import { useMemo } from 'react';
import { useStore } from '@/store';
import { clsx } from 'clsx';

const PIPELINE_PHASES = [
  { id: 'create_project', label: 'Create Project', category: 'intake' },
  { id: 'capture_intent', label: 'Capture Intent', category: 'intake' },
  { id: 'enrich_context', label: 'Enrich Context', category: 'intake' },
  { id: 'generate_specification', label: 'Specification', category: 'design' },
  { id: 'validate_specification', label: 'Validate Spec', category: 'design' },
  { id: 'generate_functional_design', label: 'Functional Design', category: 'design' },
  { id: 'generate_architecture', label: 'Architecture', category: 'design' },
  { id: 'generate_design_proposal', label: 'Design Proposal', category: 'design' },
  { id: 'generate_data_model', label: 'Data Model', category: 'design' },
  { id: 'generate_mcp_contracts', label: 'MCP Contracts', category: 'design' },
  { id: 'generate_governance_requirements', label: 'Governance', category: 'governance' },
  { id: 'generate_test_plan', label: 'Test Plan', category: 'governance' },
  { id: 'create_approval_baseline', label: 'Approval Baseline', category: 'governance' },
  { id: 'wait_for_approval', label: 'Wait Approval', category: 'governance' },
  { id: 'create_backlog', label: 'Backlog', category: 'build' },
  { id: 'create_git_branch', label: 'Git Branch', category: 'build' },
  { id: 'execute_build', label: 'Build', category: 'build' },
  { id: 'generate_documentation', label: 'Documentation', category: 'build' },
  { id: 'run_tests', label: 'Tests', category: 'quality' },
  { id: 'run_security_scan', label: 'Security', category: 'quality' },
  { id: 'run_governance_checks', label: 'Governance Check', category: 'quality' },
  { id: 'evaluate_release_gates', label: 'Release Gates', category: 'quality' },
  { id: 'run_refactor_if_needed', label: 'Refactor', category: 'quality' },
  { id: 'update_evidence', label: 'Evidence', category: 'delivery' },
  { id: 'extract_patterns', label: 'Patterns', category: 'delivery' },
  { id: 'update_memory', label: 'Memory', category: 'delivery' },
  { id: 'deploy_to_localhost', label: 'Deploy', category: 'delivery' },
  { id: 'generate_final_report', label: 'Final Report', category: 'delivery' },
];

const CATEGORY_COLORS: Record<string, string> = {
  intake: 'bg-[var(--accent-cyan)]',
  design: 'bg-[var(--accent-blue)]',
  governance: 'bg-[var(--accent-purple)]',
  build: 'bg-[var(--accent-green)]',
  quality: 'bg-[var(--accent-amber)]',
  delivery: 'bg-[var(--accent-red)]',
};

const CATEGORY_BORDERS: Record<string, string> = {
  intake: 'border-[var(--accent-cyan)]',
  design: 'border-[var(--accent-blue)]',
  governance: 'border-[var(--accent-purple)]',
  build: 'border-[var(--accent-green)]',
  quality: 'border-[var(--accent-amber)]',
  delivery: 'border-[var(--accent-red)]',
};

interface GraphNode {
  id: string;
  label: string;
  category: string;
  status: string;
  index: number;
  duration?: number;
  agent?: string;
  cost?: number;
  retries?: number;
  error?: string;
  artifacts?: number;
}

export function LangGraphVisualization() {
  const { phases, selectedRun } = useStore();

  const nodes: GraphNode[] = useMemo(() => {
    return PIPELINE_PHASES.map((phase, index) => {
      const dbPhase = phases.find(p => p.name === phase.id);
      return {
        id: phase.id,
        label: phase.label,
        category: phase.category,
        status: dbPhase?.status || 'pending',
        index,
        duration: dbPhase?.started_at && dbPhase?.completed_at
          ? Math.round((new Date(dbPhase.completed_at).getTime() - new Date(dbPhase.started_at).getTime()) / 1000)
          : undefined,
        agent: dbPhase?.agent_id || undefined,
        cost: dbPhase?.cost,
        retries: dbPhase?.retry_count,
        error: dbPhase?.error_message || undefined,
      };
    });
  }, [phases]);

  const runningNode = nodes.find(n => n.status === 'running');
  const completedCount = nodes.filter(n => n.status === 'completed').length;
  const failedCount = nodes.filter(n => n.status === 'failed').length;
  const totalCost = nodes.reduce((sum, n) => sum + (n.cost || 0), 0);

  if (!selectedRun) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-5xl mb-4">🏭</div>
          <h2 className="text-xl font-semibold mb-2">LangGraph Pipeline</h2>
          <p className="text-sm text-[var(--text-muted)]">Start a run to visualize the workflow</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Header Stats */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold">Pipeline</h2>
          <span className="text-xs text-[var(--text-muted)]">
            {completedCount}/{nodes.length} phases
          </span>
          {failedCount > 0 && (
            <span className="text-xs text-[var(--accent-red)]">{failedCount} failed</span>
          )}
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="text-[var(--text-muted)]">
            Cost: <span className="text-[var(--text-primary)] font-mono">${totalCost.toFixed(4)}</span>
          </span>
          {runningNode && (
            <span className="flex items-center gap-1">
              <span className="status-dot status-running" />
              <span className="text-[var(--accent-blue)]">{runningNode.label}</span>
            </span>
          )}
        </div>
      </div>

      {/* Category Legend */}
      <div className="flex items-center gap-3 mb-4">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1.5">
            <span className={clsx('w-2.5 h-2.5 rounded-sm', color)} />
            <span className="text-xs text-[var(--text-muted)] capitalize">{cat}</span>
          </div>
        ))}
      </div>

      {/* Graph Grid */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-10 gap-1.5">
          {nodes.map((node, i) => {
            const isRunning = node.status === 'running';
            const isCompleted = node.status === 'completed';
            const isFailed = node.status === 'failed';
            const isPending = node.status === 'pending';

            return (
              <div key={node.id} className="relative">
                {/* Connection line to next node */}
                {i < nodes.length - 1 && (
                  <div className="absolute top-1/2 left-full w-1.5 h-px bg-[var(--border-secondary)] z-0" />
                )}

                {/* Node */}
                <div
                  className={clsx(
                    'relative z-10 rounded-md p-2 border transition-all cursor-pointer',
                    'hover:ring-1 hover:ring-[var(--accent-blue)]',
                    isRunning && `border-[var(--accent-blue)] bg-[var(--accent-blue)]/10 ring-1 ring-[var(--accent-blue)] animate-pulse`,
                    isCompleted && `border-[var(--accent-green)] bg-[var(--accent-green)]/10`,
                    isFailed && `border-[var(--accent-red)] bg-[var(--accent-red)]/10`,
                    isPending && 'border-[var(--border-primary)] bg-[var(--bg-tertiary)]',
                    !isRunning && !isCompleted && !isFailed && !isPending && 'border-[var(--border-secondary)] bg-[var(--bg-tertiary)]',
                  )}
                >
                  {/* Status indicator */}
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className={clsx('status-dot', `status-${node.status}`)} />
                    <span className="text-[10px] font-mono text-[var(--text-muted)]">{node.index + 1}</span>
                  </div>

                  {/* Label */}
                  <div className="text-[10px] font-medium leading-tight truncate" title={node.label}>
                    {node.label}
                  </div>

                  {/* Running indicator */}
                  {isRunning && (
                    <div className="mt-1">
                      <div className="h-1 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                        <div className="h-full bg-[var(--accent-blue)] rounded-full animate-pulse" style={{ width: '60%' }} />
                      </div>
                    </div>
                  )}

                  {/* Cost */}
                  {node.cost && node.cost > 0 && (
                    <div className="text-[9px] text-[var(--text-muted)] mt-0.5 font-mono">
                      ${node.cost.toFixed(4)}
                    </div>
                  )}

                  {/* Error indicator */}
                  {isFailed && node.error && (
                    <div className="text-[9px] text-[var(--accent-red)] mt-0.5 truncate" title={node.error}>
                      ⚠ {node.error}
                    </div>
                  )}

                  {/* Retry indicator */}
                  {node.retries && node.retries > 0 && (
                    <div className="text-[9px] text-[var(--accent-amber)] mt-0.5">
                      ↻ {node.retries}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-4 pt-3 border-t border-[var(--border-primary)]">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="status-dot status-pending" />
              <span className="text-[var(--text-muted)]">Pending: {nodes.filter(n => n.status === 'pending').length}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="status-dot status-running" />
              <span className="text-[var(--text-muted)]">Running: {nodes.filter(n => n.status === 'running').length}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="status-dot status-completed" />
              <span className="text-[var(--text-muted)]">Completed: {completedCount}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="status-dot status-failed" />
              <span className="text-[var(--text-muted)]">Failed: {failedCount}</span>
            </span>
          </div>
          <div className="text-[var(--text-muted)]">
            Run: <span className="font-mono text-[var(--text-primary)]">{selectedRun.id.slice(0, 8)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
