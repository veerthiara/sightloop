"""Benchmark RTSP detection quality across candidate YOLO models."""

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
    parser = argparse.ArgumentParser(description="Benchmark YOLO detection quality on RTSP frames.")
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
    parser.add_argument(
        "--model-name",
        default=None,
        help="Optional model override, for example yolov8s.pt.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=None,
        help="Optional confidence threshold override.",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write automated JSON and Markdown baseline reports.",
    )
    parser.add_argument(
        "--baseline-notes",
        default=None,
        help="Optional notes to attach to the baseline report.",
    )
    parser.add_argument(
        "--min-person-detections",
        type=int,
        default=1,
        help="Quality gate minimum for person detections.",
    )
    parser.add_argument(
        "--min-bottle-detections",
        type=int,
        default=1,
        help="Quality gate minimum for bottle detections.",
    )
    parser.add_argument(
        "--min-person-confidence",
        type=float,
        default=0.50,
        help="Quality gate minimum average confidence for person detections.",
    )
    parser.add_argument(
        "--min-bottle-confidence",
        type=float,
        default=0.25,
        help="Quality gate minimum average confidence for bottle detections.",
    )
    return parser.parse_args(argv)


class BenchmarkDetectionProcessor:
    """Frame callback that runs detection at an interval and records quality stats."""

    def __init__(
        self,
        detector,
        renderer,
        quality_report,
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
        self._quality_report = quality_report
        self._allowed_classes = allowed_classes
        self._confidence_threshold = confidence_threshold
        self._run_every_n_frames = run_every_n_frames
        self._filter_by_allowed_classes = filter_detections_by_allowed_classes
        self._filter_by_confidence = filter_detections_by_confidence

    def __call__(self, frame) -> None:
        if frame.frame_id % self._run_every_n_frames != 0:
            return

        detections = self._detector.detect(frame)
        detections = self._filter_by_confidence(detections, self._confidence_threshold)
        detections = self._filter_by_allowed_classes(detections, self._allowed_classes)
        self._renderer.save_annotated_frame(frame, detections)
        self._quality_report.record_detection_frame(detections, annotated_saved=True)


def main(argv: Sequence[str] | None = None) -> int:
    from sightloop_vision.app.runner import build_camera_source, build_frame_writer
    from sightloop_vision.core.config import load_config
    from sightloop_vision.services.detection import (
        DetectionBaselineWriter,
        DetectionQualityReport,
        YoloDetector,
        build_detection_baseline_report,
        is_supported_model,
    )
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline
    from sightloop_vision.services.rendering import DetectionRenderer

    args = parse_args(argv)
    config = load_config(args.config)

    if not config.detection.enabled:
        raise SystemExit("Detection is disabled in the config.")

    model_name = args.model_name or config.detection.model_name
    if not is_supported_model(model_name, config.detection.candidate_models):
        raise SystemExit(
            f"Unsupported model {model_name!r}. "
            f"Allowed candidates: {config.detection.candidate_models}"
        )

    confidence_threshold = (
        args.confidence_threshold
        if args.confidence_threshold is not None
        else config.detection.confidence_threshold
    )

    camera_source = build_camera_source(config)
    fps_tracker = FpsTracker()
    session_stats = CameraSessionStats(session_name=config.session_name)
    frame_writer = build_frame_writer(config)
    detector = YoloDetector(model_name=model_name)
    renderer = DetectionRenderer(
        output_dir=config.detection.output_dir,
        session_name=config.session_name,
        image_extension=getattr(config.detection, "image_extension", "png"),
    )
    quality_report = DetectionQualityReport()
    processor = BenchmarkDetectionProcessor(
        detector=detector,
        renderer=renderer,
        quality_report=quality_report,
        allowed_classes=config.detection.classes,
        confidence_threshold=confidence_threshold,
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

    print(
        f"Starting detection benchmark '{config.session_name}' "
        f"with model={model_name} threshold={confidence_threshold}"
    )
    frames_processed = pipeline.run(max_frames=args.max_frames)
    quality_report.set_frames_processed(frames_processed)

    summary = quality_report.to_summary_dict()
    summary["model_name"] = model_name
    summary["confidence_threshold"] = confidence_threshold
    summary["annotated_output_dir"] = str(renderer.annotated_dir)
    summary["person_output_dir"] = str(renderer.person_dir)
    summary["bottle_output_dir"] = str(renderer.bottle_dir)
    summary["no_target_output_dir"] = str(renderer.no_target_dir)
    summary["pipeline_summary"] = pipeline.final_summary

    print("Detection quality summary:")
    print(summary)

    if args.write_baseline:
        baseline_report = build_detection_baseline_report(
            session_name=config.session_name,
            model_name=model_name,
            confidence_threshold=confidence_threshold,
            run_every_n_frames=config.detection.run_every_n_frames,
            classes=config.detection.classes,
            camera_source=config.camera.source,
            output_dir=renderer.session_dir,
            quality_summary=summary,
            notes=args.baseline_notes,
            min_person_detections=args.min_person_detections,
            min_bottle_detections=args.min_bottle_detections,
            min_person_confidence=args.min_person_confidence,
            min_bottle_confidence=args.min_bottle_confidence,
        )
        writer = DetectionBaselineWriter()
        json_path, markdown_path = writer.write_all(baseline_report)
        print("Baseline reports written:")
        print({"json": str(json_path), "markdown": str(markdown_path)})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
