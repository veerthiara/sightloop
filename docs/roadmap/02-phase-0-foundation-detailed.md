# Phase 0 — Foundation and Local Camera Pipeline (Detailed Plan)

## Purpose

This document turns Phase 0 into an implementation plan you can actually build against.

The goal is not just to get a camera feed working once. The goal is to establish a clean, testable, scalable project foundation that Phase 1 and later phases can extend without large rewrites.

This detailed plan assumes:

- one Jetson device
- one camera
- one fixed workspace
- one bottle home zone
- local-first processing
- Python as the main implementation language

## Key decisions for Phase 0

### 1. Tooling choice

Use `uv` as the default project/package manager.

Why:

- faster dependency resolution and environment setup
- simple script execution
- works well for both package-based apps and local development
- easier to keep a clean developer workflow from the beginning

Poetry is still a valid option, but if you are choosing fresh, `uv` is the better default for this project.

Recommended standard:

- `uv` for virtualenv + dependency management
- `pyproject.toml` as the single project config entry point
- `pytest` for tests
- `ruff` for linting and formatting support
- `mypy` later if type coverage becomes useful

### 2. Architecture choice

Start as a small package, not a single script.

That matters because this project will likely grow into:

- camera adapters
- detection backends
- tracking/event logic
- config management
- evidence capture
- storage
- APIs or dashboards later

If you start with a modular package now, Phase 1 becomes an extension instead of a rewrite.

### 3. Testing choice

Add tests immediately in Phase 0.

Even though camera-heavy systems are hardware-driven, a large part of this project is still testable:

- config validation
- pipeline orchestration
- frame metadata handling
- logging/event formatting
- file naming and evidence-saving behavior
- dropped frame accounting
- performance stats logic

This is exactly the type of foundation where early tests prevent later chaos.

## What should start in Phase 0 vs later

Some “future-looking” work should start in Phase 0 because it affects structure, not features.

These should start now:

- project packaging with `uv`
- modular folder structure
- config system
- logging setup
- test framework
- clear interfaces between camera, processing, metrics, and persistence
- debug image/video output design

These should not be fully built now:

- detector implementation
- tracking logic
- rule engine
- event database
- alerting
- LLM or chat layer

So the answer is: not everything belongs in Phase 0, but the structural decisions that enable those later phases absolutely do.

## Phase 0 objectives

By the end of this phase, you should have:

- a runnable Python package
- repeatable local setup using `uv`
- a camera pipeline that can read frames continuously
- structured logging
- frame timing and FPS metrics
- optional debug frame saving
- optional short clip saving hooks
- config-driven camera/runtime parameters
- unit tests around non-hardware logic
- a small number of hardware smoke tests for real device validation
- clear notes about camera placement, lighting, and runtime constraints

## Recommended repository structure

Use a package layout similar to this:

```text
sightloop_vision/
├── backend/
│   ├── pyproject.toml
│   ├── README.md
│   ├── .python-version
│   ├── configs/
│   │   ├── dev.yaml
│   │   ├── jetson.yaml
│   │   └── test.yaml
│   ├── scripts/
│   │   ├── run_camera.py
│   │   ├── benchmark_camera.py
│   │   └── capture_debug_session.py
│   ├── src/
│   │   └── sightloop_vision/
│   │       ├── __init__.py
│   │       ├── app/
│   │       │   └── runner.py
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   ├── camera.py
│   │       │   ├── debug.py
│   │       │   └── output.py
│   │       ├── models/
│   │       │   └── frame.py
│   │       ├── adapters/
│   │       │   └── camera/
│   │       │       ├── base.py
│   │       │       ├── fake.py
│   │       │       └── opencv.py
│   │       ├── services/
│   │       │   ├── pipeline/
│   │       │   │   └── camera_pipeline.py
│   │       │   ├── metrics/
│   │       │   │   ├── fps.py
│   │       │   │   └── session_stats.py
│   │       │   ├── logging/
│   │       │   │   └── setup.py
│   │       │   └── debug/
│   │       │       ├── frame_writer.py
│   │       │       └── clip_writer.py
│   │       └── utils/
│   │           └── time.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_config.py
│   │   │   ├── test_fps_tracker.py
│   │   │   ├── test_session_stats.py
│   │   │   └── test_frame_writer.py
│   │   ├── integration/
│   │   │   └── test_camera_pipeline_fake_source.py
│   │   └── fixtures/
│   └── artifacts/
│       ├── frames/
│       ├── clips/
│       └── logs/
├── docs/
├── infra/
└── site/
```

