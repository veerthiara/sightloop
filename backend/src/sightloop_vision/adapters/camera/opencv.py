"""OpenCVCameraSource — concrete CameraSource backed by cv2.VideoCapture.

OpenCV is an optional dependency (``uv sync --extra camera``). Importing
this module without OpenCV installed raises a clear ``ImportError``.
On Jetson devices the system OpenCV build is typically used instead of
the pip package; install accordingly.
"""

from datetime import datetime, timezone

from sightloop_vision.models.frame import Frame

from .base import CameraOpenError, CameraSource

try:
    import cv2
except ImportError as exc:
    raise ImportError(
        "OpenCV is required for OpenCVCameraSource. "
        "Install it with: uv sync --extra camera\n"
        "On Jetson, use the system OpenCV build instead."
    ) from exc


class OpenCVCameraSource(CameraSource):
    """Camera source that reads frames using OpenCV's VideoCapture.

    Supports camera indices (int) and URI strings (RTSP, file paths, etc.).

    Args:
        source:     Camera index or URI string.
        width:      Requested frame width. Actual width may differ
                    depending on the device's supported resolutions.
        height:     Requested frame height.
        source_id:  Human-readable label used in Frame metadata.
                    Defaults to ``str(source)``.

    Example::

        with OpenCVCameraSource(source=0, width=1280, height=720) as cam:
            frame = cam.read()
    """

    def __init__(
        self,
        source: int | str = 0,
        width: int = 1280,
        height: int = 720,
        source_id: str | None = None,
    ) -> None:
        self._source = source
        self._width = width
        self._height = height
        self._source_id = source_id if source_id is not None else str(source)
        self._cap: cv2.VideoCapture | None = None
        self._frame_counter = 0

    # ------------------------------------------------------------------
    # CameraSource interface
    # ------------------------------------------------------------------

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._source)
        if not self._cap.isOpened():
            raise CameraOpenError(
                f"Could not open camera source: {self._source!r}"
            )
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._frame_counter = 0

    def read(self) -> Frame | None:
        if self._cap is None or not self._cap.isOpened():
            raise CameraOpenError("OpenCVCameraSource is not open. Call open() first.")

        ok, image = self._cap.read()
        if not ok or image is None:
            return None

        frame = Frame(
            frame_id=self._frame_counter,
            image=image,
            timestamp=datetime.now(tz=timezone.utc),
            source_id=self._source_id,
        )
        self._frame_counter += 1
        return frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
