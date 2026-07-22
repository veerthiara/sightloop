"""Render zones and tracks on frames."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from sightloop_vision.models.detection import Detection, Frame
    from sightloop_vision.models.track import Track
    from sightloop_vision.models.zone import Zone


class ZoneRenderer:
    """Draw zones and tracks on frames."""

    ZONE_COLORS = {
        "bottle_home": (0, 255, 0),      # Green
        "desk": (0, 128, 255),           # Blue
        "default": (255, 255, 0),        # Yellow
    }

    TRACK_COLORS = {
        "person": (255, 64, 64),         # Red
        "bottle": (64, 255, 64),         # Green
        "default": (255, 255, 64),       # Yellow
    }

    def __init__(
        self,
        output_dir: Path | str,
        session_name: str,
        image_extension: str = "jpg",
    ) -> None:
        self._base_output_dir = Path(output_dir)
        self._session_name = session_name
        self._image_extension = image_extension.lower().lstrip(".")
        if self._image_extension not in ("jpg", "jpeg", "png"):
            self._image_extension = "jpg"
        self.saved_frame_count = 0

    @property
    def session_dir(self) -> Path:
        return self._base_output_dir / self._session_name

    def render_zones_and_tracks(
        self,
        frame: "Frame",
        detections: list["Detection"],
        tracks: list["Track"],
        zones: list["Zone"],
    ) -> Image.Image:
        """Draw zones, detections, and tracks on a frame."""
        rgb = frame.image[:, :, ::-1].copy()
        image = Image.fromarray(rgb)
        draw = ImageDraw.Draw(image)

        # Draw zones
        for zone in zones:
            color = self.ZONE_COLORS.get(zone.name, self.ZONE_COLORS["default"])
            # Draw zone rectangle with transparency effect
            draw.rectangle(
                [(zone.x1, zone.y1), (zone.x2, zone.y2)],
                outline=color,
                width=3,
            )
            # Draw zone name
            draw.text(
                (zone.x1 + 5, zone.y1 - 20),
                zone.name,
                fill=color,
            )

        # Draw detection boxes
        for detection in detections:
            box = detection.bbox
            color = self.TRACK_COLORS.get(detection.class_name, self.TRACK_COLORS["default"])
            draw.rectangle(
                [(box.x1, box.y1), (box.x2, box.y2)],
                outline=color,
                width=2,
            )
            label = f"{detection.class_name} {detection.confidence:.2f}"
            draw.text(
                (box.x1 + 4, max(box.y1 - 14, 0)),
                label,
                fill=color,
            )

        # Draw track IDs
        for track in tracks:
            box = track.bbox
            color = self.TRACK_COLORS.get(track.class_name, self.TRACK_COLORS["default"])
            # Draw track ID with zone info if track is in any zones
            track_zones = getattr(track, "zones", [])
            zone_label = f" [{', '.join(track_zones)}]" if track_zones else ""
            draw.text(
                (box.x1 + 4, box.y2 + 2),
                f"ID:{track.track_id} (age:{track.age}){zone_label}",
                fill=color,
            )

        return image

    def save_rendered_frame(
        self,
        frame: "Frame",
        detections: list["Detection"],
        tracks: list["Track"],
        zones: list["Zone"],
    ) -> Path:
        """Save annotated frame."""
        image = self.render_zones_and_tracks(frame, detections, tracks, zones)
        output_path = self.session_dir / f"frame_{frame.frame_id:06d}.{self._image_extension}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = "JPEG" if self._image_extension in ("jpg", "jpeg") else "PNG"
        image.save(output_path, format=fmt)
        self.saved_frame_count += 1
        return output_path
