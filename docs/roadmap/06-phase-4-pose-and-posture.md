# Phase 4 — Pose and Posture Signals

## Goal

Add body understanding so the system can support non-object habits such as:
- slouching
- head down too long
- leaning posture
- inactivity
- stretch breaks later

## Why this phase comes after bottle events

Pose estimation is powerful, but it adds another layer of complexity.

If you try to do:
- object detection
- bottle logic
- posture logic
- reminders
all at once, it becomes hard to debug.

By adding posture only after the bottle event pipeline is working, you keep the project modular.

## What to build

Add a pose estimation stage to the pipeline for frames where a person is present.

This stage should extract body landmarks and compute derived posture features.

## Example posture features

You may later define features such as:
- shoulder tilt
- head angle
- torso lean
- neck position
- time spent in low-movement seated posture

The exact formulas can evolve over time.

## First posture use cases

Keep the first version very simple.

Examples:
- seated posture looks neutral vs slouched
- head bent downward for extended period
- person too still for long duration

## Output of this phase

This phase should output:
- pose landmarks
- derived posture metrics
- simple posture events

Example events:
- `posture_warning_candidate`
- `head_down_long`
- `inactivity_long`
- `stretch_break_detected` later

## Important warning

Pose systems can be sensitive to:
- camera angle
- lighting
- occlusion
- loose clothing
- desk blocking parts of the body

So do not overpromise accuracy too early.

## Deliverable

By the end of this phase:
- pose landmarks appear on screen
- one or two posture metrics are calculated
- at least one posture-related event can be logged

## Questions to think about

- Is the camera angle good enough for upper body posture?
- Do you need a separate posture camera later?
- Should posture run on every frame or every Nth frame?
- Which posture event would actually be useful in real life?

## Good design principle

Avoid trying to detect “perfect posture.”

Instead, detect practical signals like:
- sustained head-down posture
- leaning too long
- no movement for long duration

That is easier to implement and more useful.

## What not to do yet

Do not try to build:
- medical-grade posture scoring
- personalized coaching language
- complex classification of many body positions

Start with coarse categories.

## Revision ideas later

Possible revisions:
- personalized baseline posture
- posture score smoothing
- upper-body-only optimization
- pose + bottle relation features
- break detection using movement patterns

## Definition of done

This phase is done when you can say:

> I can extract body landmarks and derive at least one useful posture-related signal from my workspace camera.
