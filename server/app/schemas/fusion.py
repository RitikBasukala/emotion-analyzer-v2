"""Schemas for the multi-tier fusion mechanism."""

from typing import Dict, List, Optional

from pydantic import BaseModel

from app.schemas.common import EmotionPrediction


class ModalityContribution(BaseModel):
    """How much a single modality contributed to the final fused decision."""

    weight: float
    emotion: Optional[str] = None
    confidence: float
    contribution_to_final: float
    agreement: bool


class FusionTierBreakdown(BaseModel):
    """Explicit breakdown of the three fusion paradigms, exposed for observability.

    - early_fusion_vector: raw concatenation of every available modality's
      probability vector (Early Fusion).
    - mid_fusion_probabilities: output of the gated cross-modal projection
      that dynamically suppresses noisy/unreliable modalities (Mid-Level Fusion).
    - late_fusion_probabilities: soft-voting ensemble of independent
      unimodal decisions (Late Fusion).
    """

    early_fusion_vector: List[float]
    mid_fusion_probabilities: Dict[str, float]
    late_fusion_probabilities: Dict[str, float]


class FusionRequest(BaseModel):
    """Standalone fusion request: combine already-computed unimodal predictions."""

    text_emotion: Optional[EmotionPrediction] = None
    audio_emotion: Optional[EmotionPrediction] = None
    facial_emotion: Optional[EmotionPrediction] = None


class FusionResult(BaseModel):
    """Complete output of the fusion engine."""

    text_emotion: Optional[EmotionPrediction] = None
    audio_emotion: Optional[EmotionPrediction] = None
    facial_emotion: Optional[EmotionPrediction] = None
    final_emotion: str
    final_confidence: float
    final_probabilities: Dict[str, float]
    fusion_weights: Dict[str, float]
    fusion_method: str
    modality_contributions: Dict[str, ModalityContribution]
    tiers: FusionTierBreakdown
    inference_time_ms: float
