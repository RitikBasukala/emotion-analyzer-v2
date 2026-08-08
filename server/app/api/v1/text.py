"""Text modality router - HTTP transport only, no business logic."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_text_service
from app.db.session import get_db
from app.schemas.text import TextAnalysisResponse, TextAnalyzeRequest
from app.services.text_service import TextEmotionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/text", tags=["text"])


@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    payload: TextAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    service: TextEmotionService = Depends(get_text_service),
) -> TextAnalysisResponse:
    """Analyze emotion in a raw text string."""
    try:
        return await service.analyze(db, text=payload.text)
    except RuntimeError as exc:
        logger.exception("text.analyze.model_error")
        raise HTTPException(
            status_code=503, detail=f"Text model unavailable: {exc}"
        ) from exc
    except Exception as exc:
        logger.exception("text.analyze.failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
