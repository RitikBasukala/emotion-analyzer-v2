"""Configuration for the facial/video emotion model."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FacialEmotionConfig:
    """Facial emotion model configuration."""

    detector_backend: str = "opencv"
    emotion_model: str = "DeepFace-FER"
    model_path: Optional[str] = None
    device: str = "cpu"
    enforce_detection: bool = False
    enabled: bool = True

    frame_extraction_fps: int = 2
    max_frames: int = 30
