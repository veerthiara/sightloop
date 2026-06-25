"""Ultralytics YOLO detector adapter."""

from __future__ import annotations

from sightloop_vision.models import BBox, Detection, Frame
from sightloop_vision.services.detection.base import Detector


class YoloDetector(Detector):
    """Run object detection through Ultralytics YOLO."""

    def __init__(self, model_name: str = "yolov8n.pt") -> None:
        self._model_name = model_name
        self._model = None

    def detect(self, frame: Frame) -> list[Detection]:
        model = self._load_model()
        results = model.predict(frame.image, verbose=False)
        detections: list[Detection] = []

        for result in results:
            names = result.names
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_index = int(box.cls[0].item())
                bbox = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_name=str(names[cls_index]),
                        confidence=float(box.conf[0].item()),
                        bbox=BBox(
                            x1=float(bbox[0]),
                            y1=float(bbox[1]),
                            x2=float(bbox[2]),
                            y2=float(bbox[3]),
                        ),
                        frame_id=frame.frame_id,
                        timestamp=frame.timestamp,
                    )
                )

        return detections

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from ultralytics import YOLO
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise ImportError(
                "Ultralytics is required for YoloDetector. "
                "Install it with: uv sync --extra detection"
            ) from exc

        self._model = YOLO(self._model_name)
        return self._model
