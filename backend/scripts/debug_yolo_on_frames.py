"""Debug YOLO detections on saved frames."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path before importing local modules
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ruff: noqa: E402
import cv2

# ruff: noqa: E402
from sightloop_vision.services.detection import YoloDetector


def main():
    detector = YoloDetector(model_name="yolov8n.pt")
    detector._load_model()  # Load model first

    frames_dir = Path("artifacts/tracking/jetson-session")
    frame_files = sorted(frames_dir.glob("frame_*.png"))[:5]

    print(f"Testing {len(frame_files)} frames...\n")

    for frame_file in frame_files:
        print(f"\n--- {frame_file.name} ---")
        # Load and run detection
        img = cv2.imread(str(frame_file))
        if img is None:
            print(f"  Could not load {frame_file}")
            continue

        # Run YOLO directly
        results = detector._model(img, verbose=False)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < 0.35:
                    continue
                cls_name = detector._model.names[cls_id]
                if cls_name in ['person', 'bottle', 'cup', 'wine glass', 'bowl', 'vase']:
                    xyxy = box.xyxy[0].tolist()
                    print(f"  {cls_name:12s} {conf:.2f}  bbox={xyxy}")


if __name__ == "__main__":
    main()
