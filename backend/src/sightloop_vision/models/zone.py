"""Zone model for rectangular regions of interest."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sightloop_vision.models.detection import BBox


@dataclass(frozen=True)
class Zone:
    """Rectangular zone with a name and type."""

    name: str
    type: Literal["rectangle"]
    x1: int
    y1: int
    x2: int
    y2: int

    def __post_init__(self) -> None:
        if self.x2 <= self.x1:
            raise ValueError(f"Zone {self.name}: x2 must be > x1")
        if self.y2 <= self.y1:
            raise ValueError(f"Zone {self.name}: y2 must be > y1")

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the zone."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def contains_bbox_center(self, bbox: "BBox") -> bool:
        """Check if the center of a bounding box is inside the zone."""
        center_x = (bbox.x1 + bbox.x2) / 2
        center_y = (bbox.y1 + bbox.y2) / 2
        return self.contains_point(center_x, center_y)

    def center(self) -> tuple[float, float]:
        """Return the center point of the zone."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def width(self) -> int:
        return self.x2 - self.x1

    def height(self) -> int:
        return self.y2 - self.y1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Zone":
        return cls(
            name=data["name"],
            type=data["type"],
            x1=data["x1"],
            y1=data["y1"],
            x2=data["x2"],
            y2=data["y2"],
        )
