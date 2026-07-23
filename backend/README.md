# SightLoop Vision Backend

Camera-first vision service package for the SightLoop Vision project.

Typical commands:

```bash
# Run tests and lint
uv run pytest
uv run ruff check .

# Run camera pipeline (debug frames only)
uv run python scripts/run_camera.py --config configs/dev.yaml

# Run detection on RTSP stream
uv run python scripts/run_detection.py --config configs/jetson.yaml

# Run detection benchmark with quality gates and baseline reports
uv run python scripts/benchmark_detection.py --config configs/jetson.yaml --write-baseline

# Capture calibration frames for multi-position setup
uv run python scripts/capture_calibration_frames.py --config configs/dev.yaml \
  --position-label desk-front-angle --session-name calib-desk-front-angle \
  --max-frames 300 --save-every-n-frames 10 --notes "Front angle, morning light"

# Repeat for other positions
uv run python scripts/capture_calibration_frames.py --config configs/dev.yaml \
  --position-label desk-top-angle --session-name calib-desk-top-angle \
  --max-frames 300 --save-every-n-frames 10 --notes "Top-down angle"

uv run python scripts/capture_calibration_frames.py --config configs/dev.yaml \
  --position-label desk-evening-light --session-name calib-desk-evening \
  --max-frames 300 --save-every-n-frames 10 --notes "Evening lamp light"

# Run tracking with zones (Phase 2 Rev01)
export TAPO_RTSP_URL='rtsp://USER:PASSWORD@CAMERA_IP:554/stream1'
uv run python scripts/run_tracking.py --config configs/jetson.yaml --max-frames 300

# Run tracking with zone calibration report (Phase 2 Rev02)
export TAPO_RTSP_URL='rtsp://USER:PASSWORD@CAMERA_IP:554/stream1'
uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --write-zone-report \
  --zone-notes "Fixed right-side desk camera. Initial zone calibration run."

# Run diagnostics only (no camera)
uv run python scripts/run_tracking.py --config configs/jetson.yaml --diagnostics-only

# Run with zone validation
uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --require-zones \
  --warn-if-no-bottle \
  --write-zone-report \
  --zone-notes "Fixed right-side desk camera. Zone sanity run."
```

## Artifact Structure

After running the above commands, artifacts are organized as:

```
artifacts/
├── frames/              # Raw debug frames from run_camera.py
│   └── {session_name}/
├── detections/          # Detection outputs from run_detection.py / benchmark
│   └── {session_name}/
│       ├── annotated/   # All frames with bounding boxes
│       ├── person/      # Frames containing person detections
│       ├── bottle/      # Frames containing bottle detections
│       └── no_target/   # Frames with no target detections
├── baselines/           # Automated baseline reports from benchmark
│   └── {session_name}/
│       ├── detection-baseline.json
│       └── detection-baseline.md
├── calibration/         # Calibration reference frames
│   └── {session_name}/
│       ├── frames/              # Clean reference frames
│       ├── manifest.json        # Capture metadata
│       └── contact_sheet.jpg    # Visual overview (optional)
└── tracking/            # Tracking outputs from run_tracking.py
    └── {session_name}/
        ├── annotated/   # Frames with zones, tracks, and IDs
└── zones/               # Zone calibration reports
    └── {session_name}/
        ├── zone-calibration-report.json
        ├── zone-calibration-report.md
        └── zone-state-summary.json
```

## Calibration Review

Use the review template to assess calibration frames for Phase 2 zone setup:

```
docs/implementation/phase-1/calibration-review-template.md
```

**Note:** Rev04 captures evidence automatically, but zone selection remains manual.

## Zone Calibration Workflow (Phase 2 Rev03)

1. **Run tracking with diagnostics:**
   ```bash
   uv run python scripts/run_tracking.py --config configs/jetson.yaml --diagnostics-only
   ```

2. **Run tracking with zone report:**
   ```bash
   uv run python scripts/run_tracking.py \
     --config configs/jetson.yaml \
     --max-frames 300 \
     --write-zone-report \
     --zone-notes "Fixed right-side desk camera. Initial zone calibration run."
   ```

3. **Review annotated frames** in `artifacts/tracking/{session}/`:
   - Green rectangle = `bottle_home` zone
   - Blue rectangle = `desk` zone
   - Track labels show zone membership (e.g., `ID:1 (age:5) bottle_home,desk`)

4. **Check zone report** in `artifacts/zones/{session}/zone-calibration-report.md`:
   - Zone hit counts by class
   - Track counts by class
   - Zone entry/exit events
   - Frames inside zone per track
   - Review checklist for manual verification

5. **Adjust zones** in `configs/jetson.yaml`:
   ```yaml
   zones:
     - name: bottle_home
       type: rectangle
       x1: 550   # Adjust left edge
       y1: 420   # Adjust top edge
       x2: 900   # Adjust right edge
       y2: 750   # Adjust bottom edge
   ```

6. **Re-run and verify** - repeat until zones align with actual object positions.

## New CLI Options (Rev03)

| Flag | Description |
|------|-------------|
| `--diagnostics-only` | Load config, print diagnostics, exit without camera |
| `--require-zones` | Fail fast if no zones configured |
| `--warn-if-no-bottle` | Warning if zero bottle tracks created |
| `--write-zone-report` | Write JSON + Markdown zone calibration reports |
| `--zone-notes` | Notes to include in zone calibration report |

## Why Visible Bottle ≠ YOLO Detection

- **Occlusion**: Hand holding bottle covers most visual features
- **Pose change**: Bottle tilted/horizontal vs vertical training pose
- **Confidence drop**: Partial visibility drops confidence below threshold
- **Class confusion**: Blue bottle may resemble "cup" or "vase" to COCO-trained model

This revision adds diagnostics to catch these issues before pickup inference.