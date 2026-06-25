"""Unit tests for frame save interval behavior."""

from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from sightloop_vision.models import Frame
from sightloop_vision.services.debug import FrameWriter


class TestDebugSaveInterval:
    def _make_frame(self, frame_id: int) -> Frame:
        return Frame(
            frame_id=frame_id,
            image=np.zeros((2, 2, 3), dtype=np.uint8),
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            source_id="fake",
        )

    def test_should_save_every_second_frame(self, tmp_path: Path) -> None:
        writer = FrameWriter(tmp_path, "session-a", save_every_n_frames=2)

        assert writer.should_save(self._make_frame(0)) is True
        assert writer.should_save(self._make_frame(1)) is False
        assert writer.should_save(self._make_frame(2)) is True
