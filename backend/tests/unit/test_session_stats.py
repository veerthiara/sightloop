"""Unit tests for camera session stats."""

from datetime import datetime, timedelta, timezone

from sightloop_vision.models import Frame
from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker


class TestCameraSessionStats:
    def _make_frame(
        self,
        frame_id: int,
        timestamp: datetime,
        source_id: str = "cam0",
    ) -> Frame:
        import numpy as np

        image = np.zeros((240, 320, 3), dtype=np.uint8)
        return Frame(
            frame_id=frame_id,
            image=image,
            timestamp=timestamp,
            source_id=source_id,
        )

    def test_tracks_session_state_and_serializable_summary(self) -> None:
        started_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        ended_at = started_at + timedelta(seconds=2)
        frame = self._make_frame(0, started_at, source_id="fake")
        fps_tracker = FpsTracker()
        fps_tracker.record_frame(started_at)
        fps_tracker.record_frame(started_at + timedelta(seconds=1))

        stats = CameraSessionStats(session_name="session-a")
        stats.start(started_at)
        stats.record_frame(frame)
        stats.finish(ended_at)

        summary = stats.to_summary_dict(fps_tracker)

        assert summary["session_name"] == "session-a"
        assert summary["started_at"] == started_at.isoformat()
        assert summary["ended_at"] == ended_at.isoformat()
        assert summary["frame_count"] == 1
        assert summary["duration_secs"] == 2.0
        assert summary["average_fps"] == 1.0
        assert summary["source_id"] == "fake"
        assert summary["frame_width"] == 320
        assert summary["frame_height"] == 240

    def test_start_resets_existing_state(self) -> None:
        started_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        stats = CameraSessionStats(session_name="session-b")
        stats.start(started_at)
        stats.frame_count = 99
        stats.source_id = "old"

        stats.start(started_at + timedelta(seconds=5))

        assert stats.frame_count == 0
        assert stats.source_id is None
        assert stats.ended_at is None
