# SightLoop Vision

This repository is structured to support both planning and execution for a camera-based vision service that begins on Jetson with a narrow bottle-pickup workflow and later integrates into a separate application stack.

## Repository layout

- `docs/roadmap/` contains phase plans and project roadmap documents
- `docs/architecture/` contains design, workflow, and structural guidance
- `docs/implementation/` contains revision-by-revision implementation notes
- `site/` contains the Docusaurus documentation site
- `backend/` is reserved for the vision service code
- `infra/local/` contains local development infrastructure

## How to use this repo

Read the roadmap documents first.

Use the architecture docs to keep technical structure and workflow consistent.

As work begins, create implementation notes under `docs/implementation/` so each revision has a clear scope, testing plan, and result summary.

## Key conventions

- use `uv` for Python environment and dependency management
- keep modules separated by responsibility
- add tests from the beginning
- avoid flattening the whole project into scripts
- document each implementation revision explicitly
- keep this repository focused on the vision service and documentation, not duplicated frontend or RAG code

## Local git hooks

To enable local branch and commit validation plus backend lint/test checks:

- `make setup-git-hooks`
- `make new-branch PHASE=00 REV=03 SLUG=camera-pipeline`

The hooks enforce:

- phase branch names like `phase-00-rev-02-foundation`
- phase commit subjects like `phase-0 rev-02: frame model and camera abstraction`
- `ruff` and `pytest` on staged backend changes

## Primary roadmap docs

- `docs/roadmap/01-project-overview.md`
- `docs/roadmap/02-phase-0-foundation.md`
- `docs/roadmap/02-phase-0-foundation-detailed.md`
- `docs/roadmap/03-phase-1-detection.md`

## Agent and assistant conventions

- `AGENTS.md` contains repository-local instructions for coding agents such as Codex
- `.github/copilot-instructions.md` contains repository-local instructions for GitHub Copilot

## Docs site

The project docs are rendered with Docusaurus from the content under `docs/`.

Typical commands:

- `cd site && npm start`
- `cd site && npm run build`

## RTSP Validation

Use the Jetson config as the main RTSP validation path.

Example:

```bash
cd backend
export TAPO_RTSP_URL='rtsp://username:password@camera-ip:554/stream1'
uv run python scripts/validate_camera_setup.py --config configs/jetson.yaml --max-frames 300
```

After a run, inspect:

- `backend/artifacts/frames/`

If you want a custom session label:

```bash
uv run python scripts/validate_camera_setup.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --session-name tapo-validation-01
```

## RTSP Detection

Install detection dependencies, export the RTSP URL, and run the baseline detector:

```bash
cd backend
uv sync --extra dev --extra camera --extra detection
export TAPO_RTSP_URL='rtsp://USER:PASSWORD@CAMERA_IP:554/stream1'
uv run python scripts/run_detection.py --config configs/jetson.yaml --max-frames 300
```

For tuning and model comparison:

```bash
uv run python scripts/benchmark_detection.py --config configs/jetson.yaml --max-frames 300
uv run python scripts/benchmark_detection.py --config configs/jetson.yaml --max-frames 300 --model-name yolov8s.pt
```

Write automated baseline reports:

```bash
uv run python scripts/benchmark_detection.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --write-baseline
```

Or attach notes while writing the baseline:

```bash
uv run python scripts/benchmark_detection.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --model-name yolov8s.pt \
  --write-baseline \
  --baseline-notes "Evening light test, review bottle boxes carefully."
```

Inspect generated outputs:

- `backend/artifacts/baselines/{session_name}/detection-baseline.json`
- `backend/artifacts/baselines/{session_name}/detection-baseline.md`

The automated quality gate is only a first-pass signal. Visual review is still required to confirm the boxes are actually correct.
