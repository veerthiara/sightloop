"""Main camera pipeline loop.

Keeps the frame-reading loop separate from camera adapter setup so later
revisions can layer metrics, debug writers, and inference on top.
"""

from __future__ import annotations

from typing import Any

from sightloop_vision.adapters.camera import CameraSource


class CameraPipeline:
    """Continuously read frames from a camera source until stopped."""

    def __init__(self, source: CameraSource, display_enabled: bool = False) -> None:
        self._source = source
        self._display_enabled = display_enabled
        self.processed_frames = 0

    def run(self, max_frames: int | None = None) -> int:
        """Run the pipeline until the stream ends or execution is interrupted."""
        cv2 = self._load_display_backend() if self._display_enabled else None
        self.processed_frames = 0

        self._source.open()
        try:
            while True:
                if max_frames is not None and self.processed_frames >= max_frames:
                    break

                frame = self._source.read()
                if frame is None:
                    break

                self.processed_frames += 1

                if cv2 is not None:
                    cv2.imshow("SightLoop Vision", frame.image)
                    key = cv2.waitKey(1) & 0xFF
                    if key in (27, ord("q")):
                        break
        except KeyboardInterrupt:
            return self.processed_frames
        finally:
            self._source.close()
            if cv2 is not None:
                cv2.destroyAllWindows()

        return self.processed_frames

    def _load_display_backend(self) -> Any:
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise ImportError(
                "OpenCV is required when display_enabled=True."
            ) from exc
        return cv2
