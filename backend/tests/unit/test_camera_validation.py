"""Unit tests for camera validation summaries."""

from pathlib import Path

from sightloop_vision.services.validation import (
    CameraValidationReport,
    build_validation_report,
    mask_camera_source,
)


class TestCameraValidation:
    def test_masks_credentials_in_rtsp_url(self) -> None:
        masked = mask_camera_source("rtsp://sightloop:LetsCreateAwesome$*@192.168.50.207:554/stream1")

        assert masked == "rtsp://***:***@192.168.50.207:554/stream1"

    def test_leaves_non_credential_source_unchanged(self) -> None:
        assert mask_camera_source("rtsp://192.168.50.207:554/stream1") == "rtsp://192.168.50.207:554/stream1"
        assert mask_camera_source(0) == "0"

    def test_builds_serializable_validation_report(self) -> None:
        report = build_validation_report(
            session_name="rtsp-check",
            camera_source="rtsp://user:pass@192.168.50.207:554/stream1",
            final_summary={
                "frame_count": 42,
                "duration_secs": 7.5,
                "average_fps": 5.6,
            },
            debug_output_path=Path("artifacts/frames/rtsp-check"),
            success=True,
        )

        summary = report.to_summary_dict()

        assert isinstance(report, CameraValidationReport)
        assert summary["session_name"] == "rtsp-check"
        assert summary["camera_source"] == "rtsp://***:***@192.168.50.207:554/stream1"
        assert summary["frames_processed"] == 42
        assert summary["duration_seconds"] == 7.5
        assert summary["average_fps"] == 5.6
        assert summary["debug_output_path"] == "artifacts/frames/rtsp-check"
        assert summary["success"] is True
