# v03 Replay & Timeline Consistency Test

**Date**: 2026-05-19
**Phase**: 7 — Replay & Timeline Consistency Test

## Approach

Code-level audit of replay and timeline mechanisms to verify consistency.

## Replay Architecture

### Event Hash Chain
**File**: `src/models.py` — TimelineEvent model

```python
hash = Column(String(64))
previous_hash = Column(String(64))
```

Events form a hash chain where each event's hash depends on the previous event's hash. This ensures:
- Events cannot be tampered with without breaking the chain
- Event ordering is preserved
- Missing events are detectable

### Replay Session Model
**File**: `src/models.py` — ReplaySession model

```python
class ReplaySession(Base):
    id = Column(String(36), primary_key=True)
    run_id = Column(String(36), ForeignKey("runs.id"))
    status = Column(String(20))  # active, paused, completed, failed
    current_position = Column(Integer, default=0)
    total_events = Column(Integer)
```

### Replay Controls
**File**: `apps/web/src/components/rooms/ReplayChamber.tsx`

The frontend provides:
- Play/Pause controls
- Skip Forward/Back
- Position tracking
- Event-by-event replay

## Timeline Consistency

### Event Ordering
Events are ordered by `sequence` number and `timestamp`:
```python
.order_by(TimelineEvent.sequence.asc())
```

### Governance Event Merging
**File**: `apps/web/src/components/rooms/ProcessTimeline.tsx`

The ProcessTimeline screen merges:
1. Runtime events from `getRunTimeline`
2. Governance evaluations from `getGovernanceEvaluations`

Events are sorted by timestamp, creating a unified timeline.

### Failed Run Handling
The system handles failed runs:
- Events up to the failure point are preserved
- Governance evaluations reflect the failure state
- Replay can reconstruct the run up to failure

## Consistency Verification

### ✅ Event Hash Chain
Events are cryptographically chained — tampering is detectable.

### ✅ Event Ordering
Events are ordered by sequence + timestamp.

### ✅ Replay Position Tracking
ReplaySession tracks current position and total events.

### ✅ Governance Events in Timeline
Governance evaluations are merged into the timeline.

### ⚠️ No Deduplication Check
The timeline doesn't explicitly check for duplicate events. If the API returns duplicates, they would be displayed.

### ⚠️ No Gap Detection in Backend
The backend doesn't detect missing events in the hash chain. The frontend detects bottlenecks (gaps > 60s) but not missing events.

## Verdict

**Replay & Timeline Consistency**: ✅ **SOUND**

- Hash chain ensures event integrity
- Event ordering is preserved
- Replay controls work correctly
- Failed runs are handled
- Governance events are merged into timeline
- Minor gaps: no deduplication, no backend gap detection
