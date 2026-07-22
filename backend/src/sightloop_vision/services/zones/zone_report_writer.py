"""Zone calibration report writers."""

from __future__ import annotations

import json
from pathlib import Path

from sightloop_vision.services.zones.zone_report import ZoneCalibrationReport


class ZoneReportWriter:
    """Persist JSON and Markdown zone calibration reports."""

    def __init__(self, output_root: Path | str = Path("artifacts/zones")) -> None:
        self._output_root = Path(output_root)

    def session_dir(self, session_name: str) -> Path:
        return self._output_root / session_name

    def write_json(self, report: ZoneCalibrationReport) -> Path:
        output_path = self.session_dir(report.session_name) / "zone-calibration-report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report.to_summary_dict(), indent=2, sort_keys=True) + "\n"
        )
        return output_path

    def write_markdown(self, report: ZoneCalibrationReport) -> Path:
        output_path = self.session_dir(report.session_name) / "zone-calibration-report.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._render_markdown(report))
        return output_path

    def write_all(self, report: ZoneCalibrationReport) -> tuple[Path, Path]:
        return self.write_json(report), self.write_markdown(report)

    def _render_markdown(self, report: ZoneCalibrationReport) -> str:
        zones_md = "\n".join(
            f"- **{z['name']}** ({z['type']}): "
            f"x1={z['x1']}, y1={z['y1']}, x2={z['x2']}, y2={z['y2']}"
            for z in report.zones
        ) or "No zones configured."

        zone_hits_lines = []
        for zone_name, count in report.zone_hits_by_name.items():
            zone_hits_lines.append(f"- **{zone_name}**: {count}")
        zone_hits_md = "\n".join(zone_hits_lines) if zone_hits_lines else "- (no hits recorded)"

        zone_hits_class_lines = []
        for zone_name, class_counts in report.zone_hits_by_class.items():
            class_md = ", ".join(f"{cls}: {cnt}" for cls, cnt in class_counts.items())
            zone_hits_class_lines.append(f"- **{zone_name}**: {class_md}")
        zone_hits_class_md = (
            "\n".join(zone_hits_class_lines)
            if zone_hits_class_lines
            else "No zone hits by class."
        )

        track_counts_lines = [
            f"- **{cls}**: {cnt}" for cls, cnt in sorted(report.track_count_by_class.items())
        ] or ["- (no tracks)"]
        track_counts_md = "\n".join(track_counts_lines)

        notes = report.notes or "None provided."

        return (
            f"# Zone Calibration Report\n\n"
            f"## Summary\n\n"
            f"- Session: `{report.session_name}`\n"
            f"- Camera source: `{report.camera_source_masked}`\n"
            f"- Frames processed: `{report.frames_processed}`\n"
            f"- Detection frames processed: `{report.detection_frames_processed}`\n"
            f"- Created at: `{report.created_at}`\n\n"
            f"## Configured Zones\n\n"
            f"{zones_md}\n\n"
            f"## Zone Hit Counts (all classes)\n\n"
            f"{zone_hits_md}\n\n"
            f"## Zone Hit Counts by Class\n\n"
            f"{zone_hits_class_md}\n\n"
            f"## Track Counts by Class\n\n"
            f"{track_counts_md}\n\n"
            f"## Key Zone Metrics\n\n"
            f"- `bottle_home` hits: `{report.bottle_home_hits}`\n"
            f"- `desk` hits: `{report.desk_hits}`\n\n"
            f"## Notes\n\n"
            f"{notes}\n\n"
            f"## Manual Review Checklist\n\n"
            f"- [ ] Open `artifacts/tracking/{report.session_name}/` and review annotated frames\n"
            f"- [ ] Verify `bottle_home` zone covers the bottle rest position\n"
            f"- [ ] Verify `desk` zone covers the desk surface area\n"
            f"- [ ] Check if tracks are correctly entering/exiting zones\n"
            f"- [ ] Check for false positives (tracks in zones when no object present)\n"
            f"- [ ] Check for missed detections (object in zone but no track)\n"
            f"- [ ] Adjust zone coordinates in `configs/jetson.yaml` if needed\n"
            f"- [ ] Re-run tracking after adjustments to verify\n"
            f"- [ ] Document any zone changes in version control\n"
        )
