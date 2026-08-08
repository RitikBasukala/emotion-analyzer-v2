"""Persistence tier for analysis records.

This is the only module that talks directly to the ORM/database layer for
analysis data. Services depend on this repository instead of importing
`app.db.models`/sessions directly, keeping business logic decoupled from
storage details.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Analysis, AudioResult, TextResult, VideoResult
from app.ml.fusion import FusionOutput
from app.schemas.common import EmotionPrediction

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """Async CRUD operations for analyses and their per-modality detail rows."""

    async def save_text_analysis(
        self, db: AsyncSession, *, text: str, prediction: EmotionPrediction
    ) -> Analysis:
        analysis = Analysis(
            modality="text",
            input_text=text[:500],
            final_emotion=prediction.emotion,
            confidence=prediction.confidence,
        )
        analysis.text_result = TextResult(
            emotion=prediction.emotion,
            confidence=prediction.confidence,
            probabilities=prediction.probabilities,
            model_name=prediction.model_name,
            inference_time_ms=prediction.inference_time_ms,
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        logger.info(
            "repository.text_analysis.saved", extra={"analysis_id": str(analysis.id)}
        )
        return analysis

    async def save_audio_analysis(
        self,
        db: AsyncSession,
        *,
        input_file_path: Optional[str],
        transcript: Optional[str],
        tone_prediction: EmotionPrediction,
        text_prediction: Optional[EmotionPrediction],
        fusion_output: FusionOutput,
        audio_duration_seconds: Optional[float],
    ) -> Analysis:
        analysis = Analysis(
            modality="audio",
            input_file_path=input_file_path,
            transcript=transcript,
            final_emotion=fusion_output.final_emotion,
            confidence=fusion_output.final_confidence,
            fusion_weights=fusion_output.fusion_weights,
            fusion_method=fusion_output.fusion_method,
        )
        analysis.audio_result = AudioResult(
            transcript=transcript,
            transcript_emotion=text_prediction.emotion if text_prediction else None,
            transcript_confidence=text_prediction.confidence
            if text_prediction
            else None,
            tone_emotion=tone_prediction.emotion,
            tone_confidence=tone_prediction.confidence,
            tone_probabilities=tone_prediction.probabilities,
            audio_duration_seconds=audio_duration_seconds,
            model_name=tone_prediction.model_name,
            inference_time_ms=tone_prediction.inference_time_ms,
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        logger.info(
            "repository.audio_analysis.saved", extra={"analysis_id": str(analysis.id)}
        )
        return analysis

    async def save_video_analysis(
        self,
        db: AsyncSession,
        *,
        input_file_path: Optional[str],
        facial_prediction: EmotionPrediction,
        audio_prediction: Optional[EmotionPrediction],
        text_prediction: Optional[EmotionPrediction],
        fusion_output: FusionOutput,
        frame_count: Optional[int],
        frame_emotions: Optional[List[Dict[str, Any]]],
        audio_duration_seconds: Optional[float],
        inference_time_ms: Optional[float],
    ) -> Analysis:
        analysis = Analysis(
            modality="video",
            input_file_path=input_file_path,
            final_emotion=fusion_output.final_emotion,
            confidence=fusion_output.final_confidence,
            fusion_weights=fusion_output.fusion_weights,
            fusion_method=fusion_output.fusion_method,
        )
        analysis.video_result = VideoResult(
            facial_emotion=facial_prediction.emotion,
            facial_confidence=facial_prediction.confidence,
            facial_probabilities=facial_prediction.probabilities,
            audio_emotion=audio_prediction.emotion if audio_prediction else None,
            audio_confidence=audio_prediction.confidence if audio_prediction else None,
            text_emotion=text_prediction.emotion if text_prediction else None,
            text_confidence=text_prediction.confidence if text_prediction else None,
            frame_count=frame_count,
            frame_emotions=frame_emotions,
            audio_duration_seconds=audio_duration_seconds,
            inference_time_ms=inference_time_ms,
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        logger.info(
            "repository.video_analysis.saved", extra={"analysis_id": str(analysis.id)}
        )
        return analysis

    async def list_history(
        self,
        db: AsyncSession,
        *,
        modality: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Analysis], int]:
        query = select(Analysis)
        count_query = select(func.count()).select_from(Analysis)

        if modality:
            query = query.where(Analysis.modality == modality)
            count_query = count_query.where(Analysis.modality == modality)

        query = query.order_by(Analysis.created_at.desc()).limit(limit).offset(offset)

        items = (await db.execute(query)).scalars().all()
        total = (await db.execute(count_query)).scalar_one()
        return list(items), total
