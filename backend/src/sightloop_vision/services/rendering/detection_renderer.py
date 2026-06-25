"""Render and save annotated detection frames."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw

from sightloop_vision.models import Detection, Frame


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return slug.strip("-") or "session"


class DetectionRenderer:
    """Draw detection boxes and labels and save annotated output."""

    def __init__(self, output_dir: Path | str, session_name: str) -> None:
        self._base_output_dir = Path(output_dir)
        self._session_slug = _safe_slug(session_name)
        self.saved_frame_count = 0

    @property
    def session_dir(self) -> Path:
        return self._base_output_dir / self._session_slug

    def annotate_frame(self, frame: Frame, detections: list[Detection]) -> Image.Image:
        rgb = frame.image[:, :, ::-1].copy()
        image = Image.fromarray(rgb)
        draw = ImageDraw.Draw(image)

        for detection in detections:
            box = detection.bbox
            draw.rectangle(
                [(box.x1, box.y1), (box.x2, box.y2)],
                outline=(255, 64, 64),
                width=3,
            )
            label = f"{detection.class_name} {detection.confidence:.2f}"
            text_origin = (box.x1 + 4, max(box.y1 - 14, 0))
            draw.text(text_origin, label, fill=(255, 255, 0))

        return image

    def build_output_path(self, frame: Frame) -> Path:
        ts = frame.timestamp.astimezone().strftime("%Y%m%dT%H%M%S_%f%z")
        return self.session_dir / f"frame_{frame.frame_id:06d}_{ts}.png"

    def save_annotated_frame(self, frame: Frame, detections: list[Detection]) -> Path:
        image = self.annotate_frame(frame, detections)
        output_path = self.build_output_path(frame)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        self.saved_frame_count += 1
        return output_path
