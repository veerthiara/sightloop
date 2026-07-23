"""Run tracking with zones on RTSP camera."""

from __future__ import annotations

import argparse
import logging
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
    parser.add_argument(
        "--write-zone-report",
        action="store_true",
        help="Write zone calibration JSON and Markdown reports.",
    )
    parser.add_argument(
        "--zone-notes",
        default=None,
        help="Optional notes to include in the zone calibration report.",
    )
    parser.add_argument(
        "--require-zones",
        action="store_true",
        help="Fail if no zones are configured.",
    )
    parser.add_argument(
        "--diagnostics-only",
        action="store_true",
        help="Load config, print diagnostics, and exit without opening camera.",
    )
    parser.add_argument(
        "--warn-if-no-bottle",
        action="store_true",
        help="Warn if no bottle tracks are created during the run.",
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
        zone_state_tracker,
        confidence_threshold: float,
        run_every_n_frames: int,
        allowed_classes: list[str],
        warn_if_no_bottle: bool = False,
    ) -> None:
        from sightloop_vision.services.detection import (
            filter_detections_by_allowed_classes,
            filter_detections_by_confidence,
        )

        self._detector = detector
        self._renderer = renderer
        self._tracker = tracker
        self._zone_manager = zone_manager
        self._zone_state_tracker = zone_state_tracker
        self._confidence_threshold = confidence_threshold
        self._run_every_n_frames = run_every_n_frames
        self._allowed_classes = allowed_classes
        self._warn_if_no_bottle = warn_if_no_bottle
        self._filter_by_confidence = filter_detections_by_confidence
        self._filter_by_allowed_classes = filter_detections_by_allowed_classes

        self.detection_frames_processed = 0
        self.bottle_home_hits = 0
        self.desk_hits = 0
        self.track_class_counts: dict[str, int] = {}
        self._zone_hits_by_class: dict[str, dict[str, int]] = {}
        self._any_bottle_track = False

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

        # Update zone state tracker
        self._zone_state_tracker.update(tracks, frame.frame_id)

        # Evaluate zones
        for track in tracks:
            zone_names = self._zone_manager.evaluate_track(track)
            track.check_zones(self._zone_manager.zones)  # Update track's zone state

            if "bottle_home" in zone_names:
                self.bottle_home_hits += 1
            if "desk" in zone_names:
                self.desk_hits += 1

            if track.class_name == "bottle":
                self._any_bottle_track = True

            # Track zone hits by class
            for zone_name in zone_names:
                self._zone_hits_by_class.setdefault(zone_name, {})
                self._zone_hits_by_class[zone_name][track.class_name] = (
                    self._zone_hits_by_class[zone_name].get(track.class_name, 0) + 1
                )

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

    @property
    def zone_hits_by_class(self) -> dict[str, dict[str, int]]:
        return self._zone_hits_by_class

    @property
    def any_bottle_track(self) -> bool:
        return self._any_bottle_track


def print_diagnostics(config, zones, logger) -> None:
    """Print diagnostic information about the configuration."""
    print("\n=== Tracking Diagnostics ===")
    print(f"Session: {config.session_name}")
    print(f"Environment: {config.environment}")
    print(f"Camera source: {config.camera.source}")
    w = config.camera.width
    h = config.camera.height
    fps = config.camera.fps
    print(f"Camera resolution: {w}x{h} @ {fps}fps")

    print("\n--- Detection Config ---")
    print(f"  Model: {config.detection.model_name}")
    print(f"  Enabled: {config.detection.enabled}")
    print(f"  Confidence threshold: {config.detection.confidence_threshold}")
    print(f"  Run every N frames: {config.detection.run_every_n_frames}")
    print(f"  Classes: {config.detection.classes}")

    print("\n--- Zone Config ---")
    if zones:
        for zone in zones:
            print(f"  {zone.name}: ({zone.x1}, {zone.y1}) - ({zone.x2}, {zone.y2})")
    else:
        print("  NO ZONES CONFIGURED!")

    print("\n--- Tracking Config ---")
    print(f"  Max missed frames: {getattr(config.tracking, 'max_missed_frames', 30)}")
    print(
        f"  Match distance threshold: {getattr(config.tracking, 'match_distance_threshold', 100.0)}"
    )

    print("\n--- Validation ---")
    warnings = []
    if not config.detection.enabled:
        warnings.append("Detection is disabled!")
    if "person" not in config.detection.classes:
        warnings.append("'person' not in detection classes")
    if "bottle" not in config.detection.classes and "cup" not in config.detection.classes:
        warnings.append(
            "Neither 'bottle' nor 'cup' in detection classes - bottle may not be detected"
        )
    if not zones:
        warnings.append("No zones configured - zone evaluation will be skipped")
    else:
        zone_names = {z.name for z in zones}
        if "bottle_home" not in zone_names:
            warnings.append("'bottle_home' zone not found")
        if "desk" not in zone_names:
            warnings.append("'desk' zone not found")

    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    else:
        print("  All checks passed")

    print("=== End Diagnostics ===\n")


