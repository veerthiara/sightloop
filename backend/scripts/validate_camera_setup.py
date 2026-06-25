"""Run an RTSP camera validation session with metrics and debug evidence capture."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate RTSP camera setup.")
    parser.add_argument(
        "--config",
        default="configs/jetson.yaml",
        help="Path to the YAML config file relative to backend/ or absolute.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional cap on processed frames for validation runs.",
    )
    parser.add_argument(
        "--session-name",
        default=None,
        help="Optional session name override for this validation run.",
    )
    return parser.parse_args(argv)


def run_validation(
    config_path: Path | str,
    max_frames: int | None = None,
    session_name_override: str | None = None,
) -> int:
    from sightloop_vision.adapters.camera.base import CameraOpenError
    from sightloop_vision.app.runner import build_camera_source, build_frame_writer
    from sightloop_vision.core.config import ConfigLoadError, load_config
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline
    from sightloop_vision.services.validation import build_validation_report

    config = load_config(config_path)
    if session_name_override is not None:
        config = config.model_copy(update={"session_name": session_name_override})

    camera_source = build_camera_source(config)
    fps_tracker = FpsTracker()
    session_stats = CameraSessionStats(session_name=config.session_name)
    frame_writer = build_frame_writer(config)
    pipeline = CameraPipeline(
        source=camera_source,
        display_enabled=config.debug.display_enabled,
        fps_tracker=fps_tracker,
        session_stats=session_stats,
        frame_writer=frame_writer,
        metrics_log_interval_secs=config.debug.metrics_log_interval_secs,
    )

    print("Starting RTSP validation run...")
    print(f"Session: {config.session_name}")
    print(f"Config: {config_path}")

    report = None
    exit_code = 0
    try:
        pipeline.run(max_frames=max_frames)
        report = build_validation_report(
            session_name=config.session_name,
            camera_source=config.camera.source,
            final_summary=pipeline.final_summary,
            debug_output_path=frame_writer.session_dir if frame_writer is not None else None,
            success=True,
        )
    except (CameraOpenError, ConfigLoadError, ImportError, OSError, ValueError) as exc:
        report = build_validation_report(
            session_name=config.session_name,
            camera_source=config.camera.source,
            final_summary=pipeline.final_summary,
            debug_output_path=frame_writer.session_dir if frame_writer is not None else None,
            success=False,
            failure_reason=str(exc),
        )
        exit_code = 1

    print("Validation summary:")
    print(report.to_summary_dict())
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    return run_validation(
        config_path=args.config,
        max_frames=args.max_frames,
        session_name_override=args.session_name,
    )


if __name__ == "__main__":
    raise SystemExit(main())
