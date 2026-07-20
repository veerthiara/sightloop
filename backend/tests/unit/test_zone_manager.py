"""Unit tests for zone manager."""

from datetime import datetime, timezone

from sightloop_vision.models.detection import BBox, Detection
from sightloop_vision.models.zone import Zone
from sightloop_vision.services.zones.zone_manager import ZoneManager


class TestZoneManager:
    """Test ZoneManager."""

    def test_evaluate_detection(self) -> None:
        """Test detection zone evaluation."""
        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
            Zone(name="desk", type="rectangle", x1=50, y1=50, x2=400, y2=400),
        ]
        manager = ZoneManager(zones)

        detection = Detection(
            class_name="bottle",
            confidence=0.9,
            bbox=BBox(x1=150, y1=150, x2=250, y2=250),  # Center at 200, 200
            frame_id=0,
            timestamp=datetime.now(timezone.utc),
        )
        zone_names = manager.evaluate_detection(detection)
        assert "bottle_home" in zone_names
        assert "desk" in zone_names

    def test_evaluate_detection_outside(self) -> None:
        """Test detection outside all zones."""
        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
        ]
        manager = ZoneManager(zones)

        detection = Detection(
            class_name="bottle",
            confidence=0.9,
            bbox=BBox(x1=500, y1=500, x2=600, y2=600),  # Center at 550, 550
            frame_id=0,
            timestamp=datetime.now(timezone.utc),
        )
        zone_names = manager.evaluate_detection(detection)
        assert zone_names == []

    def test_evaluate_track(self) -> None:
        """Test track zone evaluation."""
        from sightloop_vision.models.track import Track

        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
            Zone(name="desk", type="rectangle", x1=50, y1=50, x2=400, y2=400),
        ]
        manager = ZoneManager(zones)

        track = Track(
            track_id=1,
            class_name="bottle",
            bbox=BBox(x1=150, y1=150, x2=250, y2=250),
            confidence=0.9,
        )
        zone_names = manager.evaluate_track(track)
        assert "bottle_home" in zone_names
        assert "desk" in zone_names

    def test_get_zone(self) -> None:
        """Test getting zone by name."""
        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
            Zone(name="desk", type="rectangle", x1=50, y1=50, x2=400, y2=400),
        ]
        manager = ZoneManager(zones)

        zone = manager.get_zone("bottle_home")
        assert zone is not None
        assert zone.name == "bottle_home"

        zone_not_found = manager.get_zone("nonexistent")
        assert zone_not_found is None
