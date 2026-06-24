"""Unit tests for Frame model and FakeCameraSource."""

from datetime import datetime, timezone

import numpy as np
import pytest

from sightloop_vision.adapters.camera.base import CameraOpenError, CameraSource
from sightloop_vision.adapters.camera.fake import FakeCameraSource
from sightloop_vision.models.frame import Frame

# ---------------------------------------------------------------------------
# Frame model
# ---------------------------------------------------------------------------


class TestFrame:
    def _make_image(self, h: int = 480, w: int = 640) -> np.ndarray:
        return np.zeros((h, w, 3), dtype=np.uint8)

    def test_frame_stores_image(self) -> None:
        img = self._make_image()
        f = Frame(frame_id=0, image=img, timestamp=datetime.now(tz=timezone.utc))
        assert f.image is img

    def test_width_and_height_derived_from_image(self) -> None:
        now = datetime.now(tz=timezone.utc)
        f = Frame(frame_id=0, image=self._make_image(240, 320), timestamp=now)
        assert f.height == 240
        assert f.width == 320

    def test_shape_property(self) -> None:
        now = datetime.now(tz=timezone.utc)
        f = Frame(frame_id=0, image=self._make_image(480, 640), timestamp=now)
        assert f.shape == (480, 640)

    def test_frame_id_stored(self) -> None:
        f = Frame(frame_id=42, image=self._make_image(), timestamp=datetime.now(tz=timezone.utc))
        assert f.frame_id == 42

    def test_default_source_id(self) -> None:
        f = Frame(frame_id=0, image=self._make_image(), timestamp=datetime.now(tz=timezone.utc))
        assert f.source_id == "unknown"

    def test_custom_source_id(self) -> None:
        f = Frame(frame_id=0, image=self._make_image(), timestamp=datetime.now(tz=timezone.utc), source_id="rtsp://cam")
        assert f.source_id == "rtsp://cam"

    def test_frame_is_frozen(self) -> None:
        f = Frame(frame_id=0, image=self._make_image(), timestamp=datetime.now(tz=timezone.utc))
        with pytest.raises(Exception):
            f.frame_id = 99  # type: ignore[misc]

    def test_1d_image_raises(self) -> None:
        now = datetime.now(tz=timezone.utc)
        with pytest.raises(ValueError, match="at least 2 dimensions"):
            Frame(frame_id=0, image=np.zeros((640,), dtype=np.uint8), timestamp=now)

    def test_repr_contains_key_info(self) -> None:
        now = datetime.now(tz=timezone.utc)
        f = Frame(
            frame_id=7, image=self._make_image(480, 640),
            timestamp=now, source_id="cam0",
        )
        r = repr(f)
        assert "7" in r
        assert "480" in r
        assert "640" in r
        assert "cam0" in r


# ---------------------------------------------------------------------------
# FakeCameraSource
# ---------------------------------------------------------------------------


class TestFakeCameraSource:
    def test_emits_correct_number_of_frames(self) -> None:
        with FakeCameraSource(total_frames=5) as cam:
            frames = list(cam)
        assert len(frames) == 5

    def test_frame_ids_increment_from_zero(self) -> None:
        with FakeCameraSource(total_frames=4) as cam:
            ids = [cam.read().frame_id for _ in range(4)]  # type: ignore[union-attr]
        assert ids == [0, 1, 2, 3]

    def test_read_returns_none_at_end_of_stream(self) -> None:
        cam = FakeCameraSource(total_frames=1)
        cam.open()
        cam.read()  # consume the one frame
        assert cam.read() is None
        cam.close()

    def test_frames_have_correct_dimensions(self) -> None:
        with FakeCameraSource(width=320, height=240, total_frames=1) as cam:
            frame = cam.read()
        assert frame is not None
        assert frame.width == 320
        assert frame.height == 240

    def test_frames_use_specified_colour(self) -> None:
        colour = (10, 20, 30)
        with FakeCameraSource(total_frames=1, colour_bgr=colour) as cam:
            frame = cam.read()
        assert frame is not None
        assert tuple(frame.image[0, 0]) == colour

    def test_source_id_propagated_to_frames(self) -> None:
        with FakeCameraSource(total_frames=1, source_id="test-cam") as cam:
            frame = cam.read()
        assert frame is not None
        assert frame.source_id == "test-cam"

    def test_timestamps_advance_monotonically(self) -> None:
        with FakeCameraSource(total_frames=3, frame_interval_secs=1.0) as cam:
            frames = list(cam)
        assert frames[1].timestamp > frames[0].timestamp
        assert frames[2].timestamp > frames[1].timestamp

    def test_read_before_open_raises(self) -> None:
        cam = FakeCameraSource(total_frames=5)
        with pytest.raises(CameraOpenError):
            cam.read()

    def test_close_stops_iteration(self) -> None:
        # After close, frames_emitted should not change.
        cam = FakeCameraSource(total_frames=10)
        cam.open()
        cam.read()
        cam.close()
        assert cam.frames_emitted == 1

    def test_frames_emitted_counter(self) -> None:
        with FakeCameraSource(total_frames=4) as cam:
            for _ in range(3):
                cam.read()
            assert cam.frames_emitted == 3

    def test_context_manager_calls_open_and_close(self) -> None:
        cam = FakeCameraSource(total_frames=2)
        with cam:
            assert cam._is_open is True
        assert cam._is_open is False

    def test_camera_source_is_abstract(self) -> None:
        # CameraSource cannot be instantiated directly.
        with pytest.raises(TypeError):
            CameraSource()  # type: ignore[abstract]

    def test_infinite_source_stops_via_context(self) -> None:
        # total_frames=-1 is infinite; collect 100 manually.
        collected: list[Frame] = []
        cam = FakeCameraSource(total_frames=-1)
        cam.open()
        for _ in range(100):
            f = cam.read()
            assert f is not None
            collected.append(f)
        cam.close()
        assert len(collected) == 100
        assert collected[-1].frame_id == 99
