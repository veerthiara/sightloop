"""FPS tracking helpers for deterministic runtime metrics."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class FpsTracker:
    """Track frame timing and expose average/current/rolling FPS."""

    def __init__(self, rolling_window_size: int = 30) -> None:
        if rolling_window_size < 2:
            raise ValueError("rolling_window_size must be at least 2.")

        self._rolling_window_size = rolling_window_size
        self.reset()

    def reset(self, started_at: datetime | None = None) -> None:
        """Reset internal counters for a new session."""
        self.frame_count = 0
        self.started_at = started_at
        self.last_frame_at: datetime | None = None
        self._recent_timestamps: deque[datetime] = deque(maxlen=self._rolling_window_size)
        self._previous_frame_at: datetime | None = None

    def record_frame(self, timestamp: datetime | None = None) -> datetime:
        """Record a processed frame and return the timestamp used."""
        ts = timestamp or _utcnow()

        if self.started_at is None:
            self.started_at = ts

        self._previous_frame_at = self.last_frame_at
        self.last_frame_at = ts
        self.frame_count += 1
        self._recent_timestamps.append(ts)
        return ts

    @property
    def duration_secs(self) -> float:
        """Elapsed time in seconds between the first and last processed frames."""
        if self.started_at is None or self.last_frame_at is None:
            return 0.0
        return max((self.last_frame_at - self.started_at).total_seconds(), 0.0)

    @property
    def average_fps(self) -> float:
        """Average FPS across the full recorded session."""
        if self.frame_count == 0:
            return 0.0
        if self.frame_count == 1:
            return 0.0

        duration = self.duration_secs
        if duration <= 0:
            return 0.0
        return (self.frame_count - 1) / duration

    @property
    def current_fps(self) -> float:
        """Instantaneous FPS from the last two recorded frames."""
        if self._previous_frame_at is None or self.last_frame_at is None:
            return 0.0

        delta = (self.last_frame_at - self._previous_frame_at).total_seconds()
        if delta <= 0:
            return 0.0
        return 1.0 / delta

    @property
    def rolling_fps(self) -> float:
        """Rolling FPS over the most recent timestamps in the configured window."""
        if len(self._recent_timestamps) < 2:
            return 0.0

        first = self._recent_timestamps[0]
        last = self._recent_timestamps[-1]
        duration = (last - first).total_seconds()
        if duration <= 0:
            return 0.0
        return (len(self._recent_timestamps) - 1) / duration

    def summary(self) -> dict[str, float | int | str | None]:
        """Return a serializable metrics snapshot."""
        return {
            "frame_count": self.frame_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_frame_at": self.last_frame_at.isoformat() if self.last_frame_at else None,
            "duration_secs": round(self.duration_secs, 6),
            "average_fps": round(self.average_fps, 6),
            "current_fps": round(self.current_fps, 6),
            "rolling_fps": round(self.rolling_fps, 6),
        }
