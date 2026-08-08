"""Audio modality router - HTTP transport only, no business logic."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_audio_service, get_settings
from app.core.config import Settings
from app.db.session import get_db
from app.schemas.audio import AudioAnalysisResponse
from app.services.audio_service import AudioEmotionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audio", tags=["audio"])

_ALLOWED_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
}


@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: AudioEmotionService = Depends(get_audio_service),
    settings: Settings = Depends(get_settings),
) -> AudioAnalysisResponse:
    """Analyze tone + cascaded transcript emotion in an uploaded audio file."""
    if file.content_type and file.content_type not in _ALLOWED_CONTENT_TYPES:
        logger.warning(
            "audio.analyze.unexpected_content_type",
            extra={"content_type": file.content_type},
        )

    if file.size and file.size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
        )

    try:
        return await service.analyze(db, file=file)
    except RuntimeError as exc:
        logger.exception("audio.analyze.model_error")
        raise HTTPException(
            status_code=503, detail=f"Audio model unavailable: {exc}"
        ) from exc
    except Exception as exc:
        logger.exception("audio.analyze.failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
