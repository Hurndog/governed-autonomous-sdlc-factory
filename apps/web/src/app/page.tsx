'use client';

import { useEffect, useRef } from 'react';
import { useStore } from '@/store';
import { api } from '@/lib/api';
import { WSClient } from '@/lib/ws';
import type { WSEvent, Phase, Artifact } from '@/types';

export default function Home() {
  const store = useStore();
  const wsRef = useRef<WSClient | null>(null);

  // Load initial data
  useEffect(() => {
    api.listProjects().then((res) => {
      store.setProjects(res.items);
    }).catch(console.error);

    api.listAgents().then((res) => {
      const agents = Array.isArray(res) ? res : (res as any)?.items || [];
      store.setAgents(agents);
    }).catch(console.error);
  }, []);

  // WebSocket connection when run is selected
  useEffect(() => {
    if (!store.selectedRun) {
      wsRef.current?.disconnect();
      wsRef.current = null;
      return;
    }

    const runId = store.selectedRun.id;
    const client = new WSClient(runId);
    wsRef.current = client;
    client.connect();

    const unsub = client.on((event: WSEvent) => {
      store.addLiveEvent(event);
      const data = event.data as Record<string, unknown> | undefined;
      if (!data) return;

      const eventType = event.type;

      if (eventType === 'phase.transition') {
        const phaseName = data.phase_name as string | undefined;
        const newStatus = data.new_status as string | undefined;
        if (phaseName && newStatus) {
          const existing = store.phases.find(p => p.name === phaseName);
          if (existing) {
            store.updatePhase(existing.id, { status: newStatus as Phase['status'] });
          } else {
            store.setPhases([
              ...store.phases,
              {
                id: `phase-${phaseName}`,
                run_id: runId,
                name: phaseName,
                status: newStatus as Phase['status'],
                order_index: store.phases.length,
                agent_id: null,
                model_used: null,
                tokens_in: 0,
                tokens_out: 0,
                cost: 0,
                retry_count: 0,
                error_message: null,
                started_at: new Date().toISOString(),
                completed_at: newStatus === 'completed' ? new Date().toISOString() : null,
                created_at: new Date().toISOString(),
              } as Phase,
            ]);
          }
        }
      } else if (eventType === 'run.started' || eventType === 'run.status_changed') {
        const status = data.status as string | undefined;
        if (status) store.updateRunStatus(runId, status as any);
      } else if (eventType === 'run.completed') {
        store.updateRunStatus(runId, 'completed');
      } else if (eventType === 'run.failed') {
        store.updateRunStatus(runId, 'failed');
      } else if (eventType === 'artifact.created') {
        const artName = data.artifact_name as string | undefined;
        if (artName) {
          store.addArtifact({
            id: `artifact-${Date.now()}`,
            task_id: '',
            run_id: runId,
            name: artName,
            artifact_type: (data.artifact_type as string) || 'unknown',
            content: null,
            file_path: null,
            version: 1,
            is_baseline: false,
            is_locked: false,
            metadata: data,
            created_at: new Date().toISOString(),
          } as Artifact);
        }
      } else if (eventType === 'cost.recorded') {
        const cost = (data.cost as number) || 0;
        const current = store.costReport;
        store.setCostReport({
          run_id: runId,
          total_cost: (current?.total_cost || 0) + cost,
          budget_limit: current?.budget_limit || null,
          remaining_budget: current?.remaining_budget != null ? current.remaining_budget - cost : null,
          warning_threshold: current?.warning_threshold || 0.8,
          is_near_limit: false,
          is_hard_limit_reached: false,
          local_cost: (current?.local_cost || 0) + (data.is_local ? cost : 0),
          paid_cost: (current?.paid_cost || 0) + (data.is_local ? 0 : cost),
          estimated_savings: current?.estimated_savings || 0,
          by_phase: current?.by_phase || {},
          by_agent: current?.by_agent || {},
          by_model: current?.by_model || {},
        });
      } else if (eventType === 'deployment.state_changed') {
        store.setDeployment({
          id: `deploy-${Date.now()}`,
          run_id: runId,
          project_id: store.selectedProject?.id || '',
          status: (data.status as string) || 'unknown',
          localhost_url: (data.url as string) || null,
          port: null,
          container_id: null,
          health_status: 'unknown',
          deployment_log: null,
          evidence_bundle_id: null,
          started_at: new Date().toISOString(),
          completed_at: null,
          created_at: new Date().toISOString(),
        });
      }
    });

    return () => {
      unsub();
      client.disconnect();
    };
  }, [store.selectedRun?.id]);

  return null;
}
