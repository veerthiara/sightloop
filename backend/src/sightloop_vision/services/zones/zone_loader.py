"""Load zones from configuration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sightloop_vision.models.zone import Zone

if TYPE_CHECKING:
    from sightloop_vision.core.config import AppConfig


logger = logging.getLogger(__name__)


def load_zones_from_config(config: "AppConfig") -> list[Zone]:
    """Load zones from app config.

    Supports both top-level zones and detection.zones:
    zones:                                    # top-level (preferred)
      - name: "bottle_home"
        type: "rectangle"
        x1: 100
        y1: 100
        x2: 300
        y2: 300
    detection:
      zones:                                 # also supported (legacy)
        - name: "bottle_home"
          type: "rectangle"
          x1: 100
          y1: 100
          x2: 300
          y2: 300

    If neither is found, logs a warning and returns empty list.
    """
    # Try top-level zones first (preferred)
    zones_data = getattr(config, "zones", None)

    # Fall back to detection.zones (legacy)
    if not zones_data:
        zones_data = getattr(config.detection, "zones", None)

    if not zones_data:
        logger.warning(
            "No zones configured. Define zones at top-level 'zones:' or under 'detection.zones:'. "
            "Zone evaluation will be skipped."
        )
        return []

    zones = []
    for zone_data in zones_data:
        try:
            zone = Zone.from_dict(zone_data)
            zones.append(zone)
        except Exception as e:
            logger.warning("Failed to load zone %s: %s", zone_data.get("name", "unknown"), e)

    if zones:
        logger.info("Loaded %d zone(s): %s", len(zones), [z.name for z in zones])
    else:
        logger.warning("No valid zones loaded from config")

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
