"""Business logic for the multi-tier fusion mechanism."""

import logging
from typing import Optional

from app.ml.fusion import FusionEngine, FusionOutput
from app.schemas.common import EmotionPrediction
from app.schemas.fusion import FusionResult, FusionTierBreakdown, ModalityContribution

logger = logging.getLogger(__name__)


class FusionService:
    """Wraps the `FusionEngine` and translates its domain output into the API schema."""

    def __init__(self, engine: FusionEngine):
        self._engine = engine

    def fuse(
        self,
        *,
        text_prediction: Optional[EmotionPrediction] = None,
        audio_prediction: Optional[EmotionPrediction] = None,
        facial_prediction: Optional[EmotionPrediction] = None,
    ) -> FusionOutput:
        """Run the fusion engine. Returns the plain domain result.

        Kept separate from `to_schema` so callers persisting to the
        database (audio/video services) can use the domain object without
        forcing a schema round-trip.
        """
        logger.info(
            "fusion.start",
            extra={
                "has_text": text_prediction is not None,
                "has_audio": audio_prediction is not None,
                "has_facial": facial_prediction is not None,
            },
        )
        return self._engine.fuse(
            text_prediction=text_prediction,
            audio_prediction=audio_prediction,
            facial_prediction=facial_prediction,
        )

    @staticmethod
    def to_schema(output: FusionOutput) -> FusionResult:
        """Translate the ML-layer `FusionOutput` dataclass into the API `FusionResult` schema."""
        return FusionResult(
            text_emotion=output.text_emotion,
            audio_emotion=output.audio_emotion,
            facial_emotion=output.facial_emotion,
            final_emotion=output.final_emotion,
            final_confidence=output.final_confidence,
            final_probabilities=output.final_probabilities,
            fusion_weights=output.fusion_weights,
            fusion_method=output.fusion_method,
            modality_contributions={
                modality: ModalityContribution(
                    weight=contribution.weight,
                    emotion=contribution.emotion,
                    confidence=contribution.confidence,
                    contribution_to_final=contribution.contribution_to_final,
                    agreement=contribution.agreement,
                )
                for modality, contribution in output.modality_contributions.items()
            },
            tiers=FusionTierBreakdown(
                early_fusion_vector=output.early_fusion_vector,
                mid_fusion_probabilities=output.mid_fusion_probabilities,
                late_fusion_probabilities=output.late_fusion_probabilities,
            ),
            inference_time_ms=output.inference_time_ms,
        )
