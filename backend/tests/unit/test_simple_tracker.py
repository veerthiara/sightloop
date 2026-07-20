"""Unit tests for simple tracker."""

from datetime import datetime, timezone

from sightloop_vision.models.detection import BBox, Detection
from sightloop_vision.services.tracking.simple_tracker import SimpleTracker


class TestSimpleTracker:
    """Test SimpleTracker."""

    def _make_detection(
        self, class_name: str, bbox: BBox, confidence: float = 0.9, frame_id: int = 0
    ) -> Detection:
        return Detection(
            class_name=class_name,
            confidence=confidence,
            bbox=bbox,
            frame_id=frame_id,
            timestamp=datetime.now(timezone.utc),
        )

    def test_create_tracks_for_first_detections(self) -> None:
        """Test that new tracks are created for first detections."""
        tracker = SimpleTracker(max_distance=100.0, max_missed_frames=10, min_hits=1)

        detections = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200)),
            self._make_detection("bottle", BBox(x1=300, y1=300, x2=350, y2=350)),
        ]
        tracks = tracker.update(detections)

        assert len(tracks) == 2
        assert tracks[0].class_name == "person"
        assert tracks[1].class_name == "bottle"
        assert tracker.total_tracks_created == 2

    def test_match_detection_to_existing_track(self) -> None:
        """Test that nearby detections match existing tracks."""
        tracker = SimpleTracker(max_distance=100.0, max_missed_frames=10, min_hits=1)

        # First frame
        detections1 = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200)),
        ]
        tracker.update(detections1)

        # Second frame - detection slightly moved
        detections2 = [
            self._make_detection("person", BBox(x1=105, y1=105, x2=205, y2=205), frame_id=1),
        ]
        tracks = tracker.update(detections2)

        assert len(tracks) == 1
        assert tracks[0].track_id == 1
        assert tracks[0].age == 3  # age=1 on creation, +1 each update
        assert tracker.total_tracks_created == 1

    def test_new_track_for_far_detection(self) -> None:
        """Test that far detections create new tracks."""
        tracker = SimpleTracker(max_distance=50.0, max_missed_frames=10, min_hits=1)

        detections1 = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200)),
        ]
        tracker.update(detections1)

        # Far away detection
        detections2 = [
            self._make_detection("person", BBox(x1=500, y1=500, x2=600, y2=600), frame_id=1),
        ]
        tracks = tracker.update(detections2)

        assert len(tracks) == 2  # Two tracks created
        assert tracker.total_tracks_created == 2

    def test_class_aware_matching(self) -> None:
        """Test that tracks only match same class."""
        tracker = SimpleTracker(max_distance=100.0, max_missed_frames=10, min_hits=1)

        detections1 = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200)),
        ]
        tracker.update(detections1)

        # Bottle at same location - should create new track
        detections2 = [
            self._make_detection("bottle", BBox(x1=105, y1=105, x2=205, y2=205), frame_id=1),
        ]
        tracks = tracker.update(detections2)

        assert len(tracks) == 2
        assert tracker.total_tracks_created == 2

    def test_track_lost_after_missed_frames(self) -> None:
        """Test that tracks are removed after max missed frames."""
        tracker = SimpleTracker(max_distance=100.0, max_missed_frames=2, min_hits=1)

        detections1 = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200)),
        ]
        tracker.update(detections1)

        # No detections for 2 frames
        tracker.update([])
        tracks_after_1_miss = tracker.update([])
        assert len(tracks_after_1_miss) == 1

        tracks_after_2_miss = tracker.update([])
        assert len(tracks_after_2_miss) == 0  # Track removed

    def test_min_hits_confirmation(self) -> None:
        """Test that tracks need min_hits to be confirmed."""
        tracker = SimpleTracker(max_distance=100.0, max_missed_frames=10, min_hits=3)

        detections = [
            self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200), frame_id=i)
            for i in range(2)
        ]

        # Only 2 detections - not enough for min_hits=3
        tracks = tracker.update(detections[0:1])
        assert len(tracks) == 0  # Not confirmed yet

        tracks = tracker.update(detections[1:2])
        assert len(tracks) == 0  # Still not confirmed

        # Third detection confirms
        det = self._make_detection("person", BBox(x1=100, y1=100, x2=200, y2=200), frame_id=2)
        tracks = tracker.update([det])
        assert len(tracks) == 1  # Now confirmed
