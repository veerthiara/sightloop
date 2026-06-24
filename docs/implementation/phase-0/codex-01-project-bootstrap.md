# Phase 0 Revision 1 — Project Bootstrap

## Goal

Set up the repository structure, working conventions, and documentation workflow before application code begins.

## Scope

In scope:

- repository directory structure
- roadmap and architecture doc organization
- implementation note workflow
- repository instruction files
- local infrastructure folder setup

Out of scope:

- Python package bootstrapping
- camera pipeline code
- test framework setup
- frontend or RAG application code

## Tasks

- create top-level project directories
- move existing markdown files into `docs/roadmap/` and `docs/architecture/`
- add implementation note template
- add repository-local instruction files for agents
- add local infrastructure scaffold

## Testing

- verify all moved files exist in their new locations
- verify root README points to the new structure
- verify documentation conventions are written down in one stable place

## Risks Or Open Questions

- whether this repo will ever need a frontend folder at all
- whether local Docker services should remain minimal until Phase 5 storage work begins

## Exit Criteria

- the repository is no longer flat
- documentation is grouped by purpose
- future implementation revisions have a defined naming convention
- agent instructions exist in-repo

## Result Summary

- repository skeleton created
- roadmap and architecture docs moved under `docs/`
- implementation workflow scaffold added
