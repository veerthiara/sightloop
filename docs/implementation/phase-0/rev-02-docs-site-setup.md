# Phase 0 Revision 2 — Docs Site Setup

## Goal

Set up a developer-facing documentation site for SightLoop that publishes the existing project docs with structured sidebar navigation.

## Scope

In scope:

- Docusaurus site setup
- rendering docs from the repository `docs/` folder
- nested sidebar navigation for roadmap, architecture, and implementation
- GitHub Pages deployment workflow
- local search for the documentation site

Out of scope:

- custom branding assets
- backend scaffold
- consumer-facing product website

## Tasks

- scaffold a Docusaurus site under `site/`
- point Docusaurus at the repository `docs/` directory
- define sidebar groups for roadmap, architecture, and implementation
- add category metadata files for docs navigation
- add a GitHub Actions workflow for Pages deployment
- enable local search

## Testing

- run a local production build
- verify docs routing works from the repository docs tree
- verify the sidebar resolves generated indexes and nested folders

## Risks Or Open Questions

- whether the final GitHub repository name will remain `sightloop`
- whether a custom domain will be added later, which would require `baseUrl` adjustment
- whether custom logo and social preview assets should be added before making the repo public

## Exit Criteria

- the docs site builds successfully
- the docs render from the existing `docs/` directory
- the left sidebar is grouped by documentation purpose
- a Pages deployment workflow exists in the repository

## Result Summary

- Docusaurus site added under `site/`
- repo docs integrated into the site
- local search enabled
- GitHub Pages workflow added
