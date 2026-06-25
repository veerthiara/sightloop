"""Unit tests for detection domain models."""

from datetime import datetime, timezone

import pytest

from sightloop_vision.models import BBox, Detection


class TestBBox:
    def test_valid_bbox_exposes_width_and_height(self) -> None:
        bbox = BBox(x1=10, y1=20, x2=50, y2=80)
        assert bbox.width == 40
        assert bbox.height == 60

    def test_invalid_bbox_raises(self) -> None:
        with pytest.raises(ValueError, match="greater than x1"):
            BBox(x1=5, y1=0, x2=5, y2=10)


class TestDetection:
    def test_valid_detection_constructs(self) -> None:
        detection = Detection(
            class_name="person",
            confidence=0.9,
            bbox=BBox(1, 2, 3, 4),
            frame_id=7,
            timestamp=datetime.now(tz=timezone.utc),
        )
        assert detection.class_name == "person"
        assert detection.frame_id == 7

    def test_invalid_confidence_raises(self) -> None:
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            Detection(
                class_name="bottle",
                confidence=1.1,
                bbox=BBox(1, 2, 5, 6),
                frame_id=0,
                timestamp=datetime.now(tz=timezone.utc),
            )
