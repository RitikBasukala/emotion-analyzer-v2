"""Business logic for the audio-modality pipeline.

Cascade: raw audio -> acoustic tone model + Whisper transcription ->
transcript fed into the text model -> multi-tier fusion of tone + text.
"""

import asyncio
import logging
import os
import tempfile
from typing import Any, Dict, Optional

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.ml.audio_emotion import AudioEmotionModel
from app.schemas.audio import AudioAnalysisResponse
from app.schemas.common import EmotionPrediction
from app.services.analysis_repository import AnalysisRepository
from app.services.fusion_service import FusionService
from app.services.text_service import TextEmotionService

logger = logging.getLogger(__name__)


class AudioEmotionService:
    """Business logic layer for audio emotion analysis."""

    def __init__(
        self,
        model: AudioEmotionModel,
        text_service: TextEmotionService,
        fusion_service: FusionService,
        repository: AnalysisRepository,
        settings: Settings,
    ):
        self._model = model
        self._text_service = text_service
        self._fusion_service = fusion_service
        self._repository = repository
        self._settings = settings

    async def _persist_upload(self, file: UploadFile, suffix: str) -> str:
        """Stream the upload to disk asynchronously and return its path."""
        fd, path = tempfile.mkstemp(suffix=suffix, dir=str(self._settings.upload_path))
        os.close(fd)

        async with aiofiles.open(path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                await out_file.write(chunk)
        return path

    async def analyze_tone_and_transcript(self, audio_path: str) -> Dict[str, Any]:
        """Run the acoustic tone model + transcription (offloaded, CPU-bound)."""
        return await asyncio.to_thread(self._model.full_analysis, audio_path)

    async def predict_text_from_transcript(self, transcript: str) -> EmotionPrediction:
        """Cascade a transcript into the text model - shared with the video pipeline."""
        return await self._text_service.predict(transcript)

    async def analyze(
        self, db: AsyncSession, *, file: UploadFile
    ) -> AudioAnalysisResponse:
        suffix = os.path.splitext(file.filename or "")[1] or ".wav"
        audio_path = await self._persist_upload(file, suffix)
        logger.info("audio_service.analyze.start", extra={"path": audio_path})

        try:
            audio_results = await self.analyze_tone_and_transcript(audio_path)
            tone_prediction: EmotionPrediction = audio_results["tone_emotion"]
            transcript: Optional[str] = audio_results.get("transcription") or None

            text_prediction: Optional[EmotionPrediction] = None
            if transcript:
                text_prediction = await self._text_service.predict(transcript)

            fusion_output = self._fusion_service.fuse(
                text_prediction=text_prediction,
                audio_prediction=tone_prediction,
            )

            record = await self._repository.save_audio_analysis(
                db,
                input_file_path=audio_path,
                transcript=transcript,
                tone_prediction=tone_prediction,
                text_prediction=text_prediction,
                fusion_output=fusion_output,
                audio_duration_seconds=audio_results.get("audio_duration_seconds"),
            )

            logger.info(
                "audio_service.analyze.complete",
                extra={
                    "analysis_id": str(record.id),
                    "emotion": fusion_output.final_emotion,
                },
            )

            return AudioAnalysisResponse(
                analysis_id=record.id,
                transcript=transcript,
                tone_emotion=tone_prediction,
                text_emotion=text_prediction,
                fusion=self._fusion_service.to_schema(fusion_output),
                audio_duration_seconds=audio_results.get("audio_duration_seconds"),
                created_at=record.created_at,
            )
        finally:
            self._cleanup(audio_path)

    @staticmethod
    def _cleanup(path: str) -> None:
        try:
            os.unlink(path)
        except OSError:
            logger.warning("audio_service.cleanup_failed", extra={"path": path})
