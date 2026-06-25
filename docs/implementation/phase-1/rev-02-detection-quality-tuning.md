# Phase 1 Revision 2 — Detection Quality Tuning

## Goal

- Measure and improve baseline person/bottle detection reliability before adding tracking or zones.

## Scope

- In scope:
- Add a simple YOLO model registry.
- Add a detection quality report for counts and average confidence.
- Add a benchmark script with model and confidence overrides.
- Group annotated outputs into `annotated/`, `person/`, `bottle/`, and `no_target/`.
- Add unit tests for the quality report and model registry.
- Out of scope:
- tracking, zones, pickup inference, storage, alerts, posture, LLM features

## Tasks

- [x] Add `model_registry.py`.
- [x] Add `quality_report.py`.
- [x] Add `scripts/benchmark_detection.py`.
- [x] Update detection config with `candidate_models`.
- [x] Group benchmark outputs by target presence.
- [x] Add unit tests for quality report and model registry.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- model candidate lookup
- supported-model checks
- detection quality counts and average confidence
- grouped renderer output behavior

## Risks Or Open Questions

- Quality tuning remains script-driven and manual; no persistent benchmark database exists yet.
- Average confidence is useful for comparison, but does not by itself measure spatial correctness or recall.
- Grouping outputs by class presence helps triage false negatives and no-target frames, but larger-scale evaluation will still require manual review.

## Exit Criteria

- [x] Detection benchmarking can run with model overrides.
- [x] Outputs are grouped into annotated, person, bottle, and no-target folders.
- [x] Quality summaries include class counts and average confidence.
- [x] Lint and tests pass after integration.

## Result Summary

- Added a small model registry for YOLO candidate names.
- Added a detection quality report for tuning sessions.
- Added `benchmark_detection.py` for RTSP tuning runs.
- Updated detection outputs to be grouped for easier inspection.
