"""Unit tests for artifact path standardization."""

from pathlib import Path

from sightloop_vision.core.config import load_config
from sightloop_vision.services.debug import FrameWriter
from sightloop_vision.services.rendering import DetectionRenderer


class TestArtifactPaths:
    """Test that artifact paths follow the standardized structure."""

    def test_frame_writer_session_path(self, tmp_path: Path) -> None:
        """FrameWriter creates session directory under frames_dir."""
        writer = FrameWriter(tmp_path, "test-session")
        assert writer.session_dir == tmp_path / "test-session"

    def test_frame_writer_output_path_structure(self, tmp_path: Path) -> None:
        """FrameWriter output path uses standardized naming."""
        from datetime import datetime, timezone

        import numpy as np

        writer = FrameWriter(tmp_path, "test-session")
        frame_id = 42
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        from sightloop_vision.models import Frame
        frame = Frame(
            frame_id=frame_id,
            image=image,
            timestamp=timestamp,
            source_id="test",
        )

        path = writer.build_output_path(frame)
        assert path.parent == tmp_path / "test-session"
        assert path.name.startswith("frame_000042_")
        assert path.suffix == ".jpg"

    def test_detection_renderer_session_structure(self, tmp_path: Path) -> None:
        """DetectionRenderer creates annotated/person/bottle/no_target subdirs."""
        renderer = DetectionRenderer(tmp_path, "detect-session")
        assert renderer.annotated_dir == tmp_path / "detect-session" / "annotated"
        assert renderer.person_dir == tmp_path / "detect-session" / "person"
        assert renderer.bottle_dir == tmp_path / "detect-session" / "bottle"
        assert renderer.no_target_dir == tmp_path / "detect-session" / "no_target"

    def test_detection_renderer_output_path_structure(self, tmp_path: Path) -> None:
        """DetectionRenderer output path uses standardized naming."""
        from datetime import datetime, timezone

        import numpy as np

        renderer = DetectionRenderer(tmp_path, "detect-session")
        frame_id = 100
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        image = np.full((480, 640, 3), fill_value=128, dtype=np.uint8)

        from sightloop_vision.models import Frame
        frame = Frame(
            frame_id=frame_id,
            image=image,
            timestamp=timestamp,
            source_id="test",
        )

        path = renderer.build_output_path(frame)
        assert path.parent == tmp_path / "detect-session" / "annotated"
        assert path.name.startswith("frame_000100_")
        assert path.suffix == ".png"

    def test_config_output_paths_match_standard(self, tmp_path: Path) -> None:
        """Config paths use artifacts/ standard structure."""
        config_yaml = tmp_path / "test_config.yaml"
        config_yaml.write_text("""
session_name: test-session
environment: test
camera:
  source: 0
  width: 640
  height: 480
output:
  frames_dir: artifacts/frames
  clips_dir: artifacts/clips
  logs_dir: artifacts/logs
debug:
  enabled: true
  output_dir: artifacts/frames
  save_every_n_frames: 1
  display_enabled: false
  metrics_log_interval_secs: 1.0
calibration:
  output_dir: artifacts/calibration
""")

        config = load_config(config_yaml)

        assert config.output.frames_dir == Path("artifacts/frames")
        assert config.output.clips_dir == Path("artifacts/clips")
        assert config.output.logs_dir == Path("artifacts/logs")
        assert config.debug.output_dir == Path("artifacts/frames")
        assert config.calibration.output_dir == Path("artifacts/calibration")

    def test_frame_writer_image_extension_configurable(self, tmp_path: Path) -> None:
        """FrameWriter respects image_extension config."""
        writer_jpg = FrameWriter(tmp_path, "session", image_extension="jpg")
        writer_png = FrameWriter(tmp_path, "session", image_extension="png")

        assert writer_jpg.image_extension == "jpg"
        assert writer_png.image_extension == "png"

    def test_detection_renderer_image_extension_configurable(self, tmp_path: Path) -> None:
        """DetectionRenderer respects image_extension config."""
        renderer_jpg = DetectionRenderer(tmp_path, "session", image_extension="jpg")
        renderer_png = DetectionRenderer(tmp_path, "session", image_extension="png")

        assert renderer_jpg.image_extension == "jpg"
        assert renderer_png.image_extension == "png"
