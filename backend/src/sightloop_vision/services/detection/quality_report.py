"""Detection quality tracking for tuning runs."""

from __future__ import annotations

from collections import Counter, defaultdict

from sightloop_vision.models import Detection


class DetectionQualityReport:
    """Aggregate detection quality metrics across a benchmark run."""

    def __init__(self) -> None:
        self.frames_processed = 0
        self.detection_frames_processed = 0
        self.annotated_frames_saved = 0
        self._detections_by_class: Counter[str] = Counter()
        self._confidence_sums_by_class: defaultdict[str, float] = defaultdict(float)

    def set_frames_processed(self, frames_processed: int) -> None:
        self.frames_processed = frames_processed

    def record_detection_frame(
        self,
        detections: list[Detection],
        annotated_saved: bool = True,
    ) -> None:
        self.detection_frames_processed += 1
        if annotated_saved:
            self.annotated_frames_saved += 1

        for detection in detections:
            self._detections_by_class[detection.class_name] += 1
            self._confidence_sums_by_class[detection.class_name] += detection.confidence

    def detections_by_class(self) -> dict[str, int]:
        return dict(self._detections_by_class)

    def average_confidence_by_class(self) -> dict[str, float]:
        averages: dict[str, float] = {}
        for class_name, count in self._detections_by_class.items():
            if count == 0:
                continue
            averages[class_name] = round(self._confidence_sums_by_class[class_name] / count, 6)
        return averages

    def to_summary_dict(self) -> dict[str, object]:
        return {
            "frames_processed": self.frames_processed,
            "detection_frames_processed": self.detection_frames_processed,
            "detections_by_class": self.detections_by_class(),
            "average_confidence_by_class": self.average_confidence_by_class(),
            "annotated_frames_saved": self.annotated_frames_saved,
        }
