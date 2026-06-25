"""Detection services."""

from sightloop_vision.services.detection.base import Detector
from sightloop_vision.services.detection.baseline import (
    DetectionBaselineReport,
    build_detection_baseline_report,
    evaluate_detection_quality_gate,
)
from sightloop_vision.services.detection.baseline_writer import DetectionBaselineWriter
from sightloop_vision.services.detection.filters import (
    filter_detections_by_allowed_classes,
    filter_detections_by_confidence,
)
from sightloop_vision.services.detection.model_registry import (
    DEFAULT_CANDIDATE_MODELS,
    get_candidate_models,
    is_supported_model,
)
from sightloop_vision.services.detection.quality_report import DetectionQualityReport
from sightloop_vision.services.detection.yolo_detector import YoloDetector

__all__ = [
    "DetectionBaselineReport",
    "DetectionBaselineWriter",
    "DEFAULT_CANDIDATE_MODELS",
    "Detector",
    "DetectionQualityReport",
    "YoloDetector",
    "build_detection_baseline_report",
    "evaluate_detection_quality_gate",
    "filter_detections_by_allowed_classes",
    "filter_detections_by_confidence",
    "get_candidate_models",
    "is_supported_model",
]
