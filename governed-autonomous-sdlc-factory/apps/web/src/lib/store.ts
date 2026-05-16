import { create } from 'zustand';
import type {
  RuntimeHealth,
  RunItem,
  ReplaySession,
  GovernanceEvaluation,
  GovernancePolicy,
  ReleaseGate,
  ArtifactItem,
  ArtifactDetail,
  ProviderStatus,
  LogEntry,
  CostReport,
  TraceabilityLink,
  IntegrityResponse,
  EvidenceBundle,
  ProjectItem,
  ModelStatusResponse,
  SpecificationItem,
  SpecificationDetail,
  ArchitectureItem,
  ArchitectureDetail,
} from './types';

interface AppState {
  // Navigation
  activeRoom: string;
  setActiveRoom: (room: string) => void;

  // Runtime
  health: RuntimeHealth | null;
  setHealth: (h: RuntimeHealth | null) => void;

  // Runs
  runs: RunItem[];
  setRuns: (r: RunItem[]) => void;
  selectedRunId: string | null;
  setSelectedRunId: (id: string | null) => void;
  selectedRunDetail: RunItem | null;
  setSelectedRunDetail: (r: RunItem | null) => void;

  // Timeline
  timelineEvents: Array<{ id: string; sequence: number; type: string; timestamp: string; phase?: string; data?: Record<string, unknown>; hash?: string }>;
  setTimelineEvents: (e: Array<{ id: string; sequence: number; type: string; timestamp: string; phase?: string; data?: Record<string, unknown>; hash?: string }>) => void;

  // Replay
  replaySessions: ReplaySession[];
  setReplaySessions: (r: ReplaySession[]) => void;
  activeReplaySession: ReplaySession | null;
  setActiveReplaySession: (r: ReplaySession | null) => void;
  replayTimelinePosition: number;
  setReplayTimelinePosition: (pos: number) => void;

  // Governance
  governanceEvaluations: GovernanceEvaluation[];
  setGovernanceEvaluations: (g: GovernanceEvaluation[]) => void;
  governancePolicies: GovernancePolicy[];
  setGovernancePolicies: (p: GovernancePolicy[]) => void;
  releaseGates: ReleaseGate[];
  setReleaseGates: (g: ReleaseGate[]) => void;

  // Traceability
  traceabilityLinks: TraceabilityLink[];
  setTraceabilityLinks: (l: TraceabilityLink[]) => void;

  // Integrity
  integrityResult: IntegrityResponse | null;
  setIntegrityResult: (r: IntegrityResponse | null) => void;
  integrityLoading: boolean;
  setIntegrityLoading: (l: boolean) => void;

  // Artifacts
  artifacts: ArtifactItem[];
  setArtifacts: (a: ArtifactItem[]) => void;

  // Evidence
  evidenceBundles: EvidenceBundle[];
  setEvidenceBundles: (b: EvidenceBundle[]) => void;

  // Models
  modelStatus: ModelStatusResponse | null;
  setModelStatus: (m: ModelStatusResponse | null) => void;

  // Logs
  logs: LogEntry[];
  setLogs: (l: LogEntry[]) => void;

  // Costs
  costReport: CostReport | null;
  setCostReport: (c: CostReport | null) => void;

  // Projects
  projects: ProjectItem[];
  setProjects: (p: ProjectItem[]) => void;

  // Spec
  specifications: SpecificationItem[];
  setSpecifications: (s: SpecificationItem[]) => void;
  activeSpec: SpecificationDetail | null;
  setActiveSpec: (s: SpecificationDetail | null) => void;

  // Architecture
  architectures: ArchitectureItem[];
  setArchitectures: (a: ArchitectureItem[]) => void;
  activeArch: ArchitectureDetail | null;
  setActiveArch: (a: ArchitectureDetail | null) => void;

  // WebSocket
  wsConnected: boolean;
  setWsConnected: (c: boolean) => void;

  // Sidebar
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (c: boolean) => void;

  // Loading states
  globalLoading: boolean;
  setGlobalLoading: (l: boolean) => void;

