"""Text Emotion Model Service.

Loads the locally fine-tuned BERT/GoEmotions checkpoint shipped at
`app/ml/text_emotion/text_model/model.safetensors` via HuggingFace
Transformers' safetensors-native loading path (`from_pretrained` picks up
`.safetensors` automatically when present, avoiding pickle-based
deserialization entirely).

The checkpoint predicts 28 GoEmotions labels with a softmax head. The
service supports two output modes:
- `fine27`: return the 27 non-neutral emotions for direct text analysis.
- `coarse7`: aggregate the same checkpoint into the 7 shared coarse
    emotion classes used by fusion.
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

    @property
    def output_mode(self) -> str:
        return self.text_config.output_mode

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
            fine_probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()

        self._assert_softmax_outputs(fine_probs)

        inference_time_ms = (time.time() - start_time) * 1000

        if self.output_mode == "fine27":
            probabilities = self._fine27_distribution(fine_probs)
        elif self.output_mode == "coarse7":
            probabilities = self._aggregate_to_coarse(fine_probs)
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported text output mode: {self.output_mode}")

        predicted_emotion = max(probabilities, key=lambda label: probabilities[label])

        return EmotionPrediction(
            emotion=predicted_emotion,
            confidence=float(probabilities[predicted_emotion]),
            probabilities=probabilities,
            model_name=f"{self.config.model_name}:{self.output_mode}",
            inference_time_ms=inference_time_ms,
        )

    def _fine27_distribution(self, fine_probs: np.ndarray) -> Dict[str, float]:
        """Return the 27 non-neutral GoEmotions labels as a normalized distribution."""
        id2label = self.model.config.id2label
        probabilities: Dict[str, float] = {}

        for idx, fine_label in id2label.items():
            if fine_label.lower() == "neutral":
                continue
            probabilities[fine_label] = float(fine_probs[int(idx)])

        total = sum(probabilities.values())
        if total <= 0:
            return {label: 0.0 for label in probabilities}
        return {label: value / total for label, value in probabilities.items()}

    def _aggregate_to_coarse(self, fine_probs: np.ndarray) -> Dict[str, float]:
        """Map 28 GoEmotions outputs onto the 7 shared coarse labels.

        Each coarse bucket takes the summed activation of its constituent
        fine-grained labels, then the scores are renormalized so the result
        behaves like a 7-class probability distribution for fusion.
        """
        id2label = self.model.config.id2label
        coarse_scores = {label: 0.0 for label in EMOTION_LABELS}

        for idx, fine_label in id2label.items():
            coarse_label = self.text_config.goemotions_to_coarse.get(
                fine_label.lower(), "Neutral"
            )
            score = float(fine_probs[int(idx)])
            coarse_scores[coarse_label] += score

        if not any(coarse_scores.values()):
            return {label: 0.0 for label in EMOTION_LABELS}

        total = sum(coarse_scores.values())
        return {label: value / total for label, value in coarse_scores.items()}

    @staticmethod
    def _assert_softmax_outputs(fine_probs: np.ndarray) -> None:
        """Ensure the model outputs a normalized softmax distribution.

        This helps catch accidental sigmoid heads in tests and at runtime.
        """
        total = float(np.sum(fine_probs))
        if not np.isclose(total, 1.0, atol=1e-5):
            raise AssertionError(
                f"Expected softmax probabilities to sum to 1.0, got {total:.6f}"
            )
