# Phase 0 Revision 3 — Main Camera Pipeline

## Goal

- Build the first continuous frame-processing loop on top of `CameraSource`.
- Keep the loop narrow so later metrics and debug revisions can plug in cleanly.

## Scope

- In scope:
- Add `CameraPipeline` under `services/pipeline/`.
- Run a continuous `open -> read -> stop -> close` loop.
- Support optional `max_frames` for deterministic tests.
- Support optional OpenCV display via config.
- Wire the runner and `backend/scripts/run_camera.py` to real config + OpenCV camera startup.
- Add integration-style tests using `FakeCameraSource`.
- Out of scope:
- metrics collection
- debug frame writers
- detection, tracking, storage, alerts

## Tasks

- [x] Add `CameraPipeline` with clean shutdown behavior.
- [x] Catch `KeyboardInterrupt` and stop without leaking the camera resource.
- [x] Add backend runner wiring for config-driven local execution.
- [x] Add `backend/scripts/run_camera.py`.
- [x] Add fake-source integration tests for frame counting and cleanup.

## Testing

- `uv run pytest`
- `uv run ruff check .`
- Integration tests cover:
- exact `max_frames` processing
- end-of-stream shutdown
- source close on normal completion
- source close on `KeyboardInterrupt`

## Risks Or Open Questions

- Display support currently imports `cv2` lazily inside the pipeline; display-only failures will surface at runtime.
- The pipeline currently owns only loop control; metrics and debug hooks still need insertion points in later revisions.
- `backend/scripts/run_camera.py` adjusts `sys.path` for the local `src/` layout; that is acceptable for this thin runner script, but core logic stays in package modules.

## Exit Criteria

- [x] A `CameraSource` can be opened and consumed by a reusable pipeline class.
- [x] Fake camera tests prove deterministic frame counting.
- [x] The camera source always closes in normal and interrupt paths.
- [x] Local runner wiring exists for a config-driven OpenCV session.

## Result Summary

- Added `CameraPipeline` as the first orchestration service.
- Added config-driven runner wiring in `app/runner.py`.
- Added `backend/scripts/run_camera.py` for local execution from `backend/`.
- Added integration coverage for the fake camera pipeline path.
- Preserved a clean seam for Rev 4 metrics and Rev 5 debug writers.
