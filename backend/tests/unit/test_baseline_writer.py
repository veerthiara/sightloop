"""Unit tests for detection baseline report writing."""

import json
from pathlib import Path

from sightloop_vision.services.detection import (
    DetectionBaselineReport,
    DetectionBaselineWriter,
)


class TestBaselineWriter:
    def _report(self) -> DetectionBaselineReport:
        return DetectionBaselineReport(
            session_name="session-a",
            model_name="yolov8n.pt",
            confidence_threshold=0.35,
            run_every_n_frames=30,
            classes=["person", "bottle"],
            frames_processed=90,
            detection_frames_processed=3,
            detections_by_class={"person": 2, "bottle": 1},
            average_confidence_by_class={"person": 0.7, "bottle": 0.4},
            min_confidence_by_class={"person": 0.6, "bottle": 0.4},
            max_confidence_by_class={"person": 0.8, "bottle": 0.4},
            annotated_frames_saved=3,
            output_dir="artifacts/detections/session-a",
            masked_camera_source="rtsp://***:***@10.0.0.2:554/stream1",
            created_at="2026-06-24T12:00:00+00:00",
            quality_gate_result=True,
            quality_gate_reasons=[],
            manual_review_required=True,
            notes="Review boxes manually.",
        )

    def test_writes_json_and_markdown(self, tmp_path: Path) -> None:
        writer = DetectionBaselineWriter(tmp_path)
        report = self._report()

        json_path, markdown_path = writer.write_all(report)

        assert json_path.exists()
        assert markdown_path.exists()

        payload = json.loads(json_path.read_text())
        assert payload["masked_camera_source"] == "rtsp://***:***@10.0.0.2:554/stream1"
        markdown = markdown_path.read_text()
        assert "Manual Review Checklist" in markdown
        assert "rtsp://***:***@10.0.0.2:554/stream1" in markdown

