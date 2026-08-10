"""Multi-Tier Fusion Engine for Multimodal Emotion Recognition.

Implements three complementary fusion paradigms and combines them, since
"no single fusion strategy universally dominates across datasets, noise
levels, or modality imbalance conditions":

- Early Fusion: raw concatenation of every available modality's
  probability vector into a single joint representation.
- Mid-Level Fusion: a gated cross-modal projection (`GatedFusionLayer`)
  that dynamically suppresses noisy/unreliable modalities before they are
  combined.
- Late Fusion: a soft-voting ensemble of independent unimodal decisions,
  weighted by configurable per-modality reliability weights.

The final decision blends the mid-level and late-fusion tiers. The early
tier is retained purely for observability/analytics: this project has no
separately trained joint classifier head consuming the raw concatenated
vector, so it deliberately isn't part of the class decision itself -
exposing it lets the API/UI still show what a joint early-fusion
representation would look like.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import torch
import torch.nn as nn

from app.ml.fusion.config import FusionConfig
from app.schemas.common import EMOTION_LABELS, EmotionPrediction

logger = logging.getLogger(__name__)

_MODALITIES = ("text", "audio", "facial")


@dataclass(frozen=True)
class ModalityContributionData:
    weight: float
    emotion: Optional[str]
    confidence: float
    contribution_to_final: float
    agreement: bool


@dataclass(frozen=True)
class FusionOutput:
    """Plain domain result of the fusion engine (translated to an API schema in the service layer)."""

    final_emotion: str
    final_confidence: float
    final_probabilities: Dict[str, float]
    fusion_weights: Dict[str, float]
    fusion_method: str
    modality_contributions: Dict[str, ModalityContributionData]
    early_fusion_vector: List[float]
    mid_fusion_probabilities: Dict[str, float]
    late_fusion_probabilities: Dict[str, float]
    inference_time_ms: float
    text_emotion: Optional[EmotionPrediction] = None
    audio_emotion: Optional[EmotionPrediction] = None
    facial_emotion: Optional[EmotionPrediction] = None


class GatedFusionLayer(nn.Module):
    """Learned gate deciding, per modality, how much to trust its probability vector.

    Mirrors the mid-level "feature-transformation" fusion strategy that
    dynamically suppresses noisy modalities and highlights informative
    ones. Weights are fixed-seed initialized (deterministic) placeholders
    pending supervised fine-tuning on labeled multimodal data; swapping in
    trained weights requires no change to any caller.
    """

    def __init__(self, num_classes: int, num_modalities: int = 3, seed: int = 7):
        super().__init__()
        generator = torch.Generator().manual_seed(seed)

        linear_projections = [
            nn.Linear(num_classes, num_classes) for _ in range(num_modalities)
        ]
        gate_layer = nn.Linear(num_classes * num_modalities, num_modalities)

        with torch.no_grad():
            for projection in linear_projections:
                nn.init.xavier_uniform_(projection.weight, generator=generator)
                projection.bias.zero_()
            nn.init.xavier_uniform_(gate_layer.weight, generator=generator)
            gate_layer.bias.zero_()

        self.projections = nn.ModuleList(linear_projections)
        self.gate = gate_layer

    def forward(
        self, modality_vectors: torch.Tensor, availability_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            modality_vectors: (num_modalities, num_classes) probability vectors,
                zero-filled for unavailable modalities.
            availability_mask: (num_modalities,) 1.0 if available, else 0.0.

        Returns:
            (num_classes,) gated + renormalized probability distribution.
        """
        projected = torch.stack(
            [
                torch.softmax(proj(vec), dim=-1)
                for proj, vec in zip(self.projections, modality_vectors)
            ]
        )  # (num_modalities, num_classes)

        concat = projected.flatten()
        raw_gates = self.gate(concat)
        # Mask out unavailable modalities before softmax so they get exactly
        # zero gate weight instead of competing for probability mass.
        raw_gates = raw_gates.masked_fill(availability_mask == 0, float("-inf"))
        gates = torch.softmax(raw_gates, dim=-1)  # (num_modalities,)

        gated = (projected * gates.unsqueeze(-1)).sum(dim=0)  # (num_classes,)
        total = gated.sum()
        if total <= 0:
            return torch.full_like(gated, 1.0 / gated.numel())
        return gated / total


