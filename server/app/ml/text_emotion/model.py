"""Text Emotion Model Service.

Loads the locally fine-tuned BERT/GoEmotions checkpoint shipped at
`app/ml/text_emotion/text_model/model.safetensors` via HuggingFace
Transformers' safetensors-native loading path (`from_pretrained` picks up
`.safetensors` automatically when present, avoiding pickle-based
deserialization entirely).

The checkpoint predicts 28 fine-grained GoEmotions labels using a sigmoid
(multi-label) head. We aggregate those into the 7 coarse emotion classes
shared by every modality and the fusion engine.
"""

import logging
import time
from typing import Dict

import numpy as np
import torch

from app.ml.base import BaseModelService, ModelConfig
from app.ml.text_emotion.config import TextEmotionConfig
from app.schemas.common import EMOTION_LABELS, EmotionPrediction

logger = logging.getLogger(__name__)


class TextEmotionModel(BaseModelService):
    """Text-based emotion recognition model (local safetensors checkpoint)."""

    def __init__(self, config: TextEmotionConfig):
        super().__init__(
            ModelConfig(
                model_name="goemotions-bert-local",
                model_path=config.model_path,
                device=config.device,
                enabled=config.enabled,
            )
        )
        self.text_config = config
        self.tokenizer = None

    def load_model(self) -> None:
        """Load tokenizer + safetensors weights from the local checkpoint directory."""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            model_path = self.text_config.model_path
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            # `from_pretrained` transparently prefers `model.safetensors` over
            # any `.bin` weights when both are present in the checkpoint dir.
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.config.device)
            self.model.eval()
            self._initialized = True
        except Exception as exc:  # pragma: no cover - defensive, fail loudly
            self._initialized = False
            logger.exception(
                "text_model.load.failed",
                extra={"model_path": self.text_config.model_path},
            )
            raise RuntimeError(
                f"Failed to load text emotion model from safetensors checkpoint: {exc}"
            ) from exc

    def preprocess(self, raw_input: str) -> Dict[str, torch.Tensor]:
        assert self.tokenizer is not None
        if not isinstance(raw_input, str):
            raw_input = str(raw_input)

        encoded = self.tokenizer(
            raw_input,
            padding=True,
            truncation=True,
            max_length=self.text_config.max_length,
            return_tensors="pt",
        )
        return {k: v.to(self.config.device) for k, v in encoded.items()}

    def predict(self, input_data: str) -> EmotionPrediction:
        """Analyze emotion in a text string.

        Args:
            input_data: Raw text (user input, or a transcript cascaded
                from the audio/video pipelines).
        """
        self.ensure_loaded()
        assert self.model is not None and self.tokenizer is not None

        start_time = time.time()
        inputs = self.preprocess(input_data)

        with torch.no_grad():
            logits = self.model(**inputs).logits
            # The checkpoint's `problem_type` is `multi_label_classification`,
            # so each fine-grained label gets its own independent sigmoid
            # probability rather than a single softmax distribution.
            fine_probs = torch.sigmoid(logits)[0].cpu().numpy()

        inference_time_ms = (time.time() - start_time) * 1000

        coarse_probs = self._aggregate_to_coarse(fine_probs)
        predicted_emotion = max(coarse_probs, key=lambda label: coarse_probs[label])

        return EmotionPrediction(
            emotion=predicted_emotion,
            confidence=float(coarse_probs[predicted_emotion]),
            probabilities=coarse_probs,
            model_name=self.config.model_name,
            inference_time_ms=inference_time_ms,
        )

    def _aggregate_to_coarse(self, fine_probs: np.ndarray) -> Dict[str, float]:
        """Map 28 GoEmotions sigmoid outputs onto the 7 shared coarse labels.

        Each coarse bucket takes the *max* activation among its constituent
        fine-grained labels (a bucket is "active" if any of its underlying
        emotions fired). The resulting coarse scores remain independent
        sigmoid probabilities rather than being renormalized into a single
        distribution, so the text UI can show the strength of each emotion
        directly.
        """
        id2label = self.model.config.id2label
        coarse_scores = {label: 0.0 for label in EMOTION_LABELS}

        for idx, fine_label in id2label.items():
            coarse_label = self.text_config.goemotions_to_coarse.get(
                fine_label.lower(), "Neutral"
            )
            score = float(fine_probs[int(idx)])
            if score > coarse_scores[coarse_label]:
                coarse_scores[coarse_label] = score

        if not any(coarse_scores.values()):
            return {label: 0.0 for label in EMOTION_LABELS}

        return coarse_scores
