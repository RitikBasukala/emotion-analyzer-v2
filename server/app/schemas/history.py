"""Schemas for the analysis history endpoint."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AnalysisHistoryItem(BaseModel):
    id: uuid.UUID
    modality: str
    final_emotion: str
    confidence: float
    created_at: datetime
    input_preview: Optional[str] = None


class AnalysisHistoryResponse(BaseModel):
    items: List[AnalysisHistoryItem]
    total: int
    limit: int
    offset: int
