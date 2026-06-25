"""Main camera pipeline loop.

Keeps the frame-reading loop separate from camera adapter setup so later
revisions can layer metrics, debug writers, and inference on top.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from sightloop_vision.adapters.camera import CameraSource
from sightloop_vision.services.debug import FrameWriter
from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class CameraPipeline:
    """Continuously read frames from a camera source until stopped."""

    def __init__(
        self,
        source: CameraSource,
        display_enabled: bool = False,
        fps_tracker: FpsTracker | None = None,
        session_stats: CameraSessionStats | None = None,
        frame_writer: FrameWriter | None = None,
        metrics_log_interval_secs: float | None = None,
        metrics_log_interval_frames: int | None = None,
        metrics_logger: Callable[[str], None] | None = None,
    ) -> None:
        self._source = source
        self._display_enabled = display_enabled
        self._fps_tracker = fps_tracker
        self._session_stats = session_stats
        self._frame_writer = frame_writer
        self._metrics_log_interval_secs = metrics_log_interval_secs
        self._metrics_log_interval_frames = metrics_log_interval_frames
        self._metrics_logger = metrics_logger or print
        self.processed_frames = 0
        self.final_summary: dict[str, object] | None = None

    def run(self, max_frames: int | None = None) -> int:
        """Run the pipeline until the stream ends or execution is interrupted."""
        cv2 = self._load_display_backend() if self._display_enabled else None
        self.processed_frames = 0
        self.final_summary = None
        last_metrics_log_at: datetime | None = None

        started_at = _utcnow()
        if self._fps_tracker is not None:
            self._fps_tracker.reset(started_at=started_at)
        if self._session_stats is not None:
            self._session_stats.start(started_at=started_at)

        self._source.open()
        try:
            while True:
                if max_frames is not None and self.processed_frames >= max_frames:
                    break

                frame = self._source.read()
                if frame is None:
                    break

                self.processed_frames += 1
                frame_ts = frame.timestamp

                if self._fps_tracker is not None:
                    frame_ts = self._fps_tracker.record_frame(frame.timestamp)
                if self._session_stats is not None:
                    self._session_stats.record_frame(frame)
                if self._frame_writer is not None:
                    self._frame_writer.write_frame(frame)
                if self._should_log_metrics(frame_ts, last_metrics_log_at):
                    last_metrics_log_at = frame_ts
                    self._log_metrics(prefix="metrics")

                if cv2 is not None:
                    cv2.imshow("SightLoop Vision", frame.image)
                    key = cv2.waitKey(1) & 0xFF
                    if key in (27, ord("q")):
                        break
        except KeyboardInterrupt:
            pass
        finally:
            self._source.close()
            if cv2 is not None:
                cv2.destroyAllWindows()
            self.final_summary = self._build_final_summary()
            if self.final_summary is not None:
                self._metrics_logger(f"session-summary {self.final_summary}")

        return self.processed_frames

    def _should_log_metrics(
        self,
        frame_ts: datetime,
        last_metrics_log_at: datetime | None,
    ) -> bool:
        if self._fps_tracker is None:
            return False

        if (
            self._metrics_log_interval_frames is not None
            and self._metrics_log_interval_frames > 0
            and self.processed_frames % self._metrics_log_interval_frames == 0
        ):
            return True

        if self._metrics_log_interval_secs is None or self._metrics_log_interval_secs <= 0:
            return False

        if last_metrics_log_at is None:
            return True

        elapsed = (frame_ts - last_metrics_log_at).total_seconds()
        return elapsed >= self._metrics_log_interval_secs

    def _log_metrics(self, prefix: str) -> None:
        if self._fps_tracker is None:
            return

        snapshot = self._fps_tracker.summary()
        self._metrics_logger(f"{prefix} {snapshot}")

    def _build_final_summary(self) -> dict[str, object] | None:
        ended_at = self._fps_tracker.last_frame_at if self._fps_tracker is not None else _utcnow()

        if self._session_stats is not None:
            self._session_stats.finish(ended_at=ended_at)
            summary = self._session_stats.to_summary_dict(self._fps_tracker)
            if self._frame_writer is not None:
                summary["saved_frames"] = self._frame_writer.saved_frame_count
            return summary

        if self._fps_tracker is not None:
            summary = self._fps_tracker.summary()
            if self._frame_writer is not None:
                summary["saved_frames"] = self._frame_writer.saved_frame_count
            return summary

        return None

    def _load_display_backend(self) -> Any:
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise ImportError(
                "OpenCV is required when display_enabled=True."
            ) from exc
        return cv2
