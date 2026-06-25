# Phase 1 Revision 1 — YOLO Detection Baseline

## Goal

- Run baseline object detection on RTSP frames.
- Save annotated detection frames for `person` and `bottle` only.

## Scope

- In scope:
- Add detection domain models and config.
- Add detector interface, YOLO adapter, filters, and rendering helpers.
- Add a detection runner script for RTSP sessions.
- Save annotated frames under `artifacts/detections/{session_name}/`.
- Add unit tests for models, filters, and renderer without requiring a real YOLO model.
- Out of scope:
- tracking, zones, event inference, storage, alerts, posture, LLM features

## Tasks

- [x] Add `Detection` and `BBox` models.
- [x] Add `DetectionConfig` and wire it into `AppConfig`.
- [x] Add YOLO detector adapter and filtering helpers.
- [x] Add annotated-frame renderer.
- [x] Add `scripts/run_detection.py`.
- [x] Add unit tests for detection models, filters, and renderer.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- detection model validation
- class/confidence filtering
- annotated frame save behavior

## Risks Or Open Questions

- The YOLO adapter loads Ultralytics lazily, so missing detection dependencies will fail at runtime rather than import time.
- This baseline uses a generic model and class-name filtering only; false positives and missed transparent bottles are expected validation targets.
- Detection is currently script-driven via a frame callback, not yet integrated into a richer event pipeline.

## Exit Criteria

- [x] RTSP frames can be sampled for detection every N frames.
- [x] Only `person` and `bottle` detections are kept after filtering.
- [x] Annotated detection frames are saved to a dedicated output folder.
- [x] Lint and tests pass without requiring a real YOLO model in unit tests.

## Result Summary

- Added detection config, models, detector interface, and YOLO adapter.
- Added filtering and annotated rendering for detection outputs.
- Added `run_detection.py` for RTSP detection runs.
- Added Phase 1 implementation docs and unit test coverage.
