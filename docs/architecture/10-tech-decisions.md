# Technical Decision Notes

## Why start with YOLO

YOLO is a good starting point because:
- it is practical
- it has broad community support
- it works well for common object categories
- it gets you visible results quickly

For this project, YOLO is useful for:
- bottle detection
- person detection
- possibly chair / cup / phone later

## Why not rely on YOLO alone

YOLO answers:
- what object is present
- where it is in the frame

But habits need more than that.

Habit detection often requires:
- tracking across time
- zone reasoning
- duration thresholds
- relation to person state
- later pose understanding

So the right mindset is:

YOLO is one layer, not the whole product.

## Why rules before custom model training

Rule-based systems are a great first step when:
- the environment is constrained
- the camera is fixed
- the object is known
- the habit can be expressed as a sequence

This project matches that well.

Starting with rules gives you:
- faster iteration
- easier debugging
- more explainability
- better understanding of failure cases

## When custom training might be needed later

You may need custom data or fine-tuning if:
- your bottle is missed too often
- the detector confuses similar objects
- you want custom classes
- your scene differs too much from generic training data

But do not assume this on day one.

## Why pose should come later

Pose adds value for:
- posture
- movement quality
- head angle
- inactivity patterns

But it also adds complexity.

So the best order is:
- bottle/person detection first
- event logic first
- pose after the foundation works

## Why local event storage matters

Without storage:
- no trends
- no comparisons
- no natural-language analytics
- no useful product memory

That is why storage is not optional long term.

## Why the LLM layer is later

The LLM is most useful when it can speak about:
- real events
- real metrics
- real trends

It should not be your first dependency.

## Main architectural principle

Your project should move in this order:

Perception -> State -> Events -> Product -> LLM

Not:

LLM -> everything else

## Useful simplifying assumptions for Version 1

These assumptions make the first version easier:
- one user
- one bottle
- one desk
- one fixed camera
- one room
- one local device
- one event store

These assumptions are good engineering, not weakness.

## Decision summary

### Start with:
- Python
- OpenCV
- YOLO
- simple tracking
- zones
- rule engine
- SQLite or Postgres

### Add later:
- pose
- richer analytics
- reminders
- LangChain / LangGraph
- maybe multi-camera support

## Final guidance

The best decision is not the most advanced stack.

The best decision is the one that gets you to a reliable first event.
