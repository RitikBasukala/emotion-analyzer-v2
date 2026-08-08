"""Analysis history router - read-only transport over persisted analyses."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_repository
from app.db.session import get_db
from app.schemas.history import AnalysisHistoryItem, AnalysisHistoryResponse
from app.services.analysis_repository import AnalysisRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=AnalysisHistoryResponse)
async def get_history(
    modality: Optional[str] = Query(default=None, pattern="^(text|audio|video)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    repository: AnalysisRepository = Depends(get_repository),
) -> AnalysisHistoryResponse:
    """List previously persisted analyses, optionally filtered by modality."""
    try:
        records, total = await repository.list_history(
            db, modality=modality, limit=limit, offset=offset
        )
    except Exception as exc:
        logger.exception("history.list_failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    items = [
        AnalysisHistoryItem(
            id=record.id,
            modality=record.modality,
            final_emotion=record.final_emotion,
            confidence=record.confidence,
            created_at=record.created_at,
            input_preview=(record.input_text or record.transcript or "")[:100] or None,
        )
        for record in records
    ]
    return AnalysisHistoryResponse(items=items, total=total, limit=limit, offset=offset)
