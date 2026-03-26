# Phase Overview — Habit Enforcer Project

## Project idea

Build a camera-based system that observes a workspace and turns physical behavior into structured habit events.

The early use case is:

- detect a bottle
- detect a person
- infer bottle pickup
- later infer probable drinking events
- later expand into posture, breaks, desk presence, and other routines

## What this is really building

At a deeper level, this project has four layers:

### 1. Perception layer
This is where the camera frames are turned into useful signals.

Examples:
- person detected
- bottle detected
- chair detected
- body landmarks detected
- bottle moved from its desk position

### 2. Event layer
This is where raw detections are converted into meaningful events.

Examples:
- bottle_visible
- bottle_left_home_zone
- bottle_pickup
- probable_drink
- posture_bad
- inactivity_detected

### 3. Product layer
This is where the system becomes useful.

Examples:
- daily count of bottle pickups
- hydration reminders
- posture summaries
- “you have been sitting too long” notifications

### 4. Intelligence layer
This is where AI assistants and summaries sit.

Examples:
- “How many times did I drink water today?”
- “Show my hydration pattern this week.”
- “What habits am I missing during work hours?”

## Big picture architecture

A simple early architecture could look like this:

Camera -> Frame Reader -> Detector -> Tracker -> Rule Engine -> Event Store -> Dashboard / Alerts

Later:

Camera -> Vision Pipeline -> Event Store -> API -> LLM / Chat Layer -> Dashboard

## Main design philosophy

The design philosophy for this project should be:

### Build narrow first
Do not detect ten habits at once.  
Start with one habit that is measurable.

### Prefer rules before model training
At the beginning, use:
- pretrained models
- zones
- motion rules
- state transitions

This gives you learning and results faster than training custom models too early.

### Save evidence
Every important event should save:
- timestamp
- event type
- confidence
- possibly a debug image or clip

This is extremely valuable because it lets you review what the model thought happened.

### Design for later expansion
Even though Version 1 is simple, structure it so you can later add:
- more habits
- more cameras
- better models
- event APIs
- dashboards
- LangChain / LangGraph querying

## Initial success definition

A very good first success criterion is:

> The system can detect that a bottle resting on a desk was picked up by a person and later returned.

If you solve that well, you will already have:
- object detection
- tracking
- zone logic
- temporal reasoning
- event storage
- a foundation for future habits

## Early scope

### In scope
- one camera
- one room / one desk
- one bottle
- one user
- person + bottle detection
- bottle pickup inference
- event logging

### Out of scope for now
- multiple cameras
- cloud deployment
- model training
- conversational agent
- voice assistant
- advanced analytics
- fully general activity recognition

## Why Jetson makes sense here

Jetson is useful because this is an **edge computer for real-time video AI**.  
Instead of sending video to the cloud, you can process it locally near the camera.

This is useful for:
- lower latency
- more privacy
- learning edge AI
- experimenting with real deployment constraints

## Long-term expansion ideas

Once the bottle workflow is stable, future habits could include:
- posture monitoring
- break reminders
- phone pickup frequency
- time away from desk
- “sitting too long” detection
- bottle not present on desk
- medication reminder verification
- kitchen / stove safety use cases

## What to remember

This is not “just a YOLO project.”

It is a full system made of:
- vision
- event logic
- storage
- product UX
- later AI summarization

That is exactly why it is a great parallel project for you.
