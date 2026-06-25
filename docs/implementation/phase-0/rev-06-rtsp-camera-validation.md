# Phase 0 Revision 6 — RTSP Camera Hardware Validation

## Goal

- Prove that the Phase 0 camera pipeline runs cleanly against a real RTSP camera.
- Validate runtime, metrics, and debug frame capture before adding YOLO.

## Scope

- In scope:
- Add a dedicated RTSP validation script.
- Add a serializable validation report helper with credential masking.
- Update Jetson config to use `TAPO_RTSP_URL` instead of committed credentials.
- Add tests for validation summary behavior and secret masking.
- Update README with RTSP validation commands.
- Out of scope:
- detection, tracking, event inference, storage, alerts, LLM layers
- custom RTSP reconnect logic
- USB camera optimization

## Tasks

- [x] Add `services/validation/camera_validation.py`.
- [x] Add `scripts/validate_camera_setup.py`.
- [x] Update config loading to expand `${ENV_VAR}` placeholders.
- [x] Update `configs/jetson.yaml` for env-backed RTSP configuration.
- [x] Add unit tests for validation report masking and env config expansion.
- [x] Update README with RTSP/Tapo validation commands.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- credential masking for RTSP URLs
- serializable validation report summaries
- env-var config expansion and missing-env failures

## Risks Or Open Questions

- The validation script currently reports failure cleanly, but does not implement RTSP reconnect or retry behavior.
- Real RTSP behavior will still depend on OpenCV build quality and the camera’s stream stability.
- The committed repo intentionally documents env-driven RTSP setup but does not store the actual Tapo credentials.

## Exit Criteria

- [x] Jetson config can reference RTSP via `TAPO_RTSP_URL`.
- [x] Validation summaries mask credentials in logs.
- [x] A dedicated RTSP validation entry point exists using the current pipeline, metrics, and debug writers.
- [x] Lint and tests pass after integration.

## Result Summary

- Added a dedicated RTSP validation script and summary helper.
- Added safe credential masking for RTSP URLs in summaries.
- Updated config loading to support `${ENV_VAR}` placeholders.
- Updated README and Jetson config for Tapo-style validation workflows.
