"""Business logic for the video-modality pipeline.

Cascade: video frames -> facial micro-expression model, while the video's
audio track is extracted and run through the same audio cascade used by
`AudioEmotionService` (tone + Whisper transcript -> text model), giving
the video pipeline full temporal context from all three modalities before
the final multi-tier fusion - this is what lets the system disambiguate
complex mixed emotions (e.g. crying tears of joy while saying "I won!").
"""

import asyncio
import logging
import os
import tempfile
from typing import Optional

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.ml.facial_emotion import FacialEmotionModel
from app.schemas.common import EmotionPrediction
from app.schemas.video import VideoAnalysisResponse
from app.services.analysis_repository import AnalysisRepository
from app.services.audio_service import AudioEmotionService
from app.services.fusion_service import FusionService

logger = logging.getLogger(__name__)


class VideoEmotionService:
    """Business logic layer for video (facial + cascaded audio/text) emotion analysis."""

    def __init__(
        self,
        model: FacialEmotionModel,
        audio_service: AudioEmotionService,
        fusion_service: FusionService,
        repository: AnalysisRepository,
        settings: Settings,
    ):
        self._model = model
        self._audio_service = audio_service
        self._fusion_service = fusion_service
        self._repository = repository
        self._settings = settings

    async def _persist_upload(self, file: UploadFile, suffix: str) -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, dir=str(self._settings.upload_path))
        os.close(fd)

        async with aiofiles.open(path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                await out_file.write(chunk)
        return path

    async def _extract_audio_track(self, video_path: str) -> Optional[str]:
        """Extract the audio track from the video via ffmpeg, offloaded to a thread.

        Returns None (instead of raising) when the video has no audio
        track or `ffmpeg` is unavailable in the current environment, so
        the facial-only pipeline can still complete gracefully.
        """

        def _extract() -> Optional[str]:
            import ffmpeg

            audio_path = os.path.join(
                self._settings.upload_path, f"{os.path.basename(video_path)}.wav"
            )
            try:
                (
                    ffmpeg.input(video_path)
                    .output(
                        audio_path,
                        ac=1,
                        ar=self._settings.audio_sample_rate,
                        format="wav",
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                return audio_path
            except Exception:
                logger.warning(
                    "video_service.audio_extraction_failed",
                    extra={"video_path": video_path},
                )
                return None

        return await asyncio.to_thread(_extract)

    async def analyze(
        self, db: AsyncSession, *, file: UploadFile
    ) -> VideoAnalysisResponse:
        suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
        video_path = await self._persist_upload(file, suffix)
        extracted_audio_path: Optional[str] = None
        logger.info("video_service.analyze.start", extra={"path": video_path})

        try:
            facial_results = await asyncio.to_thread(
                self._model.analyze_video, video_path
            )
            facial_prediction = EmotionPrediction(
                emotion=facial_results["aggregated_emotion"],
                confidence=facial_results["confidence"],
                probabilities=facial_results["aggregated_probabilities"],
                model_name=self._model.config.model_name,
                inference_time_ms=facial_results["inference_time_ms"],
            )

            audio_prediction: Optional[EmotionPrediction] = None
            text_prediction: Optional[EmotionPrediction] = None
            transcript: Optional[str] = None
            audio_duration_seconds: Optional[float] = None

            extracted_audio_path = await self._extract_audio_track(video_path)
            if extracted_audio_path:
                audio_results = await self._audio_service.analyze_tone_and_transcript(
                    extracted_audio_path
                )
                audio_prediction = audio_results["tone_emotion"]
                transcript = audio_results.get("transcription") or None
                audio_duration_seconds = audio_results.get("audio_duration_seconds")
                if transcript:
                    text_prediction = (
                        await self._audio_service.predict_text_from_transcript(
                            transcript
                        )
                    )
            else:
                logger.info("video_service.no_audio_track", extra={"path": video_path})

            fusion_output = self._fusion_service.fuse(
                text_prediction=text_prediction,
                audio_prediction=audio_prediction,
                facial_prediction=facial_prediction,
            )

            record = await self._repository.save_video_analysis(
                db,
                input_file_path=video_path,
                facial_prediction=facial_prediction,
                audio_prediction=audio_prediction,
                text_prediction=text_prediction,
                fusion_output=fusion_output,
                frame_count=facial_results["frame_count"],
                frame_emotions=facial_results["frame_emotions"],
                audio_duration_seconds=audio_duration_seconds,
                inference_time_ms=facial_results["inference_time_ms"],
            )

            logger.info(
                "video_service.analyze.complete",
                extra={
                    "analysis_id": str(record.id),
                    "emotion": fusion_output.final_emotion,
                },
            )

            return VideoAnalysisResponse(
                analysis_id=record.id,
                transcript=transcript,
                facial_emotion=facial_prediction,
                audio_emotion=audio_prediction,
                text_emotion=text_prediction,
                fusion=self._fusion_service.to_schema(fusion_output),
                frame_count=facial_results["frame_count"],
                frame_emotions=facial_results["frame_emotions"],
                audio_duration_seconds=audio_duration_seconds,
                created_at=record.created_at,
            )
        finally:
            self._cleanup(video_path)
            if extracted_audio_path:
                self._cleanup(extracted_audio_path)

    @staticmethod
    def _cleanup(path: str) -> None:
        try:
            os.unlink(path)
        except OSError:
            logger.warning("video_service.cleanup_failed", extra={"path": path})
