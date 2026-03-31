"""Debug and observability settings."""

from pydantic import BaseModel, Field


class DebugConfig(BaseModel):
    """Debug and observability settings."""

    save_frame_interval_secs: float = Field(
        default=5.0,
        ge=0.1,
        description="Save one debug frame every N seconds. 0 disables saving.",
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
