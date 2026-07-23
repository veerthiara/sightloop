"""Diagnostics for detection and tracking sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sightloop_vision.models.detection import Detection
from sightloop_vision.models.track import Track

if TYPE_CHECKING:
    from sightloop_vision.models.zone import Zone


@dataclass
class DetectionDiagnostics:
    """Aggregated detection statistics for a session."""

    frames_processed: int = 0
    detection_frames_processed: int = 0
    total_raw_detections: int = 0
    total_filtered_detections: int = 0
    detections_by_class: dict[str, int] = field(default_factory=dict)
    avg_confidence_by_class: dict[str, float] = field(default_factory=dict)
    min_confidence_by_class: dict[str, float] = field(default_factory=dict)
    max_confidence_by_class: dict[str, float] = field(default_factory=dict)

    def record_detection_frame(self, detections: list[Detection]) -> None:
        self.detection_frames_processed += 1

    def record_raw_detections(self, detections: list[Detection]) -> None:
        self.frames_processed += 1
        for det in detections:
            self.total_raw_detections += 1
            self.detections_by_class[det.class_name] = (
                self.detections_by_class.get(det.class_name, 0) + 1
            )

    def record_filtered_detections(self, detections: list[Detection]) -> None:
        self.total_filtered_detections += len(detections)
        for det in detections:
            if det.class_name not in self.avg_confidence_by_class:
                self.avg_confidence_by_class[det.class_name] = det.confidence
                self.min_confidence_by_class[det.class_name] = det.confidence
                self.max_confidence_by_class[det.class_name] = det.confidence
            else:
                n = self.detections_by_class.get(det.class_name, 0) + 1
                old_avg = self.avg_confidence_by_class.get(det.class_name, 0)
                self.avg_confidence_by_class[det.class_name] = (
                    old_avg * (n - 1) + det.confidence
                ) / n
                self.min_confidence_by_class[det.class_name] = min(
                    self.min_confidence_by_class.get(det.class_name, 1.0), det.confidence
                )
                self.max_confidence_by_class[det.class_name] = max(
                    self.max_confidence_by_class.get(det.class_name, 0.0), det.confidence
                )

    def to_dict(self) -> dict:
        return {
            "frames_processed": self.frames_processed,
            "detection_frames_processed": self.detection_frames_processed,
            "total_raw_detections": self.total_raw_detections,
            "total_filtered_detections": self.total_filtered_detections,
            "detections_by_class": self.detections_by_class,
            "avg_confidence_by_class": {
                k: round(v, 3) for k, v in self.avg_confidence_by_class.items()
            },
            "min_confidence_by_class": {
                k: round(v, 3) for k, v in self.min_confidence_by_class.items()
            },
            "max_confidence_by_class": {
                k: round(v, 3) for k, v in self.max_confidence_by_class.items()
            },
        }


@dataclass
class ZoneState:
    """State of a track within a specific zone."""

    track_id: int
    track_class: str
    zone_name: str
    first_seen_frame: int
    first_seen_time: datetime
    last_seen_frame: int
    last_seen_time: datetime
    hit_count: int = 1
    is_exited: bool = False
    exited_frame: int | None = None
    exited_time: datetime | None = None

    def record_hit(self, frame_id: int, timestamp: datetime) -> None:
        self.hit_count += 1
        self.last_seen_frame = frame_id
        self.last_seen_time = timestamp

    def mark_exited(self, frame_id: int, timestamp: datetime) -> None:
        self.is_exited = True
        self.exited_frame = frame_id
        self.exited_time = timestamp

    def duration_frames(self) -> int:
        return self.last_seen_frame - self.first_seen_frame + 1

    def duration_seconds(self) -> float:
        return (self.last_seen_time - self.first_seen_time).total_seconds()

    def is_active(self) -> bool:
        return not self.is_exited

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "track_class": self.track_class,
            "zone_name": self.zone_name,
            "first_seen_frame": self.first_seen_frame,
            "first_seen_time": self.first_seen_time.isoformat(),
            "last_seen_frame": self.last_seen_frame,
            "last_seen_time": self.last_seen_time.isoformat(),
            "hit_count": self.hit_count,
            "is_exited": self.is_exited,
            "exited_frame": self.exited_frame,
            "exited_time": self.exited_time.isoformat() if self.exited_time else None,
            "duration_frames": self.duration_frames(),
            "duration_seconds": round(self.duration_seconds(), 2),
        }


@dataclass
class TrackingDiagnostics:
    """Comprehensive diagnostics for a tracking session."""

    detection_diagnostics: DetectionDiagnostics = field(default_factory=DetectionDiagnostics)
    zone_states: dict[tuple[int, str], ZoneState] = field(default_factory=dict)
    track_zone_history: dict[int, list[ZoneState]] = field(default_factory=dict)
    frames_processed: int = 0
    detection_frames_processed: int = 0
    total_tracks_created: int = 0
    active_tracks: int = 0
    tracks_by_class: dict[str, int] = field(default_factory=dict)
    zone_hits_by_class: dict[str, dict[str, int]] = field(default_factory=dict)
    zone_total_hits: dict[str, int] = field(default_factory=dict)
    zone_enter_events: list[dict] = field(default_factory=list)
    zone_exit_events: list[dict] = field(default_factory=list)

    _current_frame_id: int = 0
    _current_timestamp: datetime | None = None

    def record_detection_frame(
        self, frame_id: int, timestamp: datetime, detections: list[Detection]
    ) -> None:
        self._current_frame_id = frame_id
        self._current_timestamp = timestamp
        self.frames_processed += 1
        self.detection_diagnostics.record_detection_frame(detections)
        self.detection_diagnostics.record_raw_detections(detections)

    def record_filtered_detections(self, detections: list[Detection]) -> None:
        self.detection_diagnostics.record_filtered_detections(detections)

    def record_tracks(self, tracks: list[Track]) -> None:
        self.active_tracks = len(tracks)
        for track in tracks:
            self.tracks_by_class[track.class_name] = self.tracks_by_class.get(
                track.class_name, 0
            ) + 1

    def record_zone_evaluation(
        self, tracks: list[Track], zones: list[Zone]
    ) -> None:
        """Record which tracks are in which zones."""

        current_zone_assignments: set[tuple[int, str]] = set()
        for track in tracks:
            for zone in zones:
                if zone.contains_bbox_center(track.bbox):
                    key = (track.track_id, zone.name)
                    current_zone_assignments.add(key)

                    if key not in self.zone_states:
                        self.zone_states[key] = ZoneState(
                            track_id=track.track_id,
                            track_class=track.class_name,
                            zone_name=zone.name,
                            first_seen_frame=self._current_frame_id,
                            first_seen_time=self._current_timestamp,
                            last_seen_frame=self._current_frame_id,
                            last_seen_time=self._current_timestamp,
                        )
                    else:
                        self.zone_states[key].record_hit(
                            self._current_frame_id, self._current_timestamp
                        )

                    self.zone_hits_by_class.setdefault(zone.name, {})
                    self.zone_hits_by_class[zone.name][track.class_name] = (
                        self.zone_hits_by_class[zone.name].get(track.class_name, 0) + 1
                    )
                    self.zone_total_hits[zone.name] = (
                        self.zone_total_hits.get(zone.name, 0) + 1
                    )

                    if track.track_id not in self.track_zone_history:
                        self.track_zone_history[track.track_id] = []
                    else:
                        self.track_zone_history[track.track_id].append(
                            self.zone_states[key]
                        )

        existing_keys = set(self.zone_states.keys())
        for key in existing_keys - current_zone_assignments:
            zone_state = self.zone_states[key]
            if zone_state.is_active():
                zone_state.mark_exited(self._current_frame_id, self._current_timestamp)
                self.zone_exit_events.append({
                    "track_id": zone_state.track_id,
                    "track_class": zone_state.track_class,
                    "zone_name": zone_state.zone_name,
                    "frame_id": self._current_frame_id,
                    "timestamp": self._current_timestamp.isoformat(),
                    "duration_frames": zone_state.duration_frames(),
                    "duration_seconds": round(zone_state.duration_seconds(), 2),
                })

        self.total_tracks_created = len(set(t.track_id for t in self.zone_states.values()))

    def get_zone_state_summary(self) -> dict:
        summary = {}
        for key, state in self.zone_states.items():
            key_str = f"{key[0]}_{key[1]}"
            summary[key_str] = state.to_dict()
        return summary

    def get_zone_hit_summary(self) -> dict:
        return {
            "by_class": self.zone_hits_by_class,
            "total": self.zone_total_hits,
        }

    def get_zone_events_summary(self) -> dict:
        return {
            "enter_events": self.zone_enter_events,
            "exit_events": self.zone_exit_events,
        }

    def to_dict(self) -> dict:
        return {
            "detection_diagnostics": self.detection_diagnostics.to_dict(),
            "frames_processed": self.frames_processed,
            "detection_frames_processed": self.detection_frames_processed,
            "total_tracks_created": self.total_tracks_created,
            "active_tracks": self.active_tracks,
            "tracks_by_class": self.tracks_by_class,
            "zone_hits_by_class": self.zone_hits_by_class,
            "zone_total_hits": self.zone_total_hits,
            "zone_enter_events": self.zone_enter_events,
            "zone_exit_events": self.zone_exit_events,
            "zone_state_summary": self.get_zone_state_summary(),
            "zone_hit_summary": self.get_zone_hit_summary(),
            "zone_events_summary": self.get_zone_events_summary(),
        }


def build_tracking_diagnostics_report(
    diagnostics: TrackingDiagnostics,
    session_name: str,
    camera_source: str,
    zones: list,
    notes: str | None = None,
) -> dict:
    from sightloop_vision.services.validation import mask_camera_source

    return {
        "session_name": session_name,
        "camera_source_masked": mask_camera_source(camera_source),
        "zones": [z.to_dict() for z in zones],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
        "diagnostics": diagnostics.to_dict(),
    }
