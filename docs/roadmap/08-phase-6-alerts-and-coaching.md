# Phase 6 — Alerts and Coaching Layer

## Goal

Use stored events and live state to create useful nudges.

This is the phase where the system starts feeling like a habit assistant instead of just a logging pipeline.

## What this phase should do

Examples:
- remind you if no bottle pickup happened for a long period
- warn you if posture has been poor for too long
- prompt a break after extended inactivity
- summarize the current work session

## Why this phase comes before LLMs

You do not need an LLM to decide:
- no bottle pickup for 90 minutes
- no break for 2 hours
- posture warning count high today

These are deterministic product rules.

Build the useful behavior first.  
Then add natural-language polish later.

## What to build

Create an alerts module that consumes:
- live state
- recent events
- configurable thresholds

Examples:
- hydration reminder threshold
- inactivity threshold
- posture threshold

## Example alerts

- “No bottle pickup detected in the last 75 minutes.”
- “You have been sitting continuously for 110 minutes.”
- “Posture warning triggered 4 times in the last 30 minutes.”

## Important design choice

Separate:
- event generation
from
- alert generation

An event is evidence.  
An alert is a product decision.

This keeps your system clean.

## Deliverable

By the end of this phase:
- alerts can be generated from rules
- thresholds can be changed
- at least one reminder type is useful in real testing

## Questions to think about

- Should reminders be visible on screen, in terminal, or mobile later?
- Should alerts be suppressed while you are away from desk?
- Should bottle pickup reset the hydration reminder?
- Should probable drink and pickup be treated differently?

## Good product thinking

A habit tool should not become annoying.

So think about:
- cooldown periods
- snooze logic
- only alert when person is present
- avoid duplicate reminders

## What not to do yet

Do not add:
- chat-based explanations
- motivational essays
- complex AI-generated coaching

Make the reminder rules correct first.

## Revision ideas later

Later improvements:
- quiet hours
- personalized thresholds
- different work modes
- escalating reminders
- Slack / phone notification integration

## Definition of done

This phase is done when you can say:

> My project can take live state and past events and turn them into useful, non-annoying reminders.
