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
```

## Calibration Review

Use the review template to assess calibration frames for Phase 2 zone setup:

```
docs/implementation/phase-1/calibration-review-template.md
```

**Note:** Rev04 captures evidence automatically, but zone selection remains manual.