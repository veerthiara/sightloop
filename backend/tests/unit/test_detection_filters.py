"""Unit tests for detection filters."""

from datetime import datetime, timezone

from sightloop_vision.models import BBox, Detection
from sightloop_vision.services.detection import (
    filter_detections_by_allowed_classes,
    filter_detections_by_confidence,
)


def _detection(class_name: str, confidence: float) -> Detection:
    return Detection(
        class_name=class_name,
        confidence=confidence,
        bbox=BBox(1, 2, 10, 20),
        frame_id=0,
        timestamp=datetime.now(tz=timezone.utc),
    )


class TestDetectionFilters:
    def test_filter_by_allowed_classes(self) -> None:
        detections = [
            _detection("person", 0.9),
            _detection("bottle", 0.8),
            _detection("chair", 0.95),
        ]
        filtered = filter_detections_by_allowed_classes(detections, ["person", "bottle"])
        assert [d.class_name for d in filtered] == ["person", "bottle"]

    def test_filter_by_confidence(self) -> None:
        detections = [
            _detection("person", 0.9),
            _detection("bottle", 0.2),
        ]
        filtered = filter_detections_by_confidence(detections, 0.35)
        assert [d.class_name for d in filtered] == ["person"]
