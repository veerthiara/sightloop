"""App runner for the main camera pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from sightloop_vision.core.config import AppConfig, load_config
from sightloop_vision.services.pipeline import CameraPipeline


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the local camera runner."""
    parser = argparse.ArgumentParser(description="Run the SightLoop camera pipeline.")
    parser.add_argument(
        "--config",
        default="configs/dev.yaml",
        help="Path to the YAML config file relative to backend/ or absolute.",
    )
    return parser.parse_args(argv)


def build_camera_source(config: AppConfig):
    """Create the concrete camera source from app config."""
    from sightloop_vision.adapters.camera.opencv import OpenCVCameraSource

    return OpenCVCameraSource(
        source=config.camera.source,
        width=config.camera.width,
        height=config.camera.height,
    )


def run_from_config(config_path: Path | str) -> int:
    """Load config, build the pipeline, and run it to completion."""
    config = load_config(config_path)
    camera_source = build_camera_source(config)
    pipeline = CameraPipeline(
        source=camera_source,
        display_enabled=config.debug.display_enabled,
    )

    print(
        f"Starting session '{config.session_name}' "
        f"for environment '{config.environment}'."
    )
    processed_frames = pipeline.run()
    print(f"Stopped session '{config.session_name}' after {processed_frames} frames.")
    return processed_frames


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    """Application entry point."""
    args = parse_args(argv)
    return run_from_config(args.config)
