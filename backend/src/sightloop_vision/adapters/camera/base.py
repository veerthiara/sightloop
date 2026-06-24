"""Camera source abstraction — ABC that all camera implementations must satisfy.

Keeping this interface here means the rest of the system (pipeline, tests) can
depend on the abstract type rather than any concrete implementation.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from sightloop_vision.models.frame import Frame


class CameraSource(ABC):
    """Abstract base class for all camera source implementations.

    Implementors must provide ``open``, ``read``, and ``close``.
    The class also supports the context-manager protocol so it can be used
    with ``with`` statements.

    Example::

        with OpenCVCameraSource(source=0, width=1280, height=720) as cam:
            for frame in cam:
                process(frame)
    """

    @abstractmethod
    def open(self) -> None:
        """Open and initialise the camera source.

        Raises:
            CameraOpenError: If the source cannot be opened.
        """

    @abstractmethod
    def read(self) -> Frame | None:
        """Read the next frame from the source.

        Returns:
            A :class:`~sightloop_vision.models.frame.Frame` on success,
            or ``None`` when the stream is exhausted (end-of-file / lost signal).
        """

    @abstractmethod
    def close(self) -> None:
        """Release the camera source and any associated resources."""

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "CameraSource":
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Iterator support — iterate over frames until stream exhausted
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[Frame]:
        """Yield frames until ``read()`` returns ``None``."""
        while True:
            frame = self.read()
            if frame is None:
                break
            yield frame


class CameraOpenError(Exception):
    """Raised when a camera source cannot be opened."""
