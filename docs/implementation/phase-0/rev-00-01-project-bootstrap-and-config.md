# Phase 0 Revision 0+1 — Project Bootstrap and Typed Config

## Goal

Initialize the `sightloop-vision` Python package inside `backend/` using `uv`,
and deliver a working, validated configuration system that the rest of the service
can build on. Covers Roadmap Revision 0 (project bootstrap) and Revision 1 (typed config).

## Key Decisions

- **Package lives in `backend/`** — `backend/pyproject.toml` + `backend/src/sightloop_vision/`.
  Keeps vision service code self-contained and separate from repo docs/infra.
  (Originally the roadmap plan showed `src/` at repo root; updated to `backend/` to match
  README and copilot-instructions conventions.)
- **Package name is `sightloop_vision`** — aligns with the project branding ("SightLoop Vision")
  rather than the original `habit_enforcer` placeholder in the roadmap.
- **Pydantic v2 for config models** — gives free validation, typed access, and clear error messages
  on bad config without extra code.
- **YAML as config format** — readable, easily versioned, already conventional for this stack.
- **`uv` with optional dev dependency group** — `uv sync --extra dev` installs test and lint
  tools without polluting the runtime deps.
- **`core/config.py` instead of `config/` folder** — matches the habittracker FastAPI app
  convention where `core/` handles config loading, env setup, and shared utilities.
  Config models and the YAML loader live in a single file, same pattern as the FastAPI app's
  `core/config.py`.
- **Separate `models/` package for domain models** — `Frame`, `DetectionResult`, etc. will
  live here in later revisions. Configuration Pydantic models stay in `core/config.py`.

## Architectural Context

This revision establishes the foundation that every later phase depends on.
`AppConfig` is the single object passed through the system: camera source, resolution,
output paths, and debug settings all live here. Config is loaded once at startup and
validated early so that runtime failures caused by misconfiguration are eliminated.

The `core` module is deliberately isolated — it has no camera, pipeline, or hardware
imports. This makes it fully testable without any hardware or OpenCV dependency.

The package structure mirrors the habittracker FastAPI app layout for consistency:

| Concern | habittracker | sightloop_vision |
|---|---|---|
| Config loading | `core/config.py` | `core/config.py` |
| Domain models | `models/` | `models/` |
| API / entry points | `api/` | `app/` |
| Business logic | `services/` | `pipeline/`, `metrics/`, `debug/` |

## Flow

```
startup
  │
  ▼
load_config(path)
  │
  ├── read YAML file  ──► ConfigLoadError (file missing / bad YAML)
  │
  ├── AppConfig.model_validate(raw)
  │       ├── CameraConfig   (source, width, height, fps)
  │       ├── OutputConfig   (frames_dir, clips_dir, logs_dir)
  │       └── DebugConfig    (save_frame_interval_secs, display_enabled, ...)
  │
  └── ConfigLoadError (validation failed)
        ▼
      AppConfig  ──► passed to camera pipeline (rev-05)
```

## Scope

In scope:

- `uv` project initialisation in `backend/`
- `pyproject.toml` with runtime deps (pydantic, pyyaml) and dev deps (pytest, ruff)
- `CameraConfig`, `OutputConfig`, `DebugConfig`, `AppConfig` Pydantic models
- `load_config()` loader with `ConfigLoadError` for all failure modes
- `configs/dev.yaml`, `configs/jetson.yaml`, `configs/test.yaml`
- Unit tests covering valid load, field coercion, invalid values, and all error paths
- Lint check passing with ruff

Out of scope:

- Camera, pipeline, or hardware code
- Runner wiring (placeholder only in `app/runner.py`)
- Logging setup (rev-04)
- Frame model or camera abstraction (rev-04)

## Tasks

- [x] Initialize `uv` package project in `backend/`
- [x] Update `pyproject.toml` with all deps, pytest config, ruff config
- [x] Create `src/sightloop_vision/core/config.py` (models + loader in one file)
- [x] Create `src/sightloop_vision/models/__init__.py` (placeholder for domain models)
- [x] Create `src/sightloop_vision/app/runner.py` (placeholder)
- [x] Create `configs/dev.yaml`, `configs/jetson.yaml`, `configs/test.yaml`
- [x] Create `tests/unit/test_config_loader.py` with 23 tests
- [x] Create `tests/fixtures/test_config.yaml`
- [x] `uv run pytest` — all pass
- [x] `uv run ruff check .` — clean

## Testing

- 23 unit tests covering:
  - `CameraConfig` defaults, source coercion, field boundary validation
  - `DebugConfig` defaults and interval boundary
  - `AppConfig` construction, missing required fields, invalid environment values
  - `load_config()` — valid file, missing file, malformed YAML, non-mapping YAML,
    missing required field, invalid environment, invalid fps, string path input

## Risks Or Open Questions

- `OutputConfig` paths default to relative paths (`artifacts/frames`) — a later revision
  should ensure these are resolved relative to the project root or a configurable base.
- `app/runner.py` is a stub — the entry point script in `pyproject.toml` points to it;
  that will be wired to the camera pipeline in rev-05.

## Exit Criteria

- [x] `uv sync --extra dev` completes cleanly
- [x] `uv run pytest` passes (23/23)
- [x] `uv run ruff check .` reports no issues
- [x] Package imports resolve (`from sightloop_vision.core.config import load_config, AppConfig`)
- [x] `load_config("configs/test.yaml")` returns a typed `AppConfig` instance

## Result Summary

- `backend/` bootstrapped as a `uv` package project with Python 3.11
- Typed config system in `core/config.py` — Pydantic v2 validates all fields at load time
- `models/` package created as placeholder for domain models (Frame etc. in rev-04)
- Layout aligned with habittracker FastAPI app conventions (`core/`, `models/`)
- Three environment configs: `dev.yaml`, `jetson.yaml`, `test.yaml`
- 23 unit tests, all passing; lint clean
- Roadmap folder structure updated to reflect `backend/` root, `core/`, `models/` layout

## Next Step

**rev-04 — Frame model and camera abstraction**

Introduce `Frame` (image + timestamp + frame_id), `CameraSource` ABC with `open/read/close`,
and `OpenCVCameraSource` as the first concrete implementation. Add a `FakeCameraSource`
for use in all non-hardware tests going forward.
