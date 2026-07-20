"""Simple class-aware centroid tracker."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from sightloop_vision.models.detection import Detection
from sightloop_vision.models.track import Track
from sightloop_vision.services.tracking.base import Tracker

if TYPE_CHECKING:
    pass


class SimpleTracker(Tracker):
    """Simple centroid-based tracker with class awareness.

    Matches detections to existing tracks by:
    - Same class_name
    - Minimum Euclidean distance between bbox centers
    - Maximum distance threshold
    """

    def __init__(
        self,
        max_distance: float = 100.0,
        max_missed_frames: int = 10,
        min_hits: int = 3,
    ) -> None:
        self._max_distance = max_distance
        self._max_missed_frames = max_missed_frames
        self._min_hits = min_hits
        self._tracks: dict[int, Track] = {}
        self._next_track_id = 1
        self._total_tracks_created = 0

    @property
    def tracks(self) -> dict[int, Track]:
        return self._tracks

    def update(self, detections: list[Detection]) -> list[Track]:
        """Update tracker with new detections."""
        # Mark all existing tracks as missed
        for track in self._tracks.values():
            track.mark_missed()

        # Group detections by class
        detections_by_class: dict[str, list[Detection]] = {}
        for det in detections:
            detections_by_class.setdefault(det.class_name, []).append(det)

        # For each class, match detections to tracks
        for class_name, class_detections in detections_by_class.items():
            class_tracks = {
                tid: track for tid, track in self._tracks.items()
                if track.class_name == class_name
            }

            if not class_tracks:
                # No existing tracks for this class, create new ones
                for det in class_detections:
                    self._create_track(det)
                continue

            # Match detections to tracks using greedy assignment
            self._match_detections_to_tracks(class_detections, class_tracks)

        # Remove lost tracks
        lost_ids = [
            tid for tid, track in self._tracks.items()
            if track.is_lost(self._max_missed_frames)
        ]
        for tid in lost_ids:
            del self._tracks[tid]

        # Return confirmed tracks
        return [
            track for track in self._tracks.values()
            if track.is_confirmed(self._min_hits)
        ]

    def get_tracks(self) -> list[Track]:
        """Return all current tracks (including unconfirmed)."""
        return list(self._tracks.values())

    def _create_track(self, detection: Detection) -> Track:
        """Create a new track from a detection."""
        track_id = self._next_track_id
        self._next_track_id += 1
        self._total_tracks_created += 1

        track = Track(
            track_id=track_id,
            class_name=detection.class_name,
            bbox=detection.bbox,
            confidence=detection.confidence,
        )
        self._tracks[track_id] = track
        return track

    def _match_detections_to_tracks(
        self,
        detections: list[Detection],
        tracks: dict[int, Track],
    ) -> None:
        """Match detections to tracks using minimum distance."""
        if not detections or not tracks:
            for det in detections:
                self._create_track(det)
            return

        # Compute cost matrix (distance between bbox centers)
        track_ids = list(tracks.keys())
        cost_matrix = []
        for track in tracks.values():
            row = []
            track_center = (
                (track.bbox.x1 + track.bbox.x2) / 2,
                (track.bbox.y1 + track.bbox.y2) / 2,
            )
            for det in detections:
                det_center = (
                    (det.bbox.x1 + det.bbox.x2) / 2,
                    (det.bbox.y1 + det.bbox.y2) / 2,
                )
                dist = math.hypot(
                    track_center[0] - det_center[0],
                    track_center[1] - det_center[1],
                )
                row.append(dist)
            cost_matrix.append(row)

        # Greedy assignment: sort all pairs by distance
        pairs = []
        for i, track_id in enumerate(track_ids):
            for j, det in enumerate(detections):
                pairs.append((cost_matrix[i][j], i, j))

        pairs.sort(key=lambda x: x[0])

        used_tracks = set()
        used_detections = set()

        for dist, i, j in pairs:
            if i in used_tracks or j in used_detections:
                continue
            if dist > self._max_distance:
                continue

            track_id = track_ids[i]
            detection = detections[j]
            track = tracks[track_id]
            track.update(detection)
            used_tracks.add(i)
            used_detections.add(j)

        # Create new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in used_detections:
                self._create_track(det)

    @property
    def total_tracks_created(self) -> int:
        return self._total_tracks_created
