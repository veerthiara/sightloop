"""Unit tests for automated detection baseline reports."""

from sightloop_vision.services.detection import build_detection_baseline_report


class TestDetectionBaseline:
    def test_builds_serializable_baseline_report(self) -> None:
        report = build_detection_baseline_report(
            session_name="session-a",
            model_name="yolov8n.pt",
            confidence_threshold=0.35,
            run_every_n_frames=30,
            classes=["person", "bottle"],
            camera_source="rtsp://user:pass@10.0.0.2:554/stream1",
            output_dir="artifacts/detections/session-a",
            quality_summary={
                "frames_processed": 90,
                "detection_frames_processed": 3,
                "detections_by_class": {"person": 2, "bottle": 1},
                "average_confidence_by_class": {"person": 0.7, "bottle": 0.4},
                "min_confidence_by_class": {"person": 0.6, "bottle": 0.4},
                "max_confidence_by_class": {"person": 0.8, "bottle": 0.4},
                "annotated_frames_saved": 3,
            },
            notes="Initial baseline.",
        )

        summary = report.to_summary_dict()

        assert summary["session_name"] == "session-a"
        assert summary["model_name"] == "yolov8n.pt"
        assert summary["masked_camera_source"] == "rtsp://***:***@10.0.0.2:554/stream1"
        assert summary["quality_gate_result"] is True
        assert summary["manual_review_required"] is True
        assert summary["notes"] == "Initial baseline."

