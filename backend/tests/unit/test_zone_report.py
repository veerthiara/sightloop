"""Unit tests for zone calibration report."""

from datetime import datetime, timezone

from sightloop_vision.models.detection import BBox
from sightloop_vision.models.track import Track
from sightloop_vision.models.zone import Zone
from sightloop_vision.services.zones.zone_report import (
    ZoneCalibrationReport,
    build_zone_calibration_report,
)


class TestZoneCalibrationReport:
    """Test zone calibration report generation."""

    def test_zone_calibration_report_creation(self) -> None:
        """Test creating a zone calibration report."""
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
                {
                    "name": "desk",
                    "type": "rectangle",
                    "x1": 50,
                    "y1": 50,
                    "x2": 400,
                    "y2": 400,
                },
            ],
            frames_processed=300,
            detection_frames_processed=10,
            zone_hits_by_name={"bottle_home": 45, "desk": 120},
            zone_hits_by_class={
                "bottle_home": {"bottle": 40, "person": 5},
                "desk": {"bottle": 80, "person": 40},
            },
            track_count_by_class={"bottle": 5, "person": 3},
            bottle_home_hits=45,
            desk_hits=120,
            created_at="2024-01-15T10:30:00+00:00",
            notes="Test run",
        )

        assert report.session_name == "test-session"
        assert report.camera_source_masked == "0"
        assert len(report.zones) == 2
        assert report.bottle_home_hits == 45
        assert report.desk_hits == 120

    def test_zone_calibration_report_to_dict(self) -> None:
        """Test serializing report to dictionary."""
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

        data = report.to_summary_dict()

        assert data["session_name"] == "test-session"
        assert data["bottle_home_hits"] == 45
        assert "zones" in data
        assert "zone_hits_by_name" in data

    def test_build_zone_calibration_report(self) -> None:
        """Test building a zone calibration report from session data."""
        zones = [
            Zone(name="bottle_home", type="rectangle", x1=100, y1=100, x2=300, y2=300),
            Zone(name="desk", type="rectangle", x1=50, y1=50, x2=400, y2=400),
        ]

        # Create mock tracks
        track1 = Track(
            track_id=1,
            class_name="bottle",
            bbox=BBox(x1=150, y1=150, x2=250, y2=250),
            confidence=0.9,
        )
        track1._zone_entered = {"bottle_home": datetime.now(timezone.utc)}

        track2 = Track(
            track_id=2,
            class_name="person",
            bbox=BBox(x1=200, y1=200, x2=300, y2=400),
            confidence=0.8,
        )
        track2._zone_entered = {"desk": datetime.now(timezone.utc)}

        report = build_zone_calibration_report(
            session_name="test-session",
            camera_source=0,
            zones=zones,
            frames_processed=300,
            detection_frames_processed=10,
            zone_hits_by_name={"bottle_home": 45, "desk": 120},
            zone_hits_by_class={"bottle_home": {"bottle": 40}, "desk": {"person": 40}},
            track_count_by_class={"bottle": 5, "person": 3},
            bottle_home_hits=45,
            desk_hits=120,
            notes="Test notes",
        )

        assert report.session_name == "test-session"
        assert report.camera_source_masked == "0"
        assert len(report.zones) == 2
        assert report.bottle_home_hits == 45
        assert report.desk_hits == 120
        assert report.notes == "Test notes"
        assert "bottle" in report.track_count_by_class
        assert "person" in report.track_count_by_class
