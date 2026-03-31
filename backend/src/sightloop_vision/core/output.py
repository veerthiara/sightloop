"""Output path settings for artifacts produced during a session."""

from pathlib import Path

from pydantic import BaseModel, Field


class OutputConfig(BaseModel):
    """Paths for artifacts produced during a session."""

    frames_dir: Path = Field(
        default=Path("artifacts/frames"),
        description="Directory for debug frame images.",
    )
    clips_dir: Path = Field(
        default=Path("artifacts/clips"),
        description="Directory for short clip recordings.",
    )
    logs_dir: Path = Field(
        default=Path("artifacts/logs"),
        description="Directory for session log files.",
    )
