# Copilot Instructions

Use these repository conventions when generating code or documentation.

## Project structure

- `docs/roadmap/` contains strategic roadmap and phase planning documents
- `docs/architecture/` contains architectural and process guidance
- `docs/implementation/` contains implementation-by-revision notes
- `site/` contains the Docusaurus documentation site
- `backend/` contains the vision service code
- `infra/local/` contains local infrastructure such as Docker Compose

## Project workflow
This repository is built phase by phase and revision by revision.

Branch naming convention:
- `phase-01-bootstrap-rev-01`
- `phase-02-core-db-table-implementation-rev-01`
- `phase-02-core-db-table-implementation-rev-02`

Documentation naming convention:
- `docs/implementation/phase-01-rev01.md`
- `docs/implementation/phase-02-rev01.md`
- `docs/implementation/phase-02-rev02.md`

Ensure documentation is always updated for each phase/revision with the same title and content structure as the example in `docs/implementation/phase-04-rev01.md`.

## Documentation conventions

- use lowercase kebab-case file names
- create implementation notes under phase folders
- use revision-prefixed names such as `rev-01-project-bootstrap.md`
- keep roadmap docs high-level
- keep implementation docs concrete and execution-oriented

## Implementation note template

Every implementation note should include:

1. Goal
2. Scope
3. Tasks
4. Testing
5. Risks or open questions
6. Exit criteria
7. Result summary

## Engineering conventions

- prefer Python managed with `uv`
- optimize for modularity and separation of concerns
- add tests from the start
- avoid tightly coupling hardware code to business logic
- make future detection, tracking, and event layers easy to extend
- treat frontend and RAG systems as external integration targets unless explicitly added to this repository later

## Documentation rules
Implementation docs should stay concise and avoid bloated explanations.

Use this structure:

- Title
- Goal
- Key Decisions for this implementation, including any chat instructions and the reason i asked for changes.
- Architectural context (how this fits into the overall project direction and architecture)
- Flow Chart or Sequence Diagram (User interaction scenario or data flow)
- Scope implemented
- Files changed
- Notes
- Next step
