"""Business logic for the text-modality pipeline.

Handles raw user text input as well as text transcribed by the audio
pipeline (the cascade described in the project's fusion architecture).
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.text_emotion import TextEmotionModel
from app.schemas.common import EmotionPrediction
from app.schemas.text import TextAnalysisResponse
from app.services.analysis_repository import AnalysisRepository

logger = logging.getLogger(__name__)


class TextEmotionService:
    """Business logic layer for text emotion analysis."""

    def __init__(self, model: TextEmotionModel, repository: AnalysisRepository):
        self._model = model
        self._repository = repository

    async def predict(self, text: str) -> EmotionPrediction:
        """Run the text model without persisting anything.

        Used both by the `/text/analyze` endpoint and by the audio/video
        cascades, which need a raw prediction to feed into the fusion
        engine without creating a standalone `analyses` row for the
        intermediate transcript.
        """
        # `model.predict` is CPU-bound (tokenization + torch inference), so
        # it is offloaded to a worker thread to keep the event loop free.
        return await asyncio.to_thread(self._model.predict, text)

    async def analyze(self, db: AsyncSession, *, text: str) -> TextAnalysisResponse:
        logger.info("text_service.analyze.start", extra={"chars": len(text)})
        prediction = await self.predict(text)

        record = await self._repository.save_text_analysis(
            db, text=text, prediction=prediction
        )

        logger.info(
            "text_service.analyze.complete",
            extra={"analysis_id": str(record.id), "emotion": prediction.emotion},
        )
        return TextAnalysisResponse(
            analysis_id=record.id,
            text=text,
            prediction=prediction,
            created_at=record.created_at,
        )
