"""Session-level metrics summary for camera runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sightloop_vision.models import Frame
from sightloop_vision.services.metrics.fps import FpsTracker


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


@dataclass
class CameraSessionStats:
    """Track summary-level session metadata and expose a serializable snapshot."""

    session_name: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    frame_count: int = 0
    source_id: str | None = None
    frame_width: int | None = None
    frame_height: int | None = None

    def start(self, started_at: datetime | None = None) -> datetime:
        """Start or reset the tracked session state."""
        self.started_at = started_at or _utcnow()
        self.ended_at = None
        self.frame_count = 0
        self.source_id = None
        self.frame_width = None
        self.frame_height = None
        return self.started_at

    def record_frame(self, frame: Frame) -> None:
        """Record metadata from a processed frame."""
        self.frame_count += 1
        self.source_id = frame.source_id
        self.frame_width = frame.width
        self.frame_height = frame.height

    def finish(self, ended_at: datetime | None = None) -> datetime:
        """Mark the session complete."""
        self.ended_at = ended_at or _utcnow()
        return self.ended_at

    @property
    def duration_secs(self) -> float:
        """Elapsed session duration in seconds."""
        if self.started_at is None or self.ended_at is None:
            return 0.0
        return max((self.ended_at - self.started_at).total_seconds(), 0.0)

    def to_summary_dict(self, fps_tracker: FpsTracker | None = None) -> dict[str, object]:
        """Return a serializable summary for logs or CLI output."""
        average_fps = fps_tracker.average_fps if fps_tracker is not None else 0.0
        rolling_fps = fps_tracker.rolling_fps if fps_tracker is not None else 0.0
        current_fps = fps_tracker.current_fps if fps_tracker is not None else 0.0

        return {
            "session_name": self.session_name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "frame_count": self.frame_count,
            "duration_secs": round(self.duration_secs, 6),
            "average_fps": round(average_fps, 6),
            "rolling_fps": round(rolling_fps, 6),
            "current_fps": round(current_fps, 6),
            "source_id": self.source_id,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
        }
