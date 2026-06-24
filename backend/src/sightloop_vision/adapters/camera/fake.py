"""FakeCameraSource — deterministic camera source for use in tests.

Produces a configurable number of solid-colour frames with predictable
frame IDs and timestamps, without requiring any hardware or OpenCV.
"""

from datetime import datetime, timedelta, timezone

import numpy as np

from sightloop_vision.models.frame import Frame

from .base import CameraOpenError, CameraSource


class FakeCameraSource(CameraSource):
    """A camera source that emits a fixed number of synthetic frames.

    Each frame is a solid-colour image. Frame IDs start at 0 and increment.
    Timestamps advance by ``frame_interval_secs`` per frame for
    reproducible timing in tests.

    Args:
        width:              Frame width in pixels. Default 640.
        height:             Frame height in pixels. Default 480.
        total_frames:       Total frames to emit before returning ``None``.
                            -1 means infinite (runs until closed externally).
        colour_bgr:         Solid BGR fill colour for every frame.
                            Default is mid-grey ``(128, 128, 128)``.
        frame_interval_secs: Simulated time between frames in seconds.
                            Default 1/30 (~30 fps).
        source_id:          Identifier string, useful for multi-source tests.

    Example::

        with FakeCameraSource(total_frames=5) as cam:
            frames = list(cam)   # exactly 5 frames
    """

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        total_frames: int = 10,
        colour_bgr: tuple[int, int, int] = (128, 128, 128),
        frame_interval_secs: float = 1 / 30,
        source_id: str = "fake",
    ) -> None:
        self._width = width
        self._height = height
        self._total_frames = total_frames
        self._colour_bgr = colour_bgr
        self._frame_interval_secs = frame_interval_secs
        self._source_id = source_id

        self._is_open = False
        self._frame_counter = 0
        self._base_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)

    # ------------------------------------------------------------------
    # CameraSource interface
    # ------------------------------------------------------------------

    def open(self) -> None:
        self._is_open = True
        self._frame_counter = 0

    def read(self) -> Frame | None:
        if not self._is_open:
            raise CameraOpenError("FakeCameraSource is not open. Call open() first.")

        if self._total_frames >= 0 and self._frame_counter >= self._total_frames:
            return None

        image = np.full(
            (self._height, self._width, 3),
            fill_value=self._colour_bgr,
            dtype=np.uint8,
        )
        ts = self._base_timestamp + timedelta(
            seconds=self._frame_counter * self._frame_interval_secs
        )
        frame = Frame(
            frame_id=self._frame_counter,
            image=image,
            timestamp=ts,
            source_id=self._source_id,
        )
        self._frame_counter += 1
        return frame

    def close(self) -> None:
        self._is_open = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def frames_emitted(self) -> int:
        """Number of frames returned so far."""
        return self._frame_counter
