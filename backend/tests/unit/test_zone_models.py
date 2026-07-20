"""Unit tests for zone models."""

import pytest

from sightloop_vision.models.detection import BBox
from sightloop_vision.models.zone import Zone


class TestZoneModel:
    """Test Zone model."""

    def test_zone_creation_valid(self) -> None:
        """Create valid zone."""
        zone = Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        assert zone.name == "bottle_home"
        assert zone.type == "rectangle"
        assert zone.x1 == 100
        assert zone.x2 == 300
        assert zone.y1 == 100
        assert zone.y2 == 300

    def test_zone_creation_invalid_x2_le_x1(self) -> None:
        """Zone with x2 <= x1 raises ValueError."""
        with pytest.raises(ValueError, match="x2 must be > x1"):
            Zone(name="bad", type="rectangle", x1=300, y1=100, x2=100, y2=300)

    def test_zone_creation_invalid_y2_le_y1(self) -> None:
        """Zone with y2 <= y1 raises ValueError."""
        with pytest.raises(ValueError, match="y2 must be > y1"):
            Zone(name="bad", type="rectangle", x1=100, y1=300, x2=300, y2=100)

    def test_contains_point(self) -> None:
        """Test point containment."""
        zone = Zone(name="test", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        assert zone.contains_point(150, 150) is True
        assert zone.contains_point(100, 100) is True
        assert zone.contains_point(300, 300) is True
        assert zone.contains_point(50, 150) is False
        assert zone.contains_point(150, 50) is False
        assert zone.contains_point(350, 150) is False
        assert zone.contains_point(150, 350) is False

    def test_contains_bbox_center(self) -> None:
        """Test bbox center containment."""
        zone = Zone(name="test", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        bbox = BBox(x1=150, y1=150, x2=250, y2=250)  # Center at 200, 200
        assert zone.contains_bbox_center(bbox) is True

        bbox_outside = BBox(x1=50, y1=50, x2=100, y2=100)  # Center at 75, 75
        assert zone.contains_bbox_center(bbox_outside) is False

    def test_center(self) -> None:
        """Test zone center calculation."""
        zone = Zone(name="test", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        cx, cy = zone.center()
        assert cx == 200.0
        assert cy == 200.0

    def test_width_height(self) -> None:
        """Test zone width and height."""
        zone = Zone(name="test", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        assert zone.width() == 200
        assert zone.height() == 200

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        zone = Zone(name="test", type="rectangle", x1=100, y1=100, x2=300, y2=300)
        data = zone.to_dict()
        assert data["name"] == "test"
        assert data["type"] == "rectangle"
        assert data["x1"] == 100
        assert data["x2"] == 300
        assert data["y1"] == 100
        assert data["y2"] == 300

    def test_from_dict(self) -> None:
        """Test deserialization from dict."""
        data = {"name": "test", "type": "rectangle", "x1": 100, "y1": 100, "x2": 300, "y2": 300}
        zone = Zone.from_dict(data)
        assert zone.name == "test"
        assert zone.x1 == 100
        assert zone.x2 == 300