  // Errors
  lastError: string | null;
  setLastError: (e: string | null) => void;

  // Legacy compatibility (for existing components)
  pipelines: RunItem[];
  setPipelines: (p: RunItem[]) => void;
  activePipeline: RunItem | null;
  setActivePipeline: (p: RunItem | null) => void;
  governanceFindings: GovernanceEvaluation[];
  setGovernanceFindings: (g: GovernanceEvaluation[]) => void;
  modelStatuses: ProviderStatus[];
  setModelStatuses: (m: ProviderStatus[]) => void;
  tokenUsage: CostReport | null;
  setTokenUsage: (t: CostReport | null) => void;
}

export const useStore = create<AppState>((set) => ({
  activeRoom: 'command-center',
  setActiveRoom: (room) => set({ activeRoom: room }),

  health: null,
  setHealth: (h) => set({ health: h }),

  runs: [],
  setRuns: (r) => set({ runs: r, pipelines: r }),
  selectedRunId: null,
  setSelectedRunId: (id) => set({ selectedRunId: id }),
  selectedRunDetail: null,
  setSelectedRunDetail: (r) => set({ selectedRunDetail: r, activePipeline: r }),

  timelineEvents: [],
  setTimelineEvents: (e) => set({ timelineEvents: e }),

  replaySessions: [],
  setReplaySessions: (r) => set({ replaySessions: r }),
  activeReplaySession: null,
  setActiveReplaySession: (r) => set({ activeReplaySession: r }),
  replayTimelinePosition: 0,
  setReplayTimelinePosition: (pos) => set({ replayTimelinePosition: pos }),

  governanceEvaluations: [],
  setGovernanceEvaluations: (g) => set({ governanceEvaluations: g, governanceFindings: g }),
  governancePolicies: [],
  setGovernancePolicies: (p) => set({ governancePolicies: p }),
  releaseGates: [],
  setReleaseGates: (g) => set({ releaseGates: g }),

  traceabilityLinks: [],
  setTraceabilityLinks: (l) => set({ traceabilityLinks: l }),

  integrityResult: null,
  setIntegrityResult: (r) => set({ integrityResult: r }),
  integrityLoading: false,
  setIntegrityLoading: (l) => set({ integrityLoading: l }),

  artifacts: [],
  setArtifacts: (a) => set({ artifacts: a }),

  evidenceBundles: [],
  setEvidenceBundles: (b) => set({ evidenceBundles: b }),

  modelStatus: null,
  setModelStatus: (m) => set({ modelStatus: m }),
  logs: [],
  setLogs: (l) => set({ logs: l }),

  costReport: null,
  setCostReport: (c) => set({ costReport: c, tokenUsage: c }),

  projects: [],
  setProjects: (p) => set({ projects: p }),

  specifications: [],
  setSpecifications: (s) => set({ specifications: s }),
  activeSpec: null,
  setActiveSpec: (s) => set({ activeSpec: s }),

  architectures: [],
  setArchitectures: (a) => set({ architectures: a }),
  activeArch: null,
  setActiveArch: (a) => set({ activeArch: a }),

  wsConnected: false,
  setWsConnected: (c) => set({ wsConnected: c }),

  sidebarCollapsed: false,
  setSidebarCollapsed: (c) => set({ sidebarCollapsed: c }),

  globalLoading: false,
  setGlobalLoading: (l) => set({ globalLoading: l }),

  lastError: null,
  setLastError: (e) => set({ lastError: e }),

  // Legacy
  pipelines: [],
  setPipelines: (p) => set({ pipelines: p, runs: p }),
  activePipeline: null,
  setActivePipeline: (p) => set({ activePipeline: p, selectedRunDetail: p }),
  governanceFindings: [],
  setGovernanceFindings: (g) => set({ governanceFindings: g, governanceEvaluations: g }),
  modelStatuses: [],
  setModelStatuses: (m) => set({ modelStatuses: m }),
  tokenUsage: null,
  setTokenUsage: (t) => set({ tokenUsage: t, costReport: t }),
}));
