"""Application configuration and YAML loader.

Mirrors the ``core/config.py`` pattern used in the habittracker FastAPI app.
Keeps only the top-level AppConfig and the loader here; sub-config models
live in their own files under ``core/``.

Usage::

    from sightloop_vision.core.config import load_config

    config = load_config("configs/dev.yaml")
"""

import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

from sightloop_vision.core.calibration import CalibrationConfig
from sightloop_vision.core.camera import CameraConfig
from sightloop_vision.core.debug import DebugConfig
from sightloop_vision.core.detection import DetectionConfig, TrackingConfig
from sightloop_vision.core.output import OutputConfig

# ---------------------------------------------------------------------------
# Top-level config
# ---------------------------------------------------------------------------


class AppConfig(BaseModel):
    """Top-level application configuration.

    Combines camera, output path, and debug settings under a single object
    that is loaded once at startup and passed through the system.
    """

    session_name: str = Field(
        description="Logical name for this run, used in file naming and logs.",
    )
    environment: str = Field(
        default="dev",
        description="Runtime environment tag: dev, jetson, test.",
    )
    camera: CameraConfig = Field(default_factory=CameraConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    debug: DebugConfig = Field(default_factory=DebugConfig)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"dev", "jetson", "test"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got {v!r}")
        return v


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


class ConfigLoadError(Exception):
    """Raised when the config file cannot be read or fails validation."""


_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_env_vars(value: object) -> object:
    """Recursively expand ${VAR_NAME} placeholders inside config values."""
    if isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_expand_env_vars(item) for item in value]

    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        env_name = match.group(1)
        env_value = os.getenv(env_name)
        if env_value is None:
            raise ConfigLoadError(
                f"Environment variable {env_name!r} is required but not set."
            )
        return env_value

    return _ENV_VAR_PATTERN.sub(replace, value)


def load_config(path: Path | str) -> AppConfig:
    """Load and validate an AppConfig from a YAML file.

    Args:
        path: Path to the YAML config file.

    Returns:
        A validated :class:`AppConfig` instance.

    Raises:
        ConfigLoadError: If the file does not exist, cannot be parsed,
            or fails Pydantic validation.
    """
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigLoadError(f"Config file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text())
    except yaml.YAMLError as exc:
        raise ConfigLoadError(f"Failed to parse YAML in {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigLoadError(
            f"Expected a YAML mapping at the top level of {config_path}, "
            f"got {type(raw).__name__}"
        )

    raw = _expand_env_vars(raw)

    try:
        return AppConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigLoadError(
            f"Config validation failed for {config_path}:\n{exc}"
        ) from exc
