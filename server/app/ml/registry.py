"""Model registry - constructs and caches every ML service exactly once.

This is the only place that translates central `Settings` into the
per-model config objects. Services obtain models through this registry
via FastAPI dependency injection (see `app.api.deps`), never by
instantiating model classes themselves.
"""

import logging

from app.core.config import Settings
from app.ml.audio_emotion import AudioEmotionConfig, AudioEmotionModel
from app.ml.facial_emotion import FacialEmotionConfig, FacialEmotionModel
from app.ml.fusion import FusionConfig, FusionEngine
from app.ml.text_emotion import TextEmotionConfig, TextEmotionModel

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Lazily-constructed, process-wide singleton holder for all ML services."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self.text = TextEmotionModel(
            TextEmotionConfig(
                model_path=str(settings.text_model_path),
                device=settings.device,
                max_length=settings.text_model_max_length,
            )
        )
        self.audio = AudioEmotionModel(
            AudioEmotionConfig(
                whisper_model=settings.audio_whisper_model,
                emotion_model=settings.audio_emotion_model,
                device=settings.device,
                sample_rate=settings.audio_sample_rate,
                max_audio_length_seconds=settings.audio_max_length_seconds,
            )
        )
        self.facial = FacialEmotionModel(
            FacialEmotionConfig(
                detector_backend=settings.facial_detector_backend,
                device=settings.device,
                frame_extraction_fps=settings.facial_frame_extraction_fps,
                max_frames=settings.facial_max_frames,
            )
        )
        self.fusion = FusionEngine(
            FusionConfig(
                text_weight=settings.fusion_text_weight,
                audio_weight=settings.fusion_audio_weight,
                facial_weight=settings.fusion_facial_weight,
                fusion_method=settings.fusion_method,
                mid_late_blend=settings.fusion_mid_late_blend,
            )
        )

    def preload(self) -> None:
        """Eagerly load every model (used at startup when `PRELOAD_MODELS=true`)."""
        for name, model in (
            ("text", self.text),
            ("audio", self.audio),
            ("facial", self.facial),
        ):
            try:
                model.ensure_loaded()
            except Exception:
                logger.exception("model_registry.preload_failed", extra={"model": name})


_registry: ModelRegistry | None = None


def get_model_registry(settings: Settings | None = None) -> ModelRegistry:
    """Return the process-wide model registry, constructing it on first use."""
    global _registry
    if _registry is None:
        from app.core.config import settings as default_settings

        _registry = ModelRegistry(settings or default_settings)
    return _registry