class FusionEngine:
    """Multi-tier fusion engine combining Early, Mid-Level, and Late Fusion."""

    def __init__(self, config: Optional[FusionConfig] = None):
        self.config = config or FusionConfig()
        self.emotions = EMOTION_LABELS
        self._gated_layer = GatedFusionLayer(
            num_classes=len(self.emotions), num_modalities=len(_MODALITIES)
        )
        self._gated_layer.eval()

    def fuse(
        self,
        text_prediction: Optional[EmotionPrediction] = None,
        audio_prediction: Optional[EmotionPrediction] = None,
        facial_prediction: Optional[EmotionPrediction] = None,
    ) -> FusionOutput:
        start_time = time.time()

        predictions: Dict[str, Optional[EmotionPrediction]] = {
            "text": text_prediction,
            "audio": audio_prediction,
            "facial": facial_prediction,
        }

        if not any(predictions.values()):
            raise ValueError("fuse() requires at least one modality prediction")

        weights = self._effective_weights(predictions)

        early_vector = self._early_fusion(predictions)
        mid_probs = self._mid_level_fusion(predictions)
        late_probs = self._late_fusion(predictions, weights)

        if self.config.fusion_method in {"cross_attention", "multi_tier"}:
            blend = self.config.mid_late_blend
            final_probs = {
                label: blend * mid_probs[label] + (1 - blend) * late_probs[label]
                for label in self.emotions
            }
        elif self.config.fusion_method == "weighted_average":
            # Late fusion / soft-voting ensemble only.
            final_probs = late_probs
        else:
            raise ValueError(f"Unsupported fusion_method: {self.config.fusion_method}")

        total = sum(final_probs.values())
        if total > 0:
            final_probs = {k: v / total for k, v in final_probs.items()}

        final_emotion = max(final_probs, key=lambda label: final_probs[label])
        final_confidence = final_probs[final_emotion]

        contributions = self._modality_contributions(
            predictions, weights, final_emotion
        )
        inference_time_ms = (time.time() - start_time) * 1000

        logger.info(
            "fusion.complete",
            extra={
                "final_emotion": final_emotion,
                "modalities": [m for m, p in predictions.items() if p is not None],
                "fusion_method": self.config.fusion_method,
            },
        )

        return FusionOutput(
            text_emotion=text_prediction,
            audio_emotion=audio_prediction,
            facial_emotion=facial_prediction,
            final_emotion=final_emotion,
            final_confidence=final_confidence,
            final_probabilities=final_probs,
            fusion_weights=weights,
            fusion_method=self.config.fusion_method,
            modality_contributions=contributions,
            early_fusion_vector=early_vector,
            mid_fusion_probabilities=mid_probs,
            late_fusion_probabilities=late_probs,
            inference_time_ms=inference_time_ms,
        )

    # ------------------------------------------------------------------
    # Early Fusion: feature concatenation
    # ------------------------------------------------------------------
    def _early_fusion(
        self, predictions: Dict[str, Optional[EmotionPrediction]]
    ) -> List[float]:
        vector: List[float] = []
        for modality in _MODALITIES:
            pred = predictions[modality]
            if pred is not None:
                vector.extend(
                    pred.probabilities.get(label, 0.0) for label in self.emotions
                )
        return vector

    # ------------------------------------------------------------------
    # Mid-Level Fusion: gated transformer-style projection
    # ------------------------------------------------------------------
    def _mid_level_fusion(
        self, predictions: Dict[str, Optional[EmotionPrediction]]
    ) -> Dict[str, float]:
        vectors, mask = [], []
        for modality in _MODALITIES:
            pred = predictions[modality]
            if pred is not None:
                vectors.append(
                    [pred.probabilities.get(label, 0.0) for label in self.emotions]
                )
                mask.append(1.0)
            else:
                vectors.append([0.0] * len(self.emotions))
                mask.append(0.0)

        modality_tensor = torch.tensor(vectors, dtype=torch.float32)
        mask_tensor = torch.tensor(mask, dtype=torch.float32)

        with torch.no_grad():
            gated = self._gated_layer(modality_tensor, mask_tensor)

        return {label: float(p) for label, p in zip(self.emotions, gated.tolist())}

    # ------------------------------------------------------------------
    # Late Fusion: soft-voting ensemble
    # ------------------------------------------------------------------
    def _late_fusion(
        self,
        predictions: Dict[str, Optional[EmotionPrediction]],
        weights: Dict[str, float],
    ) -> Dict[str, float]:
        combined = {label: 0.0 for label in self.emotions}
        for modality, pred in predictions.items():
            if pred is None:
                continue
            weight = weights[modality]
            for label in self.emotions:
                combined[label] += pred.probabilities.get(label, 0.0) * weight

        total = sum(combined.values())
        if total <= 0:
            uniform = 1.0 / len(self.emotions)
            return {label: uniform for label in self.emotions}
        return {label: v / total for label, v in combined.items()}

    # ------------------------------------------------------------------
    # Weighting & explainability helpers
    # ------------------------------------------------------------------
    def _effective_weights(
        self, predictions: Dict[str, Optional[EmotionPrediction]]
    ) -> Dict[str, float]:
        available = {
            modality: pred is not None for modality, pred in predictions.items()
        }
        base_weights = {
            "text": self.config.text_weight,
            "audio": self.config.audio_weight,
            "facial": self.config.facial_weight,
        }
        adjusted = {
            modality: (weight if available[modality] else 0.0)
            for modality, weight in base_weights.items()
        }

        total = sum(adjusted.values())
        if total <= 0:
            n = len(_MODALITIES)
            return {modality: 1.0 / n for modality in _MODALITIES}
        return {modality: value / total for modality, value in adjusted.items()}

    def _modality_contributions(
        self,
        predictions: Dict[str, Optional[EmotionPrediction]],
        weights: Dict[str, float],
        final_emotion: str,
    ) -> Dict[str, ModalityContributionData]:
        contributions: Dict[str, ModalityContributionData] = {}
        for modality, pred in predictions.items():
            if pred is None:
                contributions[modality] = ModalityContributionData(
                    weight=0.0,
                    emotion=None,
                    confidence=0.0,
                    contribution_to_final=0.0,
                    agreement=False,
                )
                continue

            weight = weights[modality]
            contributions[modality] = ModalityContributionData(
                weight=weight,
                emotion=pred.emotion,
                confidence=pred.confidence,
                contribution_to_final=pred.probabilities.get(final_emotion, 0.0)
                * weight,
                agreement=pred.emotion == final_emotion,
            )
        return contributions

    def get_weights(self) -> Dict[str, float]:
        return {
            "text": self.config.text_weight,
            "audio": self.config.audio_weight,
            "facial": self.config.facial_weight,
        }
