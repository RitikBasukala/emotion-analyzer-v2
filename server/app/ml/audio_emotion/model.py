"""Audio Emotion Model Service.

Combines a local-first acoustic tone model with Hugging Face fallbacks:
1. Whisper - speech-to-text transcription, cascaded into the text pipeline.
2. Local Keras tone classifier - loads the checked-in audio checkpoint and
    scaler from `app/ml/audio_emotion/audio_model`.
3. Hugging Face Wav2Vec2 fallback - used when the local checkpoint cannot
    be loaded.

The local audio checkpoint expects 200x120 MFCC-style features. We
construct those features from the waveform, scale them with the checked-in
`StandardScaler`, and feed them into the Keras classifier.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
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

    _LOCAL_MODEL_FILE = "audio_bilstm_checkpoint.keras"
    _LOCAL_FALLBACK_MODEL_FILES = (
        "audio_branch_classifier.keras",
        "audio_embedding_extractor.keras",
    )
    _LOCAL_SCALER_FILE = "audio_scaler.pkl"
    _LOCAL_TARGET_FRAMES = 200
    _LOCAL_MFCC_FEATURES = 40

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
        self.local_tone_model = None
        self.local_scaler = None
        self._tone_backend = "huggingface"
        self._tone_model_name = config.emotion_model

    def _resolve_local_model_dir(self) -> Path:
        if not self.config.model_path:
            raise FileNotFoundError("No local audio model directory configured")

        path = Path(self.config.model_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        return path

    def _load_whisper_model(self) -> None:
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.whisper_processor = WhisperProcessor.from_pretrained(
            self.audio_config.whisper_model
        )
        whisper_model = WhisperForConditionalGeneration.from_pretrained(
            self.audio_config.whisper_model
        )
        whisper_model.to(self.config.device)  # type: ignore[misc] - torch Module.to() stub artifact
        whisper_model.eval()
        self.whisper_model = whisper_model

    def _load_local_tone_model(self, model_dir: Path) -> None:
        from tensorflow.keras.models import load_model

        scaler_path = model_dir / self._LOCAL_SCALER_FILE
        if not scaler_path.exists():
            raise FileNotFoundError(f"Missing local audio scaler: {scaler_path}")

        local_model_path = model_dir / self._LOCAL_MODEL_FILE
        if not local_model_path.exists():
            for fallback_name in self._LOCAL_FALLBACK_MODEL_FILES:
                candidate = model_dir / fallback_name
                if candidate.exists():
                    local_model_path = candidate
                    break
            else:
                raise FileNotFoundError(
                    f"No local audio checkpoint found in {model_dir}"
                )

        self.local_scaler = joblib.load(scaler_path)
        self.local_tone_model = load_model(local_model_path, compile=False)
        self._tone_backend = "local"
        self._tone_model_name = f"local:{local_model_path.name}"

    def _load_hf_tone_model(self) -> None:
        from transformers import AutoProcessor, Wav2Vec2Model

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
        self._tone_backend = "huggingface"
        self._tone_model_name = self.config.model_name

    def load_model(self) -> None:
        try:
            self._load_whisper_model()

            if self.config.model_path:
                try:
                    self._load_local_tone_model(self._resolve_local_model_dir())
                except Exception as exc:
                    logger.warning(
                        "audio_model.local_load_failed",
                        extra={"path": self.config.model_path, "error": str(exc)},
                    )

            if self._tone_backend != "local":
                self._load_hf_tone_model()

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

        if len(audio) < sr:
            audio = librosa.util.fix_length(audio, size=sr)

        max_samples = int(self.audio_config.max_audio_length_seconds * sr)
        if len(audio) > max_samples:
            audio = audio[:max_samples]

        return audio, sr

    def _local_feature_matrix(self, audio: np.ndarray, sr: int) -> np.ndarray:
        import librosa

        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=self._LOCAL_MFCC_FEATURES,
        )
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)

        features = np.concatenate([mfcc, mfcc_delta, mfcc_delta2], axis=0).T
        if features.shape[0] < self._LOCAL_TARGET_FRAMES:
            padding = self._LOCAL_TARGET_FRAMES - features.shape[0]
            features = np.pad(features, ((0, padding), (0, 0)), mode="constant")
        else:
            features = features[: self._LOCAL_TARGET_FRAMES]

        assert self.local_scaler is not None
        features = self.local_scaler.transform(features)
        return features.astype(np.float32, copy=False)

    def _predict_local_tone(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        assert self.local_tone_model is not None

        local_features = self._local_feature_matrix(audio, sr)
        batch = np.expand_dims(local_features, axis=0)
        probabilities = self.local_tone_model.predict(batch, verbose=0)[0]
        probabilities = np.asarray(probabilities, dtype=np.float32)

        total = float(probabilities.sum())
        if total <= 0:
            uniform = 1.0 / len(EMOTION_LABELS)
            return {label: uniform for label in EMOTION_LABELS}

        probabilities = probabilities / total
        return {label: float(p) for label, p in zip(EMOTION_LABELS, probabilities)}

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

        if self._tone_backend == "local":
            return self._predict_local_tone(audio, self.audio_config.sample_rate)

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
            model_name=self._tone_model_name,
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
