"""Detection filtering helpers."""

from sightloop_vision.models import Detection


def filter_detections_by_allowed_classes(
    detections: list[Detection],
    allowed_classes: set[str] | list[str],
) -> list[Detection]:
    """Keep only detections whose class names are allowed."""
    allowed = set(allowed_classes)
    return [detection for detection in detections if detection.class_name in allowed]


def filter_detections_by_confidence(
    detections: list[Detection],
    confidence_threshold: float,
) -> list[Detection]:
    """Keep only detections meeting the minimum confidence threshold."""
    return [
        detection
        for detection in detections
        if detection.confidence >= confidence_threshold
    ]
