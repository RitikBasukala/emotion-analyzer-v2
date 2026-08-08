"""Schemas for the video-modality endpoints."""

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

from app.schemas.common import EmotionPrediction
from app.schemas.fusion import FusionResult


class FrameEmotion(BaseModel):
    frame_index: int
    emotion: str
    confidence: float
    probabilities: dict[str, float]


class VideoAnalysisResponse(BaseModel):
    analysis_id: uuid.UUID
    modality: Literal["video"] = "video"
    transcript: Optional[str] = None
    facial_emotion: EmotionPrediction
    audio_emotion: Optional[EmotionPrediction] = None
    text_emotion: Optional[EmotionPrediction] = None
    fusion: FusionResult
    frame_count: Optional[int] = None
    frame_emotions: Optional[List[FrameEmotion]] = None
    audio_duration_seconds: Optional[float] = None
    created_at: datetime
