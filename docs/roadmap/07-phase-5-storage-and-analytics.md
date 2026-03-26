# Phase 5 — Event Storage and Analytics

## Goal

Turn the vision system into a product by storing events and making them reviewable.

At this point, the project is no longer just live inference.  
It becomes a habit history system.

## Why this phase matters

If you do not store events, you cannot answer useful questions like:
- How many times did I pick up my bottle today?
- When do I usually forget hydration?
- How long am I sitting continuously?
- Did posture worsen in afternoon hours?

This phase creates the memory of the system.

## What to store

Store structured events instead of raw frames as your primary source of truth.

A good event record may include:
- event_id
- camera_id
- event_type
- start_ts
- end_ts
- confidence
- rule_version
- metadata_json
- debug_image_path or clip path if available

## Storage choice

For Version 1, you can keep this simple.

Use:
- SQLite if you want easiest local setup
or
- Postgres if you want a more production-like backend from the beginning

Given your background, either is fine.

## What to build

Build a storage layer and a small API or script interface that can:
- write events
- query events by date
- count events per day
- retrieve recent events
- show event breakdown by type

## First analytics views

Examples of simple analytics:
- bottle pickups today
- probable drinks today
- hours with no hydration events
- person present duration
- posture warning counts

## Deliverable

By the end of this phase:
- event history is persistent
- you can query past events
- you can produce at least one daily summary

## Suggested first tables

You might later split into:
- `events`
- `event_evidence`
- `sessions`
- `camera_configs`

But for Version 1, one `events` table with metadata may be enough.

## Important design idea

Store both:
- the final event
- some reasoning metadata

That way you can later inspect why an event happened.

## Questions to think about

- Do you want local-only storage at first?
- Should raw video clips be optional because of disk usage?
- Do you want one session per day or per run?
- How much retention do you want for debug evidence?

## What not to do yet

Do not over-engineer:
- distributed storage
- cloud sync
- heavy backend auth
- big multi-user schema

The goal is one-user local history first.

## Revision ideas later

Future revisions could include:
- daily rollups
- event replay UI
- confidence trend analysis
- export to CSV
- backend API service
- event annotations for manual correction

## Definition of done

This phase is done when you can say:

> My system stores structured habit events and I can query or summarize them across time.
