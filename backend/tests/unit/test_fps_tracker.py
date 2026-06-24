"""Unit tests for FPS tracking."""

from datetime import datetime, timedelta, timezone

import pytest

from sightloop_vision.services.metrics import FpsTracker


class TestFpsTracker:
    def test_requires_window_of_at_least_two(self) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            FpsTracker(rolling_window_size=1)

    def test_records_started_and_last_frame_timestamps(self) -> None:
        tracker = FpsTracker()
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)

        tracker.record_frame(ts)

        assert tracker.frame_count == 1
        assert tracker.started_at == ts
        assert tracker.last_frame_at == ts

    def test_calculates_average_current_and_rolling_fps_deterministically(self) -> None:
        tracker = FpsTracker(rolling_window_size=3)
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)

        tracker.record_frame(base)
        tracker.record_frame(base + timedelta(seconds=0.5))
        tracker.record_frame(base + timedelta(seconds=1.0))

        assert tracker.average_fps == 2.0
        assert tracker.current_fps == 2.0
        assert tracker.rolling_fps == 2.0

    def test_rolling_fps_uses_recent_window(self) -> None:
        tracker = FpsTracker(rolling_window_size=3)
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)

        tracker.record_frame(base)
        tracker.record_frame(base + timedelta(seconds=1.0))
        tracker.record_frame(base + timedelta(seconds=2.0))
        tracker.record_frame(base + timedelta(seconds=2.5))

        assert tracker.average_fps == pytest.approx(1.2)
        assert tracker.current_fps == pytest.approx(2.0)
        assert tracker.rolling_fps == pytest.approx(1.3333333333)

    def test_summary_is_serializable(self) -> None:
        tracker = FpsTracker()
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        tracker.record_frame(ts)

        summary = tracker.summary()

        assert summary["frame_count"] == 1
        assert summary["started_at"] == ts.isoformat()
        assert summary["last_frame_at"] == ts.isoformat()
