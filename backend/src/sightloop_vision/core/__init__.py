"""Core package — configuration loading, environment setup, and shared utilities."""

from sightloop_vision.core.camera import CameraConfig
from sightloop_vision.core.config import AppConfig, ConfigLoadError, load_config
from sightloop_vision.core.debug import DebugConfig
from sightloop_vision.core.detection import DetectionConfig
from sightloop_vision.core.output import OutputConfig

__all__ = [
    "AppConfig",
    "CameraConfig",
    "ConfigLoadError",
    "DebugConfig",
    "DetectionConfig",
    "OutputConfig",
    "load_config",
]
