"""Schemas for the text-modality endpoints."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import EmotionPrediction


class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)


class TextAnalysisResponse(BaseModel):
    analysis_id: uuid.UUID
    modality: Literal["text"] = "text"
    text: str
    prediction: EmotionPrediction
    created_at: datetime
