# Phase 0 Revision 5 — Debug Evidence Capture

## Goal

- Save lightweight visual evidence from the camera pipeline for later inspection.
- Keep debug capture separate from inference and event logic.

## Scope

- In scope:
- Add a `FrameWriter` under `services/debug/`.
- Add a minimal `ClipWriter` placeholder for a later revision.
- Extend config with debug enablement, output directory, and save interval by frame count.
- Wire optional frame saving into the camera pipeline and local runner.
- Add unit and integration tests for save interval behavior and saved output.
- Out of scope:
- full video clip recording
- detection, tracking, storage, alerts
- complex artifact management or metadata indexing

## Tasks

- [x] Add `FrameWriter` with deterministic filenames and per-session folders.
- [x] Add `ClipWriter` placeholder interface.
- [x] Update `CameraPipeline` to call the frame writer optionally.
- [x] Update configs and runner wiring for debug capture.
- [x] Add unit tests for frame writing and interval logic.
- [x] Extend pipeline integration tests for saved debug output.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- frame writer enable/disable behavior
- deterministic output paths
- save interval selection
- Integration coverage includes:
- expected saved frame count through the pipeline
- saved filenames for fake-camera runs
- final summary includes saved frame count

## Risks Or Open Questions

- The current implementation writes portable pixmap (`.ppm`) images to avoid adding new runtime image dependencies in this revision.
- Clip writing is intentionally a no-op placeholder so the pipeline seam exists without taking on video lifecycle complexity yet.
- Debug output directory now lives in `debug.output_dir`, but the runner still falls back to `output.frames_dir` when the override is omitted.

## Exit Criteria

- [x] The pipeline can save debug frames without coupling to inference logic.
- [x] Saved frames use deterministic filenames grouped by session.
- [x] Debug frame capture can be disabled cleanly.
- [x] Lint and tests pass with debug capture enabled.

## Result Summary

- Added `FrameWriter` and `ClipWriter` under `services/debug/`.
- Updated debug config and runtime wiring for optional evidence capture.
- Extended the pipeline to save selected frames and report saved frame counts.
- Added unit and integration coverage for debug evidence behavior.
