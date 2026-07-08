"""Detection runtime settings."""

from pathlib import Path

from pydantic import BaseModel, Field


class DetectionConfig(BaseModel):
    """Object detection settings."""

    enabled: bool = Field(
        default=False,
        description="Enable object detection for the current session.",
    )
    model_name: str = Field(
        default="yolov8n.pt",
        description="Ultralytics model name or path.",
    )
    candidate_models: list[str] = Field(
        default_factory=lambda: ["yolov8n.pt", "yolov8s.pt"],
        description="Allowed candidate model names for benchmarking.",
    )
    confidence_threshold: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Minimum confidence required after detection.",
    )
    classes: list[str] = Field(
        default_factory=lambda: ["person", "bottle"],
        description="Class names to keep after detection.",
    )
    run_every_n_frames: int = Field(
        default=30,
        ge=1,
        description="Run detection every N processed frames.",
    )
    output_dir: Path = Field(
        default=Path("artifacts/detections"),
        description="Directory for annotated detection frames.",
    )
    image_extension: str = Field(
        default="png",
        description="Image file extension for detection frames (jpg, png).",
    )
