"""Debug YOLO detections on live RTSP stream."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path before importing local modules
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ruff: noqa: E402
import sys

# ruff: noqa: E402
from pathlib import Path

# ruff: noqa: E402
from sightloop_vision.app.runner import build_camera_source

# ruff: noqa: E402
from sightloop_vision.core.config import load_config

# ruff: noqa: E402
from sightloop_vision.services.detection import YoloDetector


def main():
    config = load_config("configs/jetson.yaml")
    camera_source = build_camera_source(config)
    detector = YoloDetector(model_name=config.detection.model_name)

    # Load model to access class names
    detector._load_model()

    print(f"Model: {config.detection.model_name}")
    print(f"All model classes: {detector._model.names}")
    print(f"Filtered classes: {config.detection.classes}")
    print(f"Confidence threshold: {config.detection.confidence_threshold}")
    print("=" * 60)

    camera_source.open()
    try:
        for frame_id in range(10):
            frame = camera_source.read()
            if frame is None:
                continue

            # Run detection WITHOUT filtering
            raw_detections = detector.detect(frame)

            print(f"\nFrame {frame_id}: {len(raw_detections)} raw detections")
            for det in raw_detections:
                cx = (det.bbox.x1 + det.bbox.x2) // 2
                cy = (det.bbox.y1 + det.bbox.y2) // 2
                bbox_str = (
                    f"bbox=({det.bbox.x1},{det.bbox.y1},{det.bbox.x2},{det.bbox.y2}) "
                    f"center=({cx},{cy})"
                )
                print(f"  {det.class_name:20s}  conf={det.confidence:.3f}  {bbox_str}")

            if raw_detections:
                # Also show filtered
                from sightloop_vision.services.detection import (
                    filter_detections_by_allowed_classes,
                    filter_detections_by_confidence,
                )
                filtered = filter_detections_by_confidence(raw_detections, 0.35)
                filtered = filter_detections_by_allowed_classes(filtered, ["person", "bottle"])
                print(f"  -> After filtering (person/bottle, conf>=0.35): {len(filtered)}")
                for det in filtered:
                    print(f"     KEPT: {det.class_name} conf={det.confidence:.3f}")
            else:
                print("  -> No detections at all")

    finally:
        camera_source.close()


if __name__ == "__main__":
    main()
