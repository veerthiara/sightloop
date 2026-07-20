"""Run tracking with zones on RTSP camera."""

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
    parser = argparse.ArgumentParser(description="Run tracking with zones on RTSP stream.")
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


class TrackingProcessor:
    """Frame callback that runs detection, tracking, and zone evaluation."""

    def __init__(
        self,
        detector,
        renderer,
        tracker,
        zone_manager,
        confidence_threshold: float,
        run_every_n_frames: int,
        allowed_classes: list[str],
    ) -> None:
        from sightloop_vision.services.detection import (
            filter_detections_by_allowed_classes,
            filter_detections_by_confidence,
        )

        self._detector = detector
        self._renderer = renderer
        self._tracker = tracker
        self._zone_manager = zone_manager
        self._confidence_threshold = confidence_threshold
        self._run_every_n_frames = run_every_n_frames
        self._allowed_classes = allowed_classes
        self._filter_by_confidence = filter_detections_by_confidence
        self._filter_by_allowed_classes = filter_detections_by_allowed_classes

        self.detection_frames_processed = 0
        self.bottle_home_hits = 0
        self.desk_hits = 0
        self.track_class_counts: dict[str, int] = {}

    def __call__(self, frame) -> None:
        if frame.frame_id % self._run_every_n_frames != 0:
            return

        # Run detection
        detections = self._detector.detect(frame)
        detections = self._filter_by_confidence(detections, self._confidence_threshold)
        detections = self._filter_by_allowed_classes(detections, self._allowed_classes)

        self.detection_frames_processed += 1

        # Update tracker
        tracks = self._tracker.update(detections)

        # Evaluate zones
        for track in tracks:
            zone_names = self._zone_manager.evaluate_track(track)
            if "bottle_home" in zone_names:
                self.bottle_home_hits += 1
            if "desk" in zone_names:
                self.desk_hits += 1

        # Save annotated frame
        self._renderer.save_rendered_frame(
            frame=frame,
            detections=detections,
            tracks=tracks,
            zones=self._zone_manager.zones,
        )

        # Update stats
        for track in tracks:
            count = self.track_class_counts.get(track.class_name, 0)
            self.track_class_counts[track.class_name] = count + 1


def main(argv: Sequence[str] | None = None) -> int:
    from sightloop_vision.app.runner import build_camera_source, build_frame_writer
    from sightloop_vision.core.config import load_config
    from sightloop_vision.services.detection import YoloDetector
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline
    from sightloop_vision.services.rendering import ZoneRenderer
    from sightloop_vision.services.tracking import SimpleTracker
    from sightloop_vision.services.zones import ZoneManager, load_zones_from_config

    args = parse_args(argv)
    config = load_config(args.config)

    if not config.detection.enabled:
        raise SystemExit("Detection is disabled in the config.")

    camera_source = build_camera_source(config)
    fps_tracker = FpsTracker()
    session_stats = CameraSessionStats(session_name=config.session_name)
    frame_writer = build_frame_writer(config)
    detector = YoloDetector(model_name=config.detection.model_name)

    # Load zones from config
    zones = load_zones_from_config(config)
    zone_manager = ZoneManager(zones)

    # Create tracker
    max_missed = getattr(config.tracking, "max_missed_frames", 30)
    match_dist = getattr(config.tracking, "match_distance_threshold", 100.0)
    tracker = SimpleTracker(
        max_distance=match_dist,
        max_missed_frames=max_missed,
        min_hits=3,
    )

    # Create renderer for tracking output
    tracking_output_dir = getattr(config.tracking, "output_dir", Path("artifacts/tracking"))
    renderer = ZoneRenderer(
        output_dir=tracking_output_dir,
        session_name=config.session_name,
        image_extension=getattr(config.detection, "image_extension", "jpg"),
    )

    processor = TrackingProcessor(
        detector=detector,
        renderer=renderer,
        tracker=tracker,
        zone_manager=zone_manager,
        confidence_threshold=config.detection.confidence_threshold,
        run_every_n_frames=config.detection.run_every_n_frames,
        allowed_classes=config.detection.classes,
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

    print(f"Starting tracking session '{config.session_name}'")
    print(f"Zones loaded: {[z.name for z in zones]}")
    frames_processed = pipeline.run(max_frames=args.max_frames)
    print(f"Stopped tracking session '{config.session_name}'")
    print(
        {
            "frames_processed": frames_processed,
            "detection_frames_processed": processor.detection_frames_processed,
            "total_tracks_created": tracker.total_tracks_created,
            "active_tracks": len(tracker.get_tracks()),
            "bottle_tracks": processor.track_class_counts.get("bottle", 0),
            "person_tracks": processor.track_class_counts.get("person", 0),
            "bottle_home_zone_hits": processor.bottle_home_hits,
            "desk_zone_hits": processor.desk_hits,
            "annotated_output_dir": str(renderer.session_dir),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
