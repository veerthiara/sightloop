# Suggested Folder Structure

This is a suggested starting structure for your project.

You do not need to implement all of it on day one.

```text
habit-enforcer/
├── README.md
├── docs/
│   ├── 01-project-overview.md
│   ├── 02-phase-0-foundation.md
│   ├── 03-phase-1-detection.md
│   ├── 04-phase-2-tracking-and-zones.md
│   ├── 05-phase-3-event-inference.md
│   ├── 06-phase-4-pose-and-posture.md
│   ├── 07-phase-5-storage-and-analytics.md
│   ├── 08-phase-6-alerts-and-coaching.md
│   ├── 09-phase-7-llm-layer.md
│   ├── 10-tech-decisions.md
│   └── 11-folder-structure.md
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   └── camera_profiles/
│   ├── camera/
│   │   ├── frame_reader.py
│   │   └── recorder.py
│   ├── detection/
│   │   ├── detector.py
│   │   └── models/
│   ├── tracking/
│   │   └── tracker.py
│   ├── zones/
│   │   ├── zone_manager.py
│   │   └── zone_config.json
│   ├── events/
│   │   ├── rule_engine.py
│   │   ├── event_builder.py
│   │   └── schemas.py
│   ├── pose/
│   │   └── pose_engine.py
│   ├── storage/
│   │   ├── db.py
│   │   ├── event_repository.py
│   │   └── models.py
│   ├── alerts/
│   │   └── alert_engine.py
│   └── utils/
│       ├── logging.py
│       ├── time.py
│       └── drawing.py
├── data/
│   ├── debug_frames/
│   ├── debug_clips/
│   ├── exports/
│   └── local.db
├── tests/
│   ├── test_rules.py
│   ├── test_zones.py
│   └── test_event_inference.py
└── scripts/
    ├── run_camera.py
    ├── benchmark.py
    └── replay_session.py
```

## Why this structure is useful

It separates responsibilities:

- `camera/` handles frame input
- `detection/` handles model inference
- `tracking/` handles persistence over time
- `zones/` handles spatial scene logic
- `events/` handles business reasoning
- `storage/` handles persistence
- `alerts/` handles reminders
- `pose/` is added later without polluting earlier phases

## Early simplification

You do not need to create all folders immediately.

You can start smaller, for example:

```text
habit-enforcer/
├── app/
│   ├── main.py
│   ├── frame_reader.py
│   ├── detector.py
│   ├── tracker.py
│   ├── rule_engine.py
│   └── config.py
├── data/
└── docs/
```

Then split into modules as the project grows.

## Suggested evolution

### Early stage
Keep code compact and understandable.

### Mid stage
Split by domain as soon as:
- files become too long
- you add more than one type of event
- you add storage
- you add pose

### Later stage
Add API and frontend folders if you want:
- backend service
- dashboard
- event review UI
- chat layer

## Final advice

Optimize for:
- clarity
- debuggability
- change over time

Do not over-architect on day one.
