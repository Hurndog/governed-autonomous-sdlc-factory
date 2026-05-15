# Replay Chamber Specification

## 1. Purpose

The Replay Chamber is NOT decorative UI. It is:
- **Forensic infrastructure** — reconstruct and inspect any execution
- **Explainability infrastructure** — understand why decisions were made
- **Governance inspection infrastructure** — audit governance decisions
- **Runtime debugging infrastructure** — diagnose failures and divergence

## 2. Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPLAY CHAMBER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │   ARTIFACT GRAPH     │  │   EXECUTION TIMELINE  │  │   GOVERNANCE    │  │
│  │                      │  │                       │  │                  │  │
│  │  [spec]──→[arch]    │  │  ●──●──●──●──●──●──●  │  │  ✅ no-missing  │  │
│  │    │        │        │  │  │  │  │  │  │  │  │  │  │  ❌ no-tests   │  │
│  │    ▼        ▼        │  │  ▼  ▼  ▼  ▼  ▼  ▼  ▼  │  │  ❌ coverage   │  │
│  │  [test]  [gov]      │  │  S1 S2 S3 S4 S5 S6 S7  │  │  ✅ readme     │  │
│  │    │        │        │  │                       │  │                  │  │
│  │    └────┬───┘        │  │  ◄──── Play ────►     │  │  [Details...]   │  │
│  │         ▼            │  │  Speed: 1x 2x 5x      │  │                  │  │
│  │     [snapshot]       │  │                       │  │                  │  │
│  │                      │  │                       │  │                  │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │   EVENT STREAM       │  │   ARTIFACT INSPECTOR  │  │   REPLAY DIFF   │  │
│  │                      │  │                       │  │                  │  │
│  │  18:44:35 pipeline.  │  │  Name: requirements   │  │  Baseline: 41   │  │
│  │  18:44:35 spec.gen   │  │  Type: specification  │  │  Replay: 41     │  │
│  │  18:44:35 spec.val   │  │  Phase: specification │  │  Match: ✅      │  │
│  │  18:44:35 arch.gen   │  │  Hash: abc123...      │  │                  │  │
│  │  18:44:35 gov.eval   │  │  Size: 7759 bytes     │  │  Divergence: 0  │  │
│  │  18:44:35 test.gen   │  │                       │  │  Score: 1.000   │  │
│  │  18:44:35 trace.link │  │  [View Content]       │  │                  │  │
│  │  18:44:35 snapshot   │  │  [View Lineage]       │  │  [Compare...]   │  │
│  │                      │  │                       │  │                  │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │   TELEMETRY OVERLAY                                                   │  │
│  │                                                                       │  │
│  │  Duration ████████████████████████████████████████ 601ms              │  │
│  │  Artifacts ████████████████████████████████████████ 41                │  │
│  │  Links     ████████████████████████████████████████ 76                │  │
│  │  Events    ████████████████████████████████████████ 84                │  │
│  │  Gov Pass  ████████████████████████████████████████ 6/10              │  │
│  │  Gov Fail  ████████████████████████████████████████ 4/10              │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. Component Specifications

### 3.1 Execution Timeline (Center)
- Chronological event stream
- Play/pause/rewind controls
- Speed control (1x, 2x, 5x)
- Step markers
- Error highlighting
- Click-to-inspect any event

### 3.2 Artifact Graph (Left)
- Interactive graph visualization
- Nodes: artifacts (color-coded by type)
- Edges: lineage links
- Click node → inspect artifact
- Click edge → inspect lineage
- Filter by type, phase, time

### 3.3 Governance Panel (Right)
- Policy evaluation results
- Pass/fail/warning indicators
- Click → view evidence
- Override history
- Remediation suggestions

### 3.4 Event Stream (Bottom-Left)
- Real-time event feed
- Filterable by type, severity
- Searchable
- Click → jump to timeline position

### 3.5 Artifact Inspector (Bottom-Center)
- Full artifact content viewer
- Metadata display
- Hash verification
- Lineage traversal
- Download capability

### 3.6 Replay Diff Engine (Bottom-Right)
- Baseline vs replay comparison
- Divergence highlighting
- Integrity score display
- Export comparison report

### 3.7 Telemetry Overlay (Bottom)
- Key metrics at a glance
- Visual bar charts
- Threshold indicators
- Trend arrows (vs baseline)

## 4. Interaction Model

### 4.1 Navigation
- **Timeline scrubbing** → updates all panels to that point in time
- **Artifact selection** → highlights lineage, shows governance, loads content
- **Event selection** → jumps to timeline position, shows context
- **Governance selection** → shows affected artifacts, evidence, reasoning

### 4.2 Replay Controls
```
[◄◄] [◄] [▶/❚❚] [►] [►►]  Speed: [1x ▼]  Loop: [ ]
```
- Play/Pause: Start/stop timeline playback
- Step forward/backward: Move one event at a time
- Skip to start/end: Jump to beginning/end
- Speed: 1x, 2x, 5x playback speed
- Loop: Continuous replay

### 4.3 Comparison Mode
```
Baseline: [FIRST_OPERATIONAL_VERTICAL_SLICE ▼]
Replay:   [Run 2 ▼]
[Compare]
```
- Select baseline and replay runs
- Side-by-side timeline comparison
- Divergence highlighting
- Export comparison report

## 5. API Endpoints

```
GET  /api/v1/replay/runs/{run_id}/timeline          # Full timeline
GET  /api/v1/replay/runs/{run_id}/artifacts          # Artifact graph data
GET  /api/v1/replay/runs/{run_id}/governance         # Governance results
GET  /api/v1/replay/runs/{run_id}/events             # Event stream
GET  /api/v1/replay/runs/{run_id}/telemetry          # Telemetry data
GET  /api/v1/replay/artifacts/{id}/content           # Artifact content
GET  /api/v1/replay/artifacts/{id}/lineage           # Lineage subtree
GET  /api/v1/replay/runs/{run_id}/snapshot           # Snapshot data
POST /api/v1/replay/compare                          # Compare two runs
GET  /api/v1/replay/runs/{run_id}/export             # Export full replay package
```

## 6. Implementation Phases

### Phase 1: Backend (Current)
- Timeline reconstruction API
- Artifact graph API
- Governance inspection API
- Replay comparison API

### Phase 2: Frontend Shell (Next)
- Timeline component
- Artifact graph component
- Basic navigation

### Phase 3: Full Chamber (Future)
- All panels
- Replay controls
- Comparison mode
- Telemetry overlay
- Export functionality
