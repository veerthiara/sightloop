# Habit Enforcer

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
