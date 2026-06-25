"""Automated baseline reporting for detection benchmark runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sightloop_vision.services.validation import mask_camera_source


def _utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def evaluate_detection_quality_gate(
    *,
    detections_by_class: dict[str, int],
    average_confidence_by_class: dict[str, float],
    annotated_frames_saved: int,
    min_person_detections: int = 1,
    min_bottle_detections: int = 1,
    min_person_confidence: float = 0.50,
    min_bottle_confidence: float = 0.25,
) -> tuple[bool, list[str]]:
    """Return pass/fail plus human-readable reasons for the detection baseline gate."""
    reasons: list[str] = []

    person_count = detections_by_class.get("person", 0)
    bottle_count = detections_by_class.get("bottle", 0)
    person_conf = average_confidence_by_class.get("person", 0.0)
    bottle_conf = average_confidence_by_class.get("bottle", 0.0)

    if person_count < min_person_detections:
        reasons.append(
            f"person detections below threshold: {person_count} < {min_person_detections}"
        )
    if bottle_count < min_bottle_detections:
        reasons.append(
            f"bottle detections below threshold: {bottle_count} < {min_bottle_detections}"
        )
    if person_conf < min_person_confidence:
        reasons.append(
            "average person confidence below threshold: "
            f"{person_conf:.3f} < {min_person_confidence:.3f}"
        )
    if bottle_conf < min_bottle_confidence:
        reasons.append(
            "average bottle confidence below threshold: "
            f"{bottle_conf:.3f} < {min_bottle_confidence:.3f}"
        )
    if annotated_frames_saved < 1:
        reasons.append("annotated frames saved below threshold: 0 < 1")

    return len(reasons) == 0, reasons


@dataclass
class DetectionBaselineReport:
    """Serializable detection baseline report."""

    session_name: str
    model_name: str
    confidence_threshold: float
    run_every_n_frames: int
    classes: list[str]
    frames_processed: int
    detection_frames_processed: int
    detections_by_class: dict[str, int]
    average_confidence_by_class: dict[str, float]
    min_confidence_by_class: dict[str, float]
    max_confidence_by_class: dict[str, float]
    annotated_frames_saved: int
    output_dir: str
    masked_camera_source: str
    created_at: str
    quality_gate_result: bool
    quality_gate_reasons: list[str]
    manual_review_required: bool
    notes: str | None = None

    def to_summary_dict(self) -> dict[str, object]:
        return {
            "session_name": self.session_name,
            "model_name": self.model_name,
            "confidence_threshold": self.confidence_threshold,
            "run_every_n_frames": self.run_every_n_frames,
            "classes": self.classes,
            "frames_processed": self.frames_processed,
            "detection_frames_processed": self.detection_frames_processed,
            "detections_by_class": self.detections_by_class,
            "average_confidence_by_class": self.average_confidence_by_class,
            "min_confidence_by_class": self.min_confidence_by_class,
            "max_confidence_by_class": self.max_confidence_by_class,
            "annotated_frames_saved": self.annotated_frames_saved,
            "output_dir": self.output_dir,
            "masked_camera_source": self.masked_camera_source,
            "created_at": self.created_at,
            "quality_gate_result": self.quality_gate_result,
            "quality_gate_reasons": self.quality_gate_reasons,
            "manual_review_required": self.manual_review_required,
            "notes": self.notes,
        }


def build_detection_baseline_report(
    *,
    session_name: str,
    model_name: str,
    confidence_threshold: float,
    run_every_n_frames: int,
    classes: list[str],
    camera_source: int | str,
    output_dir: Path | str,
    quality_summary: dict[str, object],
    notes: str | None = None,
    min_person_detections: int = 1,
    min_bottle_detections: int = 1,
    min_person_confidence: float = 0.50,
    min_bottle_confidence: float = 0.25,
) -> DetectionBaselineReport:
    """Build a baseline report from benchmark summary data."""
    detections_by_class = dict(quality_summary.get("detections_by_class", {}))
    average_confidence_by_class = dict(quality_summary.get("average_confidence_by_class", {}))
    min_confidence_by_class = dict(quality_summary.get("min_confidence_by_class", {}))
    max_confidence_by_class = dict(quality_summary.get("max_confidence_by_class", {}))
    annotated_frames_saved = int(quality_summary.get("annotated_frames_saved", 0))

    quality_gate_result, quality_gate_reasons = evaluate_detection_quality_gate(
        detections_by_class=detections_by_class,
        average_confidence_by_class=average_confidence_by_class,
        annotated_frames_saved=annotated_frames_saved,
        min_person_detections=min_person_detections,
        min_bottle_detections=min_bottle_detections,
        min_person_confidence=min_person_confidence,
        min_bottle_confidence=min_bottle_confidence,
    )

    return DetectionBaselineReport(
        session_name=session_name,
        model_name=model_name,
        confidence_threshold=confidence_threshold,
        run_every_n_frames=run_every_n_frames,
        classes=classes,
        frames_processed=int(quality_summary.get("frames_processed", 0)),
        detection_frames_processed=int(quality_summary.get("detection_frames_processed", 0)),
        detections_by_class=detections_by_class,
        average_confidence_by_class=average_confidence_by_class,
        min_confidence_by_class=min_confidence_by_class,
        max_confidence_by_class=max_confidence_by_class,
        annotated_frames_saved=annotated_frames_saved,
        output_dir=str(output_dir),
        masked_camera_source=mask_camera_source(camera_source),
        created_at=_utcnow_iso(),
        quality_gate_result=quality_gate_result,
        quality_gate_reasons=quality_gate_reasons,
        manual_review_required=True,
        notes=notes,
    )
