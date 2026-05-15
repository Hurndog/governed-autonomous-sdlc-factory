import { create } from 'zustand';
import type {
  RuntimeHealth,
  Pipeline,
  ReplaySession,
  GovernanceFinding,
  ModelStatus,
  TokenUsage,
  Artifact,
  Specification,
  Architecture,
} from './types';

interface AppState {
  // Navigation
  activeRoom: string;
  setActiveRoom: (room: string) => void;

  // Runtime
  health: RuntimeHealth | null;
  setHealth: (h: RuntimeHealth | null) => void;

  // Pipelines
  pipelines: Pipeline[];
  setPipelines: (p: Pipeline[]) => void;
  activePipeline: Pipeline | null;
  setActivePipeline: (p: Pipeline | null) => void;

  // Replay
  replaySessions: ReplaySession[];
  setReplaySessions: (r: ReplaySession[]) => void;
  activeReplaySession: ReplaySession | null;
  setActiveReplaySession: (r: ReplaySession | null) => void;
  replayTimelinePosition: number;
  setReplayTimelinePosition: (pos: number) => void;

  // Governance
  governanceFindings: GovernanceFinding[];
  setGovernanceFindings: (g: GovernanceFinding[]) => void;

  // Models
  modelStatuses: ModelStatus[];
  setModelStatuses: (m: ModelStatus[]) => void;
  tokenUsage: TokenUsage | null;
  setTokenUsage: (t: TokenUsage | null) => void;

  // Artifacts
  artifacts: Artifact[];
  setArtifacts: (a: Artifact[]) => void;

  // Spec
  specifications: Specification[];
  setSpecifications: (s: Specification[]) => void;
  activeSpec: Specification | null;
  setActiveSpec: (s: Specification | null) => void;

  // Architecture
  architectures: Architecture[];
  setArchitectures: (a: Architecture[]) => void;
  activeArch: Architecture | null;
  setActiveArch: (a: Architecture | null) => void;

  // WebSocket
  wsConnected: boolean;
  setWsConnected: (c: boolean) => void;

  // Sidebar
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (c: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  activeRoom: 'command-center',
  setActiveRoom: (room) => set({ activeRoom: room }),

  health: null,
  setHealth: (h) => set({ health: h }),

  pipelines: [],
  setPipelines: (p) => set({ pipelines: p }),
  activePipeline: null,
  setActivePipeline: (p) => set({ activePipeline: p }),

  replaySessions: [],
  setReplaySessions: (r) => set({ replaySessions: r }),
  activeReplaySession: null,
  setActiveReplaySession: (r) => set({ activeReplaySession: r }),
  replayTimelinePosition: 0,
  setReplayTimelinePosition: (pos) => set({ replayTimelinePosition: pos }),

  governanceFindings: [],
  setGovernanceFindings: (g) => set({ governanceFindings: g }),

  modelStatuses: [],
  setModelStatuses: (m) => set({ modelStatuses: m }),
  tokenUsage: null,
  setTokenUsage: (t) => set({ tokenUsage: t }),

  artifacts: [],
  setArtifacts: (a) => set({ artifacts: a }),

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
}));
