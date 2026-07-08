"""Calibration capture settings."""

from pathlib import Path

from pydantic import BaseModel, Field


class CalibrationConfig(BaseModel):
    """Calibration capture settings."""

    output_dir: Path = Field(
        default=Path("artifacts/calibration"),
        description="Directory for calibration reference frames.",
    )
    image_extension: str = Field(
        default="jpg",
        description="Image file extension for calibration frames (jpg, png).",
    )
