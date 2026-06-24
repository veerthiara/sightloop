"""Frame — the core data structure passed through the vision pipeline.

A Frame wraps a raw numpy image array with stable metadata so that downstream
modules (pipeline, metrics, debug writers, detectors) never receive raw
OpenCV-specific objects directly.
"""

from dataclasses import dataclass, field
from datetime import datetime

import numpy as np


@dataclass(frozen=True)
class Frame:
    """A single captured video frame with associated metadata.

    All pipeline stages receive and return ``Frame`` objects, keeping
    OpenCV-specific types confined to the camera module.

    Attributes:
        frame_id:   Monotonically increasing integer starting from 0. Uniquely
                    identifies this frame within a session.
        image:      H×W×C uint8 numpy array in BGR colour order (OpenCV default).
        timestamp:  UTC datetime when the frame was captured.
        source_id:  Opaque string identifying the camera source
                    (e.g. ``"0"`` for index 0, or a URI).
        width:      Frame width in pixels (derived from image shape).
        height:     Frame height in pixels (derived from image shape).
    """

    frame_id: int
    image: np.ndarray
    timestamp: datetime
    source_id: str = "unknown"

    # Derived fields — populated automatically from image shape.
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self) -> None:
        if self.image.ndim < 2:
            raise ValueError("Frame image must have at least 2 dimensions (H, W).")
        # frozen=True requires object.__setattr__ for derived fields.
        object.__setattr__(self, "height", self.image.shape[0])
        object.__setattr__(self, "width", self.image.shape[1])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(height, width)`` for quick size checks."""
        return self.height, self.width

    def __repr__(self) -> str:
        return (
            f"Frame(id={self.frame_id}, "
            f"shape={self.height}x{self.width}, "
            f"source={self.source_id!r}, "
            f"ts={self.timestamp.isoformat()})"
        )
