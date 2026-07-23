"""Zone state tracking service for tracking track-zone relationships over time."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sightloop_vision.models.track import Track
    from sightloop_vision.models.zone import Zone
    from sightloop_vision.models.zone_state import TrackZoneState, ZoneStateSummary


class ZoneStateTracker:
    """Tracks zone state for all tracks across frames."""

    def __init__(self, zones: list["Zone"]) -> None:
        self._zones = zones
        self._zone_names = {z.name for z in zones}
        self._track_states: dict[int, "TrackZoneState"] = {}
        self._total_tracks_by_class: dict[str, int] = defaultdict(int)
        self._zone_entries: dict[str, int] = defaultdict(int)
        self._zone_exits: dict[str, int] = defaultdict(int)
        self._frames_inside_by_zone: dict[str, int] = defaultdict(int)

    def update(self, tracks: list["Track"], frame_id: int) -> None:
        """Update zone state for all tracks in current frame."""
        from sightloop_vision.models.zone_state import TrackZoneState

        for track in tracks:
            # Get or create track state
            if track.track_id not in self._track_states:
                self._track_states[track.track_id] = TrackZoneState(
                    track_id=track.track_id,
                    track_class=track.class_name,
                )
                # Count new tracks by class
                self._total_tracks_by_class[track.class_name] += 1

            # Get current zones for this track
            current_zones = set()
            for zone in self._zones:
                if zone.contains_bbox_center(track.bbox):
                    current_zones.add(zone.name)

            # Update track zone state
            track_state = self._track_states[track.track_id]
            events = track_state.update(current_zones, frame_id)

            # Record events
            for zone_name, event_type in events:
                if event_type == "enter":
                    self._zone_entries[zone_name] += 1
                elif event_type == "exit":
                    self._zone_exits[zone_name] += 1

        # Update frames inside counters for all active tracks
        for track_state in self._track_states.values():
            for zone_name in track_state.current_zones:
                self._frames_inside_by_zone[zone_name] += 1

    def get_track_state(self, track_id: int) -> "TrackZoneState | None":
        """Get zone state for a specific track."""
        return self._track_states.get(track_id)

    def get_all_track_states(self) -> dict[int, "TrackZoneState"]:
        """Get all track zone states."""
        return dict(self._track_states)

    def get_zone_entry_count(self, zone_name: str) -> int:
        return self._zone_entries.get(zone_name, 0)

    def get_zone_exit_count(self, zone_name: str) -> int:
        return self._zone_exits.get(zone_name, 0)

    def get_frames_inside(self, zone_name: str) -> int:
        return self._frames_inside_by_zone.get(zone_name, 0)

    def get_total_tracks_by_class(self) -> dict[str, int]:
        return dict(self._total_tracks_by_class)

    def get_zone_entry_summary(self) -> dict[str, int]:
        return dict(self._zone_entries)

    def get_zone_exit_summary(self) -> dict[str, int]:
        return dict(self._zone_exits)

    def get_frames_inside_summary(self) -> dict[str, int]:
        return dict(self._frames_inside_by_zone)

    def build_summary(self) -> "ZoneStateSummary":
        """Build a summary for reporting."""
        from sightloop_vision.models.zone_state import ZoneStateSummary

        return ZoneStateSummary(
            track_count_by_class=dict(self._total_tracks_by_class),
            zone_entries_by_name=dict(self._zone_entries),
            zone_exits_by_name=dict(self._zone_exits),
            frames_inside_by_zone=dict(self._frames_inside_by_zone),
            bottle_tracks_created=self._total_tracks_by_class.get("bottle", 0),
            person_tracks_created=self._total_tracks_by_class.get("person", 0),
        )

    def reset(self) -> None:
        """Reset all tracking state."""
        self._track_states.clear()
        self._total_tracks_by_class.clear()
        self._zone_entries.clear()
        self._zone_exits.clear()
        self._frames_inside_by_zone.clear()
