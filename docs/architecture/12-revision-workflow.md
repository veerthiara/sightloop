# Revision Workflow for This Project

## Why use a revision-based approach

This project will evolve through discovery.

You will likely change:
- camera angle
- object model choice
- thresholds
- rules
- storage schema
- alert logic

So a revision workflow is the right way to manage it.

## Suggested working style

For each phase:
1. write the first version of the plan
2. implement a narrow slice
3. test with real footage
4. document what failed
5. revise the phase plan
6. then move forward

This is much better than writing a perfect plan once.

## Suggested phase revision naming

You can structure your notes like this:

- Phase-0-Revision-1
- Phase-0-Revision-2
- Phase-1-Revision-1
- Phase-1-Revision-2

Or use folders:
- `docs/revisions/phase-1/rev-01.md`
- `docs/revisions/phase-1/rev-02.md`

## What each revision note should contain

A good revision note should include:

### 1. Current goal
What exact thing are you trying to prove now?

### 2. What changed
What changed from the last plan?

### 3. Why it changed
What did you learn from real testing?

### 4. New scope
What is in and out now?

### 5. Risks
What could fail?

### 6. Deliverable
What counts as success for this revision?

## Example revision flow

### Phase 1 Revision 1
- basic YOLO bottle/person detection
- test one bottle and one desk

### Phase 1 Revision 2
- confidence tuning
- add debug frame capture
- handle evening lighting better

### Phase 2 Revision 1
- add bottle home zone
- add track ids

### Phase 3 Revision 2
- reduce duplicate pickup events
- add event cooldown logic

## My recommendation for you

Use this same pattern you are already using in your other project:
- phase file
- revision file
- focused implementation
- review
- revise

That will work very well here too.

## Definition of success for the planning style

This planning method is successful when:
- you always know the current scope
- you avoid mixing too many unknowns
- each revision solves a specific problem
- the project remains learnable
