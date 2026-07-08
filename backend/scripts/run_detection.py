"""Run RTSP object detection and save annotated frames."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLO detection on RTSP frames.")
    parser.add_argument(
        "--config",
        default="configs/jetson.yaml",
        help="Path to the YAML config file relative to backend/ or absolute.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional cap on processed frames.",
    )
    return parser.parse_args(argv)


class DetectionProcessor:
    """Frame callback that runs detection every N frames and saves annotations."""

    def __init__(
        self,
        detector,
        renderer,
        allowed_classes: list[str],
        confidence_threshold: float,
        run_every_n_frames: int,
    ) -> None:
        from sightloop_vision.services.detection import (
            filter_detections_by_allowed_classes,
            filter_detections_by_confidence,
        )

        self._detector = detector
        self._renderer = renderer
        self._allowed_classes = allowed_classes
        self._confidence_threshold = confidence_threshold
        self._run_every_n_frames = run_every_n_frames
        self._filter_by_allowed_classes = filter_detections_by_allowed_classes
        self._filter_by_confidence = filter_detections_by_confidence

        self.detection_frames_processed = 0
        self.class_counts: Counter[str] = Counter()

    def __call__(self, frame) -> None:
        if frame.frame_id % self._run_every_n_frames != 0:
            return

        detections = self._detector.detect(frame)
        detections = self._filter_by_confidence(detections, self._confidence_threshold)
        detections = self._filter_by_allowed_classes(detections, self._allowed_classes)

        self.detection_frames_processed += 1
        self.class_counts.update(detection.class_name for detection in detections)
        self._renderer.save_annotated_frame(frame, detections)


def main(argv: Sequence[str] | None = None) -> int:
    from sightloop_vision.app.runner import build_camera_source, build_frame_writer
    from sightloop_vision.core.config import load_config
    from sightloop_vision.services.detection import YoloDetector
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline
    from sightloop_vision.services.rendering import DetectionRenderer

    args = parse_args(argv)
    config = load_config(args.config)

    if not config.detection.enabled:
        raise SystemExit("Detection is disabled in the config.")

    camera_source = build_camera_source(config)
    fps_tracker = FpsTracker()
    session_stats = CameraSessionStats(session_name=config.session_name)
    frame_writer = build_frame_writer(config)
    detector = YoloDetector(model_name=config.detection.model_name)
    renderer = DetectionRenderer(
        output_dir=config.detection.output_dir,
        session_name=config.session_name,
        image_extension=getattr(config.detection, "image_extension", "png"),
    )
    processor = DetectionProcessor(
        detector=detector,
        renderer=renderer,
        allowed_classes=config.detection.classes,
        confidence_threshold=config.detection.confidence_threshold,
        run_every_n_frames=config.detection.run_every_n_frames,
    )
    pipeline = CameraPipeline(
        source=camera_source,
        display_enabled=config.debug.display_enabled,
        fps_tracker=fps_tracker,
        session_stats=session_stats,
        frame_writer=frame_writer,
        frame_processor=processor,
        metrics_log_interval_secs=config.debug.metrics_log_interval_secs,
    )

    print(f"Starting detection session '{config.session_name}'")
    frames_processed = pipeline.run(max_frames=args.max_frames)
    print(f"Stopped detection session '{config.session_name}'")
    print(
        {
            "frames_processed": frames_processed,
            "detection_frames_processed": processor.detection_frames_processed,
            "person_detections": processor.class_counts.get("person", 0),
            "bottle_detections": processor.class_counts.get("bottle", 0),
            "annotated_output_dir": str(renderer.session_dir),
            "pipeline_summary": pipeline.final_summary,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
