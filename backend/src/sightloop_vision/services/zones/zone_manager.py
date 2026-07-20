"""Zone management for evaluating detections against zones."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sightloop_vision.models.detection import Detection
from sightloop_vision.models.zone import Zone

if TYPE_CHECKING:
    from sightloop_vision.models.track import Track


class ZoneManager:
    """Manage zones and evaluate which zones contain detections or tracks."""

    def __init__(self, zones: list[Zone]) -> None:
        self._zones = zones
        self._zone_map = {zone.name: zone for zone in zones}

    @property
    def zones(self) -> list[Zone]:
        return self._zones

    def get_zone(self, name: str) -> Zone | None:
        return self._zone_map.get(name)

    def evaluate_detection(self, detection: Detection) -> list[str]:
        """Return list of zone names that contain the detection bbox center."""
        zone_names = []
        for zone in self._zones:
            if zone.contains_bbox_center(detection.bbox):
                zone_names.append(zone.name)
        return zone_names

    def evaluate_track(self, track: "Track") -> list[str]:
        """Return list of zone names that contain the track bbox center."""
        zone_names = []
        for zone in self._zones:
            if zone.contains_bbox_center(track.bbox):
                zone_names.append(zone.name)
        return zone_names

    def get_zone_events(self, track: "Track") -> list[tuple[str, str]]:
        """Get zone enter/exit events for a track."""
        return track.check_zones(self._zones)
