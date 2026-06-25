"""Detection services."""

from sightloop_vision.services.detection.base import Detector
from sightloop_vision.services.detection.filters import (
    filter_detections_by_allowed_classes,
    filter_detections_by_confidence,
)
from sightloop_vision.services.detection.yolo_detector import YoloDetector

__all__ = [
    "Detector",
    "YoloDetector",
    "filter_detections_by_allowed_classes",
    "filter_detections_by_confidence",
]
