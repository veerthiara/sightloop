"""Detector interface."""

from abc import ABC, abstractmethod

from sightloop_vision.models import Detection, Frame


class Detector(ABC):
    """Abstract object detector."""

    @abstractmethod
    def detect(self, frame: Frame) -> list[Detection]:
        """Return detections for a frame."""
