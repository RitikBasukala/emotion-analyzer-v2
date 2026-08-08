"""Schemas for the audio-modality endpoints."""

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from app.schemas.common import EmotionPrediction
from app.schemas.fusion import FusionResult


class AudioAnalysisResponse(BaseModel):
    analysis_id: uuid.UUID
    modality: Literal["audio"] = "audio"
    transcript: Optional[str] = None
    tone_emotion: EmotionPrediction
    text_emotion: Optional[EmotionPrediction] = None
    fusion: FusionResult
    audio_duration_seconds: Optional[float] = None
    created_at: datetime
