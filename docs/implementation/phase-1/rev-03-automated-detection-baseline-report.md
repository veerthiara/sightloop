# Phase 1 Revision 3 — Automated Detection Baseline Report

## Goal

- Generate machine-readable and human-readable baseline reports from detection benchmarks.
- Reduce manual bookkeeping while keeping visual review mandatory.

## Scope

- In scope:
- Add a serializable detection baseline report model.
- Add a baseline writer for JSON and Markdown outputs.
- Add simple automated quality gate logic.
- Extend `benchmark_detection.py` with baseline-writing flags and gate thresholds.
- Add unit tests for baseline reports, writers, and quality gates.
- Out of scope:
- tracking, zones, pickup inference, storage, alerts, posture, LLM features

## Tasks

- [x] Add `baseline.py`.
- [x] Add `baseline_writer.py`.
- [x] Add automated quality gate evaluation.
- [x] Update `benchmark_detection.py` with baseline-writing options.
- [x] Add unit tests for baseline report, writer, and gate logic.
- [x] Update README with baseline reporting examples.

## Testing

- `uv run ruff check .`
- `uv run pytest`
- Unit coverage includes:
- baseline report serialization
- JSON and Markdown writing
- quality gate pass/fail behavior

## Risks Or Open Questions

- The quality gate is intentionally simple and should not be treated as proof of spatial correctness.
- Manual review is still required even when the automated gate passes.
- Markdown reporting is optimized for quick human review, not full experiment tracking at scale.

## Exit Criteria

- [x] Benchmark runs can optionally write JSON and Markdown baseline reports.
- [x] RTSP credentials are masked in written outputs.
- [x] Automated gate status and reasons are included in the report.
- [x] Lint and tests pass after integration.

## Result Summary

- Added automated baseline reporting and report writing.
- Added a simple first-pass detection quality gate.
- Extended benchmark CLI with baseline-writing and gate-threshold overrides.
- Added documentation and unit coverage for the reporting flow.
