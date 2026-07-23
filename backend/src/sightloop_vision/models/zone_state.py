"""Zone state tracking for individual tracks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class TrackZoneState:
    """Tracks zone state for a single track."""

    track_id: int
    track_class: str

    # Current state
    current_zones: set[str] = field(default_factory=set)
    previous_zones: set[str] = field(default_factory=set)

    # History
    entered_zones: set[str] = field(default_factory=set)
    exited_zones: set[str] = field(default_factory=set)

    # Frame counts
    frames_inside_by_zone: dict[str, int] = field(default_factory=dict)
    first_seen_in_zone_frame_id: dict[str, int] = field(default_factory=dict)
    last_seen_in_zone_frame_id: dict[str, int] = field(default_factory=dict)

    def update(self, current_zone_names: set[str], frame_id: int) -> list[tuple[str, str]]:
        """Update zone state.

        Returns list of (zone_name, event) where event is 'enter' or 'exit'.
        """
        self.previous_zones = self.current_zones.copy()
        self.current_zones = current_zone_names.copy()

        events = []

        # Check for zone entries
        for zone_name in self.current_zones - self.previous_zones:
            self.entered_zones.add(zone_name)
            if zone_name not in self.first_seen_in_zone_frame_id:
                self.first_seen_in_zone_frame_id[zone_name] = frame_id
            events.append((zone_name, "enter"))

        # Check for zone exits
        for zone_name in self.previous_zones - self.current_zones:
            self.exited_zones.add(zone_name)
            self.last_seen_in_zone_frame_id[zone_name] = frame_id
            events.append((zone_name, "exit"))

        # Update frames inside counters
        for zone_name in self.current_zones:
            self.frames_inside_by_zone[zone_name] = self.frames_inside_by_zone.get(zone_name, 0) + 1

        return events

    def is_in_zone(self, zone_name: str) -> bool:
        return zone_name in self.current_zones

    def get_zone_duration_frames(self, zone_name: str) -> int:
        """Get total frames spent in a zone."""
        return self.frames_inside_by_zone.get(zone_name, 0)

    def get_zone_entry_frame(self, zone_name: str) -> int | None:
        return self.first_seen_in_zone_frame_id.get(zone_name)

    def get_zone_exit_frame(self, zone_name: str) -> int | None:
        return self.last_seen_in_zone_frame_id.get(zone_name)

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "track_class": self.track_class,
            "current_zones": sorted(self.current_zones),
            "entered_zones": sorted(self.entered_zones),
            "exited_zones": sorted(self.exited_zones),
            "frames_inside_by_zone": self.frames_inside_by_zone,
            "first_seen_in_zone_frame_id": self.first_seen_in_zone_frame_id,
            "last_seen_in_zone_frame_id": self.last_seen_in_zone_frame_id,
        }


@dataclass
class ZoneStateSummary:
    """Aggregate zone state summary for reporting."""

    track_count_by_class: dict[str, int]
    zone_entries_by_name: dict[str, int]
    zone_exits_by_name: dict[str, int]
    frames_inside_by_zone: dict[str, int]
    bottle_tracks_created: int
    person_tracks_created: int
    no_bottle_detected_warning: bool = False
    diagnostics_warnings: list[str] = field(default_factory=list)
    diagnostics_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "track_count_by_class": self.track_count_by_class,
            "zone_entries_by_name": self.zone_entries_by_name,
            "zone_exits_by_name": self.zone_exits_by_name,
            "frames_inside_by_zone": self.frames_inside_by_zone,
            "bottle_tracks_created": self.bottle_tracks_created,
            "person_tracks_created": self.person_tracks_created,
            "no_bottle_detected_warning": self.no_bottle_detected_warning,
            "diagnostics_warnings": self.diagnostics_warnings,
            "diagnostics_errors": self.diagnostics_errors,
        }
