# Phase 0 Revision 2 — Frame Model and Camera Abstraction

## Goal

Introduce a stable `Frame` data structure and an abstract `CameraSource` interface so the rest of the pipeline never depends on raw OpenCV objects directly. Provide a `FakeCameraSource` for tests and an `OpenCVCameraSource` for real hardware.

## Key Decisions

- **`adapters/` vs `services/` split** — hardware boundary code (camera adapters, future detector adapters) lives under `adapters/`. Processing and orchestration (pipeline, metrics, debug, logging) lives under `services/`. This follows a ports-and-adapters pattern and keeps I/O boundaries separate from business logic. As phases progress, new adapters (e.g. `adapters/detector/`) and services (e.g. `services/pipeline/`) slot in without restructuring.
- **Frame as a frozen dataclass** — immutability prevents accidental mutation as a frame travels through the pipeline. `width` and `height` are derived automatically from the numpy image shape.
- **ABC-based CameraSource** — forces all camera implementations to provide `open()`, `read()`, `close()`. Context manager and iterator support are mixed in at the base class level.
- **FakeCameraSource for deterministic testing** — produces solid-colour frames with predictable IDs and timestamps, no hardware needed. Supports finite and infinite modes.
- **OpenCV as an optional dependency** — installed via `uv sync --extra camera`. The `opencv.py` module raises a clear `ImportError` if `cv2` is missing, so core tests never require it.
- **numpy is a core dependency** — needed by Frame for the image array. Added to `[project.dependencies]`.

## Architectural Context

This revision implements **Roadmap Revision 2** from `docs/roadmap/02-phase-0-foundation-detailed.md`.

The `Frame` model lives in `models/` (domain data), while camera implementations live in `camera/` (hardware boundary). This follows the separation of concerns established in the roadmap: camera code stays at the edge, domain objects stay in the centre, and the pipeline (Revision 3) will connect them.

```
camera/base.py  →  models/frame.py  ←  pipeline (rev-03)
camera/fake.py ↗        ↑
camera/opencv.py ↗       │
                    metrics, debug (rev-04, rev-05)
```

## Scope Implemented

- `Frame` frozen dataclass with derived `width`/`height`, shape validation, and repr
- `CameraSource` ABC with context manager and iterator support
- `CameraOpenError` exception for failed camera opens
- `FakeCameraSource` — configurable synthetic frame emitter for tests
- `OpenCVCameraSource` — real camera backed by `cv2.VideoCapture`
- 22 unit tests covering Frame construction, immutability, edge cases, and FakeCameraSource behaviour
- numpy added to project dependencies
- opencv-python added as optional `[camera]` extra

## Files Changed

| File | Change |
| --- | --- |
| `backend/src/sightloop_vision/models/frame.py` | New — Frame frozen dataclass |
| `backend/src/sightloop_vision/models/__init__.py` | Updated — re-exports Frame |
| `backend/src/sightloop_vision/adapters/__init__.py` | New — adapters package |
| `backend/src/sightloop_vision/adapters/camera/__init__.py` | New — exports CameraSource, FakeCameraSource, CameraOpenError |
| `backend/src/sightloop_vision/adapters/camera/base.py` | New — CameraSource ABC + CameraOpenError |
| `backend/src/sightloop_vision/adapters/camera/fake.py` | New — FakeCameraSource |
| `backend/src/sightloop_vision/adapters/camera/opencv.py` | New — OpenCVCameraSource (requires cv2) |
| `backend/src/sightloop_vision/services/__init__.py` | New — services package placeholder |
| `backend/tests/unit/test_frame_and_camera.py` | New — 22 tests for Frame + FakeCameraSource |
| `backend/pyproject.toml` | Updated — numpy dep, opencv-python optional extra |
| `backend/uv.lock` | Updated — resolved new dependencies |
| `docs/roadmap/02-phase-0-foundation-detailed.md` | Updated — folder structure reflects adapters/ + services/ layout |
| `docs/implementation/phase-0/codex-01-project-bootstrap.md` | Renamed from rev-01 (pre-roadmap Codex work) |
| `docs/implementation/phase-0/codex-02-docs-site-setup.md` | Renamed from rev-02 (pre-roadmap Codex work) |
| `docs/implementation/phase-0/rev-00-01-project-bootstrap-and-config.md` | Renamed from rev-03 to align with roadmap revision numbering |

## Notes

- **Implementation doc renaming**: Codex pre-work docs (previously rev-01, rev-02) were renamed to `codex-01-*` and `codex-02-*` to free up revision numbers for roadmap-aligned naming. The config/bootstrap work (previously rev-03) was renamed to `rev-00-01-*` since it covers Roadmap Revision 0 + Revision 1 combined.
- **config.py corruption fix**: The `core/config.py` file was corrupted by a terminal heredoc issue in the previous session. It was recreated from scratch, verified with `ast.parse`, and the fix was amended into the rev-03 commit on `phase-00-rev-03-foundation`.
- OpenCV tests are not included in the unit test suite since they require hardware. Hardware smoke tests will come in Revision 6.
- The `timedelta` import inside `FakeCameraSource.read()` could be moved to module level — minor cleanup for later.

## Next Step

**Revision 3 — Main camera pipeline**: Build the continuous processing loop that reads frames from a CameraSource, attaches timestamps, updates metrics hooks, and handles clean shutdown.
