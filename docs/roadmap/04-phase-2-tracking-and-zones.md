# Phase 2 — Tracking and Spatial Zones

## Goal

Move from frame-by-frame detection to understanding persistence and movement.

This phase answers questions like:
- Is this the same bottle across frames?
- Did the bottle leave its usual place?
- Is the bottle on the desk or not?
- Is the person present continuously or only briefly?

## Why this phase matters

Detection alone tells you what is visible in one frame.

But habits are not single frames.  
Habits happen across time.

To detect habits, you need:
- object continuity
- scene regions
- movement over time

That is why tracking and zones are essential.

## What to build

Add two concepts to your pipeline:

### 1. Tracking
Tracking lets you follow objects frame to frame.

Even a simple tracker is valuable because it gives the system a notion of continuity.

### 2. Zones
Zones are named regions in the image.

Examples:
- bottle_home_zone
- desk_zone
- person_zone
- face_candidate_zone later
- off_desk_zone implicitly

## Early zone design

For Version 1, define at least:

### Bottle home zone
Where the bottle normally rests on the desk.

### Desk zone
The visible surface where desk-related logic happens.

### Person presence zone
A region that helps validate that a person is truly in the desk scene.

## Event examples unlocked by this phase

Once tracking and zones exist, you can detect events like:
- bottle_entered_home_zone
- bottle_left_home_zone
- person_present
- person_absent
- bottle_missing_from_desk

These are already useful events even before pickup inference.

## What to log

Track logs should include:
- object id
- class name
- timestamp
- position / box
- current zone
- confidence
- track age or persistence if available

## Deliverable

By the end of this phase:
- the bottle can be tracked across frames
- zones are drawn or configured
- you can detect when bottle leaves and returns to the desk zone
- you can estimate person presence duration

## Good debugging practices

You should visually render:
- tracked object IDs
- zone boundaries
- current state text on the frame

Examples:
- bottle #3 in home zone
- person present: yes
- bottle out of home zone for 12.4 sec

## Questions to think about

- Should zones be hardcoded or loaded from config?
- Do you want one config per room / camera?
- How much jitter do you need to tolerate before calling it “left zone”?
- Should the system wait 1–2 seconds before confirming a zone exit?

## What not to do yet

Do not try to decide:
- “user drank water”
- “user is slouching”
- “user needs reminder”

This phase is about reliable low-level scene state.

## Brainstorm notes

A major insight here is that many useful products are not built from deep learning alone.

Sometimes the most important logic is:
- where is the object?
- has it moved?
- how long has it been gone?
- who was present when it moved?

That is product logic, not just model logic.

## Revision ideas later

Possible future improvements:
- better tracker
- configurable zone editor
- smoothing / hysteresis
- per-camera calibration
- multi-object handling if multiple bottles appear

## Definition of done

This phase is done when you can say:

> I can track the bottle and person over time, and I know when the bottle leaves or returns to its normal desk area.
