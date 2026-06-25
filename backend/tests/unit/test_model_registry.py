"""Unit tests for supported detection model registry."""

from sightloop_vision.services.detection import (
    DEFAULT_CANDIDATE_MODELS,
    get_candidate_models,
    is_supported_model,
)


class TestModelRegistry:
    def test_default_candidates_include_expected_models(self) -> None:
        assert DEFAULT_CANDIDATE_MODELS == ["yolov8n.pt", "yolov8s.pt"]
        assert get_candidate_models() == ["yolov8n.pt", "yolov8s.pt"]

    def test_uses_configured_candidates_when_provided(self) -> None:
        candidates = ["custom-a.pt", "custom-b.pt"]
        assert get_candidate_models(candidates) == candidates

    def test_checks_supported_model_membership(self) -> None:
        assert is_supported_model("yolov8n.pt") is True
        assert is_supported_model("yolov8m.pt") is False
        assert is_supported_model("custom-a.pt", ["custom-a.pt"]) is True
