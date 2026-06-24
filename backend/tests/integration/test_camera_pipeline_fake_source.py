"""Integration-style tests for the main camera pipeline using FakeCameraSource."""

from sightloop_vision.adapters.camera.fake import FakeCameraSource
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
