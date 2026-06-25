"""Unit tests for automated detection quality gates."""

from sightloop_vision.services.detection import evaluate_detection_quality_gate


class TestDetectionQualityGate:
    def test_quality_gate_passes_with_minimum_signal(self) -> None:
        passed, reasons = evaluate_detection_quality_gate(
            detections_by_class={"person": 3, "bottle": 2},
            average_confidence_by_class={"person": 0.6, "bottle": 0.3},
            annotated_frames_saved=2,
        )

        assert passed is True
        assert reasons == []

    def test_quality_gate_returns_reasons_for_failures(self) -> None:
        passed, reasons = evaluate_detection_quality_gate(
            detections_by_class={"person": 0, "bottle": 0},
            average_confidence_by_class={"person": 0.1, "bottle": 0.1},
            annotated_frames_saved=0,
        )

        assert passed is False
        assert len(reasons) == 5
