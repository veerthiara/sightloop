"""Unit tests for debug frame writing."""

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from sightloop_vision.models import Frame
from sightloop_vision.services.debug import FrameWriter


class TestFrameWriter:
    def _make_frame(self, frame_id: int = 0, source_id: str = "fake") -> Frame:
        image = np.full((4, 6, 3), fill_value=(10, 20, 30), dtype=np.uint8)
        return Frame(
            frame_id=frame_id,
            image=image,
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            source_id=source_id,
        )

    def test_requires_positive_save_interval(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="at least 1"):
            FrameWriter(tmp_path, "session", save_every_n_frames=0)

    def test_builds_safe_per_session_path(self, tmp_path: Path) -> None:
        writer = FrameWriter(tmp_path, "session with spaces")
        frame = self._make_frame()

        path = writer.build_output_path(frame)

        assert path.parent == tmp_path / "session-with-spaces"
        assert path.name.startswith("frame_000000_")
        assert path.suffix == ".ppm"

    def test_write_frame_saves_ppm_file(self, tmp_path: Path) -> None:
        writer = FrameWriter(tmp_path, "session-a", save_every_n_frames=1)
        frame = self._make_frame(frame_id=0)

        path = writer.write_frame(frame)

        assert path is not None
        assert path.exists()
        assert writer.saved_frame_count == 1
        assert path.read_bytes().startswith(b"P6\n")

    def test_write_frame_skips_when_interval_does_not_match(self, tmp_path: Path) -> None:
        writer = FrameWriter(tmp_path, "session-a", save_every_n_frames=3)
        frame = self._make_frame(frame_id=1)

        path = writer.write_frame(frame)

        assert path is None
        assert writer.saved_frame_count == 0
        assert not writer.session_dir.exists()

    def test_write_frame_skips_cleanly_when_disabled(self, tmp_path: Path) -> None:
        writer = FrameWriter(tmp_path, "session-a", save_every_n_frames=1, enabled=False)
        frame = self._make_frame(frame_id=0)

        path = writer.write_frame(frame)

        assert path is None
        assert writer.saved_frame_count == 0
