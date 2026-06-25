"""Unit tests for detection rendering."""

from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from sightloop_vision.models import BBox, Detection, Frame
from sightloop_vision.services.rendering import DetectionRenderer


class TestDetectionRenderer:
    def _make_frame(self, frame_id: int = 0) -> Frame:
        image = np.zeros((40, 60, 3), dtype=np.uint8)
        return Frame(
            frame_id=frame_id,
            image=image,
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            source_id="fake",
        )

    def _make_detection(self) -> Detection:
        return Detection(
            class_name="person",
            confidence=0.88,
            bbox=BBox(5, 6, 25, 30),
            frame_id=0,
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

    def test_annotate_frame_returns_image(self) -> None:
        renderer = DetectionRenderer("artifacts/detections", "session-a")
        image = renderer.annotate_frame(self._make_frame(), [self._make_detection()])
        assert image.size == (60, 40)

    def test_save_annotated_frame_writes_png(self, tmp_path: Path) -> None:
        renderer = DetectionRenderer(tmp_path, "session-a")
        output_path = renderer.save_annotated_frame(
            self._make_frame(frame_id=3),
            [self._make_detection()],
        )
        assert output_path.exists()
        assert output_path.suffix == ".png"
        assert renderer.saved_frame_count == 1
