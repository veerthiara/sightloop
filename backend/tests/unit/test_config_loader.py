"""Unit tests for the config loader and models."""

from pathlib import Path

import pytest

from sightloop_vision.core import (
    AppConfig,
    CameraConfig,
    ConfigLoadError,
    DebugConfig,
    DetectionConfig,
    OutputConfig,
    load_config,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
VALID_CONFIG = FIXTURES_DIR / "test_config.yaml"


# ---------------------------------------------------------------------------
# AppConfig model validation
# ---------------------------------------------------------------------------


class TestCameraConfig:
    def test_defaults_are_valid(self) -> None:
        cam = CameraConfig()
        assert cam.source == 0
        assert cam.width == 1280
        assert cam.height == 720
        assert cam.fps == 30

    def test_integer_source(self) -> None:
        cam = CameraConfig(source=2)
        assert cam.source == 2

    def test_string_uri_source(self) -> None:
        cam = CameraConfig(source="rtsp://10.0.0.1:554/stream")
        assert cam.source == "rtsp://10.0.0.1:554/stream"

    def test_numeric_string_is_coerced_to_int(self) -> None:
        cam = CameraConfig(source="1")
        assert cam.source == 1
        assert isinstance(cam.source, int)

    def test_fps_below_minimum_raises(self) -> None:
        with pytest.raises(Exception):
            CameraConfig(fps=0)

    def test_fps_above_maximum_raises(self) -> None:
        with pytest.raises(Exception):
            CameraConfig(fps=999)

    def test_width_below_minimum_raises(self) -> None:
        with pytest.raises(Exception):
            CameraConfig(width=0)


class TestDebugConfig:
    def test_defaults_are_valid(self) -> None:
        d = DebugConfig()
        assert d.enabled is False
        assert d.output_dir is None
        assert d.save_every_n_frames == 30
        assert d.display_enabled is False
        assert d.metrics_log_interval_secs == 10.0

    def test_save_interval_below_minimum_raises(self) -> None:
        with pytest.raises(Exception):
            DebugConfig(save_every_n_frames=0)


class TestAppConfig:
    def test_valid_config_constructs(self) -> None:
        cfg = AppConfig(session_name="my-session")
        assert cfg.session_name == "my-session"
        assert cfg.environment == "dev"
        assert isinstance(cfg.camera, CameraConfig)
        assert isinstance(cfg.output, OutputConfig)
        assert isinstance(cfg.debug, DebugConfig)
        assert isinstance(cfg.detection, DetectionConfig)

    def test_missing_session_name_raises(self) -> None:
        with pytest.raises(Exception):
            AppConfig()  # type: ignore[call-arg]

    def test_invalid_environment_raises(self) -> None:
        with pytest.raises(Exception):
            AppConfig(session_name="s", environment="production")

    def test_all_valid_environments_accepted(self) -> None:
        for env in ("dev", "jetson", "test"):
            cfg = AppConfig(session_name="s", environment=env)
            assert cfg.environment == env


# ---------------------------------------------------------------------------
# load_config — file-based tests
# ---------------------------------------------------------------------------


class TestLoadConfig:
    def test_valid_yaml_loads_successfully(self) -> None:
        cfg = load_config(VALID_CONFIG)
        assert isinstance(cfg, AppConfig)
        assert cfg.session_name == "fixture-session"
        assert cfg.environment == "test"

    def test_camera_fields_loaded_correctly(self) -> None:
        cfg = load_config(VALID_CONFIG)
        assert cfg.camera.width == 640
        assert cfg.camera.height == 480
        assert cfg.camera.fps == 15

    def test_debug_display_disabled(self) -> None:
        cfg = load_config(VALID_CONFIG)
        assert cfg.debug.display_enabled is False

    def test_debug_frame_writer_fields_loaded(self) -> None:
        cfg = load_config(VALID_CONFIG)
        assert cfg.debug.enabled is True
        assert cfg.debug.save_every_n_frames == 2
        assert cfg.debug.output_dir == Path("/tmp/sightloop-test/frames")

    def test_nonexistent_file_raises_config_load_error(self) -> None:
        with pytest.raises(ConfigLoadError, match="not found"):
            load_config(Path("/does/not/exist.yaml"))

    def test_invalid_yaml_raises_config_load_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text(": invalid: yaml: {")
        with pytest.raises(ConfigLoadError, match="Failed to parse YAML"):
            load_config(bad)

    def test_non_mapping_yaml_raises_config_load_error(self, tmp_path: Path) -> None:
        scalar = tmp_path / "scalar.yaml"
        scalar.write_text("just a string\n")
        with pytest.raises(ConfigLoadError, match="Expected a YAML mapping"):
            load_config(scalar)

    def test_missing_required_field_raises_config_load_error(self, tmp_path: Path) -> None:
        missing_session = tmp_path / "no_session.yaml"
        missing_session.write_text("environment: dev\n")
        with pytest.raises(ConfigLoadError, match="validation failed"):
            load_config(missing_session)

    def test_invalid_environment_raises_config_load_error(self, tmp_path: Path) -> None:
        bad_env = tmp_path / "bad_env.yaml"
        bad_env.write_text("session_name: s\nenvironment: production\n")
        with pytest.raises(ConfigLoadError, match="validation failed"):
            load_config(bad_env)

    def test_invalid_fps_raises_config_load_error(self, tmp_path: Path) -> None:
        bad_fps = tmp_path / "bad_fps.yaml"
        bad_fps.write_text("session_name: s\ncamera:\n  fps: 0\n")
        with pytest.raises(ConfigLoadError, match="validation failed"):
            load_config(bad_fps)

    def test_accepts_path_string(self) -> None:
        cfg = load_config(str(VALID_CONFIG))
        assert isinstance(cfg, AppConfig)

    def test_detection_defaults_load_when_missing_from_yaml(self) -> None:
        cfg = load_config(VALID_CONFIG)
        assert cfg.detection.enabled is False
        assert cfg.detection.model_name == "yolov8n.pt"
        assert cfg.detection.candidate_models == ["yolov8n.pt", "yolov8s.pt"]
        assert cfg.detection.classes == ["person", "bottle"]

    def test_expands_env_var_placeholders(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TEST_RTSP_URL", "rtsp://user:pass@10.0.0.1:554/stream1")
        config_file = tmp_path / "env.yaml"
        config_file.write_text(
            "session_name: env-test\n"
            "camera:\n"
            "  source: \"${TEST_RTSP_URL}\"\n"
        )

        cfg = load_config(config_file)

        assert cfg.camera.source == "rtsp://user:pass@10.0.0.1:554/stream1"

    def test_missing_env_var_placeholder_raises_config_load_error(
        self,
        tmp_path: Path,
    ) -> None:
        config_file = tmp_path / "missing_env.yaml"
        config_file.write_text(
            "session_name: env-test\n"
            "camera:\n"
            "  source: \"${MISSING_RTSP_URL}\"\n"
        )

        with pytest.raises(ConfigLoadError, match="required but not set"):
            load_config(config_file)