## Separation of concerns

Keep responsibilities narrow from the start.

### `core`

Responsible for:

- loading environment-specific settings (YAML, env vars)
- validating required fields
- exposing typed config objects

Should not:

- open cameras
- compute FPS
- write files

### `models`

Responsible for:

- domain data structures (Frame, detection results, events)
- keeping domain models separate from config models

Should not:

- contain config loading logic
- depend on hardware or camera code

### `camera`

Responsible for:

- connecting to a camera source
- reading frames
- exposing frame metadata
- handling reconnect behavior later

Should not:

- run detection
- save debug images directly
- own business rules

### `pipeline`

Responsible for:

- orchestrating the main loop
- reading frames from a source
- passing frame data to metrics/debug hooks
- handling lifecycle start/stop behavior

Should not:

- contain camera implementation details
- own config parsing
- hardcode output paths

### `metrics`

Responsible for:

- FPS calculation
- dropped-frame estimates
- latency timing
- session summaries

Should not:

- depend on hardware-specific camera code

### `debug`

Responsible for:

- saving frames
- naming files
- optionally saving clips later

Should not:

- know about detector logic
- own runtime orchestration

### `app`

Responsible for:

- wiring together config, camera, pipeline, metrics, and debug outputs

This separation is what will make later detector/tracker/event modules easy to introduce.

## Recommended Phase 0 implementation order

Build Phase 0 in small revisions instead of one large pass.

## Revision 0 — Project bootstrap

### Goal

Create the package skeleton and local developer workflow.

### Tasks

- initialize `pyproject.toml`
- set up `uv`
- create `src/` layout
- add `pytest`
- add `ruff`
- add basic README instructions
- add `.gitignore`
- add artifact directories or create them at runtime

### Deliverables

- `uv sync` works
- `uv run pytest` works
- `uv run ruff check .` works
- package imports resolve cleanly

### Tests to add

- basic smoke test that package modules import
- config loader smoke test with test config fixture

## Revision 1 — Typed config and runtime settings

### Goal

Make runtime behavior config-driven before hardware logic grows.

### Suggested config fields

- camera source index or URI
- resolution width/height
- target FPS
- output directories
- debug frame save interval
- display enabled/disabled
- session name
- environment name

### Tasks

- create config models
- create config file loader
- validate missing/invalid values early
- expose one app config object to the rest of the system

### Deliverables

- app can start from config file
- invalid config fails early with a clear error

### Tests to add

- valid config loads successfully
- missing required field raises expected error
- invalid numeric values are rejected

## Revision 2 — Frame model and camera abstraction

### Goal

Avoid tying the whole system directly to OpenCV objects.

### Suggested abstractions

- `Frame`: image array + timestamp + frame_id + source metadata
- `CameraSource` interface: `open()`, `read()`, `close()`
- `OpenCVCameraSource`: initial concrete implementation

### Why this matters

Once detection starts, it becomes very useful to have stable frame objects and replaceable camera sources for tests.

### Deliverables

- a fake camera source can be used in tests
- OpenCV camera source can read real frames

### Tests to add

- fake source emits predictable frames
- pipeline handles end-of-stream correctly
- frame IDs increment correctly

## Revision 3 — Main camera pipeline

### Goal

Build the continuous processing loop.

### Tasks

- open source
- read frames continuously
- attach timestamps
- update metrics
- optionally display frame
- optionally emit frames to debug writers
- stop cleanly on interrupt

### Deliverables

- stable loop over a live camera
- visible session start/stop logs
- clean shutdown behavior

### Tests to add

- pipeline processes N fake frames then exits cleanly
- pipeline handles read failures without crashing unexpectedly
- stop signal path closes resources

## Revision 4 — Metrics and observability

### Goal

Measure runtime behavior before adding inference cost.

### Metrics to capture

- current FPS
- rolling average FPS
- frame count
- session duration
- dropped frame estimate if available
- frame resolution
- timestamped session start/end

### Tasks

- implement FPS tracker
- implement session stats collector
- output structured logs
- optionally emit periodic metric summaries every N seconds

### Deliverables

- logs are useful enough to compare camera settings
- you can benchmark multiple resolutions/frame-rate combinations

