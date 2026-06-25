"""Services — processing and orchestration modules.

Planned modules:
  pipeline/  — main frame-reading loop (rev-03)
  metrics/   — FPS tracker, session stats (rev-04)
  debug/     — frame and clip writers (rev-05)
  logging/   — structured log setup (rev-05)
"""

from sightloop_vision.services.debug import ClipWriter, FrameWriter
from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
from sightloop_vision.services.pipeline import CameraPipeline
from sightloop_vision.services.validation import (
    CameraValidationReport,
    build_validation_report,
    mask_camera_source,
)

__all__ = [
    "CameraPipeline",
    "CameraSessionStats",
    "ClipWriter",
    "FpsTracker",
    "FrameWriter",
    "CameraValidationReport",
    "build_validation_report",
    "mask_camera_source",
]
