import { create } from 'zustand';
import type {
  Project, Run, Phase, Agent, LogEvent, Artifact, CostReport, Deployment, WSEvent,
  SpecificationVersion, ArchitectureVersion, GovernancePolicy, GovernanceEvaluation,
  GovernanceReleaseGate, TestPlan, TraceabilityLink, RunSnapshot,
} from '@/types';

interface AppState {
  // Projects
  projects: Project[];
  selectedProject: Project | null;
  setProjects: (p: Project[]) => void;
  selectProject: (p: Project | null) => void;

  // Runs
  runs: Run[];
  selectedRun: Run | null;
  setRuns: (r: Run[]) => void;
  selectRun: (r: Run | null) => void;
  updateRunStatus: (id: string, status: Run['status']) => void;

  // Phases
  phases: Phase[];
  setPhases: (p: Phase[]) => void;
  updatePhase: (id: string, updates: Partial<Phase>) => void;

  // Agents
  agents: Agent[];
  setAgents: (a: Agent[]) => void;

  // Logs
  logs: LogEvent[];
  addLog: (log: LogEvent) => void;
  clearLogs: () => void;

  // Artifacts
  artifacts: Artifact[];
  addArtifact: (a: Artifact) => void;

  // Costs
  costReport: CostReport | null;
  setCostReport: (r: CostReport | null) => void;

  // Deployment
  deployment: Deployment | null;
  setDeployment: (d: Deployment | null) => void;

  // Live events
  liveEvents: WSEvent[];
  addLiveEvent: (e: WSEvent) => void;
  clearLiveEvents: () => void;

  // =============================================================================
  // PHASE 4: ENGINE STATE
  // =============================================================================

  // Specification
  currentSpec: SpecificationVersion | null;
  setCurrentSpec: (s: SpecificationVersion | null) => void;
  specVersions: SpecificationVersion[];
  setSpecVersions: (s: SpecificationVersion[]) => void;

  // Architecture
  currentArch: ArchitectureVersion | null;
  setCurrentArch: (a: ArchitectureVersion | null) => void;
  archVersions: ArchitectureVersion[];
  setArchVersions: (a: ArchitectureVersion[]) => void;

  // Governance
  governancePolicies: GovernancePolicy[];
  setGovernancePolicies: (p: GovernancePolicy[]) => void;
  governanceEvaluations: GovernanceEvaluation[];
  setGovernanceEvaluations: (e: GovernanceEvaluation[]) => void;
  releaseGates: GovernanceReleaseGate[];
  setReleaseGates: (g: GovernanceReleaseGate[]) => void;

  // Test Plan
  currentTestPlan: TestPlan | null;
  setCurrentTestPlan: (t: TestPlan | null) => void;

  // Traceability
  traceabilityLinks: TraceabilityLink[];
  setTraceabilityLinks: (l: TraceabilityLink[]) => void;

  // Snapshots
  snapshots: RunSnapshot[];
  setSnapshots: (s: RunSnapshot[]) => void;

  // UI state
  activeScreen: string;
  setActiveScreen: (s: string) => void;
  inspectorOpen: boolean;
  toggleInspector: () => void;
  selectedPhaseId: string | null;
  setSelectedPhaseId: (id: string | null) => void;
  commandInput: string;
  setCommandInput: (s: string) => void;
}

export const useStore = create<AppState>((set) => ({
  // Projects
  projects: [],
  selectedProject: null,
  setProjects: (projects) => set({ projects }),
  selectProject: (project) => set({ selectedProject: project }),

  // Runs
  runs: [],
  selectedRun: null,
  setRuns: (runs) => set({ runs }),
  selectRun: (run) => set({ selectedRun: run }),
  updateRunStatus: (id, status) =>
    set((s) => ({
      runs: s.runs.map((r) => (r.id === id ? { ...r, status } : r)),
      selectedRun: s.selectedRun?.id === id ? { ...s.selectedRun, status } : s.selectedRun,
    })),

  // Phases
  phases: [],
  setPhases: (phases) => set({ phases }),
  updatePhase: (id, updates) =>
    set((s) => ({
      phases: s.phases.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),

  // Agents
  agents: [],
  setAgents: (agents) => set({ agents }),

  // Logs
  logs: [],
  addLog: (log) => set((s) => ({ logs: [...s.logs, log] })),
  clearLogs: () => set({ logs: [] }),

  // Artifacts
  artifacts: [],
  addArtifact: (artifact) => set((s) => ({ artifacts: [...s.artifacts, artifact] })),

  // Costs
  costReport: null,
  setCostReport: (costReport) => set({ costReport }),

  // Deployment
  deployment: null,
  setDeployment: (deployment) => set({ deployment }),

  // Live events
  liveEvents: [],
  addLiveEvent: (event) => set((s) => ({ liveEvents: [...s.liveEvents, event] })),
  clearLiveEvents: () => set({ liveEvents: [] }),

  // =============================================================================
  // PHASE 4: ENGINE STATE INITIALIZERS
  // =============================================================================

  // Specification
  currentSpec: null,
  setCurrentSpec: (currentSpec) => set({ currentSpec }),
  specVersions: [],
  setSpecVersions: (specVersions) => set({ specVersions }),

  // Architecture
  currentArch: null,
  setCurrentArch: (currentArch) => set({ currentArch }),
  archVersions: [],
  setArchVersions: (archVersions) => set({ archVersions }),

  // Governance
  governancePolicies: [],
  setGovernancePolicies: (governancePolicies) => set({ governancePolicies }),
  governanceEvaluations: [],
  setGovernanceEvaluations: (governanceEvaluations) => set({ governanceEvaluations }),
  releaseGates: [],
  setReleaseGates: (releaseGates) => set({ releaseGates }),

  // Test Plan
  currentTestPlan: null,
  setCurrentTestPlan: (currentTestPlan) => set({ currentTestPlan }),

  // Traceability
  traceabilityLinks: [],
  setTraceabilityLinks: (traceabilityLinks) => set({ traceabilityLinks }),

  // Snapshots
  snapshots: [],
  setSnapshots: (snapshots) => set({ snapshots }),

  // UI
  activeScreen: 'command-center',
  setActiveScreen: (activeScreen) => set({ activeScreen }),
  inspectorOpen: true,
  toggleInspector: () => set((s) => ({ inspectorOpen: !s.inspectorOpen })),
  selectedPhaseId: null,
  setSelectedPhaseId: (selectedPhaseId) => set({ selectedPhaseId }),
  commandInput: '',
  setCommandInput: (commandInput) => set({ commandInput }),
}));
