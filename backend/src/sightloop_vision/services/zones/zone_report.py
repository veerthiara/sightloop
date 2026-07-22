"""Zone calibration reporting for tracking runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sightloop_vision.models.zone import Zone
from sightloop_vision.services.validation import mask_camera_source


def _utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class ZoneCalibrationReport:
    """Serializable zone calibration report."""

    session_name: str
    camera_source_masked: str
    zones: list[dict]
    frames_processed: int
    detection_frames_processed: int
    zone_hits_by_name: dict[str, int]
    zone_hits_by_class: dict[str, dict[str, int]]
    track_count_by_class: dict[str, int]
    bottle_home_hits: int
    desk_hits: int
    created_at: str
    notes: str | None = None

    def to_summary_dict(self) -> dict:
        return {
            "session_name": self.session_name,
            "camera_source_masked": self.camera_source_masked,
            "zones": self.zones,
            "frames_processed": self.frames_processed,
            "detection_frames_processed": self.detection_frames_processed,
            "zone_hits_by_name": self.zone_hits_by_name,
            "zone_hits_by_class": self.zone_hits_by_class,
            "track_count_by_class": self.track_count_by_class,
            "bottle_home_hits": self.bottle_home_hits,
            "desk_hits": self.desk_hits,
            "created_at": self.created_at,
            "notes": self.notes,
        }


def build_zone_calibration_report(
    *,
    session_name: str,
    camera_source: int | str,
    zones: list[Zone],
    frames_processed: int,
    detection_frames_processed: int,
    zone_hits_by_name: dict[str, int],
    zone_hits_by_class: dict[str, dict[str, int]],
    track_count_by_class: dict[str, int],
    bottle_home_hits: int,
    desk_hits: int,
    notes: str | None = None,
) -> ZoneCalibrationReport:
    """Build a zone calibration report from tracking session data."""
    zones_data = []
    for zone in zones:
        if hasattr(zone, "to_dict"):
            zones_data.append(zone.to_dict())
        else:
            zones_data.append(zone)

    return ZoneCalibrationReport(
        session_name=session_name,
        camera_source_masked=mask_camera_source(camera_source),
        zones=zones_data,
        frames_processed=frames_processed,
        detection_frames_processed=detection_frames_processed,
        zone_hits_by_name=zone_hits_by_name,
        zone_hits_by_class=zone_hits_by_class,
        track_count_by_class=track_count_by_class,
        bottle_home_hits=bottle_home_hits,
        desk_hits=desk_hits,
        created_at=_utcnow_iso(),
        notes=notes,
    )
