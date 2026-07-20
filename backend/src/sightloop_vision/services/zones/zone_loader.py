"""Load zones from configuration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from sightloop_vision.models.zone import Zone

if TYPE_CHECKING:
    from sightloop_vision.core.config import AppConfig


def load_zones_from_config(config: "AppConfig") -> list[Zone]:
    """Load zones from app config.

    Zones are defined in the detection section of the config:
    detection:
      zones:
        - name: "bottle_home"
          type: "rectangle"
          x1: 100
          y1: 100
          x2: 300
          y2: 300
        - name: "desk_area"
          type: "rectangle"
          x1: 200
          y1: 200
          x2: 600
          y2: 600
    """
    zones_data = getattr(config.detection, "zones", None)
    if not zones_data:
        return []

    zones = []
    for zone_data in zones_data:
        zone = Zone.from_dict(zone_data)
        zones.append(zone)

    return zones


def save_zones_to_file(zones: list[Zone], path: Path) -> None:
    """Save zones to a JSON file."""
    import json

    data = [zone.to_dict() for zone in zones]
    path.write_text(json.dumps(data, indent=2))


def load_zones_from_file(path: Path) -> list[Zone]:
    """Load zones from a JSON file."""
    import json

    if not path.exists():
        return []

    data = json.loads(path.read_text())
    return [Zone.from_dict(zone_data) for zone_data in data]
