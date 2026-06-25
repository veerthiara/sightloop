"""Small registry for supported YOLO model names."""

DEFAULT_CANDIDATE_MODELS = ["yolov8n.pt", "yolov8s.pt"]


def get_candidate_models(configured_models: list[str] | None = None) -> list[str]:
    """Return configured models or the default candidate list."""
    return configured_models or DEFAULT_CANDIDATE_MODELS.copy()


def is_supported_model(model_name: str, configured_models: list[str] | None = None) -> bool:
    """Return whether the model name is in the candidate list."""
    return model_name in get_candidate_models(configured_models)
