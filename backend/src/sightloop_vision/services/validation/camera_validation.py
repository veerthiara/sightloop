"""Validation summary helpers for RTSP camera bring-up."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def mask_camera_source(camera_source: int | str) -> str:
    """Mask credentials in camera source strings for logs and summaries."""
    if isinstance(camera_source, int):
        return str(camera_source)

    parts = urlsplit(camera_source)
    if not parts.scheme or "@" not in parts.netloc:
        return camera_source

    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port is not None else ""
    masked_netloc = f"***:***@{host}{port}"
    return urlunsplit((parts.scheme, masked_netloc, parts.path, parts.query, parts.fragment))


@dataclass
class CameraValidationReport:
    """Serializable summary of an RTSP validation run."""

    session_name: str
    camera_source: str
    frames_processed: int
    duration_seconds: float
    average_fps: float
    debug_output_path: str | None
    success: bool
    failure_reason: str | None = None

    def to_summary_dict(self) -> dict[str, object]:
        """Return a serializable validation summary."""
        return {
            "session_name": self.session_name,
            "camera_source": self.camera_source,
            "frames_processed": self.frames_processed,
            "duration_seconds": round(self.duration_seconds, 6),
            "average_fps": round(self.average_fps, 6),
            "debug_output_path": self.debug_output_path,
            "success": self.success,
            "failure_reason": self.failure_reason,
        }


def build_validation_report(
    *,
    session_name: str,
    camera_source: int | str,
    final_summary: dict[str, object] | None,
    debug_output_path: Path | str | None,
    success: bool,
    failure_reason: str | None = None,
) -> CameraValidationReport:
    """Build a validation report from pipeline summary data."""
    summary = final_summary or {}
    return CameraValidationReport(
        session_name=session_name,
        camera_source=mask_camera_source(camera_source),
        frames_processed=int(summary.get("frame_count", 0)),
        duration_seconds=float(summary.get("duration_secs", 0.0)),
        average_fps=float(summary.get("average_fps", 0.0)),
        debug_output_path=str(debug_output_path) if debug_output_path is not None else None,
        success=success,
        failure_reason=failure_reason,
    )
