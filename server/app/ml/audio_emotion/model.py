"""Audio Emotion Model Service.

Combines two independently swappable HuggingFace models:
1. Whisper - speech-to-text transcription, cascaded into the text pipeline.
2. Wav2Vec2 - acoustic tone/pitch/velocity representation for emotion.

The Wav2Vec2 backbone here ships without a fine-tuned classification head
(no labeled acoustic-emotion checkpoint was provided for this project), so
we attach a small fixed-seed linear projection head on top of its pooled
hidden state to produce a deterministic, reproducible 7-way distribution.
This is clearly a placeholder pending a properly fine-tuned head — swap
`_ProjectionHead` for a trained classifier without touching any caller.
"""

import logging
import time
from typing import Any, Dict, Tuple

import numpy as np
import torch
import torch.nn as nn

from app.ml.audio_emotion.config import AudioEmotionConfig
from app.ml.base import BaseModelService, ModelConfig
from app.schemas.common import EMOTION_LABELS, EmotionPrediction

logger = logging.getLogger(__name__)


class _ProjectionHead(nn.Module):
    """Deterministic placeholder classification head over pooled Wav2Vec2 features."""

    def __init__(self, hidden_size: int, num_classes: int, seed: int = 42):
        super().__init__()
        generator = torch.Generator().manual_seed(seed)
        linear = nn.Linear(hidden_size, num_classes)
        with torch.no_grad():
            nn.init.xavier_uniform_(linear.weight, generator=generator)
            linear.bias.zero_()
        self.linear = linear

    def forward(self, pooled_hidden_state: torch.Tensor) -> torch.Tensor:
        return torch.softmax(self.linear(pooled_hidden_state), dim=-1)


class AudioEmotionModel(BaseModelService):
    """Audio-based emotion recognition: transcription + acoustic tone analysis."""

    def __init__(self, config: AudioEmotionConfig):
        super().__init__(
            ModelConfig(
                model_name=config.emotion_model,
                model_path=config.emotion_model_path,
                device=config.device,
                enabled=config.enabled,
            )
        )
        self.audio_config = config
        self.whisper_model = None
        self.whisper_processor = None
        self.emotion_processor = None
        self.emotion_backbone = None
        self.projection_head: _ProjectionHead | None = None

    def load_model(self) -> None:
        try:
            from transformers import (
                AutoProcessor,
                Wav2Vec2Model,
                WhisperForConditionalGeneration,
                WhisperProcessor,
            )

            self.whisper_processor = WhisperProcessor.from_pretrained(
                self.audio_config.whisper_model
            )
            whisper_model = WhisperForConditionalGeneration.from_pretrained(
                self.audio_config.whisper_model
            )
            whisper_model.to(self.config.device)  # type: ignore[misc] - torch Module.to() stub artifact
            whisper_model.eval()
            self.whisper_processor = WhisperProcessor.from_pretrained(
                self.audio_config.whisper_model
            )
            self.whisper_model = whisper_model

            model_name = self.config.model_path or self.config.model_name
            emotion_backbone = Wav2Vec2Model.from_pretrained(model_name)
            emotion_backbone.to(self.config.device)  # type: ignore[misc] - torch Module.to() stub artifact
            emotion_backbone.eval()
            self.emotion_processor = AutoProcessor.from_pretrained(model_name)
            self.emotion_backbone = emotion_backbone

            self.projection_head = _ProjectionHead(
                hidden_size=self.emotion_backbone.config.hidden_size,
                num_classes=len(EMOTION_LABELS),
            ).to(self.config.device)
            self.projection_head.eval()

            self._initialized = True
        except Exception as exc:  # pragma: no cover - defensive, fail loudly
            self._initialized = False
            logger.exception("audio_model.load.failed")
            raise RuntimeError(f"Failed to load audio emotion model: {exc}") from exc

    def preprocess(self, raw_input: str) -> Tuple[np.ndarray, int]:
        """Load + trim + length-cap an audio file. `raw_input` is a filesystem path."""
        import librosa

        audio, sr = librosa.load(raw_input, sr=self.audio_config.sample_rate, mono=True)
        audio, _ = librosa.effects.trim(audio)
        sr = int(sr)

        max_samples = int(self.audio_config.max_audio_length_seconds * sr)
        if len(audio) > max_samples:
            audio = audio[:max_samples]

        return audio, sr

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio to text via Whisper, cascaded into the text pipeline."""
        self.ensure_loaded()
        assert self.whisper_processor is not None and self.whisper_model is not None

        inputs = self.whisper_processor(
            audio, sampling_rate=self.audio_config.sample_rate, return_tensors="pt"
        )
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_ids = self.whisper_model.generate(**inputs)
            first_sequence = (
                generated_ids[0]
                if not isinstance(generated_ids, dict)
                else generated_ids
            )
            transcription = self.whisper_processor.decode(
                first_sequence, skip_special_tokens=True
            )

        return transcription.strip()

    def analyze_tone(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze acoustic tone/pitch/velocity emotion signal from raw audio."""
        self.ensure_loaded()
        assert self.emotion_processor is not None and self.emotion_backbone is not None
        assert self.projection_head is not None

        inputs = self.emotion_processor(
            audio, sampling_rate=self.audio_config.sample_rate, return_tensors="pt"
        )
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        with torch.no_grad():
            hidden_states = self.emotion_backbone(**inputs).last_hidden_state.mean(
                dim=1
            )
            probs = self.projection_head(hidden_states)[0].cpu().numpy()

        return {label: float(p) for label, p in zip(EMOTION_LABELS, probs)}

    def predict(self, input_data: str) -> EmotionPrediction:
        """Analyze acoustic-tone emotion only (no transcription)."""
        self.ensure_loaded()

        start_time = time.time()
        audio, _ = self.preprocess(input_data)
        tone_probs = self.analyze_tone(audio)
        inference_time_ms = (time.time() - start_time) * 1000

        predicted_emotion = max(tone_probs, key=lambda label: tone_probs[label])
        return EmotionPrediction(
            emotion=predicted_emotion,
            confidence=tone_probs[predicted_emotion],
            probabilities=tone_probs,
            model_name=self.config.model_name,
            inference_time_ms=inference_time_ms,
        )

    def full_analysis(self, audio_path: str) -> Dict[str, Any]:
        """Complete audio analysis: transcription + acoustic tone in one pass."""
        self.ensure_loaded()

        start_time = time.time()
        audio, sr = self.preprocess(audio_path)

        transcription = self.transcribe(audio)
        tone_prediction = self.predict(audio_path)

        total_time_ms = (time.time() - start_time) * 1000

        return {
            "transcription": transcription,
            "tone_emotion": tone_prediction,
            "audio_duration_seconds": len(audio) / sr,
            "total_inference_time_ms": total_time_ms,
        }
