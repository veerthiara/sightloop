"""Camera adapter package — CameraSource ABC and implementations."""

from .base import CameraOpenError, CameraSource
from .fake import FakeCameraSource

__all__ = ["CameraOpenError", "CameraSource", "FakeCameraSource"]
