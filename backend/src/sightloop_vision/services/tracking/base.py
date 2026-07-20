"""Base tracker interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sightloop_vision.models.detection import Detection

if TYPE_CHECKING:
    from sightloop_vision.models.track import Track


class Tracker(ABC):
    """Base class for object trackers."""

    @abstractmethod
    def update(self, detections: list[Detection]) -> list["Track"]:
        """Update tracker with new detections and return active tracks."""
        ...

    @abstractmethod
    def get_tracks(self) -> list["Track"]:
        """Return all current tracks."""
        ...