def main(argv: Sequence[str] | None = None) -> int:
    from sightloop_vision.app.runner import build_camera_source, build_frame_writer
    from sightloop_vision.core.config import load_config
    from sightloop_vision.services.detection import YoloDetector
    from sightloop_vision.services.metrics import CameraSessionStats, FpsTracker
    from sightloop_vision.services.pipeline import CameraPipeline
    from sightloop_vision.services.rendering import ZoneRenderer
    from sightloop_vision.services.tracking import SimpleTracker
    from sightloop_vision.services.zones import ZoneManager, load_zones_from_config
    from sightloop_vision.services.zones.zone_report import build_zone_calibration_report
    from sightloop_vision.services.zones.zone_report_writer import ZoneReportWriter
    from sightloop_vision.services.zones.zone_state_tracker import ZoneStateTracker

    args = parse_args(argv)
    config = load_config(args.config)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Load zones
    zones = load_zones_from_config(config)

    # Print diagnostics
    print_diagnostics(config, zones, logger)

    # Check zone requirements
    if args.require_zones and not zones:
        logger.error("--require-zones specified but no zones configured")
        return 1

    if args.diagnostics_only:
        print("\nDiagnostics only mode - exiting without running camera")
        return 0

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
    zone_state_tracker = ZoneStateTracker(zones)

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
        zone_state_tracker=zone_state_tracker,
        confidence_threshold=config.detection.confidence_threshold,
        run_every_n_frames=config.detection.run_every_n_frames,
        allowed_classes=config.detection.classes,
        warn_if_no_bottle=args.warn_if_no_bottle,
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

    # Print summary
    zone_state_summary = zone_state_tracker.build_summary()

    summary = {
        "frames_processed": frames_processed,
        "detection_frames_processed": processor.detection_frames_processed,
        "total_tracks_created": tracker.total_tracks_created,
        "active_tracks": len(tracker.get_tracks()),
        "bottle_tracks": zone_state_summary.bottle_tracks_created,
        "person_tracks": zone_state_summary.person_tracks_created,
        "bottle_home_zone_hits": zone_state_tracker.get_zone_entry_count("bottle_home"),
        "desk_zone_hits": zone_state_tracker.get_zone_entry_count("desk"),
        "zone_entries": zone_state_tracker.get_zone_entry_summary(),
        "zone_exits": zone_state_tracker.get_zone_exit_summary(),
        "frames_inside_zones": zone_state_tracker.get_frames_inside_summary(),
        "annotated_output_dir": str(renderer.session_dir),
    }
    print(summary)

    if args.warn_if_no_bottle and not processor.any_bottle_track:
        print(
            "\nWARNING: No bottle tracks were created during this run."
            " Try lower confidence threshold, larger YOLO model (yolov8m.pt/yolov8l.pt), "
            "clearer bottle visibility, or lower run_every_n_frames."
        )

    # Write zone calibration report if requested
    if args.write_zone_report:
        from sightloop_vision.services.zones.zone_report import build_zone_calibration_report
        from sightloop_vision.services.zones.zone_report_writer import ZoneReportWriter

        zone_state_summary = zone_state_tracker.build_summary()

        report = build_zone_calibration_report(
            session_name=config.session_name,
            camera_source=config.camera.source,
            zones=zones,
            frames_processed=frames_processed,
            detection_frames_processed=processor.detection_frames_processed,
            zone_hits_by_name={
                "bottle_home": zone_state_tracker.get_zone_entry_count("bottle_home"),
                "desk": zone_state_tracker.get_zone_entry_count("desk"),
            },
            zone_hits_by_class={},  # Could be enhanced
            track_count_by_class=zone_state_summary.track_count_by_class,
            bottle_home_hits=zone_state_tracker.get_zone_entry_count("bottle_home"),
            desk_hits=zone_state_tracker.get_zone_entry_count("desk"),
            notes=args.zone_notes,
        )
        writer = ZoneReportWriter()
        json_path, md_path = writer.write_all(report)
        print("Zone calibration report written:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")

        # Also write zone state summary
        from sightloop_vision.services.zones.zone_report_writer import ZoneReportWriter
        state_report = zone_state_summary.to_dict()
        import json
        state_json_path = Path(f"artifacts/zones/{config.session_name}/zone-state-summary.json")
        state_json_path.parent.mkdir(parents=True, exist_ok=True)
        state_json_path.write_text(json.dumps(state_report, indent=2))
        print(f"Zone state summary: {state_json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
