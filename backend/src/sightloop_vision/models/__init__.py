"""Domain models package — Frame, detection results, events, etc."""

from sightloop_vision.models.detection import BBox, Detection
from sightloop_vision.models.frame import Frame

__all__ = ["BBox", "Detection", "Frame"]
