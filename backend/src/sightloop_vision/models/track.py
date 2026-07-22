"""Track model for object tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sightloop_vision.models.detection import BBox, Detection

if TYPE_CHECKING:
    from sightloop_vision.models.zone import Zone


@dataclass
class Track:
    """A tracked object with history."""

    track_id: int
    class_name: str
    bbox: BBox
    confidence: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    frames_since_update: int = 0
    hit_streak: int = 1
    age: int = 1
    _zone_entered: dict[str, datetime] = field(default_factory=dict, repr=False)
    _zone_exited: dict[str, datetime] = field(default_factory=dict, repr=False)

    def update(self, detection: Detection) -> None:
        """Update track with new detection."""
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.updated_at = datetime.now(timezone.utc)
        self.frames_since_update = 0
        self.hit_streak += 1
        self.age += 1

    def mark_missed(self) -> None:
        """Mark track as missed in current frame."""
        self.frames_since_update += 1
        self.age += 1

    def is_confirmed(self, min_hits: int = 3) -> bool:
        """Check if track is confirmed (has enough hits)."""
        return self.hit_streak >= min_hits

    def is_lost(self, max_age: int = 30) -> bool:
        """Check if track should be removed."""
        return self.frames_since_update > max_age

    def check_zones(self, zones: list["Zone"]) -> list[tuple[str, str]]:
        """Check which zones the track is in and return zone events.

        Returns list of (zone_name, event) where event is 'enter' or 'exit'.
        """
        events = []
        now = datetime.now(timezone.utc)

        for zone in zones:
            in_zone = zone.contains_bbox_center(self.bbox)
            zone_name = zone.name

            if in_zone:
                if zone_name not in self._zone_entered:
                    self._zone_entered[zone_name] = now
                    events.append((zone_name, "enter"))
                elif zone_name in self._zone_exited:
                    # Re-entered after exiting
                    self._zone_entered[zone_name] = now
                    del self._zone_exited[zone_name]
                    events.append((zone_name, "enter"))
            else:
                if zone_name in self._zone_entered and zone_name not in self._zone_exited:
                    self._zone_exited[zone_name] = now
                    events.append((zone_name, "exit"))

        return events

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "bbox": self.bbox.to_dict(),
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "frames_since_update": self.frames_since_update,
            "hit_streak": self.hit_streak,
            "age": self.age,
        }

    @property
    def zones(self) -> list[str]:
        """Return list of zone names this track is currently in."""
        return list(self._zone_entered.keys())
