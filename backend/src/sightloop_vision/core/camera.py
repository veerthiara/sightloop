"""Camera source and resolution settings."""

from pydantic import BaseModel, Field, field_validator


class CameraConfig(BaseModel):
    """Camera source and resolution settings."""

    source: int | str = Field(
        default=0,
        description="Camera index (int) or URI string for IP/RTSP cameras.",
    )
    width: int = Field(default=1280, ge=64, description="Frame width in pixels.")
    height: int = Field(default=720, ge=64, description="Frame height in pixels.")
    fps: int = Field(default=30, ge=1, le=120, description="Target capture FPS.")

    @field_validator("source", mode="before")
    @classmethod
    def coerce_source(cls, v: object) -> int | str:
        """Accept numeric strings as camera indices."""
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v
