"""Video modality router - HTTP transport only, no business logic."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_settings, get_video_service
from app.core.config import Settings
from app.db.session import get_db
from app.schemas.video import VideoAnalysisResponse
from app.services.video_service import VideoEmotionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/video", tags=["video"])


@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: VideoEmotionService = Depends(get_video_service),
    settings: Settings = Depends(get_settings),
) -> VideoAnalysisResponse:
    """Analyze facial micro-expressions (+ cascaded audio/text) in an uploaded video file."""
    if file.size and file.size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
        )

    try:
        return await service.analyze(db, file=file)
    except RuntimeError as exc:
        logger.exception("video.analyze.model_error")
        raise HTTPException(
            status_code=503, detail=f"Video model unavailable: {exc}"
        ) from exc
    except Exception as exc:
        logger.exception("video.analyze.failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
