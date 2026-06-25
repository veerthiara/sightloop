"""Unit tests for detection quality reporting."""

from datetime import datetime, timezone

from sightloop_vision.models import BBox, Detection
from sightloop_vision.services.detection import DetectionQualityReport


def _detection(class_name: str, confidence: float) -> Detection:
    return Detection(
        class_name=class_name,
        confidence=confidence,
        bbox=BBox(1, 2, 10, 20),
        frame_id=0,
        timestamp=datetime.now(tz=timezone.utc),
    )


class TestDetectionQualityReport:
    def test_aggregates_counts_and_average_confidence(self) -> None:
        report = DetectionQualityReport()
        report.set_frames_processed(60)
        report.record_detection_frame(
            [
                _detection("person", 0.8),
                _detection("person", 0.6),
                _detection("bottle", 0.5),
            ]
        )
        report.record_detection_frame([_detection("bottle", 0.9)])

        summary = report.to_summary_dict()

        assert summary["frames_processed"] == 60
        assert summary["detection_frames_processed"] == 2
        assert summary["annotated_frames_saved"] == 2
        assert summary["detections_by_class"] == {"person": 2, "bottle": 2}
        assert summary["average_confidence_by_class"] == {"person": 0.7, "bottle": 0.7}

    def test_handles_empty_report(self) -> None:
        report = DetectionQualityReport()
        assert report.to_summary_dict() == {
            "frames_processed": 0,
            "detection_frames_processed": 0,
            "detections_by_class": {},
            "average_confidence_by_class": {},
            "annotated_frames_saved": 0,
        }
