"""Integration-style tests for the main camera pipeline using FakeCameraSource."""

from pathlib import Path

from sightloop_vision.adapters.camera.base import CameraOpenError
from sightloop_vision.adapters.camera.fake import FakeCameraSource
from sightloop_vision.services.debug import FrameWriter
from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
from sightloop_vision.services.pipeline import CameraPipeline


class TrackingFakeCameraSource(FakeCameraSource):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        super().close()


class InterruptingFakeCameraSource(TrackingFakeCameraSource):
    def __init__(self, interrupt_after_reads: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._interrupt_after_reads = interrupt_after_reads
        self._read_calls = 0

    def read(self):
        if self._read_calls >= self._interrupt_after_reads:
            raise KeyboardInterrupt

        frame = super().read()
        self._read_calls += 1
        return frame


class FailingFakeCameraSource(TrackingFakeCameraSource):
    def __init__(self, fail_after_reads: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._fail_after_reads = fail_after_reads
        self._read_calls = 0

    def read(self):
        if self._read_calls >= self._fail_after_reads:
            raise CameraOpenError("synthetic read failure")

        frame = super().read()
        self._read_calls += 1
        return frame


class TestCameraPipeline:
    def test_pipeline_processes_exactly_n_frames(self) -> None:
        source = TrackingFakeCameraSource(total_frames=10)
        pipeline = CameraPipeline(source=source)

        processed = pipeline.run(max_frames=4)

        assert processed == 4
        assert pipeline.processed_frames == 4
        assert source.frames_emitted == 4

    def test_pipeline_closes_source_after_completion(self) -> None:
        source = TrackingFakeCameraSource(total_frames=2)
        pipeline = CameraPipeline(source=source)

        pipeline.run()

        assert source.close_calls == 1
        assert source._is_open is False

    def test_pipeline_handles_end_of_stream_cleanly(self) -> None:
        source = TrackingFakeCameraSource(total_frames=3)
        pipeline = CameraPipeline(source=source)

        processed = pipeline.run(max_frames=10)

        assert processed == 3
        assert pipeline.processed_frames == 3
        assert source.close_calls == 1

    def test_pipeline_stops_cleanly_on_keyboard_interrupt(self) -> None:
        source = InterruptingFakeCameraSource(
            interrupt_after_reads=2,
            total_frames=-1,
        )
        pipeline = CameraPipeline(source=source)

        processed = pipeline.run()

        assert processed == 2
        assert pipeline.processed_frames == 2
        assert source.close_calls == 1

    def test_pipeline_populates_final_session_summary(self) -> None:
        source = TrackingFakeCameraSource(total_frames=3)
        fps_tracker = FpsTracker()
        session_stats = CameraSessionStats(session_name="test-session")
        pipeline = CameraPipeline(
            source=source,
            fps_tracker=fps_tracker,
            session_stats=session_stats,
        )

        processed = pipeline.run()

        assert processed == 3
        assert pipeline.final_summary is not None
        assert pipeline.final_summary["session_name"] == "test-session"
        assert pipeline.final_summary["frame_count"] == 3
        assert pipeline.final_summary["source_id"] == "fake"
        assert pipeline.final_summary["frame_width"] == 640
        assert pipeline.final_summary["frame_height"] == 480

    def test_pipeline_logs_periodic_metrics_by_frame_count(self) -> None:
        source = TrackingFakeCameraSource(total_frames=4)
        fps_tracker = FpsTracker()
        messages: list[str] = []
        pipeline = CameraPipeline(
            source=source,
            fps_tracker=fps_tracker,
            metrics_log_interval_frames=2,
            metrics_logger=messages.append,
        )

        pipeline.run()

        assert any(message.startswith("metrics ") for message in messages)
        assert any(message.startswith("session-summary ") for message in messages)

    def test_pipeline_closes_source_on_read_failure(self) -> None:
        source = FailingFakeCameraSource(fail_after_reads=2, total_frames=-1)
        pipeline = CameraPipeline(source=source)

        try:
            pipeline.run()
        except CameraOpenError as exc:
            assert "synthetic read failure" in str(exc)

        assert source.close_calls == 1
        assert source._is_open is False

    def test_pipeline_saves_only_expected_debug_frames(self, tmp_path: Path) -> None:
        source = TrackingFakeCameraSource(total_frames=5)
        writer = FrameWriter(
            output_dir=tmp_path,
            session_name="debug-session",
            save_every_n_frames=2,
        )
        session_stats = CameraSessionStats(session_name="debug-session")
        pipeline = CameraPipeline(
            source=source,
            frame_writer=writer,
            session_stats=session_stats,
        )

        processed = pipeline.run()

        saved_files = sorted(writer.session_dir.glob("*.ppm"))
        assert processed == 5
        assert writer.saved_frame_count == 3
        assert len(saved_files) == 3
        assert saved_files[0].name.startswith("frame_000000_")
        assert saved_files[1].name.startswith("frame_000002_")
        assert saved_files[2].name.startswith("frame_000004_")
        assert pipeline.final_summary is not None
        assert pipeline.final_summary["saved_frames"] == 3
