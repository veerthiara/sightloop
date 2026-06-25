"""Writers for automated detection baseline reports."""

from __future__ import annotations

import json
from pathlib import Path

from sightloop_vision.services.detection.baseline import DetectionBaselineReport


class DetectionBaselineWriter:
    """Persist JSON and Markdown detection baseline reports."""

    def __init__(self, output_root: Path | str = Path("artifacts/baselines")) -> None:
        self._output_root = Path(output_root)

    def session_dir(self, session_name: str) -> Path:
        return self._output_root / session_name

    def write_json(self, report: DetectionBaselineReport) -> Path:
        output_path = self.session_dir(report.session_name) / "detection-baseline.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report.to_summary_dict(), indent=2, sort_keys=True) + "\n"
        )
        return output_path

    def write_markdown(self, report: DetectionBaselineReport) -> Path:
        output_path = self.session_dir(report.session_name) / "detection-baseline.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._render_markdown(report))
        return output_path

    def write_all(self, report: DetectionBaselineReport) -> tuple[Path, Path]:
        return self.write_json(report), self.write_markdown(report)

    def _render_markdown(self, report: DetectionBaselineReport) -> str:
        summary = report.to_summary_dict()
        gate_status = "PASS" if report.quality_gate_result else "FAIL"
        reasons = report.quality_gate_reasons or ["No automated gate failures."]
        notes = report.notes or "None."

        reason_lines = "\n".join(f"- {reason}" for reason in reasons)

        return (
            f"# Detection Baseline Report\n\n"
            f"## Summary\n\n"
            f"- Session: `{report.session_name}`\n"
            f"- Model: `{report.model_name}`\n"
            f"- Confidence threshold: `{report.confidence_threshold}`\n"
            f"- Run every N frames: `{report.run_every_n_frames}`\n"
            f"- Classes: `{', '.join(report.classes)}`\n"
            f"- Camera source: `{report.masked_camera_source}`\n"
            f"- Output dir: `{report.output_dir}`\n"
            f"- Created at: `{report.created_at}`\n\n"
            f"## Metrics\n\n"
            f"- Frames processed: `{summary['frames_processed']}`\n"
            f"- Detection frames processed: `{summary['detection_frames_processed']}`\n"
            f"- Annotated frames saved: `{summary['annotated_frames_saved']}`\n"
            f"- Detections by class: `{summary['detections_by_class']}`\n"
            f"- Average confidence by class: `{summary['average_confidence_by_class']}`\n"
            f"- Min confidence by class: `{summary['min_confidence_by_class']}`\n"
            f"- Max confidence by class: `{summary['max_confidence_by_class']}`\n\n"
            f"## Quality Gate\n\n"
            f"- Result: `{gate_status}`\n"
            f"- Manual review required: `{report.manual_review_required}`\n"
            f"{reason_lines}\n\n"
            f"## Notes\n\n"
            f"{notes}\n\n"
            f"## Manual Review Checklist\n\n"
            f"- Confirm `person` boxes are placed on real people, not background objects.\n"
            f"- Confirm `bottle` boxes are placed on the target bottle, not similar clutter.\n"
            f"- Review `no_target/` frames for missed detections.\n"
            f"- Review `person/` and `bottle/` grouped outputs for false positives.\n"
            f"- Decide whether the current model/threshold is acceptable for tracking work.\n"
        )
