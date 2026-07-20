"""Unit tests for zone loader."""

from pathlib import Path

from sightloop_vision.models.zone import Zone
from sightloop_vision.services.zones.zone_loader import (
    load_zones_from_config,
    load_zones_from_file,
    save_zones_to_file,
)


class TestZoneLoader:
    """Test zone loading from config and file."""

    def test_load_zones_from_config(self) -> None:
        """Load zones from app config."""
        # Create a mock config object
        class MockDetectionConfig:
            zones = [
                {
                    "name": "bottle_home",
                    "type": "rectangle",
                    "x1": 100,
                    "y1": 100,
                    "x2": 300,
                    "y2": 300,
                },
                {
                    "name": "desk",
                    "type": "rectangle",
                    "x1": 50,
                    "y1": 50,
                    "x2": 400,
                    "y2": 400,
                },
            ]

        class MockConfig:
            detection = MockDetectionConfig()

        zones = load_zones_from_config(MockConfig())
        assert len(zones) == 2
        assert zones[0].name == "bottle_home"
        assert zones[1].name == "desk"

    def test_load_zones_from_config_empty(self) -> None:
        """Load zones from config with no zones."""
        class MockDetectionConfig:
            zones = None

        class MockConfig:
            detection = MockDetectionConfig()

        zones = load_zones_from_config(MockConfig())
        assert zones == []

    def test_save_and_load_zones_file(self, tmp_path: Path) -> None:
        """Save zones to file and load them back."""
        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
            Zone(name="desk", type="rectangle", x1=50, y1=50, x2=400, y2=400),
        ]

        file_path = tmp_path / "zones.json"
        save_zones_to_file(zones, file_path)

        assert file_path.exists()

        loaded = load_zones_from_file(file_path)
        assert len(loaded) == 2
        assert loaded[0].name == "bottle_home"
        assert loaded[1].name == "desk"

    def test_load_zones_from_file_nonexistent(self, tmp_path: Path) -> None:
        """Load zones from non-existent file returns empty list."""
        file_path = tmp_path / "nonexistent.json"
        loaded = load_zones_from_file(file_path)
        assert loaded == []
