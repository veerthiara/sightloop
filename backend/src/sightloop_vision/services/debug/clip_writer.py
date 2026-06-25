"""Minimal placeholder for future clip recording."""

from __future__ import annotations

from sightloop_vision.models import Frame


class ClipWriter:
    """No-op placeholder for a future video clip writer."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def write_frame(self, frame: Frame) -> None:
        """Accept a frame without recording anything yet."""
        _ = frame
