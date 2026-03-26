# Phase 1 — Object Detection Baseline

## Goal

Detect the objects that matter for the first use case:
- person
- bottle

You may later add:
- chair
- cup
- phone
- desk-related objects

But do not start wide.

## Why this phase exists

Your first use case depends on reliable visibility.

Before you can infer a habit like “picked up bottle,” the system must first answer:
- Is there a bottle in the frame?
- Is there a person in the frame?
- Where are they?

This phase creates those raw signals.

## Recommended approach

Start with a pretrained object detector.

For Version 1, the point is not to create a perfect model.  
The point is to test whether a standard model is already good enough in your environment.

## What to build

Extend the Phase 0 pipeline so that each frame goes through detection.

For each frame:
1. read frame
2. run detector
3. filter for relevant classes
4. draw boxes
5. log detections

## Data to capture

For each detection, you should store at least:
- class name
- confidence
- bounding box
- timestamp
- frame id

Even if you are not storing to a database yet, log this to console or JSON for debugging.

## Practical tasks

### Task 1 — Bottle detection test
Run detection on your real bottle in:
- daylight
- evening light
- bottle partly hidden
- bottle at slightly different positions

### Task 2 — Person detection test
Confirm person detection works when:
- sitting at desk
- leaning
- partially out of frame
- standing and returning

### Task 3 — False positives review
Review mistakes carefully.

Important questions:
- Is another desk object detected as bottle?
- Does a transparent bottle get missed?
- Does the detector confuse cup vs bottle?

## Deliverable

By the end of this phase:
- you can see real-time boxes on frame
- bottle and person are detected often enough to continue
- you have notes on failure cases

## Minimum success criteria

You do not need perfection.

You need something like:
- bottle detected in its home location most of the time
- person detected when sitting in the scene
- enough stability to move to tracking

## What not to do yet

Do not try to infer:
- drinking
- pickup
- posture
- reminders

Detection is only the first layer.

## Questions to think about

- Is your bottle type hard for general models?
- Would a more visible bottle help the project early on?
- Do you want to standardize the bottle appearance in Version 1?
- Should you mark a fixed desk area on screen as the bottle home zone?

## Brainstorm notes

A useful early trick is to make the problem easier:
- use a distinctive bottle
- keep clutter low
- keep the resting location consistent

That is not cheating.  
That is how real products are often built in stages.

## Revision ideas later

Future revisions may include:
- model comparison
- TensorRT optimization
- confidence threshold tuning
- adding custom classes
- evaluating segmentation later if detection is not enough

## Definition of done

This phase is done when you can say:

> I can reliably detect a bottle and a person in my real scene, and I have enough confidence to start reasoning across time.
