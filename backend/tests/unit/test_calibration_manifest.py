"""Unit tests for calibration manifest."""

import sys
from pathlib import Path

# Add backend root to path for scripts import - must be before local imports
# ruff: noqa: E402
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

import json
from datetime import datetime, timezone

import numpy as np
from scripts.capture_calibration_frames import CalibrationFrameWriter


class TestCalibrationManifest:
    """Test calibration manifest generation."""

    def test_calibration_writer_creates_session_dir(self, tmp_path: Path) -> None:
        """CalibrationFrameWriter creates session directory."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test")
        assert writer.session_dir == tmp_path / "calib-test"
        assert writer.frames_dir == tmp_path / "calib-test" / "frames"

    def test_calibration_writer_saves_frames(self, tmp_path: Path) -> None:
        """CalibrationFrameWriter saves frames at specified interval."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test", save_every_n_frames=1)
        frame_id = 0
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        path = writer.write_frame(frame_id, timestamp, image)

        assert path is not None
        assert path.exists()
        assert writer.saved_frame_count == 1
        assert path.suffix == ".jpg"

    def test_calibration_writer_skips_frames_outside_interval(self, tmp_path: Path) -> None:
        """CalibrationFrameWriter skips frames not matching interval."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test", save_every_n_frames=5)
        frame_id = 1  # Not divisible by 5
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        path = writer.write_frame(frame_id, timestamp, image)

        assert path is None
        assert writer.saved_frame_count == 0

    def test_calibration_manifest_contains_required_fields(self, tmp_path: Path) -> None:
        """Manifest JSON contains all required fields."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test", save_every_n_frames=1)
        frame_id = 0
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        writer.write_frame(frame_id, timestamp, image)

        manifest_path = writer.write_manifest(
            position_label="front-angle",
            notes="Test calibration capture",
            camera_source=0,
            resolution=(640, 480),
            max_frames=100,
        )

        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())

        assert manifest["session_name"] == "calib-test"
        assert manifest["position_label"] == "front-angle"
        assert manifest["notes"] == "Test calibration capture"
        assert "created_at" in manifest
        assert manifest["camera_source_masked"] == "0"
        assert manifest["resolution"] == [640, 480]
        assert manifest["max_frames"] == 100
        assert manifest["save_every_n_frames"] == 1
        assert manifest["frames_saved"] == 1
        assert manifest["output_dir"] == str(writer.session_dir)
        assert manifest["image_extension"] == "jpg"
        assert "frames" in manifest
        assert len(manifest["frames"]) == 1

    def test_calibration_manifest_masks_rtsp_source(self, tmp_path: Path) -> None:
        """Manifest masks RTSP credentials in camera source."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test", save_every_n_frames=1)
        frame_id = 0
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        writer.write_frame(frame_id, timestamp, image)

        manifest_path = writer.write_manifest(
            position_label="front-angle",
            notes="",
            camera_source="rtsp://user:pass@192.168.1.100:554/stream1",
            resolution=(1920, 1080),
            max_frames=100,
        )

        manifest = json.loads(manifest_path.read_text())

        assert "user:pass" not in manifest["camera_source_masked"]
        assert "192.168.1.100" in manifest["camera_source_masked"]

    def test_calibration_manifest_handles_none_resolution(self, tmp_path: Path) -> None:
        """Manifest handles None resolution gracefully."""
        writer = CalibrationFrameWriter(tmp_path, "calib-test", save_every_n_frames=1)
        frame_id = 0
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        writer.write_frame(frame_id, timestamp, image)

        manifest_path = writer.write_manifest(
            position_label="front-angle",
            notes="",
            camera_source=0,
            resolution=None,
            max_frames=100,
        )

        manifest = json.loads(manifest_path.read_text())
        assert manifest["resolution"] is None
