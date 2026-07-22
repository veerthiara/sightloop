"""Unit tests for zone calibration report writer."""

import json
from pathlib import Path

from sightloop_vision.services.zones.zone_report import ZoneCalibrationReport
from sightloop_vision.services.zones.zone_report_writer import ZoneReportWriter


class TestZoneReportWriter:
    """Test zone report writer."""

    def test_write_json_report(self, tmp_path: Path) -> None:
        """Test writing JSON report."""
        writer = ZoneReportWriter(tmp_path)

        report = ZoneCalibrationReport(
            session_name="test-session",
            camera_source_masked="0",
            zones=[
                {
                    "name": "bottle_home",
                    "type": "rectangle",
                    "x1": 100,
                    "y1": 100,
                    "x2": 300,
                    "y2": 300,
                },
            ],
            frames_processed=300,
            detection_frames_processed=10,
            zone_hits_by_name={"bottle_home": 45},
            zone_hits_by_class={"bottle_home": {"bottle": 40}},
            track_count_by_class={"bottle": 5},
            bottle_home_hits=45,
            desk_hits=0,
            created_at="2024-01-15T10:30:00+00:00",
            notes="Test run",
        )

        json_path = writer.write_json(report)

        assert json_path.exists()
        assert json_path.name == "zone-calibration-report.json"
        assert json_path.parent == tmp_path / "test-session"

        data = json.loads(json_path.read_text())
        assert data["session_name"] == "test-session"
        assert data["bottle_home_hits"] == 45
        assert data["notes"] == "Test run"

    def test_write_markdown_report(self, tmp_path: Path) -> None:
        """Test writing Markdown report."""
        writer = ZoneReportWriter(tmp_path)

        report = ZoneCalibrationReport(
            session_name="test-session",
            camera_source_masked="0",
            zones=[
                {
                    "name": "bottle_home",
                    "type": "rectangle",
                    "x1": 100,
                    "y1": 100,
                    "x2": 300,
                    "y2": 300,
                },
            ],
            frames_processed=300,
            detection_frames_processed=10,
            zone_hits_by_name={"bottle_home": 45, "desk": 120},
            zone_hits_by_class={
                "bottle_home": {"bottle": 40},
                "desk": {"bottle": 80, "person": 40},
            },
            track_count_by_class={"bottle": 5, "person": 3},
            bottle_home_hits=45,
            desk_hits=120,
            created_at="2024-01-15T10:30:00+00:00",
            notes="Test run notes",
        )

        md_path = writer.write_markdown(report)

        assert md_path.exists()
        assert md_path.name == "zone-calibration-report.md"

        content = md_path.read_text()
        assert "# Zone Calibration Report" in content
        assert "test-session" in content
        assert "bottle_home" in content
        assert "Test run notes" in content
        assert "Manual Review Checklist" in content

    def test_write_all(self, tmp_path: Path) -> None:
        """Test writing both JSON and Markdown reports."""
        writer = ZoneReportWriter(tmp_path)

        report = ZoneCalibrationReport(
            session_name="test-session",
            camera_source_masked="0",
            zones=[],
            frames_processed=300,
            detection_frames_processed=10,
            zone_hits_by_name={"bottle_home": 45},
            zone_hits_by_class={"bottle_home": {"bottle": 40}},
            track_count_by_class={"bottle": 5},
            bottle_home_hits=45,
            desk_hits=0,
            created_at="2024-01-15T10:30:00+00:00",
            notes=None,
        )

        json_path, md_path = writer.write_all(report)

        assert json_path.exists()
        assert md_path.exists()
        assert json_path.name == "zone-calibration-report.json"
        assert md_path.name == "zone-calibration-report.md"
