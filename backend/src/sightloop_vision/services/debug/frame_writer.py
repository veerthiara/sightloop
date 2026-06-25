"""Frame evidence writer for debug sessions."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from sightloop_vision.models import Frame


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return slug.strip("-") or "session"


class FrameWriter:
    """Save selected frames to a deterministic per-session directory."""

    def __init__(
        self,
        output_dir: Path | str,
        session_name: str,
        save_every_n_frames: int = 30,
        enabled: bool = True,
    ) -> None:
        if save_every_n_frames < 1:
            raise ValueError("save_every_n_frames must be at least 1.")

        self._base_output_dir = Path(output_dir)
        self._session_name = session_name
        self._session_slug = _safe_slug(session_name)
        self._save_every_n_frames = save_every_n_frames
        self._enabled = enabled
        self.saved_frame_count = 0

    @property
    def session_dir(self) -> Path:
        """Directory where this session's frames will be written."""
        return self._base_output_dir / self._session_slug

    def should_save(self, frame: Frame) -> bool:
        """Return whether the given frame should be persisted."""
        if not self._enabled:
            return False
        return frame.frame_id % self._save_every_n_frames == 0

    def build_output_path(self, frame: Frame) -> Path:
        """Build a deterministic output path for a frame."""
        ts = frame.timestamp.astimezone().strftime("%Y%m%dT%H%M%S_%f%z")
        return self.session_dir / f"frame_{frame.frame_id:06d}_{ts}.ppm"

    def write_frame(self, frame: Frame) -> Path | None:
        """Write the frame if enabled and selected by the interval policy."""
        if not self.should_save(frame):
            return None

        output_path = self.build_output_path(frame)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_ppm(output_path, frame.image)
        self.saved_frame_count += 1
        return output_path

    def _write_ppm(self, path: Path, image: np.ndarray) -> None:
        if image.ndim == 2:
            header = f"P5\n{image.shape[1]} {image.shape[0]}\n255\n".encode("ascii")
            payload = image.astype(np.uint8, copy=False).tobytes()
        elif image.ndim == 3 and image.shape[2] >= 3:
            rgb = image[..., :3][:, :, ::-1].astype(np.uint8, copy=False)
            header = f"P6\n{rgb.shape[1]} {rgb.shape[0]}\n255\n".encode("ascii")
            payload = rgb.tobytes()
        else:
            raise ValueError("FrameWriter expects a 2D grayscale or 3-channel image array.")

        path.write_bytes(header + payload)
