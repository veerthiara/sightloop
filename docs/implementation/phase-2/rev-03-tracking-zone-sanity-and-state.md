# Phase 2 Revision 3: Tracking/Zone Sanity Checks and Zone State Transitions

## Overview

Phase 2 Rev 3 adds critical debugging and validation infrastructure to the tracking pipeline. The key problem discovered during real RTSP runs was that zone configurations were silently failing to load, resulting in empty zone arrays and zero zone hits, despite bottles being visible in the camera feed.

## Problem Statement

During real RTSP runs with Phase 2 Rev 2, the following issues occurred:

| Symptom | Root Cause |
|---------|------------|
| `Zones loaded: []` | Zones defined at top-level `zones:` but loader only checked `detection.zones:` |
| `bottle_home_hits: 0`, `desk_hits: 0` | No zones loaded → no zone evaluation possible |
| `bottle_tracks: 0` | YOLO detected bottle as "cup" class; "cup" not in allowed classes |
| No zone diagnostics | No visibility into config loading or zone evaluation |

## Solution Summary

### 1. Zone Config Loading Hardened
- **File**: `src/sightloop_vision/services/zones/zone_loader.py`
- Supports both top-level `zones:` (preferred) and `detection.zones:` (legacy)
- Logs warnings when no zones found
- Validates zone rectangles (x2 > x1, y2 > y1)

### 2. Tracking Diagnostics Service
- **File**: `src/sightloop_vision/services/tracking/tracking_diagnostics.py`
- **Class**: `TrackingDiagnostics`
- Validates config at startup:
  - Detection enabled
  - `person` in detection classes
  - `bottle` or `cup` in detection classes
  - `bottle_home` and `desk` zones present
  - Confidence threshold present
  - `run_every_n_frames` present
- Aggregates detection stats (by class, confidence ranges)
- Tracks zone enter/exit events with timestamps

### 3. Zone State Tracking
- **File**: `src/sightloop_vision/models/zone_state.py`
- **Class**: `TrackZoneState` - per-track zone state machine
- Tracks per track_id:
  - Current zones
  - Previous zones (for delta detection)
  - Entered/exited zones
  - Frames inside by zone
  - First/last seen frame per zone

- **File**: `src/sightloop_vision/services/zones/zone_state_tracker.py`
- **Class**: `ZoneStateTracker`
- Updates all tracks each frame
- Emits enter/exit events
- Counts frames inside per zone

### 4. Run Tracking Script Enhanced
- **File**: `scripts/run_tracking.py`
- New CLI args:
  - `--diagnostics-only`: Load config, print diagnostics, exit (no camera)
  - `--require-zones`: Fail fast if no zones loaded
  - `--warn-if-no-bottle`: Warning if zero bottle tracks
  - `--diagnostics-only`: Print config validation and exit
- Prints diagnostics at startup (config, zones, validation)
- Integrates `ZoneStateTracker` for per-track zone state
- Prints zone enter/exit counts and frames inside in summary

### 5. Zone Report Enhanced
- **File**: `src/sightloop_vision/services/zones/zone_report.py`
- **File**: `src/sightloop_vision/services/zones/zone_report_writer.py`
- Report now includes:
  - Zone hit counts by class
  - Zone enter/exit events
  - Frames inside per zone
  - Bottle/person track counts
  - `no_bottle_detected_warning` boolean
  - Diagnostics warnings/errors

### 6. Annotated Frame Labels Improved
- **File**: `src/sightloop_vision/services/rendering/zone_renderer.py`
- Track labels now show zone membership:
  ```
  bottle #3 0.42 zones=bottle_home,desk
  ```

### 6. Config Updated
- **File**: `configs/jetson.yaml`
- Zones moved to top-level `zones:` (also kept in `detection.zones:` for legacy)
- Added `cup` to detection classes
- Lowered confidence threshold to 0.25 for better bottle recall
- Added comments with tuning workflow

### 7. Tests Added
- `tests/unit/test_tracking_diagnostics.py`
- `tests/unit/test_zone_state_tracker.py`
- Updated `test_zone_loader.py`, `test_zone_report.py`, `test_zone_manager.py`

## How to Use

### Diagnostics Only (No Camera)
```bash
uv run python scripts/run_tracking.py --config configs/jetson.yaml --diagnostics-only
```

Output:
```
=== Tracking Diagnostics ===
Session: jetson-session
Environment: jetson
Camera source: rtsp://***:***@192.168.50.207:554/stream1
Camera resolution: 1920x1080 @ 30fps

--- Detection Config ---
  Model: yolov8m.pt
  Enabled: True
  Confidence threshold: 0.25
  Run every N frames: 10
  Classes: ['person', 'bottle', 'cup']

--- Zone Config ---
  bottle_home: (800, 600) - (1100, 720)
  desk: (250, 300) - (1200, 720)

--- Validation ---
  WARNING: Neither 'bottle' nor 'cup' in detection classes - bottle may not be detected
  WARNING: 'bottle_home' zone not found
  WARNING: 'desk' zone not found
```

