"""Shared Pydantic schemas used across all modality routers/services."""

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class EmotionLabel(str, Enum):
    """The 7 coarse emotion classes shared by every modality and the fusion engine."""

    HAPPY = "Happy"
    SAD = "Sad"
    ANGRY = "Angry"
    FEAR = "Fear"
    SURPRISE = "Surprise"
    DISGUST = "Disgust"
    NEUTRAL = "Neutral"


EMOTION_LABELS: list[str] = [e.value for e in EmotionLabel]


class EmotionPrediction(BaseModel):
    """Standard unimodal prediction shape returned by every emotion model."""

    emotion: str
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: Dict[str, float]
    model_name: Optional[str] = None
    inference_time_ms: Optional[float] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
