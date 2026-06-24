# Agent Instructions

This repository uses repo-local instructions so coding agents can follow the same conventions consistently.

## Project intent

Build a camera-based vision service in phases, starting from a narrow local-first Jetson workflow and expanding later into detection, tracking, event inference, and structured outputs that can be consumed by another application stack.

## Repository layout

- `docs/roadmap/`: phase plans, project overview, and long-range roadmap documents
- `docs/architecture/`: cross-cutting design docs, tech decisions, folder structure, and workflow guidance
- `docs/implementation/`: revision-by-revision implementation notes and execution records
- `site/`: Docusaurus app that publishes the documentation site from the repo docs
- `backend/`: vision service application code
- `infra/local/`: local development infrastructure such as Docker Compose

## Documentation rules

When adding or updating project documentation:

- keep roadmap documents phase-oriented and strategic
- keep implementation documents execution-oriented and revision-oriented
- prefer creating a new implementation revision note instead of overwriting historical notes
- use lowercase kebab-case file names
- use phase folders under `docs/implementation/` when revision volume grows

## Implementation note naming

Use this format by default:

- `docs/implementation/phase-0/rev-01-project-bootstrap.md`
- `docs/implementation/phase-0/rev-02-config-and-camera-abstraction.md`
- `docs/implementation/phase-1/rev-01-detection-baseline.md`

If a phase has only one note so far, still keep the `rev-01-...` prefix.

## Implementation note structure

Each implementation note should include these sections:

1. Goal
2. Scope
3. Tasks
4. Testing
5. Risks or open questions
6. Exit criteria
7. Result summary

Use short, concrete bullets. Keep the note focused on one revision.

## Coding rules

- prefer `uv` for Python dependency and command execution
- keep code modular with clear separation of concerns
- add tests from the beginning for logic that does not require hardware
- isolate hardware-specific code behind interfaces where practical
- avoid putting core logic in one-off scripts when it belongs in a module
- treat frontend, RAG, and broader product concerns as integration targets unless the user explicitly asks to build them in this repository

## Change management

- do not silently rename documentation conventions
- if moving files, update indexes and references in the same change
- preserve historical revision documents unless the user explicitly asks to delete or merge them

## Git workflow conventions

- use one phase/revision branch per implementation slice when practical
- prefer branch names like `phase-00-rev-02-foundation`
- on phase branches, prefer commit subjects like `phase-0 rev-02: short summary`
- if local hooks are installed, keep them enabled so branch and commit drift is caught before history gets messy

## If uncertain

Prefer adding a small, explicit documentation file that explains the convention rather than assuming the convention will be remembered later.
