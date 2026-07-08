"""Debug and observability settings."""

from pathlib import Path

from pydantic import BaseModel, Field


class DebugConfig(BaseModel):
    """Debug and observability settings."""

    enabled: bool = Field(
        default=False,
        description="Enable debug evidence capture such as saved frames.",
    )
    output_dir: Path | None = Field(
        default=None,
        description="Optional override directory for saved debug frames.",
    )
    save_every_n_frames: int = Field(
        default=30,
        ge=1,
        description="Save one debug frame every N processed frames.",
    )
    display_enabled: bool = Field(
        default=False,
        description="Show a live preview window. Requires a display.",
    )
    metrics_log_interval_secs: float = Field(
        default=10.0,
        ge=1.0,
        description="Emit a metrics summary log line every N seconds.",
    )
    image_extension: str = Field(
        default="jpg",
        description="Image file extension for debug frames (jpg, png).",
    )
