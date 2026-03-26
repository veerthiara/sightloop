# Phase 0 — Foundation and Local Camera Pipeline

## Goal

Before detection, build a stable camera and runtime foundation.

The goal of this phase is to prove:

- your Jetson environment works
- your camera feed is stable
- you can process frames continuously
- you can measure performance
- you can save debug frames and clips

## Why this phase matters

Many people jump directly into model inference.  
Then later they discover issues such as:
- poor lighting
- wrong camera angle
- unstable FPS
- camera disconnects
- inference pipeline lag
- resolution too high for real-time use

This phase prevents that.

## What to build

Create a minimal Python application that does the following:

1. Connects to one camera
2. Reads frames continuously
3. Displays frames locally or writes them to disk for debugging
4. Logs:
   - frame timestamps
   - frame width / height
   - FPS
   - dropped frame count if possible
5. Allows easy testing of different camera positions

## What to decide in this phase

### Camera placement
Think carefully about where the camera should be placed:
- top-down
- slightly angled from monitor side
- side angle
- wide room angle

For bottle pickup, the best angle is usually one that clearly sees:
- the desk surface
- the bottle’s resting place
- the person’s upper body

### Fixed or moving scene
Version 1 should assume:
- fixed camera
- fixed desk
- fixed bottle resting zone

This makes downstream logic much easier.

### Resolution
High resolution sounds good, but it costs more compute.  
Try to find the smallest resolution that still makes the bottle visible.

### Debug strategy
You should decide how to save evidence:
- save one image every N seconds
- save event clips later
- save a debug image when a rule fires

## Deliverable

By the end of this phase, you should have:

- a basic project folder
- camera feed visible
- logging of performance
- a few screenshots from the real setup
- notes on the best camera angle

## Suggested output logs

Examples of useful logs:
- camera connected
- resolution selected
- current FPS
- average FPS
- dropped frames
- test session started at timestamp X

## Questions to think about

- Is the bottle visually easy to detect in your lighting?
- Does the desk have clutter that may confuse detection?
- Does the bottle disappear behind the hand often?
- Is the camera angle good enough to see the bottle move upward?
- Will you run this near your real work setup or a test setup first?

## What not to do yet

Do not add:
- YOLO
- tracking
- pose detection
- database
- alerts
- LangChain

This phase is only about creating a clean pipeline.

## Revision ideas later

Possible later revisions to this phase:
- support RTSP streams
- support USB camera switching
- support multiple camera config files
- auto-save short test clips
- add benchmarking mode

## Definition of done

This phase is done when you can say:

> I have a stable single-camera Python app on Jetson, and I understand my field of view, lighting, and runtime basics.
