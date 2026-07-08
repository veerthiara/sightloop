"""Frame evidence writer for debug sessions."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image

from sightloop_vision.models import Frame


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return slug.strip("-") or "session"


def _normalize_image_extension(ext: str) -> str:
    """Normalize image extension to a supported format."""
    ext = ext.lower().lstrip(".")
    if ext in ("jpg", "jpeg"):
        return "jpg"
    if ext == "png":
        return "png"
    # Default to jpg for unknown extensions
    return "jpg"


class FrameWriter:
    """Save selected frames to a deterministic per-session directory."""

    def __init__(
        self,
        output_dir: Path | str,
        session_name: str,
        save_every_n_frames: int = 30,
        enabled: bool = True,
        image_extension: str = "jpg",
    ) -> None:
        if save_every_n_frames < 1:
            raise ValueError("save_every_n_frames must be at least 1.")

        self._base_output_dir = Path(output_dir)
        self._session_name = session_name
        self._session_slug = _safe_slug(session_name)
        self._save_every_n_frames = save_every_n_frames
        self._enabled = enabled
        self._image_extension = _normalize_image_extension(image_extension)
        self.saved_frame_count = 0

    @property
    def session_dir(self) -> Path:
        """Directory where this session's frames will be written."""
        return self._base_output_dir / self._session_slug

    @property
    def image_extension(self) -> str:
        return self._image_extension

    def should_save(self, frame: Frame) -> bool:
        """Return whether the given frame should be persisted."""
        if not self._enabled:
            return False
        return frame.frame_id % self._save_every_n_frames == 0

    def build_output_path(self, frame: Frame) -> Path:
        """Build a deterministic output path for a frame."""
        ts = frame.timestamp.astimezone().strftime("%Y%m%dT%H%M%S_%f%z")
        return self.session_dir / f"frame_{frame.frame_id:06d}_{ts}.{self._image_extension}"

    def write_frame(self, frame: Frame) -> Path | None:
        """Write the frame if enabled and selected by the interval policy."""
        if not self.should_save(frame):
            return None

        output_path = self.build_output_path(frame)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_image(output_path, frame.image)
        self.saved_frame_count += 1
        return output_path

    def _write_image(self, path: Path, image: np.ndarray) -> None:
        """Write image using PIL for JPG/PNG support."""
        if image.ndim == 2:
            # Grayscale
            pil_image = Image.fromarray(image, mode="L")
        elif image.ndim == 3 and image.shape[2] >= 3:
            # BGR to RGB
            rgb = image[..., :3][:, :, ::-1].astype(np.uint8, copy=False)
            pil_image = Image.fromarray(rgb, mode="RGB")
        else:
            raise ValueError("FrameWriter expects a 2D grayscale or 3-channel image array.")

        save_format = "JPEG" if self._image_extension == "jpg" else "PNG"
        pil_image.save(path, format=save_format)
