"""Detection domain models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BBox:
    """Bounding box in image coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        if self.x2 <= self.x1:
            raise ValueError("BBox.x2 must be greater than x1.")
        if self.y2 <= self.y1:
            raise ValueError("BBox.y2 must be greater than y1.")

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1


@dataclass(frozen=True)
class Detection:
    """Single object detection on a frame."""

    class_name: str
    confidence: float
    bbox: BBox
    frame_id: int
    timestamp: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")
