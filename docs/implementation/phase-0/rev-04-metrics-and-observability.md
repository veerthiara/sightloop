# Phase 0 Revision 4 — Metrics and Observability

## Goal

- Add testable runtime metrics before any inference or debug artifact writing.
- Keep metrics logic modular so Rev 5 can attach evidence capture without rewriting the loop.

## Scope

- In scope:
- Add FPS tracking utilities under `services/metrics/`.
- Add session summary tracking for camera runs.
- Feed metrics from `CameraPipeline` on each processed frame.
- Emit periodic metrics snapshots and a final session summary.
- Add unit tests for metrics math and summary serialization.
- Extend pipeline integration tests to assert session summaries and cleanup.
- Out of scope:
- detection, tracking, storage, alerts
- frame saving or clip writing
- complex structured logging backends

## Tasks

- [x] Add `FpsTracker` with deterministic timestamp support.
- [x] Add `CameraSessionStats` with serializable summaries.
- [x] Update `CameraPipeline` to integrate optional metrics services.
- [x] Wire runner output to print final session metrics.
- [x] Add unit tests for tracker/session math.
- [x] Extend integration tests for metrics and failure cleanup.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- average/current/rolling FPS math
- serializable session summaries
- reset behavior
- Integration coverage includes:
- final session summary population
- periodic metrics logging by frame interval
- source cleanup on read failure

## Risks Or Open Questions

- Periodic logging currently uses simple console strings, which is enough for benchmarking but not yet structured JSONL.
- The pipeline emits metrics snapshots but does not yet separate human logs from machine-readable output.
- Session duration and average FPS intentionally rely on processed-frame timestamps, not wall-clock shutdown time, to keep deterministic tests stable.

## Exit Criteria

- [x] Runtime FPS metrics are available from a dedicated service.
- [x] Session summary stats are serializable and testable.
- [x] The pipeline can emit periodic metrics and a final summary without owning FPS math.
- [x] Lint and test suites pass after integration.

## Result Summary

- Added `FpsTracker` and `CameraSessionStats` under `services/metrics/`.
- Updated `CameraPipeline` to record metrics on each processed frame.
- Added periodic metrics snapshots and final session summaries.
- Updated the local runner to print useful metrics at shutdown.
- Added unit and integration coverage for observability behavior.
