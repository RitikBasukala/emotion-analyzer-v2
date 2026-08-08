"""Standalone fusion router - HTTP transport only, no business logic.

Lets a client that already holds independently-computed unimodal
predictions (e.g. a live multi-modal dashboard) request just the fused
decision, without resubmitting raw media.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_fusion_service
from app.schemas.fusion import FusionRequest, FusionResult
from app.services.fusion_service import FusionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fuse", tags=["fusion"])


@router.post("", response_model=FusionResult)
async def fuse_predictions(
    payload: FusionRequest,
    service: FusionService = Depends(get_fusion_service),
) -> FusionResult:
    """Combine any subset of already-computed unimodal predictions."""
    if not any((payload.text_emotion, payload.audio_emotion, payload.facial_emotion)):
        raise HTTPException(
            status_code=422, detail="At least one modality prediction is required"
        )

    try:
        output = service.fuse(
            text_prediction=payload.text_emotion,
            audio_prediction=payload.audio_emotion,
            facial_prediction=payload.facial_emotion,
        )
        return service.to_schema(output)
    except Exception as exc:
        logger.exception("fuse.failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
