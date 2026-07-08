"""Capture clean calibration/reference frames from camera for multi-position setup."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture calibration frames from camera.")
    parser.add_argument(
        "--config",
        default="configs/dev.yaml",
        help="Path to the YAML config file relative to backend/ or absolute.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional cap on processed frames.",
    )
    parser.add_argument(
        "--save-every-n-frames",
        type=int,
        default=30,
        help="Save one frame every N frames (default: 30).",
    )
    parser.add_argument(
        "--session-name",
        default=None,
        help="Session name (e.g., desk-front-angle, desk-top-angle, desk-evening-light).",
    )
    parser.add_argument(
        "--position-label",
        default="",
        help="Human-readable position label (e.g., front-angle, top-angle, evening-light).",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional notes about this calibration capture.",
    )
    return parser.parse_args(argv)


class CalibrationFrameWriter:
    """Save calibration frames to a structured directory with manifest."""

    def __init__(
        self,
        output_dir: Path | str,
        session_name: str,
        image_extension: str = "jpg",
        save_every_n_frames: int = 30,
    ) -> None:
        from sightloop_vision.services.debug.frame_writer import _safe_slug

        self._base_output_dir = Path(output_dir)
        self._session_slug = _safe_slug(session_name)
        self._image_extension = self._normalize_image_extension(image_extension)
        self._save_every_n_frames = save_every_n_frames
        self._enabled = True
        self.saved_frame_count = 0
        self._frames_saved = []

    @staticmethod
    def _normalize_image_extension(ext: str) -> str:
        ext = ext.lower().lstrip(".")
        if ext in ("jpg", "jpeg"):
            return "jpg"
        if ext == "png":
            return "png"
        return "jpg"

    @property
    def session_dir(self) -> Path:
        return self._base_output_dir / self._session_slug

    @property
    def frames_dir(self) -> Path:
        return self.session_dir / "frames"

    def should_save(self, frame_id: int) -> bool:
        if not self._enabled:
            return False
        return frame_id % self._save_every_n_frames == 0

    def build_output_path(self, frame_id: int, timestamp: datetime) -> Path:
        ts = timestamp.astimezone().strftime("%Y%m%dT%H%M%S_%f%z")
        return self.frames_dir / f"frame_{frame_id:06d}_{ts}.{self._image_extension}"

    def write_frame(self, frame_id: int, timestamp: datetime, image) -> Path | None:
        """Write frame if it matches the save interval."""
        if not self.should_save(frame_id):
            return None

        output_path = self.build_output_path(frame_id, timestamp)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        import numpy as np
        from PIL import Image

        if image.ndim == 2:
            pil_image = Image.fromarray(image, mode="L")
        elif image.ndim == 3 and image.shape[2] >= 3:
            rgb = image[..., :3][:, :, ::-1].astype(np.uint8, copy=False)
            pil_image = Image.fromarray(rgb, mode="RGB")
        else:
            raise ValueError(
                "CalibrationFrameWriter expects 2D grayscale or 3-channel image array."
            )

        pil_image.save(
            output_path,
            format="JPEG" if self._image_extension == "jpg" else "PNG",
            quality=90 if self._image_extension == "jpg" else None,
        )

        self.saved_frame_count += 1
        self._frames_saved.append(str(output_path.relative_to(self.session_dir)))
        return output_path

    def write_manifest(
        self,
        position_label: str,
        notes: str,
        camera_source: int | str,
        resolution: tuple[int, int] | None,
        max_frames: int | None,
        created_at: str | None = None,
    ) -> Path:
        """Write calibration manifest JSON."""
        if created_at is None:
            created_at = datetime.now(tz=timezone.utc).isoformat()

        from sightloop_vision.services.validation import mask_camera_source

        manifest = {
            "session_name": self._session_slug,
            "position_label": position_label,
            "notes": notes,
            "created_at": created_at,
            "camera_source_masked": mask_camera_source(camera_source),
            "resolution": list(resolution) if resolution else None,
            "max_frames": max_frames,
            "save_every_n_frames": self._save_every_n_frames,
            "frames_saved": self.saved_frame_count,
            "output_dir": str(self.session_dir),
            "image_extension": self._image_extension,
            "frames": self._frames_saved,
        }

        manifest_path = self.session_dir / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest_path

    def create_contact_sheet(
        self, max_frames_per_sheet: int = 12, thumb_size: tuple[int, int] = (320, 180)
    ) -> Path | None:
        """Create a contact sheet from saved frames."""
        if not self._frames_saved:
            return None

        from PIL import Image

        frames_to_use = self._frames_saved[:max_frames_per_sheet]
        if not frames_to_use:
            return None

        cols = 4
        rows = (len(frames_to_use) + cols - 1) // cols
        sheet_width = cols * thumb_size[0]
        sheet_height = rows * thumb_size[1]

        contact_sheet = Image.new("RGB", (sheet_width, sheet_height), color=(30, 30, 30))

        for idx, frame_rel_path in enumerate(frames_to_use):
            frame_path = self.session_dir / frame_rel_path
            if not frame_path.exists():
                continue

            try:
                img = Image.open(frame_path)
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)

                x = (idx % cols) * thumb_size[0]
                y = (idx // cols) * thumb_size[1]
                contact_sheet.paste(img, (x, y))
            except Exception:
                continue

        contact_sheet_path = self.session_dir / "contact_sheet.jpg"
        contact_sheet.save(contact_sheet_path, format="JPEG", quality=85)
        return contact_sheet_path


def main(argv: Sequence[str] | None = None) -> int:
    from sightloop_vision.app.runner import build_camera_source
    from sightloop_vision.core.config import load_config
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline

    args = parse_args(argv)
    config = load_config(args.config)

    # Override session name if provided
    if args.session_name:
        config = config.model_copy(update={"session_name": args.session_name})

    # Get image extension from calibration config
    image_extension = getattr(config.calibration, "image_extension", "jpg")
    calibration_output_dir = getattr(config.calibration, "output_dir", "artifacts/calibration")

    camera_source = build_camera_source(config)
    fps_tracker = FpsTracker()
    session_stats = CameraSessionStats(session_name=config.session_name)

    calibration_writer = CalibrationFrameWriter(
        output_dir=calibration_output_dir,
        session_name=config.session_name,
        image_extension=image_extension,
        save_every_n_frames=args.save_every_n_frames,
    )

    resolution = None

    def calibration_processor(frame):
        nonlocal resolution
        if resolution is None and frame.image is not None:
            resolution = (frame.image.shape[1], frame.image.shape[0])

        calibration_writer.write_frame(
            frame_id=frame.frame_id,
            timestamp=frame.timestamp,
            image=frame.image,
        )

    pipeline = CameraPipeline(
        source=camera_source,
        display_enabled=config.debug.display_enabled,
        fps_tracker=fps_tracker,
        session_stats=session_stats,
        frame_writer=None,  # No debug frames for calibration
        frame_processor=calibration_processor,
        metrics_log_interval_secs=config.debug.metrics_log_interval_secs,
    )

    print(f"Starting calibration capture: '{config.session_name}'")
    print(f"Position: {args.position_label}")
    print(f"Save every {args.save_every_n_frames} frames")
    print(f"Max frames: {args.max_frames or 'unlimited'}")
    print(f"Output: {calibration_output_dir}/{config.session_name}/frames/")
    print(f"Image format: {image_extension}")

    frames_processed = pipeline.run(max_frames=args.max_frames)

    print(f"\nCalibration capture complete: {config.session_name}")
    print(f"Frames processed: {frames_processed}")
    print(f"Frames saved: {calibration_writer.saved_frame_count}")

    # Write manifest
    manifest_path = calibration_writer.write_manifest(
        position_label=args.position_label,
        notes=args.notes,
        camera_source=config.camera.source,
        resolution=resolution,
        max_frames=args.max_frames,
    )
    print(f"Manifest written: {manifest_path}")

    # Create contact sheet
    contact_sheet_path = calibration_writer.create_contact_sheet()
    if contact_sheet_path:
        print(f"Contact sheet: {contact_sheet_path}")

    print("\nReview template: docs/implementation/phase-1/calibration-review-template.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
