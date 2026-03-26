# Phase 3 — Event Inference and Rule Engine

## Goal

Convert low-level visual signals into meaningful habit events.

This phase is where the system becomes interesting.

Instead of only knowing:
- bottle detected
- bottle moved
- person present

You now want to infer:
- bottle pickup
- bottle put back
- probable drink attempt

## Why rules first

It is tempting to think:
“I need a model that detects drinking.”

But in many practical systems, the first version works better if you infer events from simpler signals.

For example, bottle pickup may be inferred from:
- bottle was in home zone
- bottle left home zone
- person was present
- bottle moved upward or toward person
- bottle stayed away for a meaningful duration
- bottle returned

That is a temporal pattern.  
A rule engine or state machine is a great first solution.

## What to build

Create an event inference layer that consumes:
- detections
- tracks
- zones
- durations
- presence state

Then define state transitions.

## Suggested first event states

### Bottle state
- resting_in_home_zone
- leaving_home_zone
- in_motion
- near_person_region
- missing_from_home_zone
- returned_to_home_zone

### Person state
- present
- absent
- stable_at_desk
- moving_in_scene

## Suggested first events

Start with:
- `bottle_pickup_started`
- `bottle_pickup_completed`
- `bottle_returned`
- `bottle_missing_long`
- `probable_drink_event`

Do not worry if `probable_drink_event` is initially imperfect.  
It is allowed to be a heuristic.

## Example logic

A simple event candidate could be:

1. bottle is resting in home zone
2. person is present
3. bottle leaves home zone
4. bottle moves toward upper body region or stays away for a short time
5. bottle later returns

This may count as one pickup cycle.

A stricter probable drink candidate might require:
- bottle trajectory upward
- bottle enters person upper-body area
- event duration falls within expected range

## Deliverable

By the end of this phase:
- event records are emitted
- pickup cycles can be counted
- debug logs explain why the event fired

## Critical design rule

Every inferred event should include its reasoning context.

For example:
- start time
- end time
- source track ids
- relevant zones
- rule version
- confidence or score
- short explanation string

This is extremely useful when debugging.

## Why this phase is important

This phase turns your project from:
“computer vision demo”

into:
“behavior event system”

That is a major shift.

## Questions to think about

- What is the difference between pickup and drink in your system?
- Should pickup alone count as a hydration habit, or only probable drink?
- How long must the bottle be absent before an event is valid?
- What should happen if detection is lost briefly?
- Do you need event smoothing to avoid duplicate counts?

## What not to do yet

Do not introduce:
- LLM reasoning
- natural language summaries
- advanced user coaching

The events must become trustworthy first.

## Brainstorm notes

Think like a product engineer:
- false negatives are frustrating
- false positives are annoying
- duplicate counts are dangerous
- short debug explanations are invaluable

## Revision ideas later

Future revisions may include:
- configurable rules
- scoring system instead of binary rules
- replay mode for event evaluation
- benchmark clips for regression testing

## Definition of done

This phase is done when you can say:

> My system can infer a bottle pickup event from continuous visual evidence and log it as a structured event.
