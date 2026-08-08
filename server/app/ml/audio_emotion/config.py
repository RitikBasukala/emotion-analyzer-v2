"""Configuration for the audio emotion model."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AudioEmotionConfig:
    """Audio emotion model configuration (transcription + acoustic tone)."""

    whisper_model: str = "openai/whisper-base"
    emotion_model: str = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
    emotion_model_path: Optional[str] = None
    device: str = "cpu"
    sample_rate: int = 16000
    max_audio_length_seconds: float = 30.0
    enabled: bool = True