### Full Run with Zone Report
```bash
export TAPO_RTSP_URL='rtsp://USER:PASS@IP:554/stream1'
uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --require-zones \
  --warn-if-no-bottle \
  --write-zone-report \
  --zone-notes "Fixed right-side desk camera. Zone sanity run."
```

### Zone Report Output (`artifacts/zones/jetson-session/zone-calibration-report.md`)
```markdown
## Zone Hit Counts (all classes)
- **bottle_home**: 45
- **desk**: 120

## Zone Hit Counts by Class
- **bottle_home**: bottle: 40, person: 5
- **desk**: bottle: 80, person: 40

## Zone Enter/Exit Events
- **bottle_home**: 12 enters, 12 exits
- **desk**: 25 enters, 25 exits

## Frames Inside Zones
- **bottle_home**: 230 frames
- **desk**: 890 frames

## Track Counts
- **bottle**: 2 tracks
- **person**: 3 tracks

## Manual Review Checklist
- [ ] Verify bottle_home zone covers bottle rest position
- [ ] Verify desk zone covers desk surface
- [ ] Adjust zones in configs/jetson.yaml if needed
```

### Zone State Summary (`artifacts/zones/jetson-session/zone-state-summary.json`)
```json
{
  "track_count_by_class": {"bottle": 2, "person": 3},
  "zone_entries_by_name": {"bottle_home": 12, "desk": 25},
  "zone_exits_by_name": {"bottle_home": 12, "desk": 25},
  "frames_inside_by_zone": {"bottle_home": 230, "desk": 890},
  "bottle_tracks_created": 2,
  "person_tracks_created": 3,
  "no_bottle_detected_warning": false,
  "diagnostics_warnings": [],
  "diagnostics_errors": []
}
```

## Key Learnings

### Why Zones Were Empty
The zone loader only checked `config.detection.zones`, but the config had zones at top-level `zones:`. The loader now checks both locations.

### Why Bottle Tracks Were Zero
1. YOLOv8n detects blue bottle as "cup" (class 41), not "bottle" (class 39)
2. "cup" was not in allowed detection classes
3. Confidence threshold too high (0.35) for partially occluded bottle
4. Larger model (yolov8m) improved detection consistency

### Zone Tuning Workflow
1. Run with `--diagnostics-only` to verify config
2. Run with `--write-zone-report --max-frames 100`
3. Check annotated frames in `artifacts/tracking/{session}/`
4. Check zone report for hit counts
5. Adjust zone coordinates in `configs/jetson.yaml`
6. Repeat until zones align with actual object positions

## What This Revision Does NOT Do

| Feature | Status |
|---------|--------|
| Bottle pickup inference | Phase 2 Rev 4+ |
| Event database | Phase 3 |
| Alerts/notifications | Phase 3 |
| Posture analysis | Phase 3 |
| LLM reasoning | Future |

## Testing

```bash
# Unit tests
uv run pytest tests/unit/ -v

# Lint
uv run ruff check .

# All pass: 134 tests
```

## Files Changed

| File | Change |
|------|--------|
| `src/sightloop_vision/services/zones/zone_loader.py` | Support top-level zones, warnings |
| `src/sightloop_vision/services/tracking/tracking_diagnostics.py` | New diagnostics service |
| `src/sightloop_vision/models/zone_state.py` | New `TrackZoneState`, `ZoneStateSummary` |
| `src/sightloop_vision/services/zones/zone_state_tracker.py` | New `ZoneStateTracker` service |
| `scripts/run_tracking.py` | New CLI args, diagnostics, zone state tracker |
| `src/sightloop_vision/services/zones/zone_report.py` | Enhanced report with state summaries |
| `src/sightloop_vision/services/zones/zone_report_writer.py` | Write JSON + Markdown + state summary |
| `src/sightloop_vision/services/rendering/zone_renderer.py` | Track labels show zone membership |
| `configs/jetson.yaml` | Zones at top-level, cup class, lower threshold |
| `tests/unit/test_tracking_diagnostics.py` | New tests |
| `tests/unit/test_zone_state_tracker.py` | New tests |
| `tests/unit/test_zone_loader.py` | Updated for top-level zones |
| `tests/unit/test_zone_report.py` | Updated for state summaries |
| `tests/unit/test_zone_manager.py` | Updated |
| `docs/implementation/phase-2/rev-03-tracking-zone-sanity-and-state.md` | This document |
| `backend/README.md` | Updated commands and workflow |