### Tests to add

- FPS calculations are correct for deterministic timestamps
- session summary output is stable and testable

## Revision 5 — Debug evidence capture

### Goal

Make it easy to inspect what the camera actually saw.

### Tasks

- save one frame every N seconds
- save frames on manual trigger or session end
- prepare clip writer interface even if clip saving is minimal in Phase 0
- create deterministic file naming convention

### Suggested naming

- `artifacts/frames/{session_name}/frame_{frame_id}_{timestamp}.jpg`
- `artifacts/logs/{session_name}.jsonl`

### Deliverables

- a real debug session produces inspectable artifacts
- artifacts are grouped by session

### Tests to add

- file paths are generated correctly
- save interval logic behaves as expected
- writing can be disabled without changing pipeline logic

## Revision 6 — Hardware validation pass

### Goal

Use the built tooling to evaluate the real workspace.

### Run these experiments

- test 2 to 3 candidate camera angles
- test at least 2 resolutions
- test day and evening lighting
- test bottle at home position and hand interaction
- test user sitting, leaning, standing, and returning

### Capture notes for each run

- camera placement
- bottle visibility quality
- upper-body visibility quality
- observed FPS
- dropped frames or lag
- whether saved frames are actually useful

### Deliverables

- chosen camera placement
- chosen default resolution
- chosen debug strategy
- known risks documented before Phase 1

## Suggested implementation details

### Config format

YAML is a practical default because it is readable and easy to version.

Suggested examples:

- `configs/dev.yaml` for local laptop testing
- `configs/jetson.yaml` for device runtime
- `configs/test.yaml` for unit/integration tests

### Logging format

Use standard logs for human-readable console output and JSONL for machine-readable session/event logs if possible.

That keeps debugging easy while preserving structured records for later analysis.

### Session concept

Introduce a session ID or session name from the beginning.

That helps organize:

- logs
- saved frames
- future event records
- benchmark comparisons

### Dependency boundaries

Keep OpenCV near the edges.

That means:

- OpenCV is fine inside camera/debug modules
- avoid leaking raw OpenCV assumptions across the full codebase

This makes tests simpler and later backend swaps easier.

## Test strategy from day one

Do not wait for “real features” before testing.

Use three layers:

### 1. Unit tests

Fast tests for:

- config parsing
- metrics math
- frame metadata behavior
- file path generation
- save interval logic

### 2. Integration tests

Use fake camera sources to test:

- pipeline orchestration
- logging calls
- debug writer hooks
- clean shutdown

### 3. Hardware smoke tests

Run manually on Jetson for:

- camera connection
- real FPS
- lighting validation
- real artifact capture

Important point: hardware tests should be a small layer, not the whole quality strategy.

## Suggested commands

Example workflow if using `uv`:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run python scripts/run_camera.py --config configs/jetson.yaml
uv run python scripts/benchmark_camera.py --config configs/jetson.yaml
```

## Definition of done for this detailed Phase 0

Phase 0 should be considered complete when all of the following are true:

- the project is packaged and runnable with `uv`
- camera startup is config-driven
- one camera can stream continuously in a stable loop
- FPS and session metrics are visible
- debug artifacts can be saved and reviewed
- the codebase already has meaningful tests
- modules are separated enough that Phase 1 can add detection without restructuring core pieces
- you have chosen a camera angle and baseline runtime settings based on real tests

## Exit criteria before starting Phase 1

Do not move to detection until you can answer these clearly:

- Which camera angle are you using?
- Which resolution is your default?
- Is the bottle clearly visible at rest?
- Is the user’s upper body sufficiently visible?
- What is your actual observed FPS on Jetson?
- How will you save debug evidence during detection failures?
- Can you run tests and lint checks quickly before making changes?

If these are unclear, Phase 1 will be slower and noisier than it needs to be.

## Risks to watch now

- choosing resolution too high and creating avoidable latency
- building everything inside one script and making Phase 1 harder
- relying only on manual testing
- not preserving debug artifacts
- tightly coupling the pipeline to one camera implementation
- mixing hardware control, metrics, and output logic in the same module

## Recommended next document after this

Once you agree with this structure, the next planning step should be to revise Phase 1 so it assumes these interfaces already exist:

- detector interface
- detection result model
- annotated frame renderer
- event/debug logging hooks

That will keep the transition from foundation to detection clean.